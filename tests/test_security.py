from app.core.config import Settings
from app.core.security import create_access_token
import jwt


def test_access_token_contains_expected_subject():
    settings = Settings(
        jwt_secret="a-very-long-unit-test-secret-over-32-characters",
        app_user_password_hash="not-used-in-this-test",
        openai_api_key="test",
        openai_model="test-model",
    )
    token = create_access_token("alice", settings, ["resume:generate"])
    decoded = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=[settings.jwt_algorithm],
        audience=settings.app_name,
        issuer=settings.app_name,
    )
    assert decoded["sub"] == "alice"
    assert "resume:generate" in decoded["scope"]
