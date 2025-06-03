#!/usr/bin/env python3
"""
Setup Validation Script for Amazon Bedrock Knowledge Base

This script validates your AWS credentials and Bedrock access before running the main query tool.
"""

import boto3
import os
from botocore.exceptions import ClientError, NoCredentialsError


def check_aws_credentials():
    """Check if AWS credentials are properly configured"""
    print("🔐 Checking AWS credentials...")
    
    try:
        # Try to get caller identity
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS credentials found")
        print(f"   Account ID: {identity.get('Account', 'Unknown')}")
        print(f"   User/Role ARN: {identity.get('Arn', 'Unknown')}")
        return True
        
    except NoCredentialsError:
        print("❌ No AWS credentials found")
        print("   Please configure credentials using one of:")
        print("   - aws configure")
        print("   - Environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        print("   - IAM role (if running on EC2)")
        return False
        
    except ClientError as e:
        print(f"❌ AWS credentials error: {e}")
        return False


def check_bedrock_access(region='us-east-1'):
    """Check if Bedrock service is accessible"""
    print(f"\n🤖 Checking Bedrock access in region {region}...")
    
    try:
        # Test Bedrock Agent client
        bedrock_agent = boto3.client('bedrock-agent', region_name=region)
        
        # Try to list knowledge bases (this will fail if no permissions)
        response = bedrock_agent.list_knowledge_bases()
        knowledge_bases = response.get('knowledgeBaseSummaries', [])
        
        print(f"✅ Bedrock access confirmed")
        print(f"   Found {len(knowledge_bases)} knowledge base(s)")
        
        if knowledge_bases:
            print("   Available knowledge bases:")
            for i, kb in enumerate(knowledge_bases[:3], 1):  # Show first 3
                name = kb.get('name', 'Unnamed')
                kb_id = kb.get('knowledgeBaseId', 'Unknown')
                status = kb.get('status', 'Unknown')
                print(f"   {i}. {name} (ID: {kb_id[:8]}...) - {status}")
            
            if len(knowledge_bases) > 3:
                print(f"   ... and {len(knowledge_bases) - 3} more")
        else:
            print("   No knowledge bases found. You'll need to create one first.")
        
        return True, knowledge_bases
        
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', 'Unknown')
        
        if error_code == 'AccessDeniedException':
            print("❌ Access denied to Bedrock")
            print("   Your AWS credentials don't have Bedrock permissions")
            print("   Required permissions:")
            print("   - bedrock:ListKnowledgeBases")
            print("   - bedrock:GetKnowledgeBase") 
            print("   - bedrock:Retrieve")
            print("   - bedrock:RetrieveAndGenerate")
            
        elif error_code == 'UnrecognizedClientException':
            print(f"❌ Bedrock not available in region {region}")
            print("   Try one of these regions:")
            print("   - us-east-1 (N. Virginia)")
            print("   - us-west-2 (Oregon)")
            print("   - eu-west-1 (Ireland)")
            
        else:
            print(f"❌ Bedrock error: {e}")
        
        return False, []
        
    except Exception as e:
        print(f"❌ Unexpected error accessing Bedrock: {e}")
        return False, []


def check_bedrock_runtime_access(region='us-east-1'):
    """Check if Bedrock Runtime is accessible for queries"""
    print(f"\n🔍 Checking Bedrock Runtime access...")
    
    try:
        bedrock_runtime = boto3.client('bedrock-agent-runtime', region_name=region)
        
        # We can't test retrieve without a valid knowledge base ID,
        # but we can check if the client initializes properly
        print("✅ Bedrock Runtime client initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Bedrock Runtime error: {e}")
        return False


def check_environment_variables():
    """Check for relevant environment variables"""
    print(f"\n🌍 Checking environment variables...")
    
    env_vars = {
        'AWS_REGION': os.getenv('AWS_REGION'),
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'AWS_PROFILE': os.getenv('AWS_PROFILE'),
        'KNOWLEDGE_BASE_ID': os.getenv('KNOWLEDGE_BASE_ID')
    }
    
    found_vars = {k: v for k, v in env_vars.items() if v is not None}
    
    if found_vars:
        print("✅ Found environment variables:")
        for key, value in found_vars.items():
            if 'SECRET' in key or 'KEY' in key:
                print(f"   {key}: {'*' * min(len(value), 20)}")
            else:
                print(f"   {key}: {value}")
    else:
        print("ℹ️  No relevant environment variables found")
        print("   This is OK if you're using AWS CLI profiles or IAM roles")
    
    return found_vars


def main():
    """Run all validation checks"""
    print("🔍 Amazon Bedrock Knowledge Base Setup Validation")
    print("=" * 60)
    
    # Check AWS credentials
    creds_ok = check_aws_credentials()
    if not creds_ok:
        print("\n❌ Setup validation failed - fix AWS credentials first")
        return False
    
    # Check environment variables
    env_vars = check_environment_variables()
    region = env_vars.get('AWS_REGION', 'us-east-1')
    
    # Check Bedrock access
    bedrock_ok, knowledge_bases = check_bedrock_access(region)
    if not bedrock_ok:
        print("\n❌ Setup validation failed - fix Bedrock access")
        return False
    
    # Check Bedrock Runtime
    runtime_ok = check_bedrock_runtime_access(region)
    if not runtime_ok:
        print("\n❌ Setup validation failed - Bedrock Runtime issue")
        return False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 VALIDATION SUMMARY")
    print("=" * 60)
    print("✅ AWS credentials: OK")
    print("✅ Bedrock access: OK")
    print("✅ Bedrock Runtime: OK")
    print(f"✅ Region: {region}")
    print(f"✅ Knowledge bases found: {len(knowledge_bases)}")
    
    if knowledge_bases:
        kb_id = knowledge_bases[0]['knowledgeBaseId']
        print(f"\n🎯 Ready to query! You can use knowledge base ID: {kb_id}")
        print(f"   Set environment variable: export KNOWLEDGE_BASE_ID={kb_id}")
    else:
        print(f"\n⚠️  No knowledge bases found. Create one in the Bedrock console first.")
    
    print(f"\n🚀 Run the main script: python test.py")
    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 