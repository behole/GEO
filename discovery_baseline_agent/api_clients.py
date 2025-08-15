import asyncio
import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

import openai
import anthropic
import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential
import httpx

from .config import Config

logger = logging.getLogger(__name__)

class BaseAIClient(ABC):
    """Base class for AI API clients"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.client = None
        
    @abstractmethod
    async def query(self, prompt: str, query: str) -> Dict[str, Any]:
        """Query the AI engine with a prompt"""
        pass
        
    @abstractmethod
    def get_engine_name(self) -> str:
        """Return the engine name"""
        pass

class OpenAIClient(BaseAIClient):
    """OpenAI API client for GPT models"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        super().__init__(api_key, model)
        self.client = openai.AsyncOpenAI(api_key=api_key)
        
    @retry(stop=stop_after_attempt(Config.RETRY_ATTEMPTS), 
           wait=wait_exponential(multiplier=1, min=4, max=10))
    async def query(self, prompt: str, query: str) -> Dict[str, Any]:
        """Query OpenAI API"""
        try:
            full_prompt = f"{prompt}\n\nQuery: {query}"
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that provides comprehensive information about sunscreen products, including specific brand recommendations and citations."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            return {
                "engine": self.get_engine_name(),
                "model": self.model,
                "query": query,
                "response": response.choices[0].message.content,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error for query '{query}': {str(e)}")
            return {
                "engine": self.get_engine_name(),
                "model": self.model,
                "query": query,
                "response": None,
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def get_engine_name(self) -> str:
        return "openai"

class AnthropicClient(BaseAIClient):
    """Anthropic API client for Claude models"""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        super().__init__(api_key, model)
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        
    @retry(stop=stop_after_attempt(Config.RETRY_ATTEMPTS), 
           wait=wait_exponential(multiplier=1, min=4, max=10))
    async def query(self, prompt: str, query: str) -> Dict[str, Any]:
        """Query Anthropic API"""
        try:
            full_prompt = f"{prompt}\n\nQuery: {query}"
            
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )
            
            return {
                "engine": self.get_engine_name(),
                "model": self.model,
                "query": query,
                "response": response.content[0].text,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens
                }
            }
            
        except Exception as e:
            logger.error(f"Anthropic API error for query '{query}': {str(e)}")
            return {
                "engine": self.get_engine_name(),
                "model": self.model,
                "query": query,
                "response": None,
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def get_engine_name(self) -> str:
        return "anthropic"

class GoogleAIClient(BaseAIClient):
    """Google AI API client for Gemini models"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-pro"):
        super().__init__(api_key, model)
        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel(model)
        
    @retry(stop=stop_after_attempt(Config.RETRY_ATTEMPTS), 
           wait=wait_exponential(multiplier=1, min=4, max=10))
    async def query(self, prompt: str, query: str) -> Dict[str, Any]:
        """Query Google AI API"""
        try:
            full_prompt = f"{prompt}\n\nQuery: {query}"
            
            # Google AI doesn't have native async support, so we use asyncio.to_thread
            response = await asyncio.to_thread(
                self.client.generate_content,
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=1500,
                    temperature=0.7
                )
            )
            
            return {
                "engine": self.get_engine_name(),
                "model": self.model,
                "query": query,
                "response": response.text,
                "timestamp": datetime.utcnow().isoformat(),
                "success": True,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count if hasattr(response, 'usage_metadata') else None,
                    "completion_tokens": response.usage_metadata.candidates_token_count if hasattr(response, 'usage_metadata') else None
                }
            }
            
        except Exception as e:
            logger.error(f"Google AI API error for query '{query}': {str(e)}")
            return {
                "engine": self.get_engine_name(),
                "model": self.model,
                "query": query,
                "response": None,
                "timestamp": datetime.utcnow().isoformat(),
                "success": False,
                "error": str(e)
            }
    
    def get_engine_name(self) -> str:
        return "google"

class AIClientFactory:
    """Factory for creating AI clients"""
    
    @staticmethod
    def create_clients() -> List[BaseAIClient]:
        """Create all available AI clients based on configuration"""
        clients = []
        
        config = Config.AI_ENGINES
        
        # OpenAI clients
        if config["openai"]["enabled"]:
            for model in config["openai"]["models"]:
                clients.append(OpenAIClient(Config.OPENAI_API_KEY, model))
        
        # Anthropic clients
        if config["anthropic"]["enabled"]:
            for model in config["anthropic"]["models"]:
                clients.append(AnthropicClient(Config.ANTHROPIC_API_KEY, model))
        
        # Google AI clients
        if config["google"]["enabled"]:
            for model in config["google"]["models"]:
                clients.append(GoogleAIClient(Config.GOOGLE_AI_API_KEY, model))
        
        return clients
    
    @staticmethod
    def get_enabled_engines() -> List[str]:
        """Get list of enabled engine names"""
        return [name for name, config in Config.AI_ENGINES.items() if config["enabled"]]

class ConcurrentQueryManager:
    """Manages concurrent queries across multiple AI engines"""
    
    def __init__(self, clients: List[BaseAIClient], max_concurrent: int = None):
        self.clients = clients
        self.max_concurrent = max_concurrent or Config.MAX_CONCURRENT_REQUESTS
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
    async def query_single(self, client: BaseAIClient, prompt: str, query: str) -> Dict[str, Any]:
        """Execute a single query with rate limiting"""
        async with self.semaphore:
            return await client.query(prompt, query)
    
    async def query_all_engines(self, prompt: str, query: str) -> List[Dict[str, Any]]:
        """Query all engines with a single query"""
        tasks = [
            self.query_single(client, prompt, query)
            for client in self.clients
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Exception in query for {self.clients[i].get_engine_name()}: {str(result)}")
                processed_results.append({
                    "engine": self.clients[i].get_engine_name(),
                    "model": self.clients[i].model,
                    "query": query,
                    "response": None,
                    "timestamp": datetime.utcnow().isoformat(),
                    "success": False,
                    "error": str(result)
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def query_batch(self, prompt: str, queries: List[str]) -> List[List[Dict[str, Any]]]:
        """Query all engines with a batch of queries"""
        batch_tasks = [
            self.query_all_engines(prompt, query)
            for query in queries
        ]
        
        return await asyncio.gather(*batch_tasks)