"""
认证模块 - 简单的 JWT 认证
"""
import hashlib
import os
import time
import hmac
import json
import base64
from datetime import datetime
from fastapi import Depends, HTTPException, Header
from database import get_db
from sqlalchemy.orm import Session
from models import User

SECRET_KEY = os.environ.get("SECRET_KEY", "pl5-secret-key-2024")
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASS = "admin123"


def hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def create_token(username: str) -> str:
    """创建简单的 JWT token"""
    header = base64.urlsafe_b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}).encode()).decode().rstrip("=")
    now = int(time.time())
    payload = base64.urlsafe_b64encode(json.dumps({
        "username": username,
        "exp": now + 86400 * 7,  # 7天过期
        "iat": now
    }).encode()).decode().rstrip("=")
    signature = hmac.new(
        SECRET_KEY.encode(),
        f"{header}.{payload}".encode(),
        hashlib.sha256
    ).hexdigest()
    return f"{header}.{payload}.{signature}"


def verify_token(token: str) -> dict:
    """验证 token"""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header, payload, signature = parts
        expected_sig = hmac.new(
            SECRET_KEY.encode(),
            f"{header}.{payload}".encode(),
            hashlib.sha256
        ).hexdigest()
        if signature != expected_sig:
            return None
        # 补齐 base64 padding
        payload += "=" * (4 - len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(payload))
        if data.get("exp", 0) < time.time():
            return None
        return data
    except Exception:
        return None


def init_admin_user(db: Session):
    """初始化管理员账户"""
    admin = db.query(User).filter(User.username == DEFAULT_ADMIN_USER).first()
    if not admin:
        admin = User(
            username=DEFAULT_ADMIN_USER,
            password_hash=hash_password(DEFAULT_ADMIN_PASS)
        )
        db.add(admin)
        db.commit()


def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization[7:]
    data = verify_token(token)
    if not data:
        raise HTTPException(status_code=401, detail="token无效或已过期")
    username = data.get("username")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
