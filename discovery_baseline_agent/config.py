import os
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration settings for Discovery Baseline Agent"""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY")
    
    # Request settings
    MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "5"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    RETRY_ATTEMPTS = int(os.getenv("RETRY_ATTEMPTS", "3"))
    
    # Output settings
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./results")
    CACHE_RESPONSES = os.getenv("CACHE_RESPONSES", "true").lower() == "true"
    
    # AI Engine configurations
    AI_ENGINES = {
        "openai": {
            "models": ["gpt-4", "gpt-3.5-turbo"],
            "enabled": bool(OPENAI_API_KEY)
        },
        "anthropic": {
            "models": ["claude-3-5-sonnet-20241022"],
            "enabled": bool(ANTHROPIC_API_KEY)
        },
        "google": {
            "models": ["gemini-1.5-pro"],
            "enabled": bool(GOOGLE_AI_API_KEY)
        }
    }
    
    @classmethod
    def validate(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []
        
        if not cls.OPENAI_API_KEY:
            issues.append("Missing OPENAI_API_KEY")
        if not cls.ANTHROPIC_API_KEY:
            issues.append("Missing ANTHROPIC_API_KEY")
        if not cls.GOOGLE_AI_API_KEY:
            issues.append("Missing GOOGLE_AI_API_KEY")
            
        enabled_engines = sum(1 for engine in cls.AI_ENGINES.values() if engine["enabled"])
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "enabled_engines": enabled_engines,
            "total_engines": len(cls.AI_ENGINES)
        }