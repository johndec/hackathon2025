#!/usr/bin/env python3
"""
Interactive CLI for the Azure AI RAG System

This script provides a command-line interface for chatting with the RAG system
about documentation.
"""

import os
import sys
import json
from typing import Optional
import argparse
from rag_system import create_rag_system_from_env, create_rag_system_from_keyvault, RAGSystem

def print_welcome():
    """Print welcome message"""
    print("="*60)
    print("🤖 Azure AI RAG Documentation Chat")
    print("="*60)
    print("Ask me anything about your documentation!")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("Type 'help' for more commands.")
    print("="*60)

def print_help():
    """Print help message"""
    print("\nAvailable commands:")
    print("  help - Show this help message")
    print("  quit/exit/bye - Exit the application")
    print("  clear - Clear the screen")
    print("  config - Show current configuration")
    print("\nJust type your question to get started!")

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_config(rag_system: RAGSystem):
    """Show current configuration"""
    config = rag_system.config
    print("\nCurrent Configuration:")
    print(f"  OpenAI Endpoint: {config.openai_endpoint}")
    print(f"  Search Endpoint: {config.search_endpoint}")
    print(f"  Search Index: {config.search_index_name}")
    print(f"  OpenAI Model: {config.openai_deployment_name}")
    print(f"  Embedding Model: {config.embedding_deployment_name}")
    print(f"  Max Search Results: {config.max_search_results}")
    print(f"  Max Tokens: {config.max_tokens}")

def format_response(response: dict) -> str:
    """Format the response for display"""
    output = []
    
    # Answer
    output.append("🤖 Answer:")
    output.append("-" * 50)
    output.append(response["answer"])
    
    # Sources
    if response["sources"]:
        output.append("\n📚 Sources:")
        output.append("-" * 50)
        for i, source in enumerate(response["sources"], 1):
            output.append(f"{i}. {source['title']} (Relevance: {source['score']:.2f})")
            if source.get('source'):
                output.append(f"   📄 {source['source']}")
    
    return "\n".join(output)

def setup_rag_system(args) -> Optional[RAGSystem]:
    """Set up the RAG system based on command line arguments"""
    try:
        if args.keyvault_url:
            if not args.openai_endpoint or not args.search_endpoint:
                print("Error: When using Key Vault, you must provide --openai-endpoint and --search-endpoint")
                return None
            
            print("Setting up RAG system using Azure Key Vault...")
            return create_rag_system_from_keyvault(
                args.keyvault_url,
                args.openai_endpoint,
                args.search_endpoint
            )
        else:
            print("Setting up RAG system using environment variables...")
            return create_rag_system_from_env()
    
    except Exception as e:
        print(f"Error setting up RAG system: {e}")
        print("\nPlease check your configuration:")
        print("1. Environment variables are set correctly, OR")
        print("2. Key Vault URL and endpoints are provided")
        return None

def interactive_chat(rag_system: RAGSystem):
    """Run interactive chat loop"""
    print_welcome()
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n👋 Goodbye! Thanks for chatting!")
                break
            elif user_input.lower() == 'help':
                print_help()
                continue
            elif user_input.lower() == 'clear':
                clear_screen()
                print_welcome()
                continue
            elif user_input.lower() == 'config':
                show_config(rag_system)
                continue
            
            # Process the question
            print("\n🔍 Searching documentation...")
            response = rag_system.chat(user_input)
            
            # Display the response
            print("\n" + format_response(response))
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Thanks for chatting!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try again or type 'help' for assistance.")

def single_question_mode(rag_system: RAGSystem, question: str):
    """Handle single question mode"""
    print(f"Question: {question}")
    print("\n🔍 Searching documentation...")
    
    response = rag_system.chat(question)
    print("\n" + format_response(response))

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Interactive CLI for Azure AI RAG Documentation Chat",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode using environment variables
  python chat.py
  
  # Interactive mode using Key Vault
  python chat.py --keyvault-url https://mykv.vault.azure.net/ \\
                 --openai-endpoint https://myopenai.openai.azure.com/ \\
                 --search-endpoint https://mysearch.search.windows.net
  
  # Single question mode
  python chat.py --question "How do I deploy the infrastructure?"
  
Environment Variables (when not using Key Vault):
  AZURE_OPENAI_ENDPOINT - Azure OpenAI endpoint URL
  AZURE_OPENAI_API_KEY - Azure OpenAI API key
  AZURE_SEARCH_ENDPOINT - Azure AI Search endpoint URL
  AZURE_SEARCH_API_KEY - Azure AI Search API key
        """
    )
    
    parser.add_argument(
        "--question", "-q",
        help="Ask a single question and exit (non-interactive mode)"
    )
    
    parser.add_argument(
        "--keyvault-url",
        help="Azure Key Vault URL for retrieving secrets"
    )
    
    parser.add_argument(
        "--openai-endpoint",
        help="Azure OpenAI endpoint (required when using Key Vault)"
    )
    
    parser.add_argument(
        "--search-endpoint",
        help="Azure AI Search endpoint (required when using Key Vault)"
    )
    
    args = parser.parse_args()
    
    # Set up the RAG system
    rag_system = setup_rag_system(args)
    if not rag_system:
        sys.exit(1)
    
    # Run in appropriate mode
    if args.question:
        single_question_mode(rag_system, args.question)
    else:
        interactive_chat(rag_system)

if __name__ == "__main__":
    main()