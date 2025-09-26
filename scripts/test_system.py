#!/usr/bin/env python
"""
System integration test script
"""

import os
import sys
import requests
import time
import json

def test_service(name, url, timeout=5):
    """Test if a service is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            print(f"✅ {name} is responding")
            return True
        else:
            print(f"❌ {name} returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ {name} is not responding: {str(e)}")
        return False


def test_database_api():
    """Test database API endpoints"""
    print("\n🗄️  Testing Database API...")

    # Test connection
    if not test_service("Database connection", "http://localhost:8000/api/database/test/"):
        return False

    # Test table listing
    try:
        response = requests.get("http://localhost:8000/api/database/tables/")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('tables'):
                print(f"✅ Found {len(data['tables'])} tables in database")
                return True
        print("❌ Failed to list database tables")
        return False
    except Exception as e:
        print(f"❌ Database API error: {str(e)}")
        return False


def test_embeddings_api():
    """Test embeddings API endpoints"""
    print("\n🧠 Testing Embeddings API...")

    # Test schema listing
    try:
        response = requests.get("http://localhost:8000/api/embeddings/schemas/")
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('schemas'):
                print(f"✅ Found {len(data['schemas'])} embedded schemas")
            else:
                print("⚠️  No schemas found - run embed_schemas.py first")
            return True
        print("❌ Failed to list embedded schemas")
        return False
    except Exception as e:
        print(f"❌ Embeddings API error: {str(e)}")
        return False


def test_chat_api():
    """Test chat API endpoints"""
    print("\n💬 Testing Chat API...")

    # Test chat endpoint with a simple query
    try:
        payload = {
            "message": "How many customers do we have?"
        }
        response = requests.post(
            "http://localhost:8000/api/chat/",
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Chat API is working")
                print(f"   Session ID: {data.get('session_id')}")
                print(f"   Response: {data.get('message', {}).get('content', 'N/A')[:100]}...")
                return True

        print(f"❌ Chat API failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False

    except Exception as e:
        print(f"❌ Chat API error: {str(e)}")
        return False


def test_ollama_connection():
    """Test Ollama connection"""
    print("\n🤖 Testing Ollama Connection...")

    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"✅ Ollama is running with {len(models)} models")
            for model in models:
                print(f"   - {model.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ollama connection error: {str(e)}")
        print("   Make sure Ollama is running: ollama serve")
        return False


def main():
    """Run all system tests"""
    print("🧪 Running System Integration Tests")
    print("===================================")

    tests = [
        ("Frontend", "http://localhost:3000"),
        ("Backend API", "http://localhost:8000"),
        ("Qdrant", "http://localhost:6333/health"),
        ("PostgreSQL via Backend", "http://localhost:8000/api/database/test/"),
    ]

    print("\n🔍 Testing Basic Service Connectivity...")
    all_basic_tests_passed = True

    for name, url in tests:
        if not test_service(name, url):
            all_basic_tests_passed = False

    if not all_basic_tests_passed:
        print("\n❌ Basic connectivity tests failed. Please check your setup.")
        return

    # Test Ollama separately (might not be containerized)
    ollama_ok = test_ollama_connection()

    # Test API functionality
    db_api_ok = test_database_api()
    embeddings_api_ok = test_embeddings_api()
    chat_api_ok = test_chat_api()

    print("\n📊 Test Results Summary:")
    print("========================")
    print(f"Frontend:          {'✅' if True else '❌'}")  # Already tested above
    print(f"Backend API:       {'✅' if True else '❌'}")  # Already tested above
    print(f"Qdrant:           {'✅' if True else '❌'}")   # Already tested above
    print(f"PostgreSQL:       {'✅' if True else '❌'}")   # Already tested above
    print(f"Ollama:           {'✅' if ollama_ok else '❌'}")
    print(f"Database API:     {'✅' if db_api_ok else '❌'}")
    print(f"Embeddings API:   {'✅' if embeddings_api_ok else '❌'}")
    print(f"Chat API:         {'✅' if chat_api_ok else '❌'}")

    if all([ollama_ok, db_api_ok, embeddings_api_ok, chat_api_ok]):
        print("\n🎉 All tests passed! The system is ready for use.")
        print("\n🚀 Next steps:")
        print("   1. Open http://localhost:3000 in your browser")
        print("   2. Try asking: 'How many customers do we have?'")
        print("   3. Explore the banking data with natural language queries")
    else:
        print("\n⚠️  Some tests failed. Please check the logs and configuration.")
        print("   - Check Docker containers: docker-compose logs")
        print("   - Verify Ollama is running: ollama serve")
        print("   - Run schema embedding: python scripts/embed_schemas.py")


if __name__ == "__main__":
    main()