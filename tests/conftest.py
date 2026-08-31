import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("JWT_SECRET", "unit-test-secret-that-is-at-least-32-characters")
os.environ.setdefault("APP_USER_USERNAME", "resume_user")
# Argon2 hash below is intentionally replaced in tests by monkeypatch where needed.
os.environ.setdefault(
    "APP_USER_PASSWORD_HASH",
    "$argon2id$v=19$m=65536,t=3,p=4$ZGVtb3NhbHQxMjM0NTY3OA$"
    "8VHtW0xVxCWHxY6u1eHjJEK0tVZ3fGJd5yFg7fVYVhM",
)
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("OPENAI_MODEL", "test-model")
os.environ.setdefault("METRICS_ENABLED", "false")
os.environ.setdefault("OTEL_ENABLED", "false")
