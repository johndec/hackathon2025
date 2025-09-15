# Getting Started with Azure AI RAG

This guide will help you get started with the Azure AI RAG (Retrieval Augmented Generation) system.

## Prerequisites

Before you begin, ensure you have:

1. An Azure subscription
2. Azure CLI installed and configured
3. Python 3.8 or later
4. Git

## Deployment

### Step 1: Clone the Repository

```bash
git clone https://github.com/johndec/hackathon2025.git
cd hackathon2025
```

### Step 2: Deploy Azure Infrastructure

#### Using Bash (Linux/macOS/WSL)

```bash
./deploy.sh -g my-ai-rag-rg -l eastus -p myproject
```

#### Using PowerShell (Windows)

```powershell
.\deploy.ps1 -ResourceGroupName "my-ai-rag-rg" -Location "eastus" -ProjectName "myproject"
```

### Step 3: Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4: Configure Environment

Copy the configuration template and fill in your values:

```bash
cp .env.template .env
# Edit .env with your Azure resource endpoints and keys
```

### Step 5: Index Your Documents

```bash
python src/index_documents.py --directory docs/sample --recreate-index
```

### Step 6: Start Chatting

```bash
python src/chat.py
```

## What Gets Deployed

The deployment creates the following Azure resources:

- **Azure OpenAI Service**: Provides GPT and embedding models
- **Azure AI Search**: Vector search capabilities for document retrieval
- **Storage Account**: Stores your documents
- **Key Vault**: Securely stores API keys and secrets
- **Application Insights**: Monitoring and analytics

## Security

All API keys are automatically stored in Azure Key Vault. The system supports both environment variable and Key Vault-based authentication.