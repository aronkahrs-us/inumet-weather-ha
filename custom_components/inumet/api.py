"""Sample API Client."""

from __future__ import annotations


class InumetApiClientError(Exception):
    """Exception to indicate a general API error."""


class InumetApiClientNoDataError(InumetApiClientError):
    """Exception to indicate a NoData error."""


class InumetApiClientAuthenticationError(InumetApiClientError):
    """Exception to indicate an authentication error."""
