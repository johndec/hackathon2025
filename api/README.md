# Hackathon 2025 - Python OpenAI API

A simple Flask API that interfaces with your deployed Azure OpenAI service.

## 🚀 Quick Start

### 1. Setup Environment
```bash
cd api
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Copy the template and add your API key
cp .env.template .env

# Get your API key from Azure
az cognitiveservices account keys list --name "hackathon2025-openai-jz01" --resource-group "rg-hackathon2025"
```

Edit `.env` and replace `your_api_key_here` with your actual API key.

### 3. Run the API
```bash
python app.py
```

The API will start on `http://localhost:5000`

## 📡 API Endpoints

### Health Check
```bash
GET /
```
**Response:**
```json
{
  "status": "healthy",
  "message": "Hackathon 2025 OpenAI API is running!",
  "endpoint": "https://hackathon2025-openai-jz01.openai.azure.com/",
  "deployment": "jay-hackathon-deployment"
}
```

### Chat Completion
```bash
POST /chat
```
**Request:**
```json
{
  "message": "Hello, how can you help me with my hackathon project?",
  "system_prompt": "You are a helpful AI assistant for hackathon participants.",
  "max_tokens": 500,
  "temperature": 0.7
}
```
**Response:**
```json
{
  "response": "I'd be happy to help with your hackathon project! I can assist with...",
  "model": "jay-hackathon-deployment",
  "usage": {
    "prompt_tokens": 45,
    "completion_tokens": 123,
    "total_tokens": 168
  }
}
```

### Text Completion
```bash
POST /completion
```
**Request:**
```json
{
  "prompt": "The best way to approach a hackathon is",
  "max_tokens": 150,
  "temperature": 0.7
}
```
**Response:**
```json
{
  "completion": "to start with a clear problem statement and work backwards...",
  "model": "jay-hackathon-deployment",
  "usage": {
    "prompt_tokens": 12,
    "completion_tokens": 87,
    "total_tokens": 99
  }
}
```

### Configuration Info
```bash
GET /config
```
**Response:**
```json
{
  "endpoint": "https://hackathon2025-openai-jz01.openai.azure.com/",
  "deployment": "jay-hackathon-deployment",
  "api_version": "2024-02-15-preview",
  "api_key_configured": true
}
```

## 🧪 Testing Examples

### Using curl
```bash
# Health check
curl http://localhost:5000/

# Chat completion
curl -X POST http://localhost:5000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What are some good hackathon project ideas?"}'

# Text completion
curl -X POST http://localhost:5000/completion \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A revolutionary app idea for productivity is"}'
```

### Using Python requests
```python
import requests

# Chat example
response = requests.post('http://localhost:5000/chat', json={
    'message': 'Help me brainstorm a hackathon project using AI',
    'max_tokens': 300
})
print(response.json()['response'])
```

## 🔧 Configuration

### Environment Variables
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_DEPLOYMENT`: Your model deployment name
- `AZURE_OPENAI_API_VERSION`: API version (default: 2024-02-15-preview)
- `PORT`: Server port (default: 5000)
- `FLASK_DEBUG`: Enable debug mode (default: False)

### Getting Your API Key
```bash
az cognitiveservices account keys list \
  --name "hackathon2025-openai-jz01" \
  --resource-group "rg-hackathon2025"
```

## 🔒 Security Notes

- Never commit your `.env` file to version control
- The `.env.template` file is safe to commit (no real keys)
- API keys are masked in logs and responses
- Consider implementing authentication for production use

## 🐛 Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   Configuration error: AZURE_OPENAI_API_KEY environment variable is not set
   ```
   **Solution**: Make sure your `.env` file has the correct API key

2. **Connection Errors**
   ```
   Failed to generate response: Connection error
   ```
   **Solution**: Check your internet connection and Azure OpenAI endpoint

3. **Model Not Found**
   ```
   The model deployment was not found
   ```
   **Solution**: Verify your deployment name matches the one in Azure

### Debugging
Set `FLASK_DEBUG=True` in your `.env` file for detailed error messages.

## 📂 Project Structure
```
api/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env.template      # Environment variables template
├── .env               # Your actual environment variables (don't commit!)
└── README.md          # This file
```

## 🎯 Next Steps

1. **Add Authentication**: Implement API key authentication
2. **Add Rate Limiting**: Prevent API abuse
3. **Add Logging**: Better logging and monitoring
4. **Add Tests**: Unit and integration tests
5. **Deploy**: Deploy to Azure App Service or container

## 📝 License

This project is part of the Hackathon 2025 codebase.