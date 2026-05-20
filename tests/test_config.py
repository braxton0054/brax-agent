import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from brax.core.config import Config


@pytest.fixture
def temp_config():
    with tempfile.TemporaryDirectory() as tmp:
        config_dir = Path(tmp) / ".brax"
        config_file = config_dir / "config.json"
        with patch("brax.core.config.CONFIG_DIR", config_dir):
            with patch("brax.core.config.CONFIG_FILE", config_file):
                c = Config()
                yield c


def test_config_creates_dir_and_file(temp_config):
    assert temp_config.get("onboarded") is None


def test_config_set_get(temp_config):
    temp_config.set("test_key", "test_value")
    assert temp_config.get("test_key") == "test_value"


def test_config_onboard_flow(temp_config):
    assert temp_config.is_onboarded() is False
    temp_config.mark_onboarded()
    assert temp_config.is_onboarded() is True


def test_config_workspace_default(temp_config):
    ws = temp_config.get_workspace()
    assert ws.name == "workspace"


def test_config_workspace_custom(temp_config):
    temp_config.set_workspace("/tmp/custom-ws")
    assert str(temp_config.get_workspace()) == "/tmp/custom-ws"


def test_config_agent_provider(temp_config):
    temp_config.set_agent_provider("pm", "anthropic", "sk-test", "claude-sonnet-4-20250514")
    data = temp_config.get_agent_provider("pm")
    assert data["provider"] == "anthropic"
    assert data["api_key"] == "sk-test"
    assert data["model"] == "claude-sonnet-4-20250514"


def test_config_agent_provider_with_tokens(temp_config):
    temp_config.set_agent_provider("architect", "openai", "sk-test", "gpt-4", max_input_tokens=100000, max_output_tokens=16000)
    data = temp_config.get_agent_provider("architect")
    assert data["max_input_tokens"] == 100000
    assert data["max_output_tokens"] == 16000


def test_config_all_agents(temp_config):
    temp_config.set_agent_provider("pm", "anthropic", "key1", "claude-sonnet-4-20250514")
    temp_config.set_agent_provider("architect", "openai", "key2", "gpt-4")
    agents = temp_config.all_agents()
    assert "pm" in agents
    assert "architect" in agents


def test_config_github_token(temp_config):
    assert temp_config.get_github_token() == ""
    temp_config.set_github_token("ghp_test")
    assert temp_config.get_github_token() == "ghp_test"


def test_config_github_autopush(temp_config):
    assert temp_config.get_github_autopush() is False
    temp_config.set_github_autopush(True)
    assert temp_config.get_github_autopush() is True


def test_config_init_workspace(temp_config):
    ws = temp_config.init_workspace()
    assert ws.exists()
    assert ws == temp_config.get_workspace()
    ws.rmdir()
