"""
Azure AI RAG (Retrieval Augmented Generation) Application

This module provides the main functionality for the RAG system that can
converse about documentation using Azure OpenAI and Azure AI Search.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import json
import logging
from dataclasses import dataclass
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from openai import AzureOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Config:
    """Configuration class for the RAG application"""
    openai_endpoint: str
    openai_api_key: str
    search_endpoint: str
    search_api_key: str
    search_index_name: str = "documents"
    openai_deployment_name: str = "gpt-35-turbo"
    embedding_deployment_name: str = "text-embedding-ada-002"
    max_search_results: int = 5
    max_tokens: int = 1000

class AzureKeyVaultConfig:
    """Helper class to retrieve configuration from Azure Key Vault"""
    
    def __init__(self, key_vault_url: str):
        self.key_vault_url = key_vault_url
        self.credential = DefaultAzureCredential()
        self.client = SecretClient(vault_url=key_vault_url, credential=self.credential)
    
    def get_config(self, openai_endpoint: str, search_endpoint: str) -> Config:
        """Retrieve configuration from Key Vault"""
        try:
            openai_key = self.client.get_secret("openai-api-key").value
            search_key = self.client.get_secret("search-api-key").value
            
            return Config(
                openai_endpoint=openai_endpoint,
                openai_api_key=openai_key,
                search_endpoint=search_endpoint,
                search_api_key=search_key
            )
        except Exception as e:
            logger.error(f"Error retrieving secrets from Key Vault: {e}")
            raise

class DocumentProcessor:
    """Handles document processing and indexing"""
    
    def __init__(self, config: Config):
        self.config = config
        self.openai_client = AzureOpenAI(
            azure_endpoint=config.openai_endpoint,
            api_key=config.openai_api_key,
            api_version="2023-05-15"
        )
        self.search_client = SearchClient(
            endpoint=config.search_endpoint,
            index_name=config.search_index_name,
            credential=AzureKeyCredential(config.search_api_key)
        )
    
    def generate_embeddings(self, text: str) -> List[float]:
        """Generate embeddings for text using Azure OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                input=text,
                model=self.config.embedding_deployment_name
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to break at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size * 0.7:  # Only if we're not cutting too much
                    end = start + last_period + 1
                    chunk = text[start:end]
            
            chunks.append(chunk.strip())
            start = end - overlap
            
            if start >= len(text):
                break
        
        return chunks

class RAGSystem:
    """Main RAG system for conversational AI about documentation"""
    
    def __init__(self, config: Config):
        self.config = config
        self.openai_client = AzureOpenAI(
            azure_endpoint=config.openai_endpoint,
            api_key=config.openai_api_key,
            api_version="2023-05-15"
        )
        self.search_client = SearchClient(
            endpoint=config.search_endpoint,
            index_name=config.search_index_name,
            credential=AzureKeyCredential(config.search_api_key)
        )
        self.document_processor = DocumentProcessor(config)
    
    def search_documents(self, query: str, top_k: int = None) -> List[Dict[str, Any]]:
        """Search for relevant documents using vector similarity"""
        if top_k is None:
            top_k = self.config.max_search_results
        
        try:
            # Generate embeddings for the query
            query_embeddings = self.document_processor.generate_embeddings(query)
            
            # Create vector query
            vector_query = VectorizedQuery(
                vector=query_embeddings,
                k_nearest_neighbors=top_k,
                fields="contentVector"
            )
            
            # Perform search
            results = self.search_client.search(
                search_text=query,
                vector_queries=[vector_query],
                select=["id", "content", "title", "source"],
                top=top_k
            )
            
            return [
                {
                    "id": doc["id"],
                    "content": doc["content"],
                    "title": doc.get("title", ""),
                    "source": doc.get("source", ""),
                    "score": doc["@search.score"]
                }
                for doc in results
            ]
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    def generate_response(self, question: str, context_docs: List[Dict[str, Any]]) -> str:
        """Generate response using OpenAI with retrieved context"""
        
        # Prepare context from retrieved documents
        context = "\n\n".join([
            f"Document: {doc['title']}\nContent: {doc['content']}"
            for doc in context_docs
        ])
        
        # Create system message
        system_message = """
You are a helpful AI assistant that answers questions based on the provided documentation context.
Use only the information from the context to answer questions.
If the context doesn't contain enough information to answer the question, say so clearly.
Provide clear, concise answers and cite the relevant document titles when possible.
"""
        
        # Create user message with context
        user_message = f"""
Context:
{context}

Question: {question}

Please answer the question based on the provided context.
"""
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.config.openai_deployment_name,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=self.config.max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error while generating a response."
    
    def chat(self, question: str) -> Dict[str, Any]:
        """Main chat function that combines search and generation"""
        logger.info(f"Processing question: {question}")
        
        # Search for relevant documents
        relevant_docs = self.search_documents(question)
        
        if not relevant_docs:
            return {
                "answer": "I couldn't find any relevant information in the documentation to answer your question.",
                "sources": [],
                "context_used": []
            }
        
        # Generate response
        answer = self.generate_response(question, relevant_docs)
        
        # Prepare response
        sources = [
            {
                "title": doc["title"],
                "source": doc["source"],
                "score": doc["score"]
            }
            for doc in relevant_docs
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "context_used": [doc["content"][:200] + "..." for doc in relevant_docs]
        }

def create_rag_system_from_env() -> RAGSystem:
    """Create RAG system using environment variables"""
    config = Config(
        openai_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        openai_api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
        search_api_key=os.getenv("AZURE_SEARCH_API_KEY")
    )
    return RAGSystem(config)

def create_rag_system_from_keyvault(
    key_vault_url: str,
    openai_endpoint: str,
    search_endpoint: str
) -> RAGSystem:
    """Create RAG system using Azure Key Vault for secrets"""
    kv_config = AzureKeyVaultConfig(key_vault_url)
    config = kv_config.get_config(openai_endpoint, search_endpoint)
    return RAGSystem(config)

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python rag_system.py <question>")
        sys.exit(1)
    
    question = " ".join(sys.argv[1:])
    
    try:
        # Try to create from environment variables first
        rag = create_rag_system_from_env()
        response = rag.chat(question)
        
        print("\n" + "="*50)
        print("ANSWER:")
        print("="*50)
        print(response["answer"])
        
        print("\n" + "="*50)
        print("SOURCES:")
        print("="*50)
        for i, source in enumerate(response["sources"], 1):
            print(f"{i}. {source['title']} (Score: {source['score']:.2f})")
            if source['source']:
                print(f"   Source: {source['source']}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure to set the required environment variables or use Key Vault configuration")