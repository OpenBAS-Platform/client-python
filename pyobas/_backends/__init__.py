"""
Defines http backends for processing http requests
"""

from .backend import RequestsBackend, RequestsResponse, TokenAuth

DefaultBackend = RequestsBackend
DefaultResponse = RequestsResponse

__all__ = [
    "DefaultBackend",
    "DefaultResponse",
    "TokenAuth",
]
