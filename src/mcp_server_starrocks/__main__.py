import argparse
import asyncio
import logging
import sys

from mcp_server_trino import Config
from mcp_server_trino.server import main

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger("mcp-server-starrocks")


def parse_args():
    parser = argparse.ArgumentParser(description="MCP Server for StarRocks")
    parser.add_argument("--host", required=True, help="StarRocks server host")
    parser.add_argument("--port", type=int, default=9030, help="StarRocks server port")
    parser.add_argument("--user", required=True, help="StarRocks user")
    parser.add_argument("--database", required=True, help="StarRocks database")
    parser.add_argument("--password", help="StarRocks password (if required)")
    parser.add_argument("--readonly", action="store_true", help="Run in read-only mode")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    config = Config(
        host=args.host,
        port=args.port,
        user=args.user,
        database=args.database,
        password=args.password,
        readonly=args.readonly,
    )
    
    try:
        asyncio.run(main(config))
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)