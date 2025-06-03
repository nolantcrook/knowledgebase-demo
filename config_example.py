"""
Configuration example for Bedrock Knowledge Base Query Tool

Copy this file to config.py and update with your values.
"""

# AWS Configuration
AWS_REGION = "us-east-1"  # Change to your preferred region
KNOWLEDGE_BASE_ID = "YOUR_KNOWLEDGE_BASE_ID_HERE"  # Replace with your actual KB ID

# Optional: Custom Foundation Model ARN for retrieve_and_generate
MODEL_ARN = "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0"

# Sample queries for testing
SAMPLE_QUERIES = [
    "What are the key features of our product?",
    "How do I troubleshoot connection issues?", 
    "What are the pricing options available?",
    "Tell me about security best practices",
    "What are the system requirements?",
    "How do I get started with the API?",
    "What integrations are available?",
    "How do I configure authentication?",
    "What are the rate limits?",
    "How do I handle errors?"
]

# Query configuration
DEFAULT_MAX_RESULTS = 5
DEFAULT_CONFIDENCE_THRESHOLD = 0.7 