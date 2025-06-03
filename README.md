# Amazon Bedrock Knowledge Base Query Tool

A comprehensive Python script for querying Amazon Bedrock Knowledge Bases using boto3.

## Features

- 🔍 **Query Knowledge Bases**: Search for relevant information using vector similarity
- 🤖 **AI-Generated Responses**: Use foundation models to generate answers with citations
- 📚 **Knowledge Base Management**: List and inspect available knowledge bases
- 🎯 **Interactive Interface**: Choose between sample queries, custom queries, or AI generation
- 📊 **Rich Formatting**: Well-formatted output with relevance scores and source citations

## Prerequisites

1. **AWS Account** with access to Amazon Bedrock
2. **Knowledge Base** created in Amazon Bedrock console
3. **AWS Credentials** configured (one of the following):
   - AWS CLI configured (`aws configure`)
   - Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
   - IAM role (if running on EC2/Lambda)
   - AWS SSO profile

## Required AWS Permissions

Your AWS credentials need the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:ListKnowledgeBases",
                "bedrock:GetKnowledgeBase",
                "bedrock:Retrieve",
                "bedrock:RetrieveAndGenerate"
            ],
            "Resource": "*"
        }
    ]
}
```

## Installation

1. **Clone or download** this script
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables (Recommended)

```bash
export AWS_REGION="us-east-1"
export KNOWLEDGE_BASE_ID="your-knowledge-base-id-here"
```

### Finding Your Knowledge Base ID

1. Go to the [Amazon Bedrock Console](https://console.aws.amazon.com/bedrock/)
2. Navigate to "Knowledge bases" in the left sidebar
3. Click on your knowledge base
4. Copy the "Knowledge base ID" from the details page

## Usage

### Basic Usage

```bash
python test.py
```

The script will:
1. Connect to Amazon Bedrock
2. List available knowledge bases
3. Present an interactive menu with options:
   - **Option 1**: Run predefined sample queries
   - **Option 2**: Enter your own custom query
   - **Option 3**: Use AI to generate responses with citations

### Advanced Usage

#### Programmatic Usage

```python
from test import BedrockKnowledgeBaseClient

# Initialize client
client = BedrockKnowledgeBaseClient(region_name="us-east-1")

# Simple query
results = client.query_knowledge_base(
    knowledge_base_id="your-kb-id",
    query="What are the system requirements?",
    max_results=5
)

# AI-generated response with citations
response = client.retrieve_and_generate(
    knowledge_base_id="your-kb-id",
    query="Explain the security features",
    max_results=3
)
```

#### Custom Model ARN

You can specify different foundation models for generation:

```python
response = client.retrieve_and_generate(
    knowledge_base_id="your-kb-id",
    query="Your question here",
    model_arn="arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0"
)
```

## Sample Output

### Query Results
```
================================================================================
KNOWLEDGE BASE QUERY RESULTS
================================================================================

--- Result 1 ---
Content: Our product offers advanced security features including end-to-end encryption, multi-factor authentication, and role-based access control...
Relevance Score: 0.8542
Source Type: S3
S3 Location: s3://my-knowledge-bucket/docs/security-guide.pdf
Metadata:
  document_type: security_guide
  last_updated: 2024-01-15
```

### AI Generated Response
```
================================================================================
AI GENERATED RESPONSE
================================================================================

Generated Response:
Based on the documentation, our product includes several key security features:

1. **End-to-End Encryption**: All data is encrypted both in transit and at rest
2. **Multi-Factor Authentication**: Users can enable 2FA for additional security
3. **Role-Based Access Control**: Granular permissions based on user roles

--- Sources (2 citations) ---

Citation 1:
  Reference 1: Our product offers advanced security features including end-to-end encryption...
  Source: s3://my-knowledge-bucket/docs/security-guide.pdf
```

## Troubleshooting

### Common Issues

1. **"No knowledge bases found"**
   - Ensure you have created a knowledge base in the Bedrock console
   - Check that your AWS credentials have the correct permissions
   - Verify you're using the correct AWS region

2. **"Access denied" errors**
   - Check your IAM permissions (see Required AWS Permissions above)
   - Ensure Bedrock service is available in your region

3. **"Knowledge base not ready"**
   - Wait for your knowledge base to finish syncing
   - Check the status in the Bedrock console

### Supported Regions

Amazon Bedrock is available in these regions:
- `us-east-1` (N. Virginia)
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)
- `ap-southeast-1` (Singapore)
- `ap-northeast-1` (Tokyo)

## Available Foundation Models

Common model ARNs for `retrieve_and_generate`:

- **Claude 3 Sonnet**: `arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-sonnet-20240229-v1:0`
- **Claude 3 Haiku**: `arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-haiku-20240307-v1:0`
- **Titan Text**: `arn:aws:bedrock:us-east-1::foundation-model/amazon.titan-text-express-v1`

## Best Practices

1. **Optimize Queries**: Use specific, well-formed questions for better results
2. **Limit Results**: Start with fewer results (3-5) for faster responses
3. **Monitor Costs**: Be aware that each query incurs charges for both retrieval and generation
4. **Handle Errors**: Always implement proper error handling for production use
5. **Cache Results**: Consider caching frequent queries to reduce costs

## Example Knowledge Base Setup

To get started quickly:

1. **Create an S3 bucket** with your documents (PDF, TXT, DOCX)
2. **Create a knowledge base** in Bedrock console
3. **Configure data source** pointing to your S3 bucket
4. **Wait for sync** to complete
5. **Run this script** to start querying

## License

This script is provided as-is for educational and development purposes. 