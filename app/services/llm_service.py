"""
LLM service — unified interface for OpenAI and Ollama providers.
Supports both regular generation and streaming responses.
"""

import json
from collections.abc import AsyncGenerator

import httpx
from openai import AsyncOpenAI

from app.config.settings import get_settings


class LLMService:
    """Abstraction over OpenAI and Ollama LLM APIs."""

    def __init__(self) -> None:
        self._settings = get_settings()
        # Connect timeout = 30s (fail fast if Ollama is down)
        # Read timeout = None (no limit — LLM generation can take minutes on CPU)
        self._http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(connect=30.0, read=None, write=30.0, pool=30.0)
        )

        if self._settings.LLM_PROVIDER == "openai":
            self._openai = AsyncOpenAI(api_key=self._settings.OPENAI_API_KEY)
        else:
            self._openai = None

    # ── Regular Generation ───────────────────────────────────

    async def generate(self, prompt: str) -> str:
        """Generate a complete response from the LLM."""
        if self._settings.LLM_PROVIDER == "openai":
            return await self._openai_generate(prompt)
        return await self._ollama_generate(prompt)

    async def _openai_generate(self, prompt: str) -> str:
        response = await self._openai.chat.completions.create(
            model=self._settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        return response.choices[0].message.content

    async def _ollama_generate(self, prompt: str) -> str:
        """Use streaming internally to avoid timeout on slow hardware."""
        try:
            result_parts: list[str] = []
            async with self._http_client.stream(
                "POST",
                f"{self._settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": self._settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": True,
                },
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line:
                        data = json.loads(line)
                        token = data.get("response", "")
                        if token:
                            result_parts.append(token)
            return "".join(result_parts)
        except httpx.ConnectError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self._settings.OLLAMA_BASE_URL}. "
                "Make sure Ollama is running: 'ollama serve'"
            )
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise ConnectionError(
                    f"Model '{self._settings.OLLAMA_MODEL}' not found. "
                    f"Pull it first: 'ollama pull {self._settings.OLLAMA_MODEL}'"
                )
            raise

    # ── Streaming Generation ─────────────────────────────────

    async def stream(self, prompt: str) -> AsyncGenerator[str, None]:
        """Stream response tokens as they are generated."""
        if self._settings.LLM_PROVIDER == "openai":
            async for token in self._openai_stream(prompt):
                yield token
        else:
            async for token in self._ollama_stream(prompt):
                yield token

    async def _openai_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        stream = await self._openai.chat.completions.create(
            model=self._settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta

    async def _ollama_stream(self, prompt: str) -> AsyncGenerator[str, None]:
        async with self._http_client.stream(
            "POST",
            f"{self._settings.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": self._settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": True,
            },
        ) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line:
                    data = json.loads(line)
                    token = data.get("response", "")
                    if token:
                        yield token

    # ── Cleanup ──────────────────────────────────────────────

    async def close(self) -> None:
        await self._http_client.aclose()


# ── Module-level singleton ────────────────────────────────────
llm_service = LLMService()
