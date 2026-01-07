"""
Test script for the OpenAI Agent SDK implementation
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the agent components
from backend.src.agents import get_rag_agent_manager, get_agent_chat_service

async def test_agent_creation():
    """Test that the agent is created successfully"""
    print("Testing agent creation...")

    try:
        agent_manager = get_rag_agent_manager()
        default_agent = agent_manager.get_default_agent()

        if default_agent:
            print(f"✓ Agent created successfully: {default_agent.name}")
            stats = await default_agent.get_agent_stats()
            print(f"✓ Agent stats: {stats}")
            return True
        else:
            print("✗ Failed to create agent")
            return False
    except Exception as e:
        print(f"✗ Error creating agent: {e}")
        return False

async def test_agent_query():
    """Test that the agent can process a simple query"""
    print("\nTesting agent query processing...")

    try:
        agent_manager = get_rag_agent_manager()
        result = await agent_manager.process_query("Hello, can you help me understand how RAG works?")
        print(f"✓ Agent response: {result[:100]}...")
        return True
    except Exception as e:
        print(f"✗ Error processing query: {e}")
        return False

async def test_agent_with_context():
    """Test that the agent can process a query with context"""
    print("\nTesting agent with context...")

    try:
        agent_manager = get_rag_agent_manager()
        result = await agent_manager.process_query_with_context(
            "What is RAG?",
            "RAG stands for Retrieval Augmented Generation. It's a technique that combines information retrieval with language model generation to produce more accurate and contextually relevant responses."
        )
        print(f"✓ Agent response with context: {result[:100]}...")
        return True
    except Exception as e:
        print(f"✗ Error processing query with context: {e}")
        return False

async def test_agent_chat_service():
    """Test the agent chat service integration"""
    print("\nTesting agent chat service...")

    try:
        chat_service = get_agent_chat_service()
        result = await chat_service.process_chat_message(
            query="What is the purpose of RAG in AI systems?",
            session_id=None,
            selected_text=None
        )
        print(f"✓ Chat service response: {result['response'][:100]}...")
        print(f"✓ Context used: {len(result.get('context_used', []))} items")
        print(f"✓ Grounding confidence: {result.get('grounding_confidence', 0.0)}")
        return True
    except Exception as e:
        print(f"✗ Error in chat service: {e}")
        return False

async def test_agent_with_selected_text():
    """Test the agent with selected text context"""
    print("\nTesting agent with selected text...")

    try:
        chat_service = get_agent_chat_service()
        selected_text = "RAG (Retrieval Augmented Generation) is an AI technique that improves language model responses by retrieving relevant information from external knowledge sources before generating a response."
        result = await chat_service.process_chat_message(
            query="Can you explain the concept mentioned in the selected text?",
            session_id=None,
            selected_text=selected_text
        )
        print(f"✓ Agent response with selected text: {result['response'][:100]}...")
        return True
    except Exception as e:
        print(f"✗ Error processing selected text: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("Starting OpenAI Agent SDK tests...\n")

    tests = [
        test_agent_creation,
        test_agent_query,
        test_agent_with_context,
        test_agent_chat_service,
        test_agent_with_selected_text
    ]

    results = []
    for test in tests:
        result = await test()
        results.append(result)

    print(f"\nTest Results: {sum(results)}/{len(results)} tests passed")

    if all(results):
        print("✓ All tests passed!")
        return True
    else:
        print("✗ Some tests failed")
        return False

if __name__ == "__main__":
    # Check if OPENROUTER_API_KEY is set
    if not os.getenv("OPENROUTER_API_KEY"):
        print("Error: OPENROUTER_API_KEY environment variable is not set.")
        print("Please set it in your .env file before running tests.")
        exit(1)

    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)