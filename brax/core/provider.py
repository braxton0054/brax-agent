import os
import json
import re
import httpx
from brax.core.config import Config

ENV_KEY_MAP = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "openrouter": "OPENROUTER_API_KEY",
    "ollama": "",
    "groq": "GROQ_API_KEY",
}

MODEL_LIMITS = {
    # Anthropic Claude 3
    "claude-3-opus": {"max_input": 200000, "max_output": 4096},
    "claude-3-sonnet": {"max_input": 200000, "max_output": 4096},
    "claude-3-haiku": {"max_input": 200000, "max_output": 4096},
    "claude-3-opus-20240229": {"max_input": 200000, "max_output": 4096},
    "claude-3-sonnet-20240229": {"max_input": 200000, "max_output": 4096},
    "claude-3-haiku-20240307": {"max_input": 200000, "max_output": 4096},
    # Anthropic Claude 3.5
    "claude-3-5-sonnet": {"max_input": 200000, "max_output": 8192},
    "claude-3-5-sonnet-20241022": {"max_input": 200000, "max_output": 8192},
    "claude-3-5-haiku": {"max_input": 200000, "max_output": 8192},
    "claude-3-5-haiku-20241022": {"max_input": 200000, "max_output": 8192},
    # Anthropic Claude 4
    "claude-4": {"max_input": 200000, "max_output": 16384},
    "claude-sonnet-4": {"max_input": 200000, "max_output": 16384},
    "claude-opus-4": {"max_input": 200000, "max_output": 16384},
    "claude-haiku-3-5": {"max_input": 200000, "max_output": 8192},
    # OpenAI GPT-4
    "gpt-4": {"max_input": 8192, "max_output": 4096},
    "gpt-4-32k": {"max_input": 32768, "max_output": 4096},
    "gpt-4-turbo": {"max_input": 128000, "max_output": 4096},
    "gpt-4-turbo-preview": {"max_input": 128000, "max_output": 4096},
    "gpt-4-0125-preview": {"max_input": 128000, "max_output": 4096},
    "gpt-4-1106-preview": {"max_input": 128000, "max_output": 4096},
    "gpt-4o": {"max_input": 128000, "max_output": 16384},
    "gpt-4o-2024-05-13": {"max_input": 128000, "max_output": 16384},
    "gpt-4o-mini": {"max_input": 128000, "max_output": 16384},
    # OpenAI GPT-3.5
    "gpt-3.5-turbo": {"max_input": 16385, "max_output": 4096},
    "gpt-3.5-turbo-1106": {"max_input": 16385, "max_output": 4096},
    "gpt-3.5-turbo-0125": {"max_input": 16385, "max_output": 4096},
    # Groq models
    "mixtral-8x7b-32768": {"max_input": 32768, "max_output": 8192},
    "llama2-70b-4096": {"max_input": 4096, "max_output": 4096},
    "llama3-8b-8192": {"max_input": 8192, "max_output": 8192},
    "llama3-70b-8192": {"max_input": 8192, "max_output": 8192},
    "gemma-7b-it": {"max_input": 8192, "max_output": 4096},
    "gemma2-9b-it": {"max_input": 8192, "max_output": 4096},
    # OpenRouter generic
    "openrouter/auto": {"max_input": 128000, "max_output": 16384},
    # Ollama defaults
    "llama3": {"max_input": 8192, "max_output": 4096},
    "llama3.1": {"max_input": 128000, "max_output": 8192},
    "llama3.2": {"max_input": 128000, "max_output": 8192},
    "mistral": {"max_input": 8192, "max_output": 4096},
    "codellama": {"max_input": 16384, "max_output": 4096},
    "mixtral": {"max_input": 32768, "max_output": 4096},
    "deepseek-coder": {"max_input": 128000, "max_output": 4096},
}

DEFAULT_MAX_OUTPUT = 8192
DEFAULT_MAX_INPUT = 128000

OUTPUT_TRUNCATED_WARNING = "\n\n[TRUNCATED - output hit token limit. Continue in next message.]"


class TruncationError(Exception):
    pass


def normalize_model_key(model: str) -> str:
    key = model.lower().strip()
    parts = key.replace(":", "/").split("/")
    if parts:
        return parts[-1]
    return key


def get_model_limits(model: str) -> dict:
    key = normalize_model_key(model)
    sorted_keys = sorted(MODEL_LIMITS.keys(), key=len, reverse=True)
    for known_key in sorted_keys:
        if key == known_key:
            return dict(MODEL_LIMITS[known_key])
    for known_key in sorted_keys:
        if key.startswith(known_key) and len(key) > len(known_key):
            return dict(MODEL_LIMITS[known_key])
    return {"max_input": DEFAULT_MAX_INPUT, "max_output": DEFAULT_MAX_OUTPUT}


def count_tokens(text: str) -> int:
    if not text:
        return 0
    return len(text) // 4 + 1


def truncate_text(text: str, max_tokens: int, reserve_for_response: int = 0) -> str:
    limit_chars = max_tokens * 4
    if reserve_for_response:
        limit_chars -= reserve_for_response * 4
    if limit_chars <= 0:
        return ""
    if len(text) <= limit_chars:
        return text
    return text[:limit_chars] + "\n\n[...content truncated to fit token limit...]"


