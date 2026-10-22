"""Autenticação JWT demonstrativa para execução local.

Configure AUTH_SECRET, AUTH_USERNAME e AUTH_PASSWORD por variáveis de ambiente
antes de expor a API. Os valores padrão existem somente para demonstração local.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

ALGORITHM = "HS256"
ACCESS_TOKEN_MINUTES = 60
AUTH_USERNAME = os.getenv("AUTH_USERNAME", "danilo")
AUTH_PASSWORD = os.getenv("AUTH_PASSWORD", "admin123")
AUTH_DISPLAY_NAME = os.getenv(
    "AUTH_DISPLAY_NAME", "Danilo Lopes da Silva | Assessor de Tecnologia II"
)
AUTH_SECRET = os.getenv("AUTH_SECRET", "local-only-change-this-secret-before-deployment")
_pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
_password_hash = _pwd_context.hash(AUTH_PASSWORD)
_bearer = HTTPBearer(auto_error=False)


def authenticate(username: str, password: str) -> bool:
    """Valida usuário configurado e senha usando hash PBKDF2."""
    return username == AUTH_USERNAME and _pwd_context.verify(password, _password_hash)


def create_access_token(subject: str) -> tuple[str, int]:
    """Gera token assinado com validade curta."""
    expires_delta = timedelta(minutes=ACCESS_TOKEN_MINUTES)
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {"sub": subject, "iat": now, "exp": now + expires_delta},
        AUTH_SECRET,
        algorithm=ALGORITHM,
    )
    return token, int(expires_delta.total_seconds())


def get_current_username(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> str:
    """Exige Bearer token válido para rotas protegidas."""
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token ausente, inválido ou expirado. Entre novamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthorized
    try:
        payload = jwt.decode(credentials.credentials, AUTH_SECRET, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not isinstance(username, str) or username != AUTH_USERNAME:
            raise unauthorized
        return username
    except JWTError as exc:
        raise unauthorized from exc
