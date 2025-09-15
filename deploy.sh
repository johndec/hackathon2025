#!/bin/bash

# Azure AI RAG Infrastructure Deployment Script
# This script deploys the Azure infrastructure needed for the AI RAG project

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
RESOURCE_GROUP_NAME=""
LOCATION="eastus"
PROJECT_NAME="airag"
SUBSCRIPTION_ID=""

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 -g <resource-group-name> [-s <subscription-id>] [-l <location>] [-p <project-name>]"
    echo ""
    echo "Required parameters:"
    echo "  -g <resource-group-name>    Name of the Azure resource group to create/use"
    echo ""
    echo "Optional parameters:"
    echo "  -s <subscription-id>        Azure subscription ID (if not set, uses current subscription)"
    echo "  -l <location>              Azure region (default: eastus)"
    echo "  -p <project-name>          Project name prefix for resources (default: airag)"
    echo "  -h                         Show this help message"
    echo ""
    echo "Example:"
    echo "  $0 -g my-ai-rag-rg -l westus2 -p myaiproject"
}

# Parse command line arguments
while getopts "g:s:l:p:h" opt; do
    case ${opt} in
        g )
            RESOURCE_GROUP_NAME=$OPTARG
            ;;
        s )
            SUBSCRIPTION_ID=$OPTARG
            ;;
        l )
            LOCATION=$OPTARG
            ;;
        p )
            PROJECT_NAME=$OPTARG
            ;;
        h )
            show_usage
            exit 0
            ;;
        \? )
            print_error "Invalid option: $OPTARG"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required parameters
if [ -z "$RESOURCE_GROUP_NAME" ]; then
    print_error "Resource group name is required"
    show_usage
    exit 1
fi

# Check if Azure CLI is installed
if ! command -v az &> /dev/null; then
    print_error "Azure CLI is not installed. Please install it from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
    exit 1
fi

print_status "Starting Azure AI RAG infrastructure deployment..."

# Set subscription if provided
if [ ! -z "$SUBSCRIPTION_ID" ]; then
    print_status "Setting subscription to $SUBSCRIPTION_ID"
    az account set --subscription "$SUBSCRIPTION_ID"
fi

# Get current subscription info
CURRENT_SUBSCRIPTION=$(az account show --query "name" -o tsv)
CURRENT_SUBSCRIPTION_ID=$(az account show --query "id" -o tsv)
print_status "Using subscription: $CURRENT_SUBSCRIPTION ($CURRENT_SUBSCRIPTION_ID)"

# Create resource group if it doesn't exist
print_status "Creating resource group '$RESOURCE_GROUP_NAME' in location '$LOCATION'"
az group create --name "$RESOURCE_GROUP_NAME" --location "$LOCATION"

# Update parameters file with current values
TEMP_PARAMS_FILE="main.parameters.temp.json"
cat > "$TEMP_PARAMS_FILE" << EOF
{
  "\$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "projectName": {
      "value": "$PROJECT_NAME"
    },
    "location": {
      "value": "$LOCATION"
    },
    "openAiSku": {
      "value": "S0"
    },
    "searchSku": {
      "value": "basic"
    },
    "storageSku": {
      "value": "Standard_LRS"
    },
    "tags": {
      "value": {
        "project": "hackathon2025",
        "purpose": "ai-rag",
        "environment": "dev",
        "deployedBy": "$(whoami)",
        "deployedAt": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
      }
    }
  }
}
EOF

# Deploy the infrastructure
print_status "Deploying Azure infrastructure..."
DEPLOYMENT_NAME="ai-rag-deployment-$(date +%Y%m%d-%H%M%S)"

az deployment group create \
    --resource-group "$RESOURCE_GROUP_NAME" \
    --name "$DEPLOYMENT_NAME" \
    --template-file "infrastructure/main.bicep" \
    --parameters "@$TEMP_PARAMS_FILE" \
    --verbose

# Clean up temporary file
rm -f "$TEMP_PARAMS_FILE"

# Get deployment outputs
print_status "Retrieving deployment outputs..."
OUTPUTS=$(az deployment group show --resource-group "$RESOURCE_GROUP_NAME" --name "$DEPLOYMENT_NAME" --query "properties.outputs" -o json)

# Parse and display key information
OPENAI_ENDPOINT=$(echo "$OUTPUTS" | jq -r '.openAiEndpoint.value')
SEARCH_ENDPOINT=$(echo "$OUTPUTS" | jq -r '.searchEndpoint.value')
KEY_VAULT_NAME=$(echo "$OUTPUTS" | jq -r '.keyVaultName.value')
STORAGE_ACCOUNT_NAME=$(echo "$OUTPUTS" | jq -r '.storageAccountName.value')

print_status "Deployment completed successfully!"
echo ""
echo "============================================"
echo "DEPLOYMENT SUMMARY"
echo "============================================"
echo "Resource Group: $RESOURCE_GROUP_NAME"
echo "Location: $LOCATION"
echo "Project Name: $PROJECT_NAME"
echo ""
echo "KEY ENDPOINTS:"
echo "OpenAI Endpoint: $OPENAI_ENDPOINT"
echo "Search Endpoint: $SEARCH_ENDPOINT"
echo "Key Vault: $KEY_VAULT_NAME"
echo "Storage Account: $STORAGE_ACCOUNT_NAME"
echo ""
echo "============================================"
echo ""

print_warning "IMPORTANT: API keys are stored in Key Vault '$KEY_VAULT_NAME'"
print_warning "Make sure you have appropriate permissions to access the Key Vault"

print_status "Next steps:"
echo "1. Configure your application with the endpoints above"
echo "2. Retrieve API keys from Key Vault"
echo "3. Upload your documents to the storage account"
echo "4. Set up your RAG application using the provided Python code"

print_status "Deployment script completed!"