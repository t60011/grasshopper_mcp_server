#!/usr/bin/env python3
"""
LM Studio Client for Grasshopper MCP Server
Handles communication with LM Studio API
"""

import json
import logging
import requests
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class LMStudioClient:
    """Client for communicating with LM Studio API"""
    
    def __init__(self, base_url: str = "http://localhost:1234", api_key: str = "lm-studio"):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Define available tools for Grasshopper operations
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_grasshopper_component",
                    "description": "Create a component in Grasshopper",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "component_name": {
                                "type": "string",
                                "description": "Name of the component to create (e.g., 'circle', 'point', 'line', 'extrude')"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Parameters for the component",
                                "properties": {
                                    "Radius": {"type": "number", "description": "Radius for circle"},
                                    "X": {"type": "number", "description": "X coordinate"},
                                    "Y": {"type": "number", "description": "Y coordinate"},
                                    "Z": {"type": "number", "description": "Z coordinate"},
                                    "Plane": {"type": "string", "description": "Plane (e.g., 'XY', 'XZ', 'YZ')"}
                                }
                            }
                        },
                        "required": ["component_name"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "connect_grasshopper_components",
                    "description": "Connect two components in Grasshopper",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "source_component": {
                                "type": "string",
                                "description": "Name of the source component"
                            },
                            "source_param": {
                                "type": "string",
                                "description": "Name of the source parameter (e.g., 'Circle', 'Point', 'Line')"
                            },
                            "target_component": {
                                "type": "string",
                                "description": "Name of the target component"
                            },
                            "target_param": {
                                "type": "string",
                                "description": "Name of the target parameter (e.g., 'Base', 'Start', 'End')"
                            }
                        },
                        "required": ["source_component", "source_param", "target_component", "target_param"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "clear_grasshopper_canvas",
                    "description": "Clear all components from the Grasshopper canvas",
                    "parameters": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        ]
    
    def chat_completion(self, messages: List[Dict[str, str]], model: str = "gpt-oss-20b") -> Dict[str, Any]:
        """Send a chat completion request to LM Studio"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "tools": self.tools,
                "tool_choice": "auto",
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error communicating with LM Studio: {e}")
            return {"error": str(e)}
    
    def get_available_models(self) -> List[str]:
        """Get list of available models from LM Studio"""
        try:
            response = requests.get(
                f"{self.base_url}/v1/models",
                headers=self.headers,
                timeout=10
            )
            
            response.raise_for_status()
            data = response.json()
            return [model["id"] for model in data.get("data", [])]
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting models from LM Studio: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test connection to LM Studio"""
        try:
            models = self.get_available_models()
            return len(models) > 0
        except:
            return False

class GrasshopperLLMInterface:
    """High-level interface for LLM-driven Grasshopper operations"""
    
    def __init__(self, lm_studio_client: LMStudioClient, mcp_server_url: str = "http://localhost:5000"):
        self.lm_client = lm_studio_client
        self.mcp_server_url = mcp_server_url.rstrip('/')
        self.conversation_history: List[Dict[str, str]] = []
        
        # Add system message with Grasshopper context
        self.conversation_history.append({
            "role": "system",
            "content": """You are an AI assistant that helps users create parametric designs in Grasshopper. 
            You have access to tools that can create and connect Grasshopper components.
            
            Available components:
            - circle: Creates a circle (parameters: Radius, Plane)
            - point: Creates a point (parameters: X, Y, Z)
            - line: Creates a line (parameters: Start, End)
            - extrude: Extrudes geometry (parameters: Base, Direction)
            
            When users ask you to create designs, use the available tools to create the appropriate components and connections.
            Always explain what you're doing and ask for clarification if needed."""
        })
    
    def process_user_input(self, user_input: str) -> str:
        """Process user input and execute Grasshopper operations"""
        # Add user message to conversation
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Get LLM response
        response = self.lm_client.chat_completion(self.conversation_history)
        
        if "error" in response:
            return f"Error communicating with LM Studio: {response['error']}"
        
        # Process the response
        choice = response.get("choices", [{}])[0]
        message = choice.get("message", {})
        
        # Add assistant message to conversation
        self.conversation_history.append(message)
        
        # Check if LLM wants to use tools
        tool_calls = message.get("tool_calls", [])
        if tool_calls:
            tool_results = []
            for tool_call in tool_calls:
                result = self._execute_tool_call(tool_call)
                tool_results.append(result)
            
            # Add tool results to conversation
            for i, result in enumerate(tool_results):
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_calls[i]["id"],
                    "content": json.dumps(result)
                })
            
            # Get final response from LLM
            final_response = self.lm_client.chat_completion(self.conversation_history)
            if "error" not in final_response:
                final_message = final_response.get("choices", [{}])[0].get("message", {})
                self.conversation_history.append(final_message)
                return final_message.get("content", "Operation completed.")
        
        return message.get("content", "I'm not sure how to help with that.")
    
    def _execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call"""
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        
        try:
            if function_name == "create_grasshopper_component":
                return self._create_component(arguments)
            elif function_name == "connect_grasshopper_components":
                return self._connect_components(arguments)
            elif function_name == "clear_grasshopper_canvas":
                return self._clear_canvas()
            else:
                return {"success": False, "error": f"Unknown function: {function_name}"}
        
        except Exception as e:
            logger.error(f"Error executing tool call {function_name}: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_component(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Grasshopper component"""
        try:
            response = requests.post(
                f"{self.mcp_server_url}/create_component",
                json=arguments,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"MCP Server error: {e}"}
    
    def _connect_components(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Connect Grasshopper components"""
        try:
            response = requests.post(
                f"{self.mcp_server_url}/connect_components",
                json=arguments,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"MCP Server error: {e}"}
    
    def _clear_canvas(self) -> Dict[str, Any]:
        """Clear Grasshopper canvas"""
        try:
            response = requests.post(
                f"{self.mcp_server_url}/clear_canvas",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"MCP Server error: {e}"}

def main():
    """Demo of LM Studio client"""
    # Initialize clients
    lm_client = LMStudioClient()
    interface = GrasshopperLLMInterface(lm_client)
    
    # Test connection
    if not lm_client.test_connection():
        print("Could not connect to LM Studio. Make sure it's running on localhost:1234")
        return
    
    print("Connected to LM Studio!")
    print("Available models:", lm_client.get_available_models())
    print("\nGrasshopper LLM Interface ready. Type 'quit' to exit.")
    
    while True:
        user_input = input("\nUser: ").strip()
        if user_input.lower() in ['quit', 'exit']:
            break
        
        if user_input:
            response = interface.process_user_input(user_input)
            print(f"Assistant: {response}")

if __name__ == "__main__":
    main()

