#!/usr/bin/env python3
"""
Document Indexer for Azure AI RAG System

This script processes documents and indexes them in Azure AI Search for use
with the RAG system.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SearchField, SearchFieldDataType, SimpleField,
    SearchableField, VectorSearch, VectorSearchProfile,
    HnswAlgorithmConfiguration, SemanticConfiguration,
    SemanticField, SemanticPrioritizedFields, SemanticSearch
)
from azure.core.credentials import AzureKeyCredential
from rag_system import DocumentProcessor, create_rag_system_from_env, create_rag_system_from_keyvault

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentIndexer:
    """Handles document indexing operations"""
    
    def __init__(self, search_endpoint: str, search_api_key: str, index_name: str = "documents"):
        self.search_endpoint = search_endpoint
        self.search_api_key = search_api_key
        self.index_name = index_name
        self.credential = AzureKeyCredential(search_api_key)
        self.index_client = SearchIndexClient(endpoint=search_endpoint, credential=self.credential)
        self.search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=self.credential)
    
    def create_search_index(self) -> bool:
        """Create or update the search index"""
        try:
            # Define the fields for the search index
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchableField(name="title", type=SearchFieldDataType.String),
                SearchableField(name="content", type=SearchFieldDataType.String),
                SimpleField(name="source", type=SearchFieldDataType.String, filterable=True),
                SimpleField(name="chunk_id", type=SearchFieldDataType.Int32),
                SearchField(
                    name="contentVector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,  # text-embedding-ada-002 dimensions
                    vector_search_profile_name="default"
                )
            ]
            
            # Configure vector search
            vector_search = VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(name="default")
                ],
                profiles=[
                    VectorSearchProfile(
                        name="default",
                        algorithm_configuration_name="default"
                    )
                ]
            )
            
            # Configure semantic search
            semantic_config = SemanticConfiguration(
                name="default",
                prioritized_fields=SemanticPrioritizedFields(
                    title_field=SemanticField(field_name="title"),
                    content_fields=[SemanticField(field_name="content")]
                )
            )
            
            semantic_search = SemanticSearch(configurations=[semantic_config])
            
            # Create the search index
            index = SearchIndex(
                name=self.index_name,
                fields=fields,
                vector_search=vector_search,
                semantic_search=semantic_search
            )
            
            # Create or update the index
            result = self.index_client.create_or_update_index(index)
            logger.info(f"Search index '{self.index_name}' created/updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error creating search index: {e}")
            return False
    
    def index_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """Index a batch of documents"""
        try:
            # Upload documents in batches
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i+batch_size]
                self.search_client.upload_documents(documents=batch)
                logger.info(f"Indexed batch {i//batch_size + 1}: {len(batch)} documents")
            
            logger.info(f"Successfully indexed {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error indexing documents: {e}")
            return False

def read_text_file(file_path: Path) -> str:
    """Read content from a text file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return ""

