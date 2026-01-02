#!/usr/bin/env python3
"""
Test script to verify agent integration with the chat service
"""
import asyncio
from src.agents.agent_integration import get_agent_chat_service

async def test_agent_integration():
    print("Creating agent chat service...")
    chat_service = get_agent_chat_service()
    print("Testing agent chat processing...")
    try:
        result = await chat_service.process_chat_message("Hello, how are you?")
        print(f"Full result: {result}")
        print(f"Response: {result['response']}")
        print(f"Error (if any): {result.get('error')}")
    except Exception as e:
        print(f"Error in agent chat processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_agent_integration())