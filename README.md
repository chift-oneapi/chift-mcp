# Chift MCP Server

A Model Context Protocol (MCP) server that bridges Claude and Chift API, enabling natural language interaction with Chift's financial services and integrations.

## Overview

This server parses the Chift OpenAPI specification to automatically generate MCP tools from available API methods, allowing Claude to:

- Interact with financial software and services connected through Chift
- Perform operations like retrieving, creating, updating, and deleting data
- Access the full capabilities of Chift through natural language

## Prerequisites

- Install `uv` on your system: [uv installation guide](https://docs.astral.sh/uv/getting-started/installation/)
- Claude Desktop application

## Quick Setup for Claude Desktop

1. Clone the repository:
   ```bash
   cd ~/dev/chift
   git clone https://github.com/chift-oneapi/mcp
   ```

2. Configure Claude Desktop by editing its configuration file:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
   - **Linux**: `~/.config/Claude/claude_desktop_config.json`

3. Add the following to the configuration file:
   ```json
   {
     "mcpServers": {
       "chift": {
         "command": "/path/to/uv",
         "args": [
           "run",
           "--directory",
           "/path/to/chift-mcp-server",
           "python",
           "main.py"
         ],
         "env": {
           "CHIFT_CLIENT_SECRET": "your_client_secret",
           "CHIFT_CLIENT_ID": "your_client_id",
           "CHIFT_ACCOUNT_ID": "your_account_id",
           "CHIFT_URL_BASE": "https://api.chift.eu",
           "CHIFT_CONSUMER_ID": "your_consumer_id"
         }
       }
     }
   }
   ```

4. Restart Claude Desktop and look for the tool icon in the message input.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CHIFT_CLIENT_SECRET` | Your Chift client secret |
| `CHIFT_CLIENT_ID` | Your Chift client ID |
| `CHIFT_ACCOUNT_ID` | Your Chift account ID |
| `CHIFT_CONSUMER_ID` | Your Chift consumer ID |
| `CHIFT_URL_BASE` | Chift API URL (default: https://api.chift.eu) |

## How It Works

1. The server initializes a connection to the Chift API
2. It parses the OpenAPI specification to identify available methods
3. Connections are mapped to Chift SDK modules
4. MCP tools are created based on the available API methods
5. Tools are registered with the MCP server
6. The server processes requests from Claude

## Project Structure

```
.
├── main.py                     # Entry point
├── pyproject.toml              # Dependencies
├── src
│   ├── config.py               # Environment configuration
│   ├── constants.py            # Project constants
│   ├── models.py               # Data models
│   ├── openapi_spec            # OpenAPI handling
│   │   ├── parser.py           # OpenAPI parser
│   │   └── schema              # OpenAPI schema
│   │       └── openapi.json
│   ├── tools                   # MCP tools
│   │   └── chift_mapper.py     # Maps Chift API to MCP tools
│   └── utils.py                # Helper functions
```

## Example Usages with Claude

After setup, you can ask Claude to:

- "Show me all my accounting connections"
- "Create a new invoice with the following details..."
- "How many active clients do I have?"
- etc 

## TBD (Future Work)
- [ ] **Chift SDK Migration**: Update to the latest version of the Chift SDK
- [ ] **Method Optimization**: Allow selection of specific methods (get, update, create, etc.) to reduce the number of generated tools
- [ ] **Resource Conversion**: Convert read-only methods (get/all) to MCP resources for better context management
- [ ] **Prompt Templates**: Prepare templates for common operations and workflows
- [ ] **Performance Improvements**: Optimize tool generation and execution

## Dependencies

See `pyproject.toml` for the complete list of dependencies.