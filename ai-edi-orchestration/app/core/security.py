from fastapi import Request, HTTPException
from jose import jwt
import requests
import json

from .config import get_xsuaa_config

xsuaa_config = get_xsuaa_config()

JWKS_URL = xsuaa_config["url"] + "/token_keys"
AUDIENCE = xsuaa_config["clientid"]

jwks = requests.get(JWKS_URL).json()

def validate_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = auth_header.split(" ")[1]

    try:
        decoded = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=AUDIENCE
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not has_route_scope(decoded["scope"]):
        raise HTTPException(status_code=403, detail="Insufficient scope")

    return decoded

def has_route_scope(token_scopes):
    return any(scope.endswith(".route") or scope.endswith(".admin") for scope in token_scopes)

def has_admin_scope(token_scopes):
    return any(scope.endswith(".admin") for scope in token_scopes)

def validate_admin_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = auth_header.split(" ")[1]

    try:
        decoded = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            audience=AUDIENCE
        )
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

    if not has_admin_scope(decoded["scope"]):
        raise HTTPException(status_code=403, detail="Insufficient scope")

    return decoded