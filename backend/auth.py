from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
from jose import jwt
import requests
import os

load_dotenv()

security = HTTPBearer()

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"


ANON_KEY = os.environ.get("NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY")

# 缓存 JWK（避免每次请求都访问）
jwks_cache = None

def get_jwks():
    res = requests.get(
        JWKS_URL,
        headers={
            "apikey": ANON_KEY
        }
    )
    return res.json()


def authenticate(credentials=Depends(security)):
    token = credentials.credentials
    try:
        # ① 获取 header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise Exception("Token missing kid")
        # ② 获取 jwks
        jwks = get_jwks()
        # ③ 找对应 key
        key = next(
            (k for k in jwks["keys"] if k["kid"] == kid),
            None
        )
        if key is None:
            raise Exception("Public key not found")
        # ④ 验证 token
        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated"  # Supabase 默认 audience
        )
        return {"payload": payload, "token": token}

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"无效 token: {str(e)}"
        )