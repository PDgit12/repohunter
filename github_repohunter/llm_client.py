"""
LLM Client - Supports Ollama (free/local) and OpenAI (paid API)

Usage:
    from github_repohunter.llm_client import get_llm_client
    
    client = get_llm_client()  # Auto-detects best available
    response = client.generate("Your prompt here")
"""

import os
import requests
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Abstract base for LLM clients"""
    
    @abstractmethod
    def generate(self, prompt: str, system: str = None) -> str:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass


class OllamaClient(LLMClient):
    """Free local LLM via Ollama"""
    
    def __init__(self, model: str = "llama3", base_url: str = "http://127.0.0.1:11434"):
        self.model = model
        self.base_url = base_url
    
    def is_available(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return r.status_code == 200
        except Exception:
            return False
    
    def generate(self, prompt: str, system: str = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }
        if system:
            payload["system"] = system
        
        try:
            r = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=120)
            r.raise_for_status()
            return r.json().get("response", "")
        except requests.exceptions.ConnectionError:
            raise RuntimeError("Ollama not running. Start with: ollama serve")
        except Exception as e:
            raise RuntimeError(f"Ollama error: {e}")


class OpenAIClient(LLMClient):
    """OpenAI GPT-4o API"""
    
    def __init__(self, api_key: str = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate(self, prompt: str, system: str = None) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set")
        
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 4096
        }
        
        try:
            r = requests.post(self.base_url, headers=headers, json=payload, timeout=120)
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception as e:
            raise RuntimeError(f"OpenAI error: {e}")


class TemplateClient(LLMClient):
    """Fallback template-based responses (no LLM needed)"""
    
    def is_available(self) -> bool:
        return True
    
    def generate(self, prompt: str, system: str = None) -> str:
        # Return a marker that indicates template mode
        return f"[TEMPLATE_MODE] Based on the prompt, here is a structured analysis:\n\n{prompt[:500]}..."


def get_llm_client(prefer: str = "auto") -> LLMClient:
    """
    Get the best available LLM client.
    
    Args:
        prefer: "ollama", "openai", or "auto" (tries ollama first, then openai)
    
    Returns:
        LLMClient instance
    """
    ollama = OllamaClient()
    openai = OpenAIClient()
    
    if prefer == "ollama":
        if ollama.is_available():
            return ollama
        raise RuntimeError("Ollama not available. Run: ollama serve")
    
    if prefer == "openai":
        if openai.is_available():
            return openai
        raise RuntimeError("OpenAI not available. Set OPENAI_API_KEY")
    
    # Auto mode: try ollama first (free), then openai
    if ollama.is_available():
        return ollama
    if openai.is_available():
        return openai
    
    # Fallback to template mode
    return TemplateClient()


def check_llm_status() -> dict:
    """Check which LLM backends are available"""
    ollama = OllamaClient()
    openai = OpenAIClient()
    
    return {
        "ollama": {
            "available": ollama.is_available(),
            "model": ollama.model,
            "note": "Free, local. Run: ollama serve && ollama pull llama3.2"
        },
        "openai": {
            "available": openai.is_available(),
            "model": openai.model,
            "note": "Paid API. Set OPENAI_API_KEY env var"
        },
        "active": "ollama" if ollama.is_available() else ("openai" if openai.is_available() else "template")
    }
