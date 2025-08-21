#!/usr/bin/env python3
"""
Grasshopper MCP Server
A Model Context Protocol server that bridges LM Studio and Grasshopper
"""

import json
import socket
import threading
import time
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

from component_factory import ComponentFactory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ComponentInfo:
    """Information about a Grasshopper component"""
    name: str
    internal_name: str
    description: str
    input_params: Dict[str, Any]
    output_params: Dict[str, Any]
    guid: Optional[str] = None

class GrasshopperTCPClient:
    """TCP client for communicating with Grasshopper MCP Component"""
    
    def __init__(self, host: str = "localhost", port: int = 8888):
        self.host = host
        self.port = port
        self.socket = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to Grasshopper MCP Component"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Connected to Grasshopper MCP Component at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Grasshopper: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from Grasshopper MCP Component"""
        if self.socket:
            self.socket.close()
            self.connected = False
            logger.info("Disconnected from Grasshopper MCP Component")
    
    def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Send a command to Grasshopper and receive response"""
        if not self.connected:
            if not self.connect():
                return {"success": False, "error": "Not connected to Grasshopper"}
        
        try:
            # Send command as JSON
            command_json = json.dumps(command)
            self.socket.send(command_json.encode('utf-8') + b'\n')
            
            # Receive response
            response_data = b''
            while True:
                chunk = self.socket.recv(1024)
                if not chunk:
                    break
                response_data += chunk
                if b'\n' in response_data:
                    break
            
            response_json = response_data.decode('utf-8').strip()
            response = json.loads(response_json)
            return response
            
        except Exception as e:
            logger.error(f"Error sending command to Grasshopper: {e}")
            self.connected = False
            return {"success": False, "error": str(e)}

class ComponentKnowledgeBase:
    """Knowledge base for Grasshopper components - wrapper around ComponentFactory"""
    
    def __init__(self):
        self.factory = ComponentFactory()
    
    def get_component(self, name: str) -> Optional[Any]:
        """Get component information by name"""
        return self.factory.get_component(name)
    
    def list_components(self) -> List[str]:
        """List all available component names"""
        return self.factory.list_components()
    
    def get_component_info_for_llm(self) -> str:
        """Get component information formatted for LLM"""
        return self.factory.get_component_info_for_llm()
    
    @property
    def components(self) -> Dict[str, Any]:
        """Get all components"""
        return self.factory.components

class MCPServer:
    """Main MCP Server class"""
    
    def __init__(self):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for all routes
        
        self.grasshopper_client = GrasshopperTCPClient()
        self.knowledge_base = ComponentKnowledgeBase()
        self.created_components: Dict[str, str] = {}  # name -> guid mapping
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health_check():
            """Health check endpoint"""
            return jsonify({
                "status": "healthy",
                "grasshopper_connected": self.grasshopper_client.connected,
                "components_loaded": len(self.knowledge_base.components)
            })
        
        @self.app.route('/components', methods=['GET'])
        def list_components():
            """List available components"""
            return jsonify({
                "components": self.knowledge_base.list_components(),
                "info": self.knowledge_base.get_component_info_for_llm()
            })
        
        @self.app.route('/create_component', methods=['POST'])
        def create_component():
            """Create a Grasshopper component"""
            try:
                data = request.get_json()
                component_name = data.get('component_name', '').lower()
                parameters = data.get('parameters', {})
                
                # Get component info from knowledge base
                comp_info = self.knowledge_base.get_component(component_name)
                if not comp_info:
                    return jsonify({
                        "success": False,
                        "error": f"Unknown component: {component_name}"
                    }), 400
                
                # Validate parameters
                validated_params = self._validate_parameters(comp_info, parameters)
                if "error" in validated_params:
                    return jsonify({
                        "success": False,
                        "error": validated_params["error"]
                    }), 400
                
                # Send command to Grasshopper
                command = {
                    "command": "create_component",
                    "component_name": comp_info.internal_name,
                    "parameters": validated_params
                }
                
                response = self.grasshopper_client.send_command(command)
                
                if response.get("success"):
                    # Store component GUID for future reference
                    component_guid = response.get("component_guid")
                    if component_guid:
                        self.created_components[component_name] = component_guid
                
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"Error creating component: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/connect_components', methods=['POST'])
        def connect_components():
            """Connect two components"""
            try:
                data = request.get_json()
                source_component = data.get('source_component', '').lower()
                source_param = data.get('source_param', '')
                target_component = data.get('target_component', '').lower()
                target_param = data.get('target_param', '')
                
                # Get component GUIDs
                source_guid = self.created_components.get(source_component)
                target_guid = self.created_components.get(target_component)
                
                if not source_guid or not target_guid:
                    return jsonify({
                        "success": False,
                        "error": "One or both components not found"
                    }), 400
                
                # Send command to Grasshopper
                command = {
                    "command": "connect_parameters",
                    "source_component_guid": source_guid,
                    "source_parameter_name": source_param,
                    "target_component_guid": target_guid,
                    "target_parameter_name": target_param
                }
                
                response = self.grasshopper_client.send_command(command)
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"Error connecting components: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
        
        @self.app.route('/clear_canvas', methods=['POST'])
        def clear_canvas():
            """Clear the Grasshopper canvas"""
            try:
                command = {"command": "clear_canvas"}
                response = self.grasshopper_client.send_command(command)
                
                if response.get("success"):
                    self.created_components.clear()
                
                return jsonify(response)
                
            except Exception as e:
                logger.error(f"Error clearing canvas: {e}")
                return jsonify({
                    "success": False,
                    "error": str(e)
                }), 500
    
    def _validate_parameters(self, comp_info: Any, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Validate component parameters using ComponentFactory"""
        return self.knowledge_base.factory.validate_component_parameters(
            comp_info.name.lower(), parameters
        )
    
    def run(self, host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
        """Run the MCP server"""
        logger.info(f"Starting MCP Server on {host}:{port}")
        logger.info(f"Grasshopper components loaded: {len(self.knowledge_base.components)}")
        
        # Try to connect to Grasshopper
        if self.grasshopper_client.connect():
            logger.info("Successfully connected to Grasshopper MCP Component")
        else:
            logger.warning("Could not connect to Grasshopper MCP Component. Will retry on first request.")
        
        self.app.run(host=host, port=port, debug=debug)

def main():
    """Main entry point"""
    server = MCPServer()
    server.run(debug=True)

if __name__ == "__main__":
    main()

