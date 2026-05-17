"""
Quick test script for multi-agent routing.
Run this to verify RAG and Cloudant agent routing works correctly.
"""

import sys
sys.path.insert(0, 'backend')

from agent.orchestrator import get_agent

def test_routing():
    """Test the multi-agent routing system."""
    agent = get_agent()
    
    print("=" * 60)
    print("MULTI-AGENT ROUTING TEST")
    print("=" * 60)
    
    # Test 1: RAG Agent routing
    print("\n[TEST 1] RAG Agent - SOP Query")
    print("-" * 60)
    query1 = "How do I perform maintenance on machine X?"
    print(f"Query: {query1}")
    print(f"Response:\n{agent.chat(query1)}\n")
    
    # Test 2: RAG Agent routing - manual
    print("\n[TEST 2] RAG Agent - Manual Query")
    print("-" * 60)
    query2 = "Show me the manual for equipment installation"
    print(f"Query: {query2}")
    print(f"Response:\n{agent.chat(query2)}\n")
    
    # Test 3: Cloudant Agent routing
    print("\n[TEST 3] Cloudant Agent - Machine Status")
    print("-" * 60)
    query3 = "What is the status of machine 123?"
    print(f"Query: {query3}")
    print(f"Response:\n{agent.chat(query3)}\n")
    
    # Test 4: Cloudant Agent routing - tickets
    print("\n[TEST 4] Cloudant Agent - Ticket Query")
    print("-" * 60)
    query4 = "Show me open tickets for site A"
    print(f"Query: {query4}")
    print(f"Response:\n{agent.chat(query4)}\n")
    
    # Test 5: General LLM routing
    print("\n[TEST 5] General LLM - Greeting")
    print("-" * 60)
    query5 = "Hello, how are you?"
    print(f"Query: {query5}")
    print(f"Response:\n{agent.chat(query5)}\n")
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_routing()

# Made with Bob
