#!/usr/bin/env python3
"""
Test script to verify LLM providers (Ollama and Gemini) are working correctly.
"""

import os
import sys
import django
from pathlib import Path

# Add backend to path and setup Django
backend_path = Path(__file__).parent / 'backend'
sys.path.append(str(backend_path))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from utils.llm_client import LLMClient


def test_provider(provider_name: str, api_key: str = None):
    """Test a specific LLM provider"""
    print(f"\n{'='*50}")
    print(f"Testing {provider_name.upper()} Provider")
    print(f"{'='*50}")

    # Set environment variables
    os.environ['LLM_PROVIDER'] = provider_name
    if api_key and provider_name == 'gemini':
        os.environ['GEMINI_API_KEY'] = api_key

    try:
        # Initialize client
        client = LLMClient()
        print(f"✓ LLM Client initialized for {provider_name}")

        # Test connection
        print("Testing connection...")
        connection_result = client.test_connection()

        if connection_result['success']:
            print(f"✓ Connection successful!")
            print(f"  Model: {connection_result.get('model', 'Unknown')}")
            print(f"  Response: {connection_result.get('response', 'No response')}")
        else:
            print(f"✗ Connection failed: {connection_result.get('error', 'Unknown error')}")
            return False

        # Test SQL generation
        print("\nTesting SQL generation...")
        test_schemas = [
            {
                'table_name': 'customers',
                'ddl_statement': 'CREATE TABLE customers (id SERIAL PRIMARY KEY, name VARCHAR(100), email VARCHAR(100));'
            }
        ]

        sql_query = client.generate_sql("Show me all customers", test_schemas)
        print(f"✓ SQL generated: {sql_query}")

        # Test response generation
        print("\nTesting response generation...")
        test_result = {
            'success': True,
            'data': [['John Doe', 'john@example.com']],
            'columns': ['name', 'email'],
            'row_count': 1
        }

        response = client.generate_response(
            "Show me all customers",
            sql_query,
            test_result
        )
        print(f"✓ Response generated: {response[:100]}...")

        print(f"\n✓ All tests passed for {provider_name.upper()}!")
        return True

    except Exception as e:
        print(f"✗ Error testing {provider_name}: {str(e)}")
        return False


def main():
    print("LLM Provider Test Script")
    print("This script tests both Ollama and Gemini providers")

    # Test Ollama (default)
    print("\n1. Testing Ollama (requires local Ollama installation)")
    ollama_success = test_provider('ollama')

    # Test Gemini
    print("\n2. Testing Gemini (requires API key)")
    gemini_api_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()

    if gemini_api_key:
        gemini_success = test_provider('gemini', gemini_api_key)
    else:
        print("Skipping Gemini test (no API key provided)")
        gemini_success = False

    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Ollama:  {'✓ PASS' if ollama_success else '✗ FAIL'}")
    print(f"Gemini:  {'✓ PASS' if gemini_success else '✗ FAIL (or skipped)'}")

    if ollama_success or gemini_success:
        print("\n✓ At least one provider is working!")
        print("\nTo switch providers, update the LLM_PROVIDER environment variable:")
        print("  For Ollama: LLM_PROVIDER=ollama")
        print("  For Gemini: LLM_PROVIDER=gemini (and set GEMINI_API_KEY)")
    else:
        print("\n✗ No providers are working. Please check your configuration.")


if __name__ == "__main__":
    main()