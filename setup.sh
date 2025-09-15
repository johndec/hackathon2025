#!/bin/bash

# Setup script for Azure AI RAG project
# Run this after deploying the Azure infrastructure

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_status "Setting up Azure AI RAG project..."

# Check if Python is available
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    print_error "Python is not installed. Please install Python 3.8 or later."
    exit 1
fi

# Use python3 if available, otherwise python
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi

print_status "Using Python command: $PYTHON_CMD"

# Check Python version
PYTHON_VERSION=$($PYTHON_CMD -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
print_status "Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    $PYTHON_CMD -m venv venv
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp .env.template .env
    print_warning "Please edit .env with your Azure resource endpoints and keys"
else
    print_status ".env file already exists"
fi

# Check if sample docs exist and offer to index them
if [ -d "docs/sample" ]; then
    echo ""
    read -p "Do you want to index the sample documentation? (y/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Indexing sample documentation..."
        if $PYTHON_CMD src/index_documents.py --directory docs/sample --recreate-index; then
            print_status "Sample documents indexed successfully!"
        else
            print_warning "Failed to index sample documents. You may need to configure your .env file first."
        fi
    fi
fi

print_status "Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your Azure resource information"
echo "2. Index your documents: $PYTHON_CMD src/index_documents.py --directory /path/to/your/docs"
echo "3. Start chatting: $PYTHON_CMD src/chat.py"
echo ""
echo "For help, run: $PYTHON_CMD src/chat.py --help"