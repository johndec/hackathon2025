# hackathon2025
Hackathon for the ZeroToHero AI project

## Overview
This repository contains the infrastructure as code (IaC) for deploying an Azure OpenAI service instance with a GPT-3.5 Turbo model deployment. The infrastructure is defined using Azure Bicep templates and includes automated deployment scripts.

## Architecture
- **Azure OpenAI Service**: Cognitive Services account configured for OpenAI
- **Model Deployment**: GPT-3.5 Turbo model with configurable capacity
- **Resource Group**: Container for all related resources
- **Security**: Public network access enabled (can be customized)

## Prerequisites
Before deploying, ensure you have:

1. **Azure CLI** installed and configured
   ```powershell
   # Install Azure CLI (if not already installed)
   winget install Microsoft.AzureCLI
   ```

2. **Azure Subscription** with appropriate permissions:
   - Contributor or Owner role on the subscription or resource group
   - Access to create Cognitive Services resources
   - OpenAI service availability in your region

3. **PowerShell 5.1 or later**

## Quick Start

### 1. Clone and Navigate
```powershell
git clone <repository-url>
cd hackathon2025/infrastructure
```

### 2. Deploy the Infrastructure
```powershell
# Basic deployment
.\deploy.ps1 -ResourceGroupName "rg-hackathon2025-openai"

# Advanced deployment with custom parameters
.\deploy.ps1 -ResourceGroupName "rg-hackathon2025-openai" -Location "West Europe" -SubscriptionId "your-subscription-id"
```

### 3. Customize Parameters (Optional)
Edit `parameters.json` to customize your deployment:
```json
{
  "openAIServiceName": { "value": "your-custom-name" },
  "location": { "value": "East US" },
  "modelName": { "value": "gpt-4" },
  "modelCapacity": { "value": 20 }
}
```

## File Structure
```
infrastructure/
├── main.bicep          # Main Bicep template defining Azure OpenAI resources
├── parameters.json     # Parameter file with default values
└── deploy.ps1         # PowerShell deployment script
```

## Deployment Details

### What Gets Deployed
- **Azure OpenAI Service** (`Microsoft.CognitiveServices/accounts`)
  - SKU: S0 (Standard)
  - Kind: OpenAI
  - Custom subdomain for API access
  
- **Model Deployment** (`Microsoft.CognitiveServices/accounts/deployments`)
  - Model: GPT-3.5 Turbo (default)
  - Version: 0613
  - Capacity: 10 TPM (Tokens Per Minute)

### Available Models
The template supports these models (configurable in parameters):
- `gpt-35-turbo` (default)
- `gpt-4`
- `gpt-4-turbo`
- `text-embedding-ada-002`

### Outputs
After successful deployment, you'll receive:
- **OpenAI Service Name**: Name of the created service
- **OpenAI Endpoint**: API endpoint URL
- **OpenAI Key**: Primary access key (masked in output)
- **Model Deployment Name**: Name of the model deployment

## Usage After Deployment

### Using the OpenAI API
```python
import openai

# Configure the client
openai.api_type = "azure"
openai.api_base = "https://your-service-name.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = "your-api-key"

# Make a request
response = openai.ChatCompletion.create(
    engine="gpt-35-turbo-deployment",  # Your deployment name
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)
```

### Using Azure CLI
```bash
# Test the deployment
az cognitiveservices account show --name "your-openai-service-name" --resource-group "your-resource-group"
```

## Cost Considerations
- **Azure OpenAI S0 SKU**: Pay-per-use pricing
- **Model Usage**: Charged per token (input + output)
- **Estimated Cost**: Varies based on usage, typically $0.002 per 1K tokens for GPT-3.5 Turbo

## Security Notes
- The template deploys with public network access enabled
- API keys are automatically generated and should be kept secure
- Consider implementing:
  - Virtual network integration for production
  - Managed identity authentication
  - Key rotation policies

## Troubleshooting

### Common Issues
1. **Resource Provider Not Registered**
   ```powershell
   az provider register --namespace Microsoft.CognitiveServices
   ```

2. **OpenAI Service Not Available in Region**
   - Check [Azure OpenAI Service regions](https://azure.microsoft.com/en-us/global-infrastructure/services/?products=cognitive-services)
   - Update the `location` parameter

3. **Insufficient Permissions**
   - Ensure you have Contributor role or higher
   - Verify OpenAI service access in your subscription

### Cleanup
To remove all deployed resources:
```powershell
az group delete --name "rg-hackathon2025-openai" --yes --no-wait
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test the deployment
5. Submit a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.
