import hashlib
import hmac
import secrets
import uuid

import bleach
from cryptography.fernet import Fernet

from app.extensions import bcrypt


def sanitize_text(text: str) -> str:
    """Strip all HTML tags from input text."""
    return bleach.clean(text, tags=[], strip=True)


def generate_api_key() -> tuple:
    """Generate a new API key. Returns (raw_key, hashed_key)."""
    raw_key = f"ak_{uuid.uuid4().hex}"
    hashed_key = bcrypt.generate_password_hash(raw_key, rounds=12).decode("utf-8")
    return raw_key, hashed_key


def verify_api_key(raw_key: str, hashed_key: str) -> bool:
    return bcrypt.check_password_hash(hashed_key, raw_key)


def generate_token() -> str:
    """Generate a cryptographically random token for email verification / password reset."""
    return secrets.token_urlsafe(32)


def generate_token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def encrypt_value(plaintext: str, encryption_key: str) -> str:
    """AES-256 encrypt a value using Fernet."""
    f = Fernet(encryption_key.encode())
    return f.encrypt(plaintext.encode()).decode()


def decrypt_value(ciphertext: str, encryption_key: str) -> str:
    f = Fernet(encryption_key.encode())
    return f.decrypt(ciphertext.encode()).decode()


def sign_webhook_payload(payload: bytes, secret: str) -> str:
    """HMAC-SHA256 sign a webhook payload."""
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def verify_webhook_signature(payload: bytes, secret: str, signature: str) -> bool:
    expected = sign_webhook_payload(payload, secret)
    return hmac.compare_digest(expected, signature)
