"""
SSE Python SDK

Skill Self-Evolution Engine 官方Python SDK

Usage:
    from sse_sdk import SSEClient
    
    client = SSEClient(api_key="your_key")
    client.track("my-skill", {"duration_ms": 1000})
"""

from .client import SSEClient, SSEConfig
from .exceptions import SSEError, AuthenticationError, RateLimitError

__version__ = "2.0.0"
__all__ = ["SSEClient", "SSEConfig", "SSEError", "AuthenticationError", "RateLimitError"]
