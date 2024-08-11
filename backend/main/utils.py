import secrets


def unique_string(byte: int = 10) -> str:
    return secrets.token_urlsafe(byte)