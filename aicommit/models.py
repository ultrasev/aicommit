#!/usr/bin/env python3
from abc import ABC, abstractmethod
import os
import json
import httpx
from loguru import logger
from codefast import getenv
from typing import Optional, Dict, Any, List


class LLMModel(ABC):
    """
    Base abstract class for LLM models
    """
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Generate text from the model
        """
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Get model name
        """
        pass


class SiliconFlowModel(LLMModel):
    """
    SiliconFlow API implementation
    """
    def __init__(self):
        keypath = os.path.expanduser('~/.openai_api_key')
        self.api_key = getenv("SILICONFLOW_API_KEY", keypath)
        self.model_name = "deepseek-ai/DeepSeek-V3"

    @property
    def name(self) -> str:
        return f"SiliconFlow ({self.model_name})"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Generate text using SiliconFlow API
        """
        if not self.api_key:
            return None

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.siliconflow.cn/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "stream": False,
                        "max_tokens": 800,
                        "temperature": 0.7,
                        "top_p": 0.7,
                        "top_k": 50,
                        "frequency_penalty": 0.5,
                        "n": 1,
                        "response_format": {"type": "text"}
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except (httpx.HTTPError, KeyError, json.JSONDecodeError) as e:
                logger.error(f"SiliconFlow API error: {str(e)}")
                return None


class PerplexityModel(LLMModel):
    """
    Perplexity API implementation
    """
    def __init__(self):
        keypath = os.path.expanduser('~/.perplexity_api_key')
        self.api_key = getenv("PERPLEXITY_API_KEY", keypath)
        self.model_name = "sonar-pro"

    @property
    def name(self) -> str:
        return f"Perplexity ({self.model_name})"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Generate text using Perplexity API
        """
        if not self.api_key:
            return None

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "max_tokens": 800
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except (httpx.HTTPError, KeyError, json.JSONDecodeError) as e:
                logger.error(f"Perplexity API error: {str(e)}")
                return None


class OpenRouterModel(LLMModel):
    """
    OpenRouter API implementation
    """
    def __init__(self):
        keypath = os.path.expanduser('~/.openai_api_key')
        self.api_key = getenv("OPENROUTER_API_KEY", keypath)
        self.model_name = "google/gemini-2.0-flash-001"

    @property
    def name(self) -> str:
        return f"OpenRouter ({self.model_name})"

    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Generate text using OpenRouter API
        """
        if not self.api_key:
            return None

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.api_key}"
                    },
                    json={
                        "model": self.model_name,
                        "messages": messages
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()["choices"][0]["message"]["content"]
            except (httpx.HTTPError, KeyError, json.JSONDecodeError) as e:
                logger.error(f"OpenRouter API error: {str(e)}")
                return None


class ModelFactory:
    """
    Factory class for creating LLM models
    """
    @staticmethod
    def get_models() -> List[LLMModel]:
        """
        Get a list of available models in priority order
        """
        return [
            SiliconFlowModel(),
            PerplexityModel(),
            OpenRouterModel()
        ]