#!/usr/bin/env python3
"""
Simple example script to demonstrate the Azure AI RAG system.

This script shows basic usage patterns for the RAG system.
"""

import os
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from rag_system import create_rag_system_from_env
except ImportError as e:
    print(f"Error importing RAG system: {e}")
    print("Make sure to install requirements: pip install -r requirements.txt")
    sys.exit(1)

def main():
    """Main example function"""
    print("🤖 Azure AI RAG System - Example Usage")
    print("=" * 50)
    
    # Check if environment is configured
    required_vars = [
        "AZURE_OPENAI_ENDPOINT",
        "AZURE_OPENAI_API_KEY", 
        "AZURE_SEARCH_ENDPOINT",
        "AZURE_SEARCH_API_KEY"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables or use the Key Vault configuration.")
        print("See .env.template for examples.")
        return
    
    try:
        # Create RAG system
        print("🔧 Initializing RAG system...")
        rag = create_rag_system_from_env()
        
        # Example questions
        example_questions = [
            "How do I deploy the infrastructure?",
            "What Azure services are used in this project?",
            "How do I index my own documents?",
            "What is the architecture of this system?"
        ]
        
        print("\n📝 Example Questions and Answers:")
        print("=" * 50)
        
        for i, question in enumerate(example_questions, 1):
            print(f"\n{i}. Question: {question}")
            print("-" * 30)
            
            try:
                response = rag.chat(question)
                print(f"Answer: {response['answer'][:200]}...")
                
                if response['sources']:
                    print(f"Sources: {len(response['sources'])} documents found")
                else:
                    print("Sources: No relevant documents found")
                    
            except Exception as e:
                print(f"❌ Error processing question: {e}")
        
        print("\n✅ Example completed! Use src/chat.py for interactive chatting.")
        
    except Exception as e:
        print(f"❌ Error initializing RAG system: {e}")
        print("\nTroubleshooting tips:")
        print("1. Ensure Azure resources are deployed")
        print("2. Check API keys and endpoints")
        print("3. Make sure documents are indexed")
        print("4. Verify network connectivity")

if __name__ == "__main__":
    main()