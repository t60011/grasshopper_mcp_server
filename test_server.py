#!/usr/bin/env python3
"""
Test script for Grasshopper MCP Server
"""

import requests
import json
import time

def test_mcp_server():
    """Test the MCP Server functionality"""
    base_url = "http://localhost:5000"
    
    print("Testing Grasshopper MCP Server...")
    
    # Test health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")
        return False
    
    # Test list components
    print("\n2. Testing list components...")
    try:
        response = requests.get(f"{base_url}/components", timeout=5)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Available components: {data.get('components', [])}")
    except Exception as e:
        print(f"List components failed: {e}")
    
    # Test create component
    print("\n3. Testing create component...")
    try:
        payload = {
            "component_name": "circle",
            "parameters": {
                "Radius": 10.0,
                "Plane": "XY"
            }
        }
        response = requests.post(f"{base_url}/create_component", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Create component failed: {e}")
    
    # Test create point
    print("\n4. Testing create point...")
    try:
        payload = {
            "component_name": "point",
            "parameters": {
                "X": 0.0,
                "Y": 0.0,
                "Z": 0.0
            }
        }
        response = requests.post(f"{base_url}/create_component", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Create point failed: {e}")
    
    # Test connect components
    print("\n5. Testing connect components...")
    try:
        payload = {
            "source_component": "point",
            "source_param": "Point",
            "target_component": "circle",
            "target_param": "Plane"
        }
        response = requests.post(f"{base_url}/connect_components", json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Connect components failed: {e}")
    
    # Test clear canvas
    print("\n6. Testing clear canvas...")
    try:
        response = requests.post(f"{base_url}/clear_canvas", timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Clear canvas failed: {e}")
    
    print("\nTest completed!")
    return True

def test_lm_studio_client():
    """Test LM Studio client functionality"""
    from lm_studio_client import LMStudioClient
    
    print("\nTesting LM Studio Client...")
    
    client = LMStudioClient()
    
    # Test connection
    print("1. Testing connection to LM Studio...")
    if client.test_connection():
        print("✓ Connected to LM Studio")
        models = client.get_available_models()
        print(f"Available models: {models}")
    else:
        print("✗ Could not connect to LM Studio")
        print("Make sure LM Studio is running on localhost:1234")
        return False
    
    # Test chat completion
    print("\n2. Testing chat completion...")
    try:
        messages = [
            {"role": "user", "content": "Hello, can you help me create a circle in Grasshopper?"}
        ]
        response = client.chat_completion(messages)
        if "error" in response:
            print(f"✗ Chat completion failed: {response['error']}")
        else:
            print("✓ Chat completion successful")
            choice = response.get("choices", [{}])[0]
            message = choice.get("message", {})
            print(f"Response: {message.get('content', 'No content')}")
    except Exception as e:
        print(f"✗ Chat completion failed: {e}")
    
    return True

if __name__ == "__main__":
    print("Grasshopper MCP Server Test Suite")
    print("=" * 40)
    
    # Test MCP Server
    test_mcp_server()
    
    # Test LM Studio Client
    test_lm_studio_client()

