import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from brax.core.memory import MemoryEngine, MEMORY_DIR


@pytest.fixture
def temp_memory():
    with tempfile.TemporaryDirectory() as tmp:
        mem_dir = Path(tmp) / "memory"
        with patch("brax.core.memory.MEMORY_DIR", mem_dir):
            mem_dir.mkdir(parents=True, exist_ok=True)
            engine = MemoryEngine()
            yield engine


def test_save_and_list(temp_memory):
    temp_memory.save("pm", "task_1", "Build a web app")
    temp_memory.save("pm", "task_2", "Design architecture")
    memories = temp_memory.list_agent_memories("pm")
    assert len(memories) >= 2


def test_save_error(temp_memory):
    temp_memory.save("pm", "error", "something went wrong")
    memories = temp_memory.list_agent_memories("pm")
    errors = [m for m in memories if m["key"] == "error"]
    assert len(errors) >= 1


def test_record_lesson(temp_memory):
    temp_memory.record_lesson("pm", "Always ask for requirements first")
    prompt = temp_memory.format_for_prompt("pm")
    assert "Always ask for requirements first" in prompt


def test_record_project(temp_memory):
    temp_memory.record_project("pm", "test-project")
    prompt = temp_memory.format_for_prompt("pm")
    assert "test-project" in prompt


def test_lessons_capped(temp_memory):
    for i in range(30):
        temp_memory.record_lesson("pm", f"Lesson {i}")
    prompt = temp_memory.format_for_prompt("pm")
    assert prompt.count("Lesson") <= 20
