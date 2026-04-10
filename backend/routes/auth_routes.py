from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from auth import ADMIN_USER, ADMIN_PASS, create_access_token

router = APIRouter(prefix="/api", tags=["auth"])


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest):
    if body.username != ADMIN_USER or body.password != ADMIN_PASS:
        raise HTTPException(status_code=401, detail="Usuario o clave incorrectos")
    token = create_access_token(body.username)
    return TokenResponse(access_token=token)
