from agentos.config import Settings


def test_default_app_name() -> None:
    config = Settings()

    assert config.app_name == "AgentOS"


def test_valid_api_port() -> None:
    config = Settings(api_port=8080)

    assert config.api_port == 8080


def test_debug_setting() -> None:
    config = Settings(app_debug=True)

    assert config.app_debug is True
