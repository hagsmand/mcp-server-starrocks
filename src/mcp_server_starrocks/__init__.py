from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Configuration for the StarRocks MCP server."""
    host: str
    port: int
    user: str
    database: str
    password: Optional[str] = None
    readonly: bool = False