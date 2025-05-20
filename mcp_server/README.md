# Graphiti MCP Server

Graphiti is a framework for building and querying temporally-aware knowledge graphs, specifically tailored for AI agents
operating in dynamic environments. Unlike traditional retrieval-augmented generation (RAG) methods, Graphiti
continuously integrates user interactions, structured and unstructured enterprise data, and external information into a
coherent, queryable graph. The framework supports incremental data updates, efficient retrieval, and precise historical
queries without requiring complete graph recomputation, making it suitable for developing interactive, context-aware AI
applications.

This is an experimental Model Context Protocol (MCP) server implementation for Graphiti. The MCP server exposes
Graphiti's key functionality through the MCP protocol, allowing AI assistants to interact with Graphiti's knowledge
graph capabilities.

## Features

The Graphiti MCP server exposes the following key high-level functions of Graphiti:

- **Episode Management**: Add, retrieve, and delete episodes (text, messages, or JSON data)
- **Entity Management**: Search and manage entity nodes and relationships in the knowledge graph
- **Search Capabilities**: Search for facts (edges) and node summaries using semantic and hybrid search
- **Group Management**: Organize and manage groups of related data with group_id filtering
- **Graph Maintenance**: Clear the graph and rebuild indices

## Quick Start for Claude Desktop, Cursor, and other clients

1. Clone the Graphiti GitHub repo

```bash
git clone https://github.com/getzep/graphiti.git
```

or

```bash
gh repo clone getzep/graphiti
```

Note the full path to this directory.

```
cd graphiti && pwd
```

