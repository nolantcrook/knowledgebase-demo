#!/usr/bin/env python3
"""
FastAPI Backend for Bedrock Knowledge Base UI

This backend provides REST API endpoints for searching and summarizing
content from Amazon Bedrock Knowledge Bases.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import boto3
import os
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import our knowledge base client
import sys
sys.path.append('..')
from test import BedrockKnowledgeBaseClient

app = FastAPI(
    title="Bedrock Knowledge Base API",
    description="REST API for querying Amazon Bedrock Knowledge Bases",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-west-2')
KNOWLEDGE_BASE_ID = os.getenv('KNOWLEDGE_BASE_ID', 'DFVMT0Y6LF')
MODEL_ARN = os.getenv('MODEL_ARN', f'arn:aws:bedrock:{AWS_REGION}::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0')

# Initialize Bedrock client
try:
    bedrock_client = BedrockKnowledgeBaseClient(region_name=AWS_REGION)
    logger.info(f"✅ Bedrock client initialized for region: {AWS_REGION}")
except Exception as e:
    logger.error(f"❌ Failed to initialize Bedrock client: {e}")
    bedrock_client = None

# Pydantic models
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query", min_length=1, max_length=1000)
    max_results: int = Field(default=5, description="Maximum number of results", ge=1, le=20)
    knowledge_base_id: Optional[str] = Field(default=None, description="Override knowledge base ID")

class SummarizeRequest(BaseModel):
    query: str = Field(..., description="Question for AI summarization", min_length=1, max_length=1000)
    max_results: int = Field(default=5, description="Maximum number of source documents", ge=1, le=10)
    knowledge_base_id: Optional[str] = Field(default=None, description="Override knowledge base ID")
    model_arn: Optional[str] = Field(default=None, description="Override model ARN")

class SearchResult(BaseModel):
    content: str
    score: float
    source_type: str
    source_location: Optional[str] = None
    metadata: Dict[str, Any] = {}

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    knowledge_base_id: str
    timestamp: str

class Citation(BaseModel):
    content: str
    source_location: Optional[str] = None
    metadata: Dict[str, Any] = {}

class SummarizeResponse(BaseModel):
    query: str
    generated_response: str
    citations: List[Citation]
    knowledge_base_id: str
    model_used: str
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    aws_region: str
    knowledge_base_id: str
    bedrock_available: bool

class KnowledgeBaseInfo(BaseModel):
    knowledge_base_id: str
    name: str
    description: Optional[str] = None
    status: str

# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        aws_region=AWS_REGION,
        knowledge_base_id=KNOWLEDGE_BASE_ID,
        bedrock_available=bedrock_client is not None
    )

# List knowledge bases
@app.get("/knowledge-bases", response_model=List[KnowledgeBaseInfo])
async def list_knowledge_bases():
    """List available knowledge bases"""
    if not bedrock_client:
        raise HTTPException(status_code=503, detail="Bedrock client not available")
    
    try:
        knowledge_bases = bedrock_client.list_knowledge_bases()
        
        result = []
        for kb in knowledge_bases:
            result.append(KnowledgeBaseInfo(
                knowledge_base_id=kb.get('knowledgeBaseId', ''),
                name=kb.get('name', 'Unnamed'),
                description=kb.get('description'),
                status=kb.get('status', 'Unknown')
            ))
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing knowledge bases: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list knowledge bases: {str(e)}")

# Search endpoint
@app.post("/search", response_model=SearchResponse)
async def search_knowledge_base(request: SearchRequest):
    """Search the knowledge base for relevant documents"""
    if not bedrock_client:
        raise HTTPException(status_code=503, detail="Bedrock client not available")
    
    kb_id = request.knowledge_base_id or KNOWLEDGE_BASE_ID
    if not kb_id or kb_id == 'YOUR_KNOWLEDGE_BASE_ID_HERE':
        raise HTTPException(status_code=400, detail="Knowledge base ID not configured")
    
    try:
        logger.info(f"Searching knowledge base {kb_id} for: {request.query}")
        
        # Query the knowledge base
        results = bedrock_client.query_knowledge_base(
            knowledge_base_id=kb_id,
            query=request.query,
            max_results=request.max_results
        )
        
        # Parse results
        search_results = []
        retrieval_results = results.get('retrievalResults', [])
        
        for result in retrieval_results:
            content = result.get('content', {}).get('text', 'No content available')
            score = result.get('score', 0.0)
            
            # Extract location info
            location = result.get('location', {})
            source_type = location.get('type', 'Unknown')
            source_location = None
            
            if source_type == 'S3':
                s3_location = location.get('s3Location', {})
                source_location = s3_location.get('uri', 'Unknown S3 location')
            
            # Extract metadata
            metadata = result.get('metadata', {})
            
            search_results.append(SearchResult(
                content=content,
                score=score,
                source_type=source_type,
                source_location=source_location,
                metadata=metadata
            ))
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            knowledge_base_id=kb_id,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Summarize endpoint
@app.post("/summarize", response_model=SummarizeResponse)
async def summarize_with_knowledge_base(request: SummarizeRequest):
    """Generate AI summary with citations from knowledge base"""
    if not bedrock_client:
        raise HTTPException(status_code=503, detail="Bedrock client not available")
    
    kb_id = request.knowledge_base_id or KNOWLEDGE_BASE_ID
    model_arn = request.model_arn or MODEL_ARN
    
    if not kb_id or kb_id == 'YOUR_KNOWLEDGE_BASE_ID_HERE':
        raise HTTPException(status_code=400, detail="Knowledge base ID not configured")
    
    try:
        logger.info(f"Generating summary for knowledge base {kb_id}: {request.query}")
        
        # Use retrieve and generate
        response = bedrock_client.retrieve_and_generate(
            knowledge_base_id=kb_id,
            query=request.query,
            model_arn=model_arn,
            max_results=request.max_results
        )
        
        # Extract generated response
        output = response.get('output', {})
        generated_text = output.get('text', 'No response generated')
        
        # Extract citations
        citations = []
        citation_data = response.get('citations', [])
        
        for citation in citation_data:
            references = citation.get('retrievedReferences', [])
            
            for ref in references:
                content = ref.get('content', {}).get('text', 'No content')
                location = ref.get('location', {})
                
                source_location = None
                if location and location.get('type') == 'S3':
                    s3_location = location.get('s3Location', {})
                    source_location = s3_location.get('uri', 'Unknown S3 location')
                
                metadata = ref.get('metadata', {})
                
                citations.append(Citation(
                    content=content,
                    source_location=source_location,
                    metadata=metadata
                ))
        
        return SummarizeResponse(
            query=request.query,
            generated_response=generated_text,
            citations=citations,
            knowledge_base_id=kb_id,
            model_used=model_arn.split('/')[-1] if '/' in model_arn else model_arn,
            timestamp=datetime.utcnow().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

# Get knowledge base info
@app.get("/knowledge-bases/{knowledge_base_id}")
async def get_knowledge_base_info(knowledge_base_id: str):
    """Get detailed information about a specific knowledge base"""
    if not bedrock_client:
        raise HTTPException(status_code=503, detail="Bedrock client not available")
    
    try:
        kb_info = bedrock_client.get_knowledge_base_info(knowledge_base_id)
        
        if not kb_info:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
        
        return {
            "knowledge_base_id": knowledge_base_id,
            "name": kb_info.get('name', 'Unknown'),
            "description": kb_info.get('description', 'No description'),
            "status": kb_info.get('status', 'Unknown'),
            "created_at": kb_info.get('createdAt'),
            "updated_at": kb_info.get('updatedAt'),
            "role_arn": kb_info.get('roleArn'),
            "knowledge_base_configuration": kb_info.get('knowledgeBaseConfiguration', {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting knowledge base info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get knowledge base info: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv('PORT', 8000))
    host = os.getenv('HOST', '0.0.0.0')
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"AWS Region: {AWS_REGION}")
    logger.info(f"Knowledge Base ID: {KNOWLEDGE_BASE_ID}")
    
    uvicorn.run(app, host=host, port=port) 