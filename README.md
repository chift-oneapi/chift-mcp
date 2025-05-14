# Chift MCP Server

This [MCP](https://modelcontextprotocol.io/introduction) (Model Context Protocol) server provides integration
between [Chift API](https://www.chift.eu/) and any LLM provider supporting the MCP
protocol (e.g., [Claude for Desktop](https://claude.ai/download)), allowing you to interact with your financial data
using natural
language.

## ✨ Features

- Query Chift API entities using natural language
- Access all your connected financial software and services
- Create, update, and delete financial data through conversational interfaces
- Auto-generated tools based on the Chift OpenAPI specification
- Support for multiple financial domains (accounting, commerce, invoicing, etc.)
- Configurable operation types for each domain

# Chift MCP Server API Overview

The Chift MCP Server provides integration between Chift API and LLM providers like Claude, allowing natural language
interaction with financial data.

## Available Function Categories

The toolkit includes methods across several financial domains:

### Accounting

- **Data Retrieval**: Get folders, bookyears, clients, suppliers, invoices, journal entries
- **Creation**: Create clients, suppliers, ledger accounts, analytic accounts, journals
- **Financial Operations**: Match entries, create financial entries, get account balances

### Commerce (E-commerce)

- **Product Management**: Get products, variants, update inventory quantities
- **Customer Management**: Retrieve customer information
- **Order Processing**: Get orders, create new orders
- **Store Management**: Get locations, payment methods, product categories

### Invoicing

- **Invoice Operations**: Get invoices, create new invoices
- **Product Catalog**: Get/create products
- **Contact Management**: Get/create contacts
- **Payment Tracking**: Get payments, payment methods

### Payment

- **Financial Tracking**: Get balances, transactions, payments
- **Refund Management**: Get refunds

### PMS (Property Management)

- **Hospitality Operations**: Get orders, invoices, customers
- **Financial Management**: Get payments, accounting categories, tax rates

### POS (Point of Sale)

- **Sales Operations**: Get orders, sales, products
- **Customer Management**: Get/create customers, update orders
- **Financial Tracking**: Get payments, payment methods, closures

## 📦 Installation

### Prerequisites

- A Chift account with client credentials
- Python 3.11 or higher
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

## 🔌 MCP Integration

### Claude for Desktop

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
        "chift-mcp-server",
        "stdio"
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

Alternatively, you can use this simplified configuration if you have the `chift-mcp-server` package installed:

```json
{
  "mcpServers": {
    "chift": {
      "command": "uvx",
      "args": [
        "chift-mcp-server",
        "stdio"
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

#### Local Development Configuration

If you want to run the server from a local clone of the repository for development purposes, you can use a configuration
like this:

```json
{
  "mcpServers": {
    "chift": {
      "command": "/usr/bin/uv",
      "args": [
        "run",
        "--directory",
        "/path/to/your/local/chift/mcp",
        "python",
        "-m",
        "chift_mcp"
      ],
      "env": {
        "CHIFT_CLIENT_SECRET": "your_client_secret",
        "CHIFT_CLIENT_ID": "your_client_id",
        "CHIFT_ACCOUNT_ID": "your_account_id",
        "CHIFT_URL_BASE": "http://chift.localhost:8000"
      }
    }
  }
}
```

Make sure to replace the directory path with the actual path to your local clone of the repository, and update the
environment variables with your development credentials.

#### After Configuration

1. Restart Claude for Desktop
2. You should see a tool icon in the chat input area
3. Click on the tool icon to see the available Chift API tools
4. Start chatting with Claude using the Chift tools

### PydanticAI

Learn more about PydanticAI's MCP client: [https://ai.pydantic.dev/mcp/client/](https://ai.pydantic.dev/mcp/client/)

#### Using stdio Transport

```python
import asyncio
from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerStdio

# Define environment variables for the subprocess
env = {
    "CHIFT_CLIENT_SECRET": "your_client_secret",
    "CHIFT_CLIENT_ID": "your_client_id",
    "CHIFT_ACCOUNT_ID": "your_account_id",
    "CHIFT_URL_BASE": "https://api.chift.eu"
}

# Create a server that will be run as a subprocess
server = MCPServerStdio('uvx', ['chift-mcp-server', 'stdio'], env=env)
agent = Agent('openai:gpt-4o', mcp_servers=[server])


async def main():
    async with agent.run_mcp_servers():
        result = await agent.run(
            '''
                    Please get details about consumer with ID "consumer123" 
                    and list all of its available connections.
                    '''
        )
        print(result.data)


if __name__ == "__main__":
    asyncio.run(main())
```

### Vercel AI SDK

Lear more about Vercel AI SDK https://ai-sdk.dev/docs/introduction

#### Using stdio Transport

```javascript
import {experimental_createMCPClient as createMCPClient} from 'ai';
import {Experimental_StdioMCPTransport as StdioMCPTransport} from 'ai/mcp-stdio';
import {openai} from '@ai-sdk/openai';
import {generateText} from 'ai';

async function main() {
    let mcpClient;

    try {
        // Initialize MCP client with stdio transport
        mcpClient = await createMCPClient({
            transport: new StdioMCPTransport({
                command: 'uvx',
                args: ['chift-mcp-server', 'stdio'],
                // Pass Chift environment variables
                env: {
                    CHIFT_CLIENT_SECRET: 'your_client_secret',
                    CHIFT_CLIENT_ID: 'your_client_id',
                    CHIFT_ACCOUNT_ID: 'your_account_id',
                    CHIFT_URL_BASE: 'https://api.chift.eu',
                },
            }),
        });

        // Get tools from the MCP server
        const tools = mcpClient.tools();

        // Use the tools with a language model
        const {text} = await generateText({
            model: openai('gpt-4o'),
            tools,
            maxSteps: 5, // Allow multiple tool calls in sequence
            prompt: 'Get all available consumers and then show me the connections for the first one.',
        });

        console.log(text);
    } finally {
        // Make sure to close the client
        await mcpClient?.close();
    }
}

main();
```

## 🔑 Environment Variables

The following environment variables are used by the Chift MCP Server:

- `CHIFT_CLIENT_SECRET`: Your Chift client secret
- `CHIFT_CLIENT_ID`: Your Chift client ID
- `CHIFT_ACCOUNT_ID`: Your Chift account ID
- `CHIFT_URL_BASE`: Chift API URL (default: https://api.chift.eu)
- `CHIFT_FUNCTION_CONFIG`: JSON string to configure which operations are available for each domain (optional)

## 🚀 Available Tools

The Chift MCP Server dynamically generates tools based on the Chift OpenAPI specification. These tools provide access to
various Chift API endpoints and include operations for:

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
6. The server processes natural language requests from LLMs (Claude, GPT-4, etc.)

## 💬 Example Usages

After setup, you can ask your LLM to:

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

# Or use uvx
uvx chift-mcp-server
```

Or with the configuration set in Claude Desktop, simply restart the application and look for the tool icon in the
message input.

## 🛠️ Function Configuration

The Chift MCP Server supports configuring which operations are available for each domain. By default, all operations are
enabled for all domains:

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
      "command": "uvx",
      "args": [
        "chift-mcp-server",
        "stdio"
      ],
      "env": {
        "CHIFT_CLIENT_SECRET": "your_client_secret",
        "CHIFT_CLIENT_ID": "your_client_id",
        "CHIFT_ACCOUNT_ID": "your_account_id",
        "CHIFT_URL_BASE": "https://api.chift.eu",
        "CHIFT_FUNCTION_CONFIG": "{\"accounting\": [\"get\", \"create\"], \"commerce\": [\"get\"], \"invoicing\": [\"get\", \"create\", \"update\"]}"
      }
    }
  }
}
```

This example would restrict the accounting domain to only get and create operations, commerce to only get operations,
and invoicing to get, create, and update operations.