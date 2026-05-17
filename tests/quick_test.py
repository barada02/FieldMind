"""
Quick test script to verify the orchestrator agent is working.
This is a simplified version for quick validation.
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

try:
    from agent import get_agent
    print("✓ Successfully imported agent module")
except ImportError as e:
    print(f"✗ Failed to import agent: {e}")
    print("\nMake sure you have installed all dependencies:")
    print("  cd backend && pip install -r requirements.txt")
    sys.exit(1)

try:
    print("\nInitializing orchestrator agent...")
    agent = get_agent()
    print("✓ Agent initialized successfully")
    
    print("\nTesting basic conversation...")
    response = agent.chat("Hello! Who are you?", thread_id="quick_test")
    print(f"\nUser: Hello! Who are you?")
    print(f"Agent: {response}")
    
    print("\n" + "="*70)
    print("✓ Quick test passed! The agent is working correctly.")
    print("="*70)
    print("\nNext steps:")
    print("1. Start the server: cd backend && python -m uvicorn app.main:app --reload")
    print("2. Run full tests: cd tests && python test_chat_api.py --mode test")
    print("3. Try interactive mode: cd tests && python test_chat_api.py --mode interactive")
    
except Exception as e:
    print(f"\n✗ Error during testing: {e}")
    import traceback
    traceback.print_exc()
    print("\nPlease check:")
    print("1. Your .env file has OPENAI_API_KEY, OPENAI_BASE_URL, and OPENAI_MODEL set")
    print("2. All dependencies are installed: pip install -r backend/requirements.txt")
    print("3. Your API credentials are valid")
    sys.exit(1)

# Made with Bob
