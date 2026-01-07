#!/usr/bin/env python3
"""
Test script to verify the RAG system functionality
"""

import asyncio
import httpx
import json


async def test_rag_system():
    """
    Test the RAG system endpoints
    """
    base_url = "http://localhost:8000/api/v1"

    print("Testing RAG system...")

    # Test health endpoint
    async with httpx.AsyncClient() as client:
        try:
            print("\n1. Testing health endpoint...")
            response = await client.get(f"{base_url}/health")
            print(f"Health check: {response.status_code} - {response.json()}")

            # Test query endpoint with a sample question
            print("\n2. Testing query endpoint...")
            query_data = {
                "query": "What is this book about?",
                "top_k": 3
            }
            response = await client.post(f"{base_url}/query", json=query_data)
            print(f"Query response: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Response: {result.get('response', 'No response text')[:200]}...")
                print(f"Sources: {result.get('sources', [])}")
            else:
                print(f"Query failed: {response.text}")

            # Test chat endpoint
            print("\n3. Testing chat endpoint...")
            chat_data = {
                "query": "Can you summarize what this book covers?",
                "session_id": "test-session-123"
            }
            response = await client.post(f"{base_url}/chat", json=chat_data)
            print(f"Chat response: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"Chat response: {result.get('response', 'No response text')[:200]}...")
                print(f"Session ID: {result.get('session_id')}")
            else:
                print(f"Chat failed: {response.text}")

            # Test stats endpoint
            print("\n4. Testing stats endpoint...")
            response = await client.get(f"{base_url}/query/stats")
            print(f"Stats response: {response.status_code}")
            if response.status_code == 200:
                stats = response.json()
                print(f"Stats: {json.dumps(stats, indent=2)}")
            else:
                print(f"Stats failed: {response.text}")

        except Exception as e:
            print(f"Error during testing: {e}")
            import traceback
            traceback.print_exc()


async def test_ingestion():
    """
    Test the ingestion functionality
    """
    base_url = "http://localhost:8000/api/v1"

    print("\nTesting ingestion system...")

    async with httpx.AsyncClient() as client:
        try:
            # Test ingestion status
            print("\n1. Testing ingestion status...")
            response = await client.get(f"{base_url}/ingest/status")
            print(f"Ingestion status: {response.status_code} - {response.json()}")

        except Exception as e:
            print(f"Error during ingestion testing: {e}")
            import traceback
            traceback.print_exc()


async def main():
    """
    Main test function
    """
    print("Starting RAG system tests...")

    await test_rag_system()
    await test_ingestion()

    print("\nTests completed!")


if __name__ == "__main__":
    asyncio.run(main())