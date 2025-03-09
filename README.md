# StarRocks MCP Server

A Model Control Protocol (MCP) server for interacting with StarRocks databases. This server provides a standardized interface for AI models to query and manipulate StarRocks databases through a set of defined tools.

## Overview

The StarRocks MCP Server allows AI models to:
- Execute SELECT queries on StarRocks databases
- List available tables
- Describe table schemas
- Create new tables (when not in read-only mode)
- Execute write operations like INSERT, UPDATE, DELETE (when not in read-only mode)

## Installation

### Prerequisites

- Python 3.8+
- StarRocks database instance
- SQLAlchemy
- MCP Python library

### Install from source
bash
git clone https://github.com/yourusername/mcp-server-starrocks.git
cd mcp-server-starrocks
pip install -e .


## Usage

### Starting the server
bash
python -m mcp_server_starrocks.server --host <starrocks-host> --port <starrocks-port> --user <username> --database <database-name> [--password <password>] [--readonly]


#### Command-line arguments:

- `--host`: StarRocks server host (required)
- `--port`: StarRocks server port (default: 9030)
- `--user`: StarRocks username (required)
- `--database`: StarRocks database name (required)
- `--password`: StarRocks password (if required)
- `--readonly`: Run the server in read-only mode (optional)

### Available Tools

The server provides the following tools:

#### Read-only tools:

- `read-query`: Execute a SELECT query on the StarRocks database
- `list-tables`: List all tables in the StarRocks database
- `describe-table`: Describe the schema of a specific table

#### Write tools (available when not in read-only mode):

- `write-query`: Execute an INSERT, UPDATE, or DELETE query
- `create-table`: Create a new table in the StarRocks database

## Examples

### Listing tables
json
{
"name": "list-tables",
"arguments": {}
}

### Executing a SELECT query
json
{
"name": "read-query",
"arguments": {
"query": "SELECT FROM my_table LIMIT 10"
}
}

### Describing a table
json
{
"name": "describe-table",
"arguments": {
"table_name": "my_table"
}
}

### Creating a table (when not in read-only mode)
json
{
"name": "create-table",
"arguments": {
"query": "CREATE TABLE new_table (id INT, name VARCHAR(100))"
}
}

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.