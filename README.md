# Chift MCP Server

This MCP (Model Context Protocol) server provides integration between Chift API and any LLM provider supporting the MCP protocol (e.g., Claude for Desktop), allowing you to interact with your financial data using natural language.

## ✨ Features
- Query Chift API entities using natural language
- Access all your connected financial software and services
- Create, update, and delete financial data through conversational interfaces
- Auto-generated tools based on the Chift OpenAPI specification
- Support for multiple financial domains (accounting, commerce, invoicing, etc.)
- Configurable operation types for each domain

## 📦 Installation

### Prerequisites

- A Chift account with client credentials
- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv)

Install `uv` with standalone installer:
```bash
# On macOS and Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

or through pip:
```bash
# With pip.
pip install uv

# With pipx.
pipx install uv
```

Clone the repository:
```bash
cd ~/dev/chift
git clone https://github.com/chift-oneapi/mcp
```

## 🔌 MCP Integration
Add this configuration to your MCP client config file.

In Claude Desktop, you can access the config file at:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

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
        "CHIFT_URL_BASE": "https://api.chift.eu"
      }
    }
  }
}
```

Note: If you experience any path issues, try using absolute paths for both the `uv` command and the directory.

## 🔑 Environment Variables

The following environment variables are used by the Chift MCP Server:

- `CHIFT_CLIENT_SECRET`: Your Chift client secret
- `CHIFT_CLIENT_ID`: Your Chift client ID
- `CHIFT_ACCOUNT_ID`: Your Chift account ID
- `CHIFT_URL_BASE`: Chift API URL (default: https://api.chift.eu)

## 🚀 Available Tools

The Chift MCP Server dynamically generates tools based on the Chift OpenAPI specification. These tools provide access to various Chift API endpoints and include operations for:

- Retrieving financial data
- Managing your financial connections
- Creating new financial records (invoices, payments, etc.)
- Updating existing records
- And more, based on your specific Chift integrations

## 🔍 How It Works

1. The server initializes a connection to the Chift API
2. It parses the OpenAPI specification to identify available methods
3. Connections are mapped to Chift SDK modules
4. MCP tools are created based on the available API methods
5. Tools are registered with the MCP server
6. The server processes natural language requests from Claude

## 💬 Example Usages with Claude

After setup, you can ask Claude to:

- "Show me all my accounting connections"
- "Create a new invoice with the following details..."
- "How many active clients do I have?"
- "Get the balance of my bank account"
- "Compare revenue between last month and this month"

## 🔄 Run the server

```bash
# Run directly
cd /path/to/chift-mcp-server
uv run python main.py

# Or install and run as a package
uv pip install -e .
chift-mcp-server
```

Or with the configuration set in Claude Desktop, simply restart Claude Desktop and look for the tool icon in the message input.

## 🛠️ Function Configuration

The Chift MCP Server supports configuring which operations are available for each domain. By default, all operations are enabled for all domains:

```python
DEFAULT_CONFIG = {
    "accounting": ["get", "create", "update", "add"],
    "commerce": ["get", "create", "update", "add"],
    "invoicing": ["get", "create", "update", "add"],
    "payment": ["get", "create", "update", "add"],
    "pms": ["get", "create", "update", "add"],
    "pos": ["get", "create", "update", "add"],
}
```

You can customize this configuration by setting the `CHIFT_FUNCTION_CONFIG` environment variable as a JSON string:

```json
{
  "mcpServers": {
    "chift": {
      "env": {
        "CHIFT_FUNCTION_CONFIG": '{"accounting": ["get", "create"], "commerce": ["get"]}'
      }
    }
  }
}
```

This example would restrict the accounting domain to only get and create operations, and commerce to only get operations.

## 👨‍💻 Developer Guide

If you want to contribute to the Chift MCP Server or modify it for your needs, follow these steps:

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/chift-oneapi/mcp
   cd mcp
   ```

2. Install dependencies using `uv`:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e ".[dev]"
   ```

### Development Commands

The project uses [poethepoet](https://github.com/nat-n/poethepoet) for task running. Here are the available commands:

```bash
# Lint the code
uv run poe lint

# Format the code
uv run poe format

# Run tests
uv run poe test

# Install dependencies
uv run poe install
```

### Project Structure

The Chift MCP Server is organized as a Python package with the following structure:

- `src/chift_mcp/` - Main package
  - `tools/` - MCP tool definitions and generator
  - `utils/` - Helper utilities
- `tests/` - Test files

### Adding New Features

To add new features or modify existing ones:

1. Make your changes in the appropriate files
2. Format and lint your code: `uv run poe format && uv run poe lint`
3. Run tests to ensure everything works: `uv run poe test`
4. Submit a pull request