#!/bin/bash

# Setup script for RAG-based AI SQL Assistant

set -e

echo "🚀 Setting up RAG-based AI SQL Assistant"
echo "========================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install Ollama first."
    echo "📖 Visit: https://ollama.ai/"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create .env file from example
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp .env.example .env
    echo "✅ .env file created. Please review and update the configuration."
else
    echo "ℹ️  .env file already exists. Skipping creation."
fi

# Pull Ollama model
echo "🤖 Setting up Ollama model..."
OLLAMA_MODEL=${OLLAMA_MODEL:-"llama3.2"}
echo "📥 Pulling model: $OLLAMA_MODEL"
ollama pull $OLLAMA_MODEL

# Start Ollama service
echo "🚀 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!
sleep 5

# Test Ollama connection
echo "🔍 Testing Ollama connection..."
if curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "✅ Ollama is running successfully"
else
    echo "❌ Failed to connect to Ollama"
    kill $OLLAMA_PID 2>/dev/null || true
    exit 1
fi

# Build and start Docker containers
echo "🐳 Building and starting Docker containers..."
docker-compose up -d --build

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Test service connections
echo "🔍 Testing service connections..."

# Test PostgreSQL
if docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL is not ready"
fi

# Test Qdrant
if curl -s http://localhost:6333/health > /dev/null; then
    echo "✅ Qdrant is ready"
else
    echo "❌ Qdrant is not ready"
fi

# Test Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis is not ready"
fi

# Run Django migrations
echo "🗄️  Running Django migrations..."
docker-compose exec backend python manage.py migrate

# Create embeddings for schema
echo "🧠 Creating schema embeddings..."
docker-compose exec backend python manage.py shell << 'EOF'
from apps.embeddings.services import EmbeddingService
from django.db import connection

# Get schema definitions
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM schema_definitions;")
    schemas = cursor.fetchall()

embedding_service = EmbeddingService()

schema_definitions = []
for schema in schemas:
    schema_definitions.append({
        'table_name': schema[0],
        'ddl_statement': schema[1],
        'description': schema[2]
    })

embedding_service.embed_all_schemas(schema_definitions)
print(f"✅ Embedded {len(schema_definitions)} schemas")
EOF

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📊 Service URLs:"
echo "   Frontend:     http://localhost:3000"
echo "   Backend API:  http://localhost:8000"
echo "   Qdrant UI:    http://localhost:6333/dashboard"
echo ""
echo "🛠️  Management Commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop:         docker-compose down"
echo "   Restart:      docker-compose restart"
echo ""
echo "📖 To get started:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Ask questions like 'How many customers do we have?'"
echo "   3. Check the API documentation at http://localhost:8000/admin"
echo ""