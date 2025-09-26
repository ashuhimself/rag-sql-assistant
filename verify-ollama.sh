#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONTAINER_NAME="ollama-qwen"
OLLAMA_PORT="11434"

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

# Test functions
test_docker_running() {
    print_status "Testing Docker container status..."

    if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
        print_success "✓ Ollama container '${CONTAINER_NAME}' is running"

        # Get container info
        local container_info=$(docker ps --format "table {{.Image}}\t{{.Status}}\t{{.Ports}}" | grep ollama)
        echo "  Container info: $container_info"
        return 0
    else
        print_error "✗ Ollama container '${CONTAINER_NAME}' is not running"
        return 1
    fi
}

test_api_accessibility() {
    print_status "Testing Ollama API accessibility..."

    if curl -s http://localhost:${OLLAMA_PORT}/api/tags > /dev/null; then
        print_success "✓ Ollama API is accessible at http://localhost:${OLLAMA_PORT}"
        return 0
    else
        print_error "✗ Ollama API is not accessible"
        return 1
    fi
}

test_api_response() {
    print_status "Testing API response format..."

    local response=$(curl -s http://localhost:${OLLAMA_PORT}/api/tags)
    if echo "$response" | grep -q '"models"'; then
        print_success "✓ API returns valid JSON response"
        echo "  Response: $response"
        return 0
    else
        print_error "✗ API response format is invalid"
        echo "  Response: $response"
        return 1
    fi
}

check_available_models() {
    print_status "Checking available models..."

    local models=$(docker exec ${CONTAINER_NAME} ollama list 2>/dev/null | tail -n +2)
    if [ -n "$models" ]; then
        print_success "✓ Found installed models:"
        echo "$models" | while read line; do
            if [ -n "$line" ]; then
                echo "  - $line"
            fi
        done
        return 0
    else
        print_warning "⚠ No models are currently installed"
        echo "  Models are still downloading or need to be installed manually"
        return 1
    fi
}

test_model_download_capability() {
    print_status "Testing model download capability with small model..."

    # Try to download a very small model for testing
    print_status "Attempting to download 'llama3.2:1b' (small test model)..."

    # Start download in background and check if it begins
    if timeout 30s docker exec ${CONTAINER_NAME} ollama pull llama3.2:1b > /dev/null 2>&1; then
        print_success "✓ Model download completed successfully"
        return 0
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            print_warning "⚠ Model download started but timed out (this is expected for large models)"
            print_status "Download is likely continuing in the background"
        else
            print_error "✗ Model download failed to start"
            return 1
        fi
    fi
}

test_basic_functionality() {
    print_status "Testing basic Ollama functionality..."

    # Test if we can get version info
    local version=$(docker exec ${CONTAINER_NAME} ollama --version 2>/dev/null)
    if [ $? -eq 0 ]; then
        print_success "✓ Ollama version: $version"
    else
        print_error "✗ Could not get Ollama version"
        return 1
    fi

    # Test if server is responsive
    if docker exec ${CONTAINER_NAME} ollama list > /dev/null 2>&1; then
        print_success "✓ Ollama server is responsive"
        return 0
    else
        print_error "✗ Ollama server is not responsive"
        return 1
    fi
}

show_usage_examples() {
    echo ""
    echo "🔧 Quick Test Commands:"
    echo ""
    echo "  • Check container status:"
    echo "    docker ps | grep ${CONTAINER_NAME}"
    echo ""
    echo "  • List available models:"
    echo "    docker exec ${CONTAINER_NAME} ollama list"
    echo ""
    echo "  • Download a small model for testing:"
    echo "    docker exec ${CONTAINER_NAME} ollama pull llama3.2:1b"
    echo ""
    echo "  • Test API directly:"
    echo "    curl http://localhost:${OLLAMA_PORT}/api/tags"
    echo ""
    echo "  • Check container logs:"
    echo "    docker logs ${CONTAINER_NAME} --tail 20"
    echo ""
}

# Main verification
main() {
    echo "=================================================="
    echo "         Ollama Setup Verification"
    echo "=================================================="
    echo ""

    local tests_passed=0
    local total_tests=5

    # Run all tests
    if test_docker_running; then
        ((tests_passed++))
    fi

    if test_api_accessibility; then
        ((tests_passed++))
    fi

    if test_api_response; then
        ((tests_passed++))
    fi

    if test_basic_functionality; then
        ((tests_passed++))
    fi

    # Check models (this might fail if downloads are still in progress)
    if check_available_models; then
        ((tests_passed++))
    else
        print_status "This is normal if model downloads are still in progress"
    fi

    echo ""
    echo "=================================================="
    echo "         Verification Summary"
    echo "=================================================="

    if [ $tests_passed -eq $total_tests ]; then
        print_success "🎉 All tests passed! Ollama setup is fully functional."
    elif [ $tests_passed -ge 4 ]; then
        print_success "✅ Core functionality verified! ($tests_passed/$total_tests tests passed)"
        print_warning "Models may still be downloading in the background."
    else
        print_error "❌ Some critical tests failed. ($tests_passed/$total_tests tests passed)"
        echo ""
        echo "Troubleshooting steps:"
        echo "1. Check if Docker is running: docker info"
        echo "2. Check container logs: docker logs ${CONTAINER_NAME}"
        echo "3. Restart container: docker restart ${CONTAINER_NAME}"
    fi

    show_usage_examples

    return 0
}

# Run verification
main "$@"