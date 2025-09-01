#!/usr/bin/env python3
"""
API Cost Tracker for GEO System
Calculates costs for OpenAI, Anthropic, and Google AI API usage
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class ModelCostConfig:
    """Cost configuration for a specific model"""
    input_cost_per_1k: float  # Cost per 1K input tokens
    output_cost_per_1k: float  # Cost per 1K output tokens
    
@dataclass 
class APICallCost:
    """Cost breakdown for a single API call"""
    engine: str
    model: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float
    timestamp: str

@dataclass
class CostSummary:
    """Summary of all costs for a run"""
    total_cost: float
    total_calls: int
    total_input_tokens: int
    total_output_tokens: int
    cost_by_engine: Dict[str, float]
    cost_by_model: Dict[str, float]
    call_breakdown: List[APICallCost]

class APICostTracker:
    """Tracks and calculates API costs across all providers"""
    
    # Current pricing as of January 2025 (verify these regularly!)
    COST_CONFIG = {
        "openai": {
            "gpt-4": ModelCostConfig(0.030, 0.060),  # $30/$60 per 1M tokens
            "gpt-4-turbo": ModelCostConfig(0.010, 0.030),  # $10/$30 per 1M tokens
            "gpt-3.5-turbo": ModelCostConfig(0.0015, 0.002),  # $1.50/$2.00 per 1M tokens
        },
        "anthropic": {
            "claude-3-5-sonnet-20241022": ModelCostConfig(0.003, 0.015),  # $3/$15 per 1M tokens
            "claude-3-opus": ModelCostConfig(0.015, 0.075),  # $15/$75 per 1M tokens
            "claude-3-haiku": ModelCostConfig(0.00025, 0.00125),  # $0.25/$1.25 per 1M tokens
        },
        "google": {
            "gemini-1.5-pro": ModelCostConfig(0.00125, 0.005),  # $1.25/$5 per 1M tokens
            "gemini-1.5-flash": ModelCostConfig(0.000075, 0.0003),  # $0.075/$0.30 per 1M tokens
        }
    }
    
    def __init__(self):
        self.call_costs: List[APICallCost] = []
    
    def calculate_call_cost(self, response_data: Dict[str, Any]) -> Optional[APICallCost]:
        """Calculate cost for a single API call"""
        if not response_data.get("success") or not response_data.get("usage"):
            return None
        
        engine = response_data.get("engine", "unknown")
        model = response_data.get("model", "unknown")
        usage = response_data["usage"]
        
        # Get cost configuration for this model
        if engine not in self.COST_CONFIG:
            logger.warning(f"No cost config for engine: {engine}")
            return None
            
        if model not in self.COST_CONFIG[engine]:
            logger.warning(f"No cost config for model: {model}")
            return None
        
        cost_config = self.COST_CONFIG[engine][model]
        
        # Extract token counts (handle different naming conventions)
        input_tokens = self._extract_input_tokens(usage)
        output_tokens = self._extract_output_tokens(usage)
        
        if input_tokens is None or output_tokens is None:
            logger.warning(f"Missing token data for {engine}/{model}: {usage}")
            return None
        
        # Calculate costs (pricing is per 1K tokens, so divide by 1000)
        input_cost = (input_tokens / 1000) * cost_config.input_cost_per_1k
        output_cost = (output_tokens / 1000) * cost_config.output_cost_per_1k
        total_cost = input_cost + output_cost
        
        call_cost = APICallCost(
            engine=engine,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
            timestamp=response_data.get("timestamp", datetime.utcnow().isoformat())
        )
        
        self.call_costs.append(call_cost)
        return call_cost
    
    def _extract_input_tokens(self, usage: Dict[str, Any]) -> Optional[int]:
        """Extract input tokens from usage data (handles different naming conventions)"""
        # OpenAI uses 'prompt_tokens'
        if 'prompt_tokens' in usage:
            return usage['prompt_tokens']
        # Anthropic uses 'input_tokens'
        elif 'input_tokens' in usage:
            return usage['input_tokens']
        # Google uses 'prompt_tokens' or might be None
        elif 'prompt_tokens' in usage and usage['prompt_tokens'] is not None:
            return usage['prompt_tokens']
        
        return None
    
    def _extract_output_tokens(self, usage: Dict[str, Any]) -> Optional[int]:
        """Extract output tokens from usage data (handles different naming conventions)"""
        # OpenAI uses 'completion_tokens'
        if 'completion_tokens' in usage:
            return usage['completion_tokens']
        # Anthropic uses 'output_tokens'
        elif 'output_tokens' in usage:
            return usage['output_tokens']
        # Google uses 'completion_tokens' or might be None
        elif 'completion_tokens' in usage and usage['completion_tokens'] is not None:
            return usage['completion_tokens']
        
        return None
    
    def track_batch_costs(self, response_batch: List[Dict[str, Any]]) -> List[APICallCost]:
        """Track costs for a batch of API responses"""
        batch_costs = []
        
        for response_data in response_batch:
            call_cost = self.calculate_call_cost(response_data)
            if call_cost:
                batch_costs.append(call_cost)
        
        return batch_costs
    
    def generate_cost_summary(self) -> CostSummary:
        """Generate a comprehensive cost summary"""
        if not self.call_costs:
            return CostSummary(0, 0, 0, 0, {}, {}, [])
        
        total_cost = sum(call.total_cost for call in self.call_costs)
        total_calls = len(self.call_costs)
        total_input_tokens = sum(call.input_tokens for call in self.call_costs)
        total_output_tokens = sum(call.output_tokens for call in self.call_costs)
        
        # Group by engine
        cost_by_engine = {}
        for call in self.call_costs:
            cost_by_engine[call.engine] = cost_by_engine.get(call.engine, 0) + call.total_cost
        
        # Group by model
        cost_by_model = {}
        for call in self.call_costs:
            model_key = f"{call.engine}/{call.model}"
            cost_by_model[model_key] = cost_by_model.get(model_key, 0) + call.total_cost
        
        return CostSummary(
            total_cost=total_cost,
            total_calls=total_calls,
            total_input_tokens=total_input_tokens,
            total_output_tokens=total_output_tokens,
            cost_by_engine=cost_by_engine,
            cost_by_model=cost_by_model,
            call_breakdown=self.call_costs.copy()
        )
    
    def export_cost_report(self, output_file: str, summary: Optional[CostSummary] = None) -> str:
        """Export detailed cost report to JSON file"""
        if summary is None:
            summary = self.generate_cost_summary()
        
        report_data = {
            "cost_summary": asdict(summary),
            "generation_timestamp": datetime.utcnow().isoformat(),
            "pricing_note": "Costs calculated based on January 2025 pricing. Verify current rates."
        }
        
        with open(output_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        return output_file
    
    def print_cost_summary(self, summary: Optional[CostSummary] = None) -> None:
        """Print a formatted cost summary to console"""
        if summary is None:
            summary = self.generate_cost_summary()
        
        print("\n" + "="*60)
        print("🧾 API COST SUMMARY")
        print("="*60)
        print(f"💰 Total Cost: ${summary.total_cost:.4f}")
        print(f"📞 Total API Calls: {summary.total_calls:,}")
        print(f"📝 Input Tokens: {summary.total_input_tokens:,}")
        print(f"🤖 Output Tokens: {summary.total_output_tokens:,}")
        print(f"🔤 Total Tokens: {summary.total_input_tokens + summary.total_output_tokens:,}")
        
        print("\n💡 Cost by Engine:")
        for engine, cost in sorted(summary.cost_by_engine.items()):
            percentage = (cost / summary.total_cost) * 100 if summary.total_cost > 0 else 0
            print(f"  {engine.title()}: ${cost:.4f} ({percentage:.1f}%)")
        
        print("\n🤖 Cost by Model:")
        for model, cost in sorted(summary.cost_by_model.items(), key=lambda x: x[1], reverse=True):
            percentage = (cost / summary.total_cost) * 100 if summary.total_cost > 0 else 0
            print(f"  {model}: ${cost:.4f} ({percentage:.1f}%)")
        
        # Calculate cost efficiency
        if summary.total_calls > 0:
            avg_cost_per_call = summary.total_cost / summary.total_calls
            print(f"\n📊 Average Cost per API Call: ${avg_cost_per_call:.4f}")
        
        if summary.total_input_tokens + summary.total_output_tokens > 0:
            cost_per_1k_tokens = (summary.total_cost / (summary.total_input_tokens + summary.total_output_tokens)) * 1000
            print(f"📊 Average Cost per 1K Tokens: ${cost_per_1k_tokens:.4f}")
        
        print("="*60)
        print("💡 Note: Costs based on January 2025 pricing")
        print("="*60 + "\n")
    
    def reset(self):
        """Reset cost tracking for a new run"""
        self.call_costs.clear()

# Example usage and testing
if __name__ == "__main__":
    # Test with sample data
    tracker = APICostTracker()
    
    # Sample API responses for testing
    sample_responses = [
        {
            "engine": "openai",
            "model": "gpt-4",
            "success": True,
            "usage": {
                "prompt_tokens": 150,
                "completion_tokens": 300,
                "total_tokens": 450
            }
        },
        {
            "engine": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "success": True,
            "usage": {
                "input_tokens": 200,
                "output_tokens": 400
            }
        },
        {
            "engine": "google",
            "model": "gemini-1.5-pro",
            "success": True,
            "usage": {
                "prompt_tokens": 180,
                "completion_tokens": 350
            }
        }
    ]
    
    print("Testing API Cost Tracker...")
    
    # Track costs
    for response in sample_responses:
        cost = tracker.calculate_call_cost(response)
        if cost:
            print(f"Call Cost: {cost.engine}/{cost.model} = ${cost.total_cost:.4f}")
    
    # Generate and print summary
    summary = tracker.generate_cost_summary()
    tracker.print_cost_summary(summary)