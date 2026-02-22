"""
BlackRoad Python SDK
Official Python client for the BlackRoad API
"""

__version__ = "1.0.0"
__author__ = "BlackRoad OS, Inc."

from .client import BlackRoadClient
from .agents import AgentAPI
from .tasks import TaskAPI
from .memory import MemoryAPI
from .exceptions import (
    BlackRoadError,
    AuthenticationError,
    RateLimitError,
    NotFoundError,
    ValidationError
)

__all__ = [
    "BlackRoadClient",
    "AgentAPI",
    "TaskAPI",
    "MemoryAPI",
    "BlackRoadError",
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
]
