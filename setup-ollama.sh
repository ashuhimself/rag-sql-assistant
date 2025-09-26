#!/bin/bash

set -e

echo "🚀 Setting up Ollama in Docker with Qwen 3 (14B) model..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="ollama-qwen"
OLLAMA_PORT="11434"
MODEL_NAME="qwen2.5:14b"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed and running
check_docker() {
    print_status "Checking Docker installation..."

    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi

    print_success "Docker is installed and running"
}

# Stop and remove existing container if it exists
cleanup_existing() {
    print_status "Cleaning up existing Ollama container..."

    if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_warning "Stopping and removing existing container: ${CONTAINER_NAME}"
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME} 2>/dev/null || true
    fi
}

# Pull and run Ollama container
setup_ollama_container() {
    print_status "Setting up Ollama container..."

    # Pull the latest Ollama image
    print_status "Pulling Ollama Docker image..."
    docker pull ollama/ollama:latest

    # Run Ollama container with GPU support if available
    print_status "Starting Ollama container..."
    if command -v nvidia-smi &> /dev/null; then
        print_status "NVIDIA GPU detected, enabling GPU support..."
        docker run -d \
            --gpus all \
            --name ${CONTAINER_NAME} \
            -p ${OLLAMA_PORT}:11434 \
            -v ollama-data:/root/.ollama \
            --restart unless-stopped \
            ollama/ollama:latest
    else
        print_warning "No NVIDIA GPU detected, running in CPU mode..."
        docker run -d \
            --name ${CONTAINER_NAME} \
            -p ${OLLAMA_PORT}:11434 \
            -v ollama-data:/root/.ollama \
            --restart unless-stopped \
            ollama/ollama:latest
    fi

    print_success "Ollama container started successfully"
}

# Wait for Ollama to be ready
wait_for_ollama() {
    print_status "Waiting for Ollama to be ready..."

    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:${OLLAMA_PORT}/api/tags > /dev/null 2>&1; then
            print_success "Ollama is ready"
            return 0
        fi

        print_status "Attempt ${attempt}/${max_attempts} - Waiting for Ollama..."
        sleep 2
        ((attempt++))
    done

    print_error "Ollama failed to start within expected time"
    return 1
}

# Install Qwen 3 (14B) model
install_qwen_model() {
    print_status "Installing Qwen 2.5 (14B) model..."
    print_warning "This may take a while as the model is large (~8GB)..."

    # Pull the model using docker exec
    if docker exec ${CONTAINER_NAME} ollama pull ${MODEL_NAME}; then
        print_success "Qwen 2.5 (14B) model installed successfully"
    else
        print_error "Failed to install Qwen 2.5 (14B) model"
        return 1
    fi
}

# Verify installation
verify_installation() {
    print_status "Verifying installation..."

    # Check if container is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_error "Ollama container is not running"
        return 1
    fi
    print_success "✓ Ollama container is running"

    # Check if Ollama API is accessible
    if ! curl -s http://localhost:${OLLAMA_PORT}/api/tags > /dev/null; then
        print_error "Ollama API is not accessible"
        return 1
    fi
    print_success "✓ Ollama API is accessible at http://localhost:${OLLAMA_PORT}"

    # Check if Qwen model is installed
    if docker exec ${CONTAINER_NAME} ollama list | grep -q "${MODEL_NAME}"; then
        print_success "✓ Qwen 2.5 (14B) model is installed"
    else
        print_error "Qwen 2.5 (14B) model is not found"
        return 1
    fi

    # Test model inference
    print_status "Testing model inference..."
    local test_response=$(docker exec ${CONTAINER_NAME} ollama run ${MODEL_NAME} "Hello, what is 2+2?" --no-wordwrap 2>/dev/null | head -1)

    if [ -n "$test_response" ]; then
        print_success "✓ Model inference test successful"
        echo "  Response: $test_response"
    else
        print_error "Model inference test failed"
        return 1
    fi

    return 0
}

# Display usage information
display_usage() {
    echo ""
    echo "🎉 Ollama with Qwen 2.5 (14B) setup completed successfully!"
    echo ""
    echo "📋 Usage Information:"
    echo "  • Container name: ${CONTAINER_NAME}"
    echo "  • API endpoint: http://localhost:${OLLAMA_PORT}"
    echo "  • Model name: ${MODEL_NAME}"
    echo ""
    echo "🔧 Useful Commands:"
    echo "  • Test the model:"
    echo "    docker exec ${CONTAINER_NAME} ollama run ${MODEL_NAME} \"Your question here\""
    echo ""
    echo "  • List installed models:"
    echo "    docker exec ${CONTAINER_NAME} ollama list"
    echo ""
    echo "  • Check container status:"
    echo "    docker ps | grep ${CONTAINER_NAME}"
    echo ""
    echo "  • View container logs:"
    echo "    docker logs ${CONTAINER_NAME}"
    echo ""
    echo "  • Stop the container:"
    echo "    docker stop ${CONTAINER_NAME}"
    echo ""
    echo "  • Start the container:"
    echo "    docker start ${CONTAINER_NAME}"
    echo ""
    echo "🌐 API Usage Example:"
    echo "  curl -X POST http://localhost:${OLLAMA_PORT}/api/generate \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"model\": \"${MODEL_NAME}\", \"prompt\": \"Hello, world!\"}'"
    echo ""
}

# Main execution
main() {
    echo "=================================================="
    echo "      Ollama + Qwen 2.5 (14B) Setup Script"
    echo "=================================================="
    echo ""

    check_docker
    cleanup_existing
    setup_ollama_container
    wait_for_ollama
    install_qwen_model

    if verify_installation; then
        display_usage
        exit 0
    else
        print_error "Installation verification failed"
        exit 1
    fi
}

# Handle script interruption
trap 'print_error "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@"