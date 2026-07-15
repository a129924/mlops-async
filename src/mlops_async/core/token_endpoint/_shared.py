"""Shared pure logic for token-endpoint grant implementations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from mlops_async.core.token_storage import AccessToken
from mlops_async.core.types import JSONValue


class TokenEndpointClientError(ValueError):
    """Raised when token endpoint inputs or outputs are invalid."""


TokenEndpointClientException = TokenEndpointClientError


class AuthTokenEndpoint(str, Enum):
    """Token collaborator-local endpoint identifiers."""

    OAUTH_TOKEN = "/SASLogon/oauth/token"


@dataclass(frozen=True, slots=True)
class _TokenResponse:
    access_token: str
    expires_in: int


def require_non_empty_string(value: object, *, field_name: str) -> str:
    """Validate a credential-like string without including its value in errors."""
    if not isinstance(value, str) or not value.strip():
        raise TokenEndpointClientError(f"{field_name} must be a non-empty string")
    return value


def require_password_client_secret(value: object, *, client_id: str) -> str:
    """Validate a password-grant secret with the narrow ``sas.ec`` exception.

    This preserves sasctl 1.11.7's password-grant default: ``client_id``
    defaults to ``"sas.ec"`` and ``client_secret`` to ``""`` before the
    credentials are sent as HTTP Basic authentication to ``/SASLogon/oauth/token``.
    It is a SAS Viya compatibility exception, not a general OAuth rule: only
    the exact empty string for ``sas.ec`` is allowed; whitespace and every
    other client ID remain invalid.
    """
    if client_id == "sas.ec" and isinstance(value, str) and value == "":
        return value
    return require_non_empty_string(value, field_name="client_secret")


def parse_token_response(payload: JSONValue) -> _TokenResponse:
    """Validate and normalize the JSON payload returned by a token endpoint."""
    if not isinstance(payload, dict):
        raise TokenEndpointClientError("token response must be a JSON object")

    access_token = payload.get("access_token")
    expires_in = payload.get("expires_in")

    if not isinstance(access_token, str) or not access_token:
        raise TokenEndpointClientError("token response must include a non-empty access_token")
    if not isinstance(expires_in, int) or isinstance(expires_in, bool) or expires_in <= 0:
        raise TokenEndpointClientError(
            "token response must include a positive expires_in integer"
        )

    return _TokenResponse(access_token=access_token, expires_in=expires_in)


def access_token_from_response(
    token_response: _TokenResponse,
    *,
    now: datetime,
) -> AccessToken:
    """Build an access token from a validated response and explicit current time."""
    return AccessToken(
        value=token_response.access_token,
        expires_at=now + timedelta(seconds=token_response.expires_in),
    )
