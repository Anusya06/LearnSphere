#!/bin/bash

# LearnSphere Pro - Setup Script
# This script sets up the development environment

set -e

echo "🎓 LearnSphere Pro - Setup Script"
echo "=================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11+${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found${NC}"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${BLUE}📝 Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env file created. Please edit it with your API keys.${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Setup Backend
echo ""
echo -e "${BLUE}🔧 Setting up Backend...${NC}"
cd backend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✅ Backend setup complete${NC}"

cd ..

# Setup Frontend
echo ""
echo -e "${BLUE}🎨 Setting up Frontend...${NC}"
cd frontend

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing frontend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✅ Frontend setup complete${NC}"

cd ..

# Create necessary directories
echo ""
echo -e "${BLUE}📁 Creating directories...${NC}"
mkdir -p logs
mkdir -p uploads
mkdir -p exports

echo -e "${GREEN}✅ Directories created${NC}"

# Final instructions
echo ""
echo -e "${GREEN}🎉 Setup Complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API keys (GROQ_API_KEY, etc.)"
echo "2. Start the backend:"
echo "   cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo "3. Start the frontend (in a new terminal):"
echo "   cd frontend && source venv/bin/activate && streamlit run Home.py"
echo ""
echo "Or use Docker:"
echo "   docker-compose up -d"
echo ""
echo "📚 Documentation: README.md"
echo "🚀 Deployment Guide: DEPLOYMENT.md"
echo ""
echo -e "${BLUE}Happy Learning! 🎓${NC}"