import argparse
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Config:
    """
    Configuration for the server.
    """

    db_path: Path
    """
    Path to DuckDB database file.
    """

    readonly: bool = False
    """
    Run server in read-only mode.
    """

    @staticmethod
    def from_arguments() -> Config:
        """
        Parse command line arguments.
        """
        parser = argparse.ArgumentParser(description="DuckDB MCP Server")

        parser.add_argument(
            "--db-path",
            type=Path,
            help="Path to DuckDB database file",
            required=True,
        )

        parser.add_argument(
            "--readonly",
            action="store_true",
            help="Run server in read-only mode. "
            "If the file does not exist, it is not created when connecting in read-only mode. "
            "Use duckdb.connect(), passing read_only=True. "
            "See: https://duckdb.org/docs/api/python/dbapi.html#read_only-connections",
        )

        args = parser.parse_args()
        return Config(db_path=args.db_path, readonly=args.readonly)


@dataclass
class Config:
    """
    Configuration for the StarRocks server.
    """

    host: str
    port: int
    user: str
    database: str
    password: Optional[str] = None
    readonly: bool = False

    @staticmethod
    def from_arguments() -> "Config":
        """
        Parse command line arguments.
        """
        parser = argparse.ArgumentParser(description="StarRocks MCP Server")

        parser.add_argument("--host", required=True, help="StarRocks server host")
        parser.add_argument("--port", type=int, default=9030, help="StarRocks server port")
        parser.add_argument("--user", required=True, help="StarRocks user")
        parser.add_argument("--database", required=True, help="StarRocks database")
        parser.add_argument("--password", help="StarRocks password (if required)")
        parser.add_argument("--readonly", action="store_true", help="Run in read-only mode")

        args = parser.parse_args()
        return Config(
            host=args.host,
            port=args.port,
            user=args.user,
            database=args.database,
            password=args.password,
            readonly=args.readonly,
        )