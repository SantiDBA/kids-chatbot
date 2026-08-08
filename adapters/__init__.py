"""
Adapters package - External API and data persistence layers
"""
from .data import DatabaseAdapter
from .external import GroqAdapter

__all__ = ["DatabaseAdapter", "GroqAdapter"]
