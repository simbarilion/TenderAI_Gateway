"""Хеширование пользовательских API-ключей."""

import hashlib


def hash_api_key(raw_key: str) -> str:
    """Возвращает SHA-256 хеш ключа. В БД хранится только хеш."""
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
