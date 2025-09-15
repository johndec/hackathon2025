import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")

# Initialize Azure OpenAI client
def get_openai_client():
    if not AZURE_OPENAI_API_KEY:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is not set")
    
    return AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "message": "Hackathon 2025 OpenAI API is running!",
        "endpoint": AZURE_OPENAI_ENDPOINT,
        "deployment": AZURE_OPENAI_DEPLOYMENT
    })

@app.route("/chat", methods=["POST"])
def chat():
    """Chat endpoint that calls Azure OpenAI"""
    try:
        # Get request data
        data = request.get_json()
        
        if not data or "message" not in data:
            return jsonify({"error": "Missing 'message' in request body"}), 400
        
        user_message = data["message"]
        system_prompt = data.get("system_prompt", "You are a helpful AI agent that answers questions when asked.")
        max_tokens = data.get("max_tokens", 500)
        temperature = data.get("temperature", 0.7)
        
        logger.info(f"Received chat request: {user_message[:50]}...")
        
        # Initialize OpenAI client
        client = get_openai_client()
        
        # Call Azure OpenAI
        response = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Extract response
        ai_response = response.choices[0].message.content
        
        logger.info("Successfully generated AI response")
        
        return jsonify({
            "response": ai_response,
            "model": AZURE_OPENAI_DEPLOYMENT,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        })
        
    except ValueError as ve:
        logger.error(f"Configuration error: {ve}")
        return jsonify({"error": f"Configuration error: {str(ve)}"}), 500
        
    except Exception as e:
        logger.error(f"Error calling OpenAI: {e}")
        return jsonify({"error": f"Failed to generate response: {str(e)}"}), 500

@app.route("/config", methods=["GET"])
def get_config():
    """Get current API configuration (without sensitive data)"""
    return jsonify({
        "endpoint": AZURE_OPENAI_ENDPOINT,
        "deployment": AZURE_OPENAI_DEPLOYMENT,
        "api_version": AZURE_OPENAI_API_VERSION,
        "api_key_configured": bool(AZURE_OPENAI_API_KEY)
    })

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    logger.info(f"Starting Hackathon 2025 OpenAI API on port {port}")
    logger.info(f"Azure OpenAI Endpoint: {AZURE_OPENAI_ENDPOINT}")
    logger.info(f"Deployment Name: {AZURE_OPENAI_DEPLOYMENT}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)