class AIProvider:
    def __init__(self, agent_name: str):
        self.config = Config()
        agent_cfg = self.config.get_agent_provider(agent_name)
        self.provider = agent_cfg.get("provider", "anthropic")
        self.model = agent_cfg.get("model", "")
        self.api_key = agent_cfg.get("api_key", "") or os.getenv(ENV_KEY_MAP.get(self.provider, ""), "")
        self.model_limits = get_model_limits(self.model)
        cfg_max_output = agent_cfg.get("max_output_tokens", 0)
        if cfg_max_output:
            self.max_output_tokens = cfg_max_output
        else:
            self.max_output_tokens = self.model_limits["max_output"]
        cfg_max_input = agent_cfg.get("max_input_tokens", 0)
        if cfg_max_input:
            self.max_input_tokens = cfg_max_input
        else:
            self.max_input_tokens = self.model_limits["max_input"]

    def chat(self, system: str, user: str) -> str:
        result = list(self.chat_stream(system, user))
        return "".join(result)

    def chat_stream(self, system: str, user: str):
        system = truncate_text(system, self.max_input_tokens // 3)
        combined = system + "\n" + user
        if count_tokens(combined) > self.max_input_tokens:
            user = truncate_text(
                user,
                self.max_input_tokens - count_tokens(system) - 500
            )

        if self.provider == "anthropic":
            yield from self._stream_anthropic(system, user)
        elif self.provider == "openai":
            yield from self._stream_openai(system, user)
        elif self.provider == "openrouter":
            yield from self._stream_openrouter(system, user)
        elif self.provider == "ollama":
            yield from self._stream_ollama(system, user)
        elif self.provider == "groq":
            yield from self._stream_groq(system, user)
        else:
            raise ValueError(f"Unknown provider: {self.provider}")

    def _stream_anthropic(self, system: str, user: str):
        import anthropic
        from anthropic import NOT_GIVEN
        client = anthropic.Anthropic(api_key=self.api_key)
        stop_reason = None
        with client.messages.stream(
            model=self.model,
            max_tokens=self.max_output_tokens,
            system=system,
            messages=[{"role": "user", "content": user}]
        ) as stream:
            for event in stream:
                if event.type == "content_block_delta" and event.delta.text:
                    yield event.delta.text
                if event.type == "message_delta":
                    stop_reason = event.delta.stop_reason
        if stop_reason == "max_tokens":
            yield OUTPUT_TRUNCATED_WARNING

    def _stream_openai(self, system: str, user: str):
        import openai
        client = openai.OpenAI(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            max_tokens=self.max_output_tokens,
            stream=True,
            stream_options={"include_usage": True}
        )
        finish_reason = None
        for chunk in response:
            if chunk.choices:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
                if chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason
        if finish_reason == "length":
            yield OUTPUT_TRUNCATED_WARNING

    def _stream_openrouter(self, system: str, user: str):
        with httpx.stream(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                "max_tokens": self.max_output_tokens,
                "stream": True
            },
            timeout=120
        ) as response:
            finish_reason = None
            for line in response.iter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        choices = chunk.get("choices", [])
                        if choices:
                            delta = choices[0].get("delta", {})
                            if delta.get("content"):
                                yield delta["content"]
                            if choices[0].get("finish_reason"):
                                finish_reason = choices[0]["finish_reason"]
                    except json.JSONDecodeError:
                        pass
            if finish_reason == "length":
                yield OUTPUT_TRUNCATED_WARNING

    def _stream_ollama(self, system: str, user: str):
        try:
            from ollama import Client
            client = Client(host="http://localhost:11434")
            options = {}
            if self.max_output_tokens:
                options["num_predict"] = self.max_output_tokens
            stream = client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user}
                ],
                stream=True,
                options=options
            )
            for part in stream:
                if part.get("done"):
                    if part.get("done_reason") == "length":
                        yield OUTPUT_TRUNCATED_WARNING
                    break
                content = part.get("message", {}).get("content", "")
                if content:
                    yield content
        except ImportError:
            with httpx.stream(
                "POST",
                "http://localhost:11434/api/chat",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    "options": {"num_predict": self.max_output_tokens} if self.max_output_tokens else {},
                    "stream": True
                },
                timeout=120
            ) as response:
                for line in response.iter_lines():
                    if line:
                        try:
                            data = json.loads(line)
                            content = data.get("message", {}).get("content", "")
                            if content:
                                yield content
                            if data.get("done"):
                                if data.get("done_reason") == "length":
                                    yield OUTPUT_TRUNCATED_WARNING
                                break
                        except json.JSONDecodeError:
                            pass

    def _stream_groq(self, system: str, user: str):
        from groq import Groq
        client = Groq(api_key=self.api_key)
        response = client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            max_tokens=self.max_output_tokens,
            stream=True
        )
        finish_reason = None
        for chunk in response:
            if chunk.choices:
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
                if chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason
        if finish_reason == "length":
            yield OUTPUT_TRUNCATED_WARNING
