import brax


def test_version():
    assert hasattr(brax, "__version__")
    assert brax.__version__ == "1.0.0"


def test_exports():
    assert hasattr(brax, "Config")
    assert hasattr(brax, "AIProvider")
    assert hasattr(brax, "MemoryEngine")
    assert hasattr(brax, "MessageBus")
    assert hasattr(brax, "Orchestrator")
    assert hasattr(brax, "FileWriter")
