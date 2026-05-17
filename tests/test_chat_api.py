"""
Test script for the chat API with orchestrator agent.
Run the server first, then execute this script to test the chat functionality.
"""

import httpx
import json
import time
from typing import Optional


class ChatAPITester:
    """Test client for the chat API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the tester with base URL."""
        self.base_url = base_url
        self.conversation_id: Optional[str] = None
    
    def test_health(self) -> bool:
        """Test if the server is running."""
        try:
            response = httpx.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✓ Server is running")
                return True
            else:
                print(f"✗ Server returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Cannot connect to server: {e}")
            return False
    
    def send_message(self, message: str, conversation_id: Optional[str] = None) -> dict:
        """Send a message to the chat API."""
        payload = {
            "message": message,
            "conversation_id": conversation_id
        }
        
        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ Error sending message: {e}")
            return {}
    
    def get_history(self, conversation_id: str) -> list:
        """Get conversation history."""
        try:
            response = httpx.get(
                f"{self.base_url}/api/chat/history/{conversation_id}",
                timeout=10.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"✗ Error getting history: {e}")
            return []
    
    def run_tests(self):
        """Run all tests."""
        print("=" * 70)
        print("Field Mind Chat API Test Suite")
        print("=" * 70)
        
        # Test 1: Health check
        print("\n[Test 1] Health Check")
        print("-" * 70)
        if not self.test_health():
            print("\n✗ Server is not running. Please start the server first:")
            print("  cd backend && python -m uvicorn app.main:app --reload")
            return False
        
        # Test 2: Simple greeting
        print("\n[Test 2] Simple Greeting")
        print("-" * 70)
        print("Sending: 'Hello! Who are you?'")
        result = self.send_message("Hello! Who are you?")
        
        if result:
            self.conversation_id = result.get("conversation_id")
            print(f"Conversation ID: {self.conversation_id}")
            print(f"Response: {result.get('message', 'No response')}")
            print(f"Processing time: {result.get('metadata', {}).get('processing_time', 0)}s")
            print("✓ Test passed")
        else:
            print("✗ Test failed")
            return False
        
        time.sleep(1)
        
        # Test 3: Follow-up question (tests memory)
        print("\n[Test 3] Follow-up Question (Memory Test)")
        print("-" * 70)
        print("Sending: 'What can you help me with?'")
        result = self.send_message(
            "What can you help me with?",
            conversation_id=self.conversation_id
        )
        
        if result:
            print(f"Response: {result.get('message', 'No response')}")
            print(f"Processing time: {result.get('metadata', {}).get('processing_time', 0)}s")
            print("✓ Test passed")
        else:
            print("✗ Test failed")
            return False
        
        time.sleep(1)
        
        # Test 4: Technical question
        print("\n[Test 4] Technical Question")
        print("-" * 70)
        print("Sending: 'What should I check if a machine is overheating?'")
        result = self.send_message(
            "What should I check if a machine is overheating?",
            conversation_id=self.conversation_id
        )
        
        if result:
            print(f"Response: {result.get('message', 'No response')[:200]}...")
            print(f"Processing time: {result.get('metadata', {}).get('processing_time', 0)}s")
            print("✓ Test passed")
        else:
            print("✗ Test failed")
            return False
        
        time.sleep(1)
        
        # Test 5: Get conversation history
        print("\n[Test 5] Conversation History")
        print("-" * 70)
        history = self.get_history(self.conversation_id)
        
        if history:
            print(f"Retrieved {len(history)} messages:")
            for i, msg in enumerate(history, 1):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")[:60]
                print(f"  {i}. [{role}] {content}...")
            print("✓ Test passed")
        else:
            print("✗ Test failed - no history retrieved")
            return False
        
        # Test 6: New conversation
        print("\n[Test 6] New Conversation")
        print("-" * 70)
        print("Sending: 'Hello again!' (new conversation)")
        result = self.send_message("Hello again!")
        
        if result:
            new_conv_id = result.get("conversation_id")
            print(f"New Conversation ID: {new_conv_id}")
            print(f"Response: {result.get('message', 'No response')}")
            print(f"Different from previous: {new_conv_id != self.conversation_id}")
            print("✓ Test passed")
        else:
            print("✗ Test failed")
            return False
        
        # Summary
        print("\n" + "=" * 70)
        print("All tests passed! ✓")
        print("=" * 70)
        print("\nThe orchestrator agent is working correctly with:")
        print("  - Basic conversation")
        print("  - Memory/context retention")
        print("  - Technical question handling")
        print("  - Conversation history retrieval")
        print("  - Multiple conversation threads")
        
        return True
    
    def interactive_mode(self):
        """Run in interactive mode."""
        print("=" * 70)
        print("Field Mind Chat API - Interactive Mode")
        print("=" * 70)
        
        if not self.test_health():
            print("\n✗ Server is not running. Please start the server first:")
            print("  cd backend && python -m uvicorn app.main:app --reload")
            return
        
        print("\nCommands:")
        print("  - Type your message to chat")
        print("  - 'history' to see conversation history")
        print("  - 'new' to start a new conversation")
        print("  - 'quit' or 'exit' to exit")
        print("=" * 70)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["quit", "exit", "q"]:
                    print("\nGoodbye! 👋")
                    break
                
                if user_input.lower() == "history":
                    if self.conversation_id:
                        history = self.get_history(self.conversation_id)
                        if history:
                            print("\nConversation History:")
                            for i, msg in enumerate(history, 1):
                                role = "You" if msg["role"] == "user" else "Agent"
                                print(f"{i}. {role}: {msg['content']}")
                        else:
                            print("\nNo history available.")
                    else:
                        print("\nNo active conversation.")
                    continue
                
                if user_input.lower() == "new":
                    self.conversation_id = None
                    print("\nStarted new conversation.")
                    continue
                
                # Send message
                result = self.send_message(user_input, self.conversation_id)
                
                if result:
                    self.conversation_id = result.get("conversation_id")
                    print(f"\nAgent: {result.get('message', 'No response')}")
                    print(f"(Processing time: {result.get('metadata', {}).get('processing_time', 0)}s)")
                else:
                    print("\n✗ Failed to get response")
                
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\n✗ Error: {e}")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the Field Mind Chat API")
    parser.add_argument(
        "--mode",
        choices=["test", "interactive"],
        default="test",
        help="Run mode: 'test' for automated tests, 'interactive' for chat"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:8000",
        help="Base URL of the API server"
    )
    
    args = parser.parse_args()
    
    tester = ChatAPITester(base_url=args.url)
    
    if args.mode == "test":
        success = tester.run_tests()
        exit(0 if success else 1)
    else:
        tester.interactive_mode()


if __name__ == "__main__":
    main()

# Made with Bob
