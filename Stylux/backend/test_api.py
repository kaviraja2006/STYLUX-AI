#!/usr/bin/env python3
"""
Test script for STYLUX AI Backend API
"""

import requests
import json

def test_health_endpoint():
    """Test the health endpoint."""
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"✅ Health endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False

def test_test_endpoint():
    """Test the test endpoint."""
    try:
        response = requests.get("http://localhost:8000/test")
        print(f"✅ Test endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Test endpoint failed: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint."""
    try:
        data = {
            "message": "I have fair skin and like blue colors",
            "conversation_history": [
                {
                    "sender": "user",
                    "text": "Hello",
                    "timestamp": "12:00:00"
                }
            ]
        }
        
        response = requests.post(
            "http://localhost:8000/chat",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Chat endpoint: {response.status_code}")
        result = response.json()
        print(f"   Response: {result.get('response', 'No response')[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Chat endpoint failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing STYLUX AI Backend API")
    print("=" * 50)
    
    # Test endpoints
    health_ok = test_health_endpoint()
    test_ok = test_test_endpoint()
    chat_ok = test_chat_endpoint()
    
    print("\n" + "=" * 50)
    if health_ok and test_ok and chat_ok:
        print("🎉 All tests passed! Backend is working correctly.")
    else:
        print("❌ Some tests failed. Please check the backend setup.")
    
    print("\n📚 API Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main() 