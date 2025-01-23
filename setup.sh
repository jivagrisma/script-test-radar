#!/bin/bash

# Exit on error
set -e

echo "Setting up Test Radar..."

# Check Python version
REQUIRED_PYTHON="3.11"
python_version=$(python3.11 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

if [[ "$(printf '%s\n' "$REQUIRED_PYTHON" "$python_version" | sort -V | head -n1)" != "$REQUIRED_PYTHON" ]]; then
    echo "Error: Python $REQUIRED_PYTHON or higher is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3.11 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "Creating project directories..."
mkdir -p reports
mkdir -p .cache

# Check AWS credentials
if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "Warning: AWS credentials not found in environment"
    echo "Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
fi

# Create config file if it doesn't exist
if [ ! -f "test_config.json" ]; then
    echo "Creating default configuration..."
    cp test_config.example.json test_config.json
    echo "Please update test_config.json with your AWS credentials"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating environment file..."
    cp .env.example .env
    echo "Please update .env with your configuration"
fi

# Verify AWS Bedrock access
echo "Verifying AWS Bedrock access..."
python3.11 -c "
import boto3
import json
import os
import sys

try:
    # Load config
    with open('test_config.json', 'r') as f:
        config = json.load(f)

    # Configure client
    client = boto3.client(
        'bedrock-runtime',
        aws_access_key_id=config['llm']['aws']['access_key_id'],
        aws_secret_access_key=config['llm']['aws']['secret_access_key'],
        region_name=config['llm']['aws']['region']
    )

    # Test model access with a simple prompt
    response = client.invoke_model(
        modelId=config['llm']['aws']['bedrock_model_id'],
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'messages': [
                {
                    'role': 'user',
                    'content': 'Test connection'
                }
            ],
            'max_tokens': 10,
            'temperature': 0
        })
    )
    print('AWS Bedrock connection successful')

except Exception as e:
    print(f'Error verifying AWS Bedrock access: {str(e)}')
    print('Please verify your AWS credentials and permissions')
    sys.exit(1)
"

# Install pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install

echo "Setup complete!"
echo "Next steps:"
echo "1. Update test_config.json with your AWS credentials"
echo "2. Update .env with your configuration"
echo "3. Run 'python test_run.py' to start the test analysis"

# Deactivate virtual environment
deactivate