2. Install the [Graphiti prerequisites](#prerequisites).

3. Configure Claude, Cursor, or other MCP client to use [Graphiti with a `stdio` transport](#integrating-with-mcp-clients). See the client documentation on where to find their MCP configuration files.

## Installation

### Prerequisites

1. Ensure you have Python 3.10 or higher installed.
2. One of the following databases:
   - Neo4j database (version 5.26 or later)
   - SurrealDB (version 1.2.0 or later)
3. OpenAI API key for LLM operations (optional but recommended for entity extraction)

### Setup

1. Clone the repository and navigate to the mcp_server directory
2. Use `uv` to create a virtual environment and install dependencies:

```bash
# Install uv if you don't have it already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a virtual environment and install dependencies in one step
uv sync
```

## Configuration

The server uses the following environment variables:

- `NEO4J_URI`: URI for the Neo4j database (default: `bolt://localhost:7687`)
- `NEO4J_USER`: Neo4j username (default: `neo4j`)
- `NEO4J_PASSWORD`: Neo4j password (default: `demodemo`)
- `OPENAI_API_KEY`: OpenAI API key (required for LLM operations)
- `OPENAI_BASE_URL`: Optional base URL for OpenAI API
- `MODEL_NAME`: Optional model name to use for LLM inference
- `AZURE_OPENAI_ENDPOINT`: Optional Azure OpenAI endpoint URL
- `AZURE_OPENAI_DEPLOYMENT_NAME`: Optional Azure OpenAI deployment name
- `AZURE_OPENAI_API_VERSION`: Optional Azure OpenAI API version
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`: Optional Azure OpenAI embedding deployment name
- `AZURE_OPENAI_EMBEDDING_API_VERSION`: Optional Azure OpenAI API version
- `AZURE_OPENAI_USE_MANAGED_IDENTITY`: Optional use Azure Managed Identities for authentication

You can set these variables in a `.env` file in the project directory.

## Running the Server

To run the Graphiti MCP server directly using `uv`:

```bash
uv run graphiti_mcp_server.py
```

With options:

```bash
uv run graphiti_mcp_server.py --model gpt-4.1-mini --transport sse
```

### Using uvx for SSE Transport

For a more streamlined experience with SSE transport, you can use `uvx` which is an enhanced version of `uv` with additional features:

```bash
# Install uvx if you don't have it already
pip install uvx

# Run the MCP server with SSE transport
uvx run graphiti_mcp_server.py --transport sse
```

You can also specify additional options:

```bash
uvx run graphiti_mcp_server.py --transport sse --model gpt-4-turbo-preview --group-id my-project
```

#### For SurrealDB users

```bash
# Make sure your .env.surrealdb file is set up with the correct configuration
cp .env.surrealdb.example .env.surrealdb

# Run with SurrealDB configuration
uvx run graphiti_mcp_server.py --transport sse --env-file .env.surrealdb
```

Alternatively, you can set the environment variables directly:

```bash
DATABASE_TYPE=surrealdb \
DATABASE_URI=ws://localhost:8001/rpc \
DATABASE_USER=root \
DATABASE_PASSWORD=root \
DATABASE_NAMESPACE=graphiti \
DATABASE_DB=graphiti \
uvx run graphiti_mcp_server.py --transport sse
```

Available arguments:

- `--model`: Specify the model name to use with the LLM client
- `--transport`: Choose the transport method (sse or stdio, default: sse)
- `--group-id`: Set a namespace for the graph (optional)
- `--destroy-graph`: Destroy all Graphiti graphs (use with caution)
- `--use-custom-entities`: Enable entity extraction using the predefined ENTITY_TYPES
- `--env-file`: Specify a custom environment file to use (default: .env)

### Docker Deployment

The Graphiti MCP server can be deployed using Docker. The Dockerfile uses `uv` for package management, ensuring
consistent dependency installation.

#### Environment Configuration

Before running the Docker Compose setup, you need to configure the environment variables. You have two options:

1. **Using a .env file** (recommended):

   - Copy the provided `.env.example` file to create a `.env` file:
     ```bash
     cp .env.example .env
     ```
   - Edit the `.env` file to set your OpenAI API key and other configuration options:
     ```
     # Required for LLM operations
     OPENAI_API_KEY=your_openai_api_key_here
     MODEL_NAME=gpt-4.1-mini
     # Optional: OPENAI_BASE_URL only needed for non-standard OpenAI endpoints
     # OPENAI_BASE_URL=https://api.openai.com/v1
     ```
   - The Docker Compose setup is configured to use this file if it exists (it's optional)

2. **Using environment variables directly**:
   - You can also set the environment variables when running the Docker Compose command:
     ```bash
     OPENAI_API_KEY=your_key MODEL_NAME=gpt-4.1-mini docker compose up
     ```

#### Neo4j Configuration

The Docker Compose setup includes a Neo4j container with the following default configuration:

- Username: `neo4j`
- Password: `demodemo`
- URI: `bolt://neo4j:7687` (from within the Docker network)
- Memory settings optimized for development use

#### SurrealDB Configuration (Alternative)

As an alternative to Neo4j, you can use SurrealDB with Graphiti MCP server. SurrealDB version 1.2.0 or later is required.

##### Setting up SurrealDB

1. Install SurrealDB (version 1.2.0 or later):

```bash
# macOS with Homebrew
brew install surrealdb/tap/surreal

# Linux
curl -sSf https://install.surrealdb.com | sh

# Windows
choco install surreal
```

1. Start SurrealDB:

```bash
surreal start --user root --pass root --bind 0.0.0.0:8001 memory
```

##### Docker Compose Setup

A Docker Compose configuration is provided for running the MCP server with SurrealDB:

```bash
# Start the MCP server with SurrealDB configuration
docker compose -f docker-compose-surrealdb.yml up -d
```

This configuration:

- Connects to a SurrealDB instance running on the host machine at `ws://host.docker.internal:8001/rpc`
- Uses the environment variables from `.env.surrealdb` file
- Exposes the server on port 8000 for HTTP-based SSE transport

To set up the SurrealDB environment:
```bash
# Create your SurrealDB environment file
cp .env.surrealdb.example .env.surrealdb
# Edit the file to set your API keys and database configuration
```

##### Running with the Script

For convenience, a shell script is provided to run the MCP server with SurrealDB:

```bash
# Make the script executable
chmod +x bin/graphiti-mcp-server

# Run the MCP server with SurrealDB
./bin/graphiti-mcp-server
```

The script sets the following environment variables for SurrealDB:

```bash
DATABASE_TYPE=surrealdb
DATABASE_URI=ws://localhost:8001/rpc
DATABASE_USER=root
DATABASE_PASSWORD=root
DATABASE_NAMESPACE=graphiti
DATABASE_DB=graphiti
```

## Setting up with Codeium, Claude, and Other MCP Clients

To use the Graphiti MCP server with MCP clients like Codeium, Claude, or others, you need to configure the client to connect to the running MCP server.

### Codeium Configuration

To configure Codeium to use the Graphiti MCP server:

1. Edit the MCP configuration file at `~/.codeium/windsurf/mcp_config.json`
2. Add or update the `graphiti` section to point to your running MCP server:

```json
{
  "graphiti": {
    "serverUrl": "http://localhost:8000/sse"
  }
}
```

This configuration tells Codeium to connect to the Graphiti MCP server running on localhost port 8000 using the SSE transport.

### Claude Configuration

To configure Claude to use the Graphiti MCP server:

1. Edit the MCP configuration file at `~/Library/Application Support/Windsurf/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`
2. Add or update the `graphiti` section to point to your running MCP server.

## Integrating with MCP Clients

### Configuration

To use the Graphiti MCP server with an MCP-compatible client, configure it to connect to the server:

> [!IMPORTANT]
> You will need the Python package manager, `uv` installed. Please refer to the [`uv` install instructions](https://docs.astral.sh/uv/getting-started/installation/).
>
> Ensure that you set the full path to the `uv` binary and your Graphiti project folder.

```json
{
  "mcpServers": {
    "graphiti": {
      "transport": "stdio",
      "command": "/Users/<user>/.local/bin/uv",
      "args": [
        "run",
        "--isolated",
        "--directory",
        "/Users/<user>>/dev/zep/graphiti/mcp_server",
        "--project",
        ".",
        "graphiti_mcp_server.py",
        "--transport",
        "stdio"
      ],
      "env": {
        "NEO4J_URI": "bolt://localhost:7687",
        "NEO4J_USER": "neo4j",
        "NEO4J_PASSWORD": "password",
        "OPENAI_API_KEY": "sk-XXXXXXXX",
        "MODEL_NAME": "gpt-4.1-mini"
      }
    }
  }
}
```

For SSE transport (HTTP-based), you can use this configuration:

```json
{
  "mcpServers": {
    "graphiti": {
      "transport": "sse",
      "url": "http://localhost:8000/sse"
    }
  }
}
```

## Available Tools

The Graphiti MCP server exposes the following tools:

- `add_episode`: Add an episode to the knowledge graph (supports text, JSON, and message formats)
- `search_nodes`: Search the knowledge graph for relevant node summaries
- `search_facts`: Search the knowledge graph for relevant facts (edges between entities)
- `delete_entity_edge`: Delete an entity edge from the knowledge graph
- `delete_episode`: Delete an episode from the knowledge graph
- `get_entity_edge`: Get an entity edge by its UUID
- `get_episodes`: Get the most recent episodes for a specific group
- `clear_graph`: Clear all data from the knowledge graph and rebuild indices
- `get_status`: Get the status of the Graphiti MCP server and Neo4j connection

## Working with JSON Data

The Graphiti MCP server can process structured JSON data through the `add_episode` tool with `source="json"`. This
allows you to automatically extract entities and relationships from structured data:

```

add_episode(
name="Customer Profile",
episode_body="{\"company\": {\"name\": \"Acme Technologies\"}, \"products\": [{\"id\": \"P001\", \"name\": \"CloudSync\"}, {\"id\": \"P002\", \"name\": \"DataMiner\"}]}",
source="json",
source_description="CRM data"
)

```

## Integrating with the Cursor IDE

To integrate the Graphiti MCP Server with the Cursor IDE, follow these steps:

1. Run the Graphiti MCP server using the SSE transport:

```bash
python graphiti_mcp_server.py --transport sse --use-custom-entities --group-id <your_group_id>
```

Hint: specify a `group_id` to retain prior graph data. If you do not specify a `group_id`, the server will create a new
graph

2. Configure Cursor to connect to the Graphiti MCP server.

```json
{
  "mcpServers": {
    "Graphiti": {
      "url": "http://localhost:8000/sse"
    }
  }
}
```

3. Add the Graphiti rules to Cursor's User Rules. See [cursor_rules.md](cursor_rules.md) for details.

4. Kick off an agent session in Cursor.

The integration enables AI assistants in Cursor to maintain persistent memory through Graphiti's knowledge graph
capabilities.

## Requirements

- Python 3.10 or higher
- Neo4j database (version 5.26 or later required)
- OpenAI API key (for LLM operations and embeddings)
- MCP-compatible client

## License

This project is licensed under the same license as the Graphiti project.
