#!/usr/bin/env python3
"""
GEO System Cost Estimator
Estimates API costs for different run configurations
"""

def estimate_geo_run_costs():
    """Estimate costs for a typical GEO system run"""
    
    # Typical token usage per query (based on analysis)
    avg_tokens_per_query = {
        "openai": {
            "gpt-4": {"input": 120, "output": 350},  # More expensive, higher quality
            "gpt-3.5-turbo": {"input": 100, "output": 280}
        },
        "anthropic": {
            "claude-3-5-sonnet-20241022": {"input": 110, "output": 320}
        },
        "google": {
            "gemini-1.5-pro": {"input": 100, "output": 400}  # Often more verbose
        }
    }
    
    # Current pricing (per 1K tokens)
    pricing = {
        "openai": {
            "gpt-4": {"input": 0.030, "output": 0.060},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
        },
        "anthropic": {
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015}
        },
        "google": {
            "gemini-1.5-pro": {"input": 0.00125, "output": 0.005}
        }
    }
    
    print("🧾 GEO SYSTEM COST ESTIMATES")
    print("=" * 60)
    
    # Standard run: 50 queries × 4 engines = 200 API calls
    queries = 50
    engines = ["openai/gpt-4", "openai/gpt-3.5-turbo", "anthropic/claude-3-5-sonnet-20241022", "google/gemini-1.5-pro"]
    
    total_cost = 0
    engine_costs = {}
    
    for engine_model in engines:
        engine, model = engine_model.split("/")
        
        input_tokens = avg_tokens_per_query[engine][model]["input"] * queries
        output_tokens = avg_tokens_per_query[engine][model]["output"] * queries
        
        input_cost = (input_tokens / 1000) * pricing[engine][model]["input"]
        output_cost = (output_tokens / 1000) * pricing[engine][model]["output"]
        engine_cost = input_cost + output_cost
        
        engine_costs[engine_model] = engine_cost
        total_cost += engine_cost
        
        print(f"\n{engine_model.upper()}:")
        print(f"  Input tokens: {input_tokens:,} (${input_cost:.4f})")
        print(f"  Output tokens: {output_tokens:,} (${output_cost:.4f})")
        print(f"  Subtotal: ${engine_cost:.4f}")
    
    print("\n" + "=" * 60)
    print(f"🏁 STANDARD RUN TOTAL (50 queries): ${total_cost:.4f}")
    print(f"💰 Cost per query: ${total_cost/queries:.4f}")
    print(f"📊 Most expensive: {max(engine_costs.items(), key=lambda x: x[1])[0]}")
    print(f"💡 Most efficient: {min(engine_costs.items(), key=lambda x: x[1])[0]}")
    
    # Different run sizes
    run_sizes = [10, 25, 50, 100]
    print(f"\n📊 COST BY RUN SIZE:")
    print(f"{'Queries':<8} {'Total Cost':<12} {'Per Query':<12} {'For 10 Runs':<12}")
    print("-" * 50)
    
    for size in run_sizes:
        size_cost = total_cost * (size / queries)
        per_query = size_cost / size
        batch_cost = size_cost * 10
        print(f"{size:<8} ${size_cost:<11.4f} ${per_query:<11.4f} ${batch_cost:<11.2f}")
    
    # Client billing scenarios
    print(f"\n💼 CLIENT BILLING SCENARIOS:")
    print(f"{'Scenario':<25} {'Monthly Runs':<12} {'Cost/Month':<12} {'Markup (30%)':<12}")
    print("-" * 65)
    
    scenarios = [
        ("Small client", 4, total_cost),
        ("Medium client", 12, total_cost),
        ("Large client", 24, total_cost),
        ("Enterprise client", 50, total_cost)
    ]
    
    for scenario, runs_per_month, base_cost in scenarios:
        monthly_cost = base_cost * runs_per_month
        markup_cost = monthly_cost * 1.30  # 30% markup
        print(f"{scenario:<25} {runs_per_month:<12} ${monthly_cost:<11.2f} ${markup_cost:<11.2f}")
    
    print("\n" + "=" * 60)
    print("💡 RECOMMENDATIONS:")
    print("• Gemini offers best value for money")
    print("• GPT-4 provides highest quality but 3-4x cost")
    print("• Consider 20-30% markup for client billing")
    print("• Monitor usage - costs scale linearly")
    print("• Full system run (all 4 agents) ≈ 4x discovery cost")
    print("=" * 60)

if __name__ == "__main__":
    estimate_geo_run_costs()