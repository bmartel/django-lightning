from pathlib import Path

import msgspec

from app.config import EnvSettings
from app.env import BaseEnvSettings, _parse_bool, _parse_csv_list


def test_parse_bool_utility():
    assert _parse_bool(True) is True
    assert _parse_bool(False) is False
    assert _parse_bool("1") is True
    assert _parse_bool("true") is True
    assert _parse_bool("YES") is True
    assert _parse_bool("0") is False
    assert _parse_bool("false") is False
    assert _parse_bool("no") is False


def test_parse_csv_list_utility():
    assert _parse_csv_list("a, b, c") == ["a", "b", "c"]
    assert _parse_csv_list(["x", "y"]) == ["x", "y"]
    assert _parse_csv_list("") == []


def test_env_settings_defaults():
    settings = EnvSettings.load_from_env(env_dict={})
    assert isinstance(settings, EnvSettings)
    assert settings.DEBUG is True
    assert settings.ENABLE_MCP_SERVER is True
    assert settings.ALLOWED_HOSTS == ["*"]
    assert settings.PORT == 8000


def test_env_settings_custom_values():
    env_dict = {
        "SECRET_KEY": "custom-secret-key-test",
        "DEBUG": "0",
        "ENABLE_MCP_SERVER": "1",
        "ALLOWED_HOSTS": "api.example.com, admin.example.com",
        "PORT": "9000",
        "CORS_ALLOWED_ORIGINS": "https://app.example.com",
        "USE_REDIS_CACHE": "true",
    }
    settings = EnvSettings.load_from_env(env_dict=env_dict)
    assert settings.SECRET_KEY == "custom-secret-key-test"
    assert settings.DEBUG is False
    # MCP server must be strictly False when DEBUG is False
    assert settings.ENABLE_MCP_SERVER is False
    assert settings.ALLOWED_HOSTS == ["api.example.com", "admin.example.com"]
    assert settings.PORT == 9000
    assert settings.CORS_ALLOWED_ORIGINS == ["https://app.example.com"]
    assert settings.USE_REDIS_CACHE is True


def test_redis_cache_disabled_when_url_empty():
    env_dict = {
        "USE_REDIS_CACHE": "true",
        "REDIS_URL": "",
    }
    settings = EnvSettings.load_from_env(env_dict=env_dict)
    assert settings.USE_REDIS_CACHE is False


def test_env_settings_dotenv_parsing(tmp_path: Path):
    dotenv = tmp_path / ".env"
    dotenv.write_text(
        "SECRET_KEY=file-secret-key\nDEBUG=0\nPORT=8080\n# Comment line\n", encoding="utf-8"
    )

    settings = EnvSettings.load_from_env(env_dict={}, dotenv_path=dotenv)
    assert settings.SECRET_KEY == "file-secret-key"
    assert settings.DEBUG is False
    assert settings.PORT == 8080


def test_env_settings_msgspec_type_safety():
    settings = EnvSettings.load_from_env(env_dict={})
    # Verify it is a valid msgspec.Struct instance
    struct_dict = msgspec.structs.asdict(settings)
    assert "SECRET_KEY" in struct_dict
    assert "DEBUG" in struct_dict


def test_env_settings_declarative_expansion():
    class ExpandedSettings(EnvSettings, kw_only=True):
        SENTRY_DSN: str = ""
        MAX_WORKERS: int = 4
        FEATURE_V2_ENABLED: bool = False

    env_dict = {
        "SENTRY_DSN": "https://sentry.example.com/1",
        "MAX_WORKERS": "8",
        "FEATURE_V2_ENABLED": "true",
    }

    settings = ExpandedSettings.load_from_env(env_dict=env_dict)
    assert settings.SENTRY_DSN == "https://sentry.example.com/1"
    assert settings.MAX_WORKERS == 8
    assert settings.FEATURE_V2_ENABLED is True


def test_base_env_settings_subclass():
    class CustomProjectSettings(BaseEnvSettings, kw_only=True):
        PROJECT_NAME: str = "My Project"
        DEBUG: bool = True
        ENABLE_MCP_SERVER: bool = True
        SENTRY_DSN: str = ""
        WORKER_CONCURRENCY: int = 5

    settings = CustomProjectSettings.load_from_env(
        env_dict={"PROJECT_NAME": "Lightning API", "WORKER_CONCURRENCY": "16"}
    )
    assert settings.PROJECT_NAME == "Lightning API"
    assert settings.WORKER_CONCURRENCY == 16
