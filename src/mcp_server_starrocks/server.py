import logging
from contextlib import closing
from typing import Any, List
from sqlalchemy import create_engine, text
from sqlalchemy.engine.base import Engine

import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from pydantic import AnyUrl

from mcp_server_trino import Config

logger = logging.getLogger("mcp-server-starrocks")
logger.info("Starting MCP StarRocks Server")


class StarRocksDatabase:
    def __init__(self, config: Config):
        if config.password is None:
            self.engine: Engine = create_engine(
                f'starrocks://{config.user}:@{config.host}:{config.port}/{config.database}'
            )
        else:
            self.engine: Engine = create_engine(
                f'starrocks://{config.user}:{config.password}@{config.host}:{config.port}/{config.database}'
            )
        

    def execute_query(self, query: str, parameters: list = None) -> List[Any]:
        with self.engine.connect() as connection:
            if parameters:
                result = connection.execute(text(query), parameters)
            else:
                result = connection.execute(text(query))
            
            try:
                return result.fetchall()
            except:
                # For non-SELECT queries that don't return results
                return []


async def main(config: Config):
    logger.info(f"Starting StarRocks MCP Server with connection to: {config.host}:{config.port}")

    db = StarRocksDatabase(config)
    server = Server("mcp-starrocks-server")

    logger.debug("Registering handlers")

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        tools = [
            types.Tool(
                name="read-query",
                description="Execute a SELECT query on the StarRocks database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "SELECT SQL query to execute",
                        },
                    },
                    "required": ["query"],
                },
            ),
            types.Tool(
                name="list-tables",
                description="List all tables in the StarRocks database",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            types.Tool(
                name="describe-table",
                description="Describe the schema of a specific table in the StarRocks database",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "table_name": {
                            "type": "string",
                            "description": "Name of the table to describe",
                        },
                    },
                    "required": ["table_name"],
                },
            ),
        ]

        if not getattr(config, 'readonly', False):
            tools.extend([
                types.Tool(
                    name="write-query",
                    description="Execute an INSERT, UPDATE, or DELETE query on the StarRocks database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute",
                            },
                        },
                        "required": ["query"],
                    },
                ),
                types.Tool(
                    name="create-table",
                    description="Create a new table in the StarRocks database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "CREATE TABLE SQL query to execute",
                            },
                        },
                        "required": ["query"],
                    },
                ),
            ])

        return tools

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict[str, Any] | None
    ) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
        """Handle tool execution requests"""
        try:
            if name == "list-tables":
                results = db.execute_query("SHOW TABLES")
                return [types.TextContent(type="text", text=str(results))]

            if name == "read-query":
                if not arguments["query"].strip().upper().startswith("SELECT"):
                    raise ValueError("Only SELECT queries are allowed for read-query")
                results = db.execute_query(arguments["query"])
                return [types.TextContent(type="text", text=str(results))]

            elif name == "describe-table":
                table_name = arguments["table_name"]
                results = db.execute_query(f"DESCRIBE {table_name}")
                return [types.TextContent(type="text", text=str(results))]

            elif name == "create-table":
                if getattr(config, 'readonly', False):
                    raise ValueError("Server is running in read-only mode")
                results = db.execute_query(arguments["query"])
                return [types.TextContent(type="text", text="Table created successfully.")]

            elif name == "write-query":
                if getattr(config, 'readonly', False):
                    raise ValueError("Server is running in read-only mode")
                results = db.execute_query(arguments["query"])
                return [types.TextContent(type="text", text=str(results))]

            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            return [types.TextContent(type="text", text=f"Error: {str(e)}")]

    # Run the server using stdin/stdout streams
    options = server.create_initialization_options()
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        logger.info("StarRocks MCP Server running with stdio transport")
        await server.run(
            read_stream,
            write_stream,
            options,
        )