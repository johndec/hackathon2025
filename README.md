# Azure AI RAG Documentation Chat 🤖

A complete **Retrieval Augmented Generation (RAG)** system built on Azure AI services that enables conversational AI about your documentation. Clone this repository and deploy it to your own Azure subscription to get started!

## 🎯 What This Project Does

This project provides everything you need to:

- **Deploy Azure AI infrastructure** using Bicep templates
- **Index your documentation** into a searchable vector database
- **Chat with your docs** using natural language
- **Get accurate answers** with source citations

Perfect for creating AI assistants that can answer questions about your technical documentation, knowledge bases, or any text content.

## 🏗️ Architecture

The system deploys and uses these Azure services:

- **Azure OpenAI Service**: GPT models for chat and text embeddings
- **Azure AI Search**: Vector search for document retrieval  
- **Azure Storage Account**: Document storage
- **Azure Key Vault**: Secure API key management
- **Application Insights**: Monitoring and analytics

## 🚀 Quick Start

### 1. Prerequisites

- Azure subscription
- Azure CLI or PowerShell
- Python 3.8+
- Git

### 2. Clone and Deploy

```bash
# Clone the repository
git clone https://github.com/johndec/hackathon2025.git
cd hackathon2025

# Deploy Azure infrastructure (Linux/macOS/WSL)
./deploy.sh -g my-ai-rag-rg

# Or on Windows PowerShell
.\deploy.ps1 -ResourceGroupName "my-ai-rag-rg"
```

### 3. Set Up Python Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure and Index Documents

```bash
# Copy configuration template
cp .env.template .env
# Edit .env with your deployed resource endpoints

# Index sample documentation
python src/index_documents.py --directory docs/sample --recreate-index
```

### 5. Start Chatting!

```bash
# Interactive chat
python src/chat.py

# Or ask a single question
python src/chat.py --question "How do I deploy the infrastructure?"
```

## 📁 Project Structure

```
hackathon2025/
├── infrastructure/           # Bicep templates
│   ├── main.bicep           # Main infrastructure template
│   └── main.parameters.json # Parameters file
├── src/                     # Python application
│   ├── rag_system.py       # Core RAG implementation
│   ├── chat.py             # Interactive CLI chat
│   └── index_documents.py  # Document indexing
├── docs/sample/            # Sample documentation
├── deploy.sh              # Bash deployment script
├── deploy.ps1             # PowerShell deployment script
├── requirements.txt       # Python dependencies
└── .env.template         # Configuration template
```

## 🛠️ Deployment Options

### Option 1: Environment Variables

Set these environment variables after deployment:

```bash
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_API_KEY=your-search-key
```

### Option 2: Azure Key Vault (Recommended)

The deployment automatically stores keys in Key Vault. Use this approach:

```bash
python src/chat.py \
  --keyvault-url https://your-kv.vault.azure.net/ \
  --openai-endpoint https://your-openai.openai.azure.com/ \
  --search-endpoint https://your-search.search.windows.net
```

## 📚 Adding Your Own Documents

### Supported Formats

- Text files (`.txt`)
- Markdown (`.md`) 
- HTML (`.html`)
- PDF files (`.pdf`) - requires pypdf2
- Word documents (`.docx`) - requires python-docx

### Index Your Documents

```bash
# Index a directory
python src/index_documents.py --directory ./my-docs

# Index specific files
python src/index_documents.py --files doc1.md doc2.pdf

# Custom chunk settings for better retrieval
python src/index_documents.py --directory ./docs --chunk-size 1500 --chunk-overlap 300
```

## 💬 Usage Examples

### Interactive Chat

```bash
$ python src/chat.py
🤖 Azure AI RAG Documentation Chat
Ask me anything about your documentation!

💬 You: How do I deploy this to Azure?

🤖 Answer:
To deploy this to Azure, you can use either the Bash or PowerShell deployment scripts...

📚 Sources:
1. getting-started.md (Relevance: 0.89)
```

### Single Questions

```bash
$ python src/chat.py --question "What Azure services are deployed?"

🤖 Answer:
The deployment creates the following Azure resources:
- Azure OpenAI Service: Provides GPT and embedding models
- Azure AI Search: Vector search capabilities...
```

## 🔒 Security Features

- **API keys stored in Key Vault**: No secrets in code or config files
- **RBAC integration**: Use Azure AD for access control
- **Secure defaults**: All resources configured with security best practices
- **Audit logging**: Track usage through Application Insights

## 🔧 Customization

### Modify Models

Edit `infrastructure/main.bicep` to change OpenAI models:

```bicep
resource gptDeployment 'Microsoft.CognitiveServices/accounts/deployments@2023-05-01' = {
  // Change model version or capacity here
  properties: {
    model: {
      name: 'gpt-4'  // Use GPT-4 instead
      version: '0613'
    }
  }
}
```

### Adjust Search Settings

Modify search parameters in your environment:

```bash
MAX_SEARCH_RESULTS=10
MAX_TOKENS=1500
TEMPERATURE=0.3
```

## 📊 Monitoring

Access monitoring through Azure portal:

- **Application Insights**: View usage metrics and performance
- **Azure Monitor**: Set up alerts and dashboards
- **Search Analytics**: Monitor search query patterns

## 🤝 Contributing

This is a hackathon project! Feel free to:

1. Fork the repository
2. Add new features (web UI, more document types, etc.)
3. Improve the RAG implementation
4. Submit pull requests

## 📄 License

This project is open source. Check the license file for details.

## 🆘 Support

For issues and questions:

1. Check the sample documentation in `docs/sample/`
2. Review the troubleshooting section below
3. Open an issue on GitHub

### Common Issues

**"No module named 'azure'"**: Install requirements with `pip install -r requirements.txt`

**"Authentication failed"**: Ensure you're logged into Azure CLI with `az login`

**"Index not found"**: Run the indexing script with `--recreate-index` flag

**"No search results"**: Check that documents were indexed successfully and your search index contains data

---

**Ready to chat with your docs? Deploy now and start exploring! 🚀**
