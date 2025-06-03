#!/usr/bin/env python3
"""
Amazon Bedrock Knowledge Base Query Script

This script demonstrates how to query a Bedrock knowledge base using boto3.
It includes examples for both simple queries and advanced retrieval with metadata.

Requirements:
- boto3
- AWS credentials configured (via AWS CLI, environment variables, or IAM roles)
- Access to Amazon Bedrock service
- A configured knowledge base in your AWS account

Usage:
    python test.py
"""

import boto3
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class BedrockKnowledgeBaseClient:
    """Client for interacting with Amazon Bedrock Knowledge Base"""
    
    def __init__(self, region_name: str = "us-west-2"):
        """
        Initialize the Bedrock client
        
        Args:
            region_name: AWS region where your knowledge base is located
        """
        self.region_name = region_name
        
        # Initialize Bedrock Runtime client for knowledge base queries
        self.bedrock_agent_runtime = boto3.client(
            'bedrock-agent-runtime',
            region_name=region_name
        )
        
        # Initialize Bedrock Agent client for knowledge base management
        self.bedrock_agent = boto3.client(
            'bedrock-agent',
            region_name=region_name
        )
    
    def list_knowledge_bases(self) -> List[Dict[str, Any]]:
        """
        List all available knowledge bases in the account
        
        Returns:
            List of knowledge base information
        """
        try:
            response = self.bedrock_agent.list_knowledge_bases()
            return response.get('knowledgeBaseSummaries', [])
        except Exception as e:
            print(f"Error listing knowledge bases: {e}")
            return []
    
    def get_knowledge_base_info(self, knowledge_base_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific knowledge base
        
        Args:
            knowledge_base_id: The ID of the knowledge base
            
        Returns:
            Knowledge base details or None if not found
        """
        try:
            response = self.bedrock_agent.get_knowledge_base(
                knowledgeBaseId=knowledge_base_id
            )
            return response.get('knowledgeBase')
        except Exception as e:
            print(f"Error getting knowledge base info: {e}")
            return None
    
    def query_knowledge_base(
        self,
        knowledge_base_id: str,
        query: str,
        max_results: int = 5,
        next_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query the knowledge base for relevant information
        
        Args:
            knowledge_base_id: The ID of the knowledge base to query
            query: The search query
            max_results: Maximum number of results to return (1-100)
            next_token: Token for pagination
            
        Returns:
            Query results with retrieved documents and metadata
        """
        try:
            params = {
                'knowledgeBaseId': knowledge_base_id,
                'retrievalQuery': {
                    'text': query
                },
                'retrievalConfiguration': {
                    'vectorSearchConfiguration': {
                        'numberOfResults': max_results
                    }
                }
            }
            
            if next_token:
                params['nextToken'] = next_token
            
            response = self.bedrock_agent_runtime.retrieve(**params)
            return response
            
        except Exception as e:
            print(f"Error querying knowledge base: {e}")
            return {}
    
    def retrieve_and_generate(
        self,
        knowledge_base_id: str,
        query: str,
        model_arn: str = "arn:aws:bedrock:us-west-2::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0",
        max_results: int = 5
    ) -> Dict[str, Any]:
        """
        Retrieve information from knowledge base and generate a response using a foundation model
        
        Args:
            knowledge_base_id: The ID of the knowledge base
            query: The user query
            model_arn: ARN of the foundation model to use for generation
            max_results: Maximum number of documents to retrieve
            
        Returns:
            Generated response with source citations
        """
        try:
            response = self.bedrock_agent_runtime.retrieve_and_generate(
                input={
                    'text': query
                },
                retrieveAndGenerateConfiguration={
                    'type': 'KNOWLEDGE_BASE',
                    'knowledgeBaseConfiguration': {
                        'knowledgeBaseId': knowledge_base_id,
                        'modelArn': model_arn,
                        'retrievalConfiguration': {
                            'vectorSearchConfiguration': {
                                'numberOfResults': max_results
                            }
                        }
                    }
                }
            )
            return response
            
        except Exception as e:
            print(f"Error in retrieve and generate: {e}")
            return {}
    
    def format_query_results(self, results: Dict[str, Any]) -> str:
        """
        Format query results for display
        
        Args:
            results: Raw results from query_knowledge_base
            
        Returns:
            Formatted string representation
        """
        if not results or 'retrievalResults' not in results:
            return "No results found."
        
        formatted = []
        formatted.append("=" * 80)
        formatted.append("KNOWLEDGE BASE QUERY RESULTS")
        formatted.append("=" * 80)
        
        for i, result in enumerate(results['retrievalResults'], 1):
            formatted.append(f"\n--- Result {i} ---")
            
            # Content
            content = result.get('content', {}).get('text', 'No content available')
            formatted.append(f"Content: {content[:500]}{'...' if len(content) > 500 else ''}")
            
            # Score
            score = result.get('score', 0)
            formatted.append(f"Relevance Score: {score:.4f}")
            
            # Location (source)
            location = result.get('location', {})
            if location:
                location_type = location.get('type', 'Unknown')
                formatted.append(f"Source Type: {location_type}")
                
                if location_type == 'S3':
                    s3_location = location.get('s3Location', {})
                    bucket = s3_location.get('uri', 'Unknown')
                    formatted.append(f"S3 Location: {bucket}")
            
            # Metadata
            metadata = result.get('metadata', {})
            if metadata:
                formatted.append("Metadata:")
                for key, value in metadata.items():
                    formatted.append(f"  {key}: {value}")
        
        return "\n".join(formatted)
    
    def format_generated_response(self, response: Dict[str, Any]) -> str:
        """
        Format retrieve and generate response for display
        
        Args:
            response: Raw response from retrieve_and_generate
            
        Returns:
            Formatted string representation
        """
        if not response:
            return "No response generated."
        
        formatted = []
        formatted.append("=" * 80)
        formatted.append("AI GENERATED RESPONSE")
        formatted.append("=" * 80)
        
        # Generated text
        output = response.get('output', {})
        text = output.get('text', 'No response text available')
        formatted.append(f"\nGenerated Response:\n{text}")
        
        # Citations
        citations = response.get('citations', [])
        if citations:
            formatted.append(f"\n--- Sources ({len(citations)} citations) ---")
            for i, citation in enumerate(citations, 1):
                formatted.append(f"\nCitation {i}:")
                
                # Retrieved references
                references = citation.get('retrievedReferences', [])
                for j, ref in enumerate(references, 1):
                    content = ref.get('content', {}).get('text', 'No content')
                    location = ref.get('location', {})
                    
                    formatted.append(f"  Reference {j}: {content[:200]}{'...' if len(content) > 200 else ''}")
                    
                    if location and location.get('type') == 'S3':
                        s3_uri = location.get('s3Location', {}).get('uri', 'Unknown')
                        formatted.append(f"  Source: {s3_uri}")
        
        return "\n".join(formatted)


def main():
    """Main function demonstrating knowledge base queries"""
    
    # Configuration - Update these values for your setup
    REGION = os.getenv('AWS_REGION', 'us-west-2')
    KNOWLEDGE_BASE_ID = os.getenv('KNOWLEDGE_BASE_ID', 'DFVMT0Y6LF')
    
    # Sample queries to test
    SAMPLE_QUERIES = [
        "describe this knowledge base"
    ]
    
    print("🔍 Amazon Bedrock Knowledge Base Query Tool")
    print("=" * 60)
    
    # Initialize client
    try:
        kb_client = BedrockKnowledgeBaseClient(region_name=REGION)
        print(f"✅ Connected to Bedrock in region: {REGION}")
    except Exception as e:
        print(f"❌ Failed to initialize Bedrock client: {e}")
        return
    
    # List available knowledge bases
    print("\n📚 Available Knowledge Bases:")
    knowledge_bases = kb_client.list_knowledge_bases()
    
    if not knowledge_bases:
        print("No knowledge bases found in your account.")
        print("\nTo use this script:")
        print("1. Create a knowledge base in Amazon Bedrock console")
        print("2. Set the KNOWLEDGE_BASE_ID environment variable")
        print("3. Ensure your AWS credentials have proper permissions")
        return
    
    for i, kb in enumerate(knowledge_bases, 1):
        kb_id = kb.get('knowledgeBaseId', 'Unknown')
        name = kb.get('name', 'Unnamed')
        status = kb.get('status', 'Unknown')
        print(f"  {i}. {name} (ID: {kb_id}) - Status: {status}")
    
    # Use specified knowledge base or first available one
    if KNOWLEDGE_BASE_ID == 'YOUR_KNOWLEDGE_BASE_ID_HERE':
        if knowledge_bases:
            KNOWLEDGE_BASE_ID = knowledge_bases[0]['knowledgeBaseId']
            print(f"\n🎯 Using first available knowledge base: {KNOWLEDGE_BASE_ID}")
        else:
            print("❌ No knowledge base ID specified and none available")
            return
    else:
        print(f"\n🎯 Using specified knowledge base: {KNOWLEDGE_BASE_ID}")
    
    # Get knowledge base details
    kb_info = kb_client.get_knowledge_base_info(KNOWLEDGE_BASE_ID)
    if kb_info:
        print(f"📋 Knowledge Base: {kb_info.get('name', 'Unknown')}")
        print(f"📝 Description: {kb_info.get('description', 'No description')}")
        print(f"🔄 Status: {kb_info.get('status', 'Unknown')}")
    
    # Interactive query mode
    print(f"\n🤖 Ready to query knowledge base!")
    print("Choose an option:")
    print("1. Use sample queries")
    print("2. Enter custom query")
    print("3. Test retrieve and generate")
    
    try:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == "1":
            # Sample queries
            print(f"\n🔍 Running sample queries...")
            for i, query in enumerate(SAMPLE_QUERIES, 1):
                print(f"\n{'='*60}")
                print(f"Sample Query {i}: {query}")
                print('='*60)
                
                results = kb_client.query_knowledge_base(
                    knowledge_base_id=KNOWLEDGE_BASE_ID,
                    query=query,
                    max_results=3
                )
                
                print(kb_client.format_query_results(results))
                
                # Pause between queries
                if i < len(SAMPLE_QUERIES):
                    input("\nPress Enter to continue to next query...")
        
        elif choice == "2":
            # Custom query
            query = input("\nEnter your query: ").strip()
            if query:
                print(f"\n🔍 Searching for: {query}")
                
                results = kb_client.query_knowledge_base(
                    knowledge_base_id=KNOWLEDGE_BASE_ID,
                    query=query,
                    max_results=5
                )
                
                print(kb_client.format_query_results(results))
        
        elif choice == "3":
            # Retrieve and generate
            query = input("\nEnter your question for AI generation: ").strip()
            if query:
                print(f"\n🤖 Generating AI response for: {query}")
                
                response = kb_client.retrieve_and_generate(
                    knowledge_base_id=KNOWLEDGE_BASE_ID,
                    query=query,
                    max_results=5
                )
                
                print(kb_client.format_generated_response(response))
        
        else:
            print("Invalid choice. Please run the script again.")
    
    except KeyboardInterrupt:
        print("\n\n👋 Query session ended by user.")
    except Exception as e:
        print(f"\n❌ Error during query: {e}")
    
    print(f"\n✅ Knowledge base query session completed.")


if __name__ == "__main__":
    main()
