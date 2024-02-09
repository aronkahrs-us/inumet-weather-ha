"""Sample API Client."""
from __future__ import annotations
from inumet_api import INUMET

class InumetApiClientError(Exception):
    """Exception to indicate a general API error."""


class InumetApiClientNoDataError(
    InumetApiClientError
):
    """Exception to indicate a NoData error."""


class InumetApiClientAuthenticationError(
    InumetApiClientError
):
    """Exception to indicate an authentication error."""
