#!/bin/bash

# Setup script for PDF Notes API

set -e

echo "====================================="
echo "PDF Notes API - Setup Script"
echo "====================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file with your credentials:"
    echo "   - SUPABASE_URL"
    echo "   - SUPABASE_KEY"
    echo "   - GEMINI_API_KEY (or OPENAI_API_KEY)"
    echo ""
    read -p "Press enter to continue after editing .env file..."
else
    echo "✓ .env file already exists"
fi

# Create necessary directories
echo ""
echo "Creating directories..."
mkdir -p uploads
mkdir -p data/chroma
echo "✓ Directories created"

# Check if Docker is installed
echo ""
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✓ Docker is installed"

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi
echo "✓ Docker Compose is installed"

# Build Docker images
echo ""
echo "Building Docker images..."
docker-compose build

echo ""
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Make sure you've configured .env with your credentials"
echo ""
echo "2. Set up Supabase database:"
echo "   - Go to your Supabase project"
echo "   - Open SQL Editor"
echo "   - Run the SQL from supabase_schema.sql"
echo ""
echo "3. Start the services:"
echo "   docker-compose up"
echo ""
echo "4. Access the API:"
echo "   - API: http://localhost:8000"
echo "   - Docs: http://localhost:8000/docs"
echo "   - Flower: http://localhost:5555"
echo ""
echo "5. Test with a PDF:"
echo "   curl -X POST http://localhost:8000/upload \\"
echo "     -F 'file=@your-file.pdf'"
echo ""
echo "====================================="
