# Grasshopper MCP Server

A Model Context Protocol (MCP) server that bridges LM Studio and Grasshopper, enabling AI-driven parametric design through natural language instructions.

## Overview

This project allows you to control Grasshopper through natural language by leveraging Large Language Models (LLMs) running in LM Studio. The system consists of:

1. **MCP Server (Python)**: Acts as a bridge between LM Studio and Grasshopper
2. **LM Studio Client**: Handles communication with LM Studio's OpenAI-compatible API
3. **Grasshopper MCP Component**: A Grasshopper plugin that receives and executes commands

## Features

- Natural language interface for Grasshopper operations
- Support for gtp-oss 20B/120B models via LM Studio
- Component creation (Circle, Point, Line, Extrude, etc.)
- Component connection and parameter management
- Real-time communication between LLM and Grasshopper
- Extensible component knowledge base

## Installation

### Prerequisites

- Python 3.8 or higher
- LM Studio with gtp-oss model loaded
- Rhino 7+ with Grasshopper
- Grasshopper MCP Component (GH_MCP.gha) - to be developed

### Python Dependencies

```bash
pip install -r requirements.txt
```

### LM Studio Setup

1. Download and install LM Studio
2. Load a gtp-oss model (20B or 120B)
3. Start the local server (default: localhost:1234)
4. Ensure the server is running in OpenAI compatibility mode

## Usage

### Starting the MCP Server

```bash
python mcp_server.py
```

The server will start on `http://localhost:5000` by default.

### Using the LM Studio Client

```bash
python lm_studio_client.py
```

This provides an interactive interface where you can type natural language commands like:
- "Create a circle with radius 10"
- "Create a point at coordinates (5, 5, 0)"
- "Connect the circle to an extrude component"
- "Clear the canvas"

### API Endpoints

The MCP Server provides the following REST API endpoints:

- `GET /health` - Health check
- `GET /components` - List available components
- `POST /create_component` - Create a Grasshopper component
- `POST /connect_components` - Connect two components
- `POST /clear_canvas` - Clear the Grasshopper canvas

## Architecture

```
User Input (Natural Language)
    ↓
LM Studio (gtp-oss LLM)
    ↓
LM Studio Client (Function Calls)
    ↓
MCP Server (Command Processing)
    ↓
Grasshopper MCP Component (TCP)
    ↓
Grasshopper (Component Creation)
```

## Component Knowledge Base

The system includes a knowledge base of Grasshopper components with:
- Component names and internal identifiers
- Input/output parameters and types
- Default values and constraints
- Usage examples

Currently supported components:
- **Circle**: Create circles with radius and plane
- **Point**: Create points from X, Y, Z coordinates
- **Line**: Create lines between two points
- **Extrude**: Extrude curves or surfaces

## Development

### Adding New Components

To add support for new Grasshopper components:

1. Update the `ComponentKnowledgeBase` class in `mcp_server.py`
2. Add component information including parameters and types
3. Update the LM Studio tools definition in `lm_studio_client.py`
4. Implement the component creation logic in the Grasshopper MCP Component

### Testing

The system can be tested without Grasshopper by running the MCP Server and using the health check endpoint:

```bash
curl http://localhost:5000/health
```

## Troubleshooting

### Common Issues

1. **LM Studio Connection Failed**
   - Ensure LM Studio is running on localhost:1234
   - Check that a model is loaded and the server is started
   - Verify OpenAI compatibility mode is enabled

2. **Grasshopper Connection Failed**
   - Ensure the Grasshopper MCP Component is installed and running
   - Check that the TCP port (8888) is not blocked
   - Verify Grasshopper is open with the MCP component on the canvas

3. **Component Creation Errors**
   - Check the component knowledge base for supported components
   - Verify parameter types and required values
   - Review the MCP Server logs for detailed error messages

## Future Enhancements

- Support for more Grasshopper components
- Advanced parameter validation
- Visual feedback and preview
- Batch operations and scripting
- Integration with Grasshopper's native scripting components
- Support for custom user-defined components

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

