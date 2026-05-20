from brax.core.provider import count_tokens, get_model_limits, truncate_text, MODEL_LIMITS


def test_count_tokens_empty():
    assert count_tokens("") == 0


def test_count_tokens_simple():
    assert count_tokens("hello world") > 0


def test_get_model_limits_exact():
    limits = get_model_limits("claude-sonnet-4-20250514")
    assert limits["max_input"] > 0
    assert limits["max_output"] > 0


def test_get_model_limits_prefix():
    limits = get_model_limits("claude-sonnet-4-20250514-test")
    assert limits["max_input"] > 0


def test_get_model_limits_unknown():
    limits = get_model_limits("unknown-model-xyz")
    assert limits["max_input"] >= 100000
    assert limits["max_output"] > 0


def test_truncate_text_no_truncate():
    text = "short text"
    result = truncate_text(text, 1000)
    assert result == text


def test_truncate_text_with_truncate():
    text = "a" * 1000
    result = truncate_text(text, 100)
    assert len(result) < len(text)
    assert "truncated" in result.lower()


def test_model_limits_structure():
    for model, limits in MODEL_LIMITS.items():
        assert "max_input" in limits
        assert "max_output" in limits
        assert limits["max_input"] > 0
        assert limits["max_output"] > 0