def process_documents(
    document_processor: DocumentProcessor,
    file_paths: List[Path],
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> List[Dict[str, Any]]:
    """Process documents and prepare them for indexing"""
    documents = []
    doc_id = 0
    
    for file_path in file_paths:
        logger.info(f"Processing file: {file_path}")
        
        # Read file content
        content = read_text_file(file_path)
        if not content:
            continue
        
        # Get file info
        title = file_path.stem
        source = str(file_path)
        
        # Split into chunks
        chunks = document_processor.chunk_text(content, chunk_size, chunk_overlap)
        
        for chunk_id, chunk in enumerate(chunks):
            # Generate embeddings for the chunk
            try:
                embeddings = document_processor.generate_embeddings(chunk)
                
                # Create document
                document = {
                    "id": f"doc_{doc_id}",
                    "title": title,
                    "content": chunk,
                    "source": source,
                    "chunk_id": chunk_id,
                    "contentVector": embeddings
                }
                
                documents.append(document)
                doc_id += 1
                
            except Exception as e:
                logger.error(f"Error processing chunk {chunk_id} from {file_path}: {e}")
                continue
        
        logger.info(f"Processed {len(chunks)} chunks from {file_path}")
    
    return documents

def find_documents(directory: Path, extensions: List[str] = None) -> List[Path]:
    """Find all documents in a directory"""
    if extensions is None:
        extensions = ['.txt', '.md', '.rst', '.html', '.pdf']
    
    documents = []
    
    for ext in extensions:
        documents.extend(directory.rglob(f'*{ext}'))
    
    return sorted(documents)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Index documents for Azure AI RAG System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index all documents in a directory
  python index_documents.py --directory ./docs
  
  # Index specific files
  python index_documents.py --files doc1.txt doc2.md
  
  # Use Key Vault for configuration
  python index_documents.py --directory ./docs \\
                           --keyvault-url https://mykv.vault.azure.net/ \\
                           --openai-endpoint https://myopenai.openai.azure.com/ \\
                           --search-endpoint https://mysearch.search.windows.net
  
  # Custom chunk settings
  python index_documents.py --directory ./docs --chunk-size 1500 --chunk-overlap 300
        """
    )
    
    # Document source options
    source_group = parser.add_mutually_exclusive_group(required=True)
    source_group.add_argument(
        "--directory", "-d",
        type=Path,
        help="Directory containing documents to index"
    )
    source_group.add_argument(
        "--files", "-f",
        nargs="+",
        type=Path,
        help="Specific files to index"
    )
    
    # Configuration options
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
    
    # Index options
    parser.add_argument(
        "--index-name",
        default="documents",
        help="Name of the search index (default: documents)"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=1000,
        help="Size of text chunks (default: 1000)"
    )
    parser.add_argument(
        "--chunk-overlap",
        type=int,
        default=200,
        help="Overlap between chunks (default: 200)"
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=['.txt', '.md', '.rst'],
        help="File extensions to process (default: .txt .md .rst)"
    )
    parser.add_argument(
        "--recreate-index",
        action="store_true",
        help="Recreate the search index (will delete existing data)"
    )
    
    args = parser.parse_args()
    
    # Set up RAG system for document processing
    try:
        if args.keyvault_url:
            if not args.openai_endpoint or not args.search_endpoint:
                print("Error: When using Key Vault, you must provide --openai-endpoint and --search-endpoint")
                sys.exit(1)
            
            rag_system = create_rag_system_from_keyvault(
                args.keyvault_url,
                args.openai_endpoint,
                args.search_endpoint
            )
        else:
            rag_system = create_rag_system_from_env()
        
        # Update index name if specified
        rag_system.config.search_index_name = args.index_name
        
    except Exception as e:
        logger.error(f"Error setting up RAG system: {e}")
        sys.exit(1)
    
    # Create document indexer
    indexer = DocumentIndexer(
        search_endpoint=rag_system.config.search_endpoint,
        search_api_key=rag_system.config.search_api_key,
        index_name=args.index_name
    )
    
    # Create or update search index
    if args.recreate_index or args.index_name != "documents":
        logger.info("Creating/updating search index...")
        if not indexer.create_search_index():
            logger.error("Failed to create search index")
            sys.exit(1)
    
    # Find documents to process
    if args.directory:
        if not args.directory.exists():
            logger.error(f"Directory not found: {args.directory}")
            sys.exit(1)
        
        logger.info(f"Finding documents in {args.directory}")
        file_paths = find_documents(args.directory, args.extensions)
    else:
        file_paths = args.files
        # Verify files exist
        for file_path in file_paths:
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                sys.exit(1)
    
    if not file_paths:
        logger.warning("No documents found to process")
        sys.exit(0)
    
    logger.info(f"Found {len(file_paths)} documents to process")
    
    # Process documents
    logger.info("Processing documents and generating embeddings...")
    documents = process_documents(
        rag_system.document_processor,
        file_paths,
        args.chunk_size,
        args.chunk_overlap
    )
    
    if not documents:
        logger.warning("No documents were successfully processed")
        sys.exit(0)
    
    # Index documents
    logger.info(f"Indexing {len(documents)} document chunks...")
    if indexer.index_documents(documents):
        logger.info("Document indexing completed successfully!")
    else:
        logger.error("Document indexing failed")
        sys.exit(1)

if __name__ == "__main__":
    main()