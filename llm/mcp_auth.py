"""MCP 演示用身份认证（Bearer Token + stdio 环境变量）。"""

from __future__ import annotations

import os
import secrets
import time
from dataclasses import dataclass

from mcp.server.auth.provider import AccessToken, TokenVerifier

MCP_SCOPE = "mcp:tools"


def auth_enabled() -> bool:
  return os.getenv("MCP_AUTH_ENABLED", "false").lower() in {"1", "true", "yes", "on"}


def get_static_token() -> str | None:
  token = os.getenv("MCP_API_TOKEN")
  return token or None


def get_credentials() -> tuple[str, str]:
  return (
    os.getenv("MCP_USERNAME", "demo"),
    os.getenv("MCP_PASSWORD", "demo"),
  )


def verify_credentials(username: str, password: str) -> bool:
  expected_user, expected_password = get_credentials()
  user_ok = secrets.compare_digest(username, expected_user)
  password_ok = secrets.compare_digest(password, expected_password)
  return user_ok and password_ok


@dataclass
class IssuedToken:
  token: str
  client_id: str
  scopes: list[str]
  expires_at: int


class TokenStore:
  def __init__(self, ttl_seconds: int = 3600) -> None:
    self.ttl_seconds = ttl_seconds
    self._tokens: dict[str, IssuedToken] = {}

  def issue(self, client_id: str, scopes: list[str] | None = None) -> str:
    token = secrets.token_urlsafe(32)
    self._tokens[token] = IssuedToken(
      token=token,
      client_id=client_id,
      scopes=scopes or [MCP_SCOPE],
      expires_at=int(time.time()) + self.ttl_seconds,
    )
    return token

  def get(self, token: str) -> IssuedToken | None:
    issued = self._tokens.get(token)
    if issued is None:
      return None
    if issued.expires_at < int(time.time()):
      del self._tokens[token]
      return None
    return issued


class DemoTokenVerifier:
  """校验静态 MCP_API_TOKEN 或通过 /auth/token 签发的 Bearer Token。"""

  def __init__(
    self,
    static_token: str | None,
    token_store: TokenStore,
    required_scopes: list[str] | None = None,
  ) -> None:
    self.static_token = static_token
    self.token_store = token_store
    self.required_scopes = required_scopes or [MCP_SCOPE]

  async def verify_token(self, token: str) -> AccessToken | None:
    if self.static_token and secrets.compare_digest(token, self.static_token):
      return AccessToken(
        token=token,
        client_id="static-client",
        scopes=self.required_scopes,
      )

    issued = self.token_store.get(token)
    if issued is None:
      return None

    return AccessToken(
      token=token,
      client_id=issued.client_id,
      scopes=issued.scopes,
      expires_at=issued.expires_at,
      subject=issued.client_id,
    )


def build_auth_settings(server_base_url: str) -> "AuthSettings":
  from pydantic import AnyHttpUrl

  from mcp.server.auth.settings import AuthSettings

  base = server_base_url.rstrip("/")
  return AuthSettings(
    issuer_url=AnyHttpUrl(base),
    resource_server_url=AnyHttpUrl(f"{base}/mcp"),
    required_scopes=[MCP_SCOPE],
  )


def create_token_verifier(token_store: TokenStore) -> TokenVerifier:
  return DemoTokenVerifier(get_static_token(), token_store)


def validate_stdio_auth() -> None:
  if not auth_enabled():
    return
  if not get_static_token():
    raise SystemExit(
      "stdio 模式已启用 MCP 认证，请设置 MCP_API_TOKEN 并通过客户端 env 传入子进程。",
    )


def issue_login_token(token_store: TokenStore, username: str, password: str) -> str | None:
  if not verify_credentials(username, password):
    return None
  return token_store.issue(client_id=username)
