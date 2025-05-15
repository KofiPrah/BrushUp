#!/bin/bash
# This script helps set up AWS S3 environment variables for the Art Critique application

# Make the script executable: chmod +x setup_s3_env.sh
# Run with: ./setup_s3_env.sh

echo "Art Critique - AWS S3 Environment Setup"
echo "========================================"
echo "This script will guide you through setting up environment variables for AWS S3 storage."
echo "These variables will be saved to a .env file that you can source in your environment."
echo ""

# Check if .env file exists and ask to overwrite
if [ -f .env ]; then
    read -p "A .env file already exists. Do you want to append to it? (y/n): " overwrite
    if [ "$overwrite" != "y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

echo "# AWS S3 Configuration - Added $(date)" >> .env

# Ask for AWS Access Key ID
read -p "Enter your AWS Access Key ID: " aws_access_key_id
echo "AWS_ACCESS_KEY_ID=\"$aws_access_key_id\"" >> .env

# Ask for AWS Secret Access Key
read -p "Enter your AWS Secret Access Key: " aws_secret_access_key
echo "AWS_SECRET_ACCESS_KEY=\"$aws_secret_access_key\"" >> .env

# Ask for S3 Bucket Name
read -p "Enter your S3 Bucket Name: " aws_bucket_name
echo "AWS_STORAGE_BUCKET_NAME=\"$aws_bucket_name\"" >> .env

# Ask for AWS Region
read -p "Enter your AWS Region (e.g., us-east-1): " aws_region
echo "AWS_S3_REGION_NAME=\"$aws_region\"" >> .env

# Set USE_S3 to True
echo "USE_S3=\"True\"" >> .env

echo ""
echo "Environment variables have been saved to .env file."
echo "To use these variables, run: source .env"
echo ""
echo "NOTE: Keep this file secure and do not commit it to version control!"
echo "The .env file has been added to .gitignore, but always double-check before committing."

# Make sure .env is not executable
chmod 600 .env

echo "Done!"