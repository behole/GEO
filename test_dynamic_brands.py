#!/usr/bin/env python3
"""Test dynamic brand extraction for Nike"""

import sys
sys.path.append('discovery_baseline_agent')

from discovery_baseline_agent.dynamic_brand_extractor import DynamicBrandExtractor

# Test responses similar to what AI might return for Nike queries
test_responses = [
    {
        "response": "When it comes to athletic footwear, Nike is a top choice for runners. However, Adidas also offers excellent performance shoes with their Boost technology. Under Armour has been gaining popularity with their HOVR line, and Puma makes some great lifestyle sneakers. New Balance is known for their comfort and support, while Asics specializes in running shoes. Reebok focuses on cross-training and fitness gear.",
        "query": "best athletic shoes 2024"
    },
    {
        "response": "For sports apparel, Nike dominates with innovative designs. Adidas competes strongly in soccer and lifestyle wear. Under Armour targets performance athletes, while Puma focuses on motorsports and lifestyle. Lululemon leads in yoga and athleisure, and Champion offers affordable basics.",
        "query": "top sports brands"
    },
    {
        "response": "Nike's Air Max line is popular, but you should also consider Adidas Ultra Boost for comfort. Brooks makes excellent running shoes, and Hoka offers maximum cushioning. Saucony is great for racing, while Mizuno provides stability options.",
        "query": "running shoe recommendations"
    }
]

def test_nike_competitor_discovery():
    print("Testing Nike competitor discovery...")
    print("=" * 50)
    
    extractor = DynamicBrandExtractor("Nike", "fitness")
    all_competitors = {}
    
    for i, test in enumerate(test_responses):
        print(f"\nTest {i+1}: {test['query']}")
        print("-" * 30)
        
        brands = extractor.extract_brands_from_response(test['response'], test['query'])
        
        for brand, mentions in brands.items():
            if brand.lower() != "nike":
                if brand not in all_competitors:
                    all_competitors[brand] = []
                all_competitors[brand].extend(mentions)
        
        print(f"Found brands: {list(brands.keys())}")
    
    print("\n" + "=" * 50)
    print("SUMMARY: All Discovered Competitors")
    print("=" * 50)
    
    for brand, mentions in sorted(all_competitors.items()):
        total_confidence = sum(m.confidence for m in mentions)
        avg_confidence = total_confidence / len(mentions)
        print(f"{brand}: {len(mentions)} mentions, avg confidence: {avg_confidence:.2f}")
        
        # Show sample contexts
        for mention in mentions[:2]:  # Show first 2 mentions
            print(f"  → {mention.mention_type}: '{mention.context[:60]}...'")
    
    # Test the get_top_competitors method
    print("\n" + "=" * 50)
    print("TOP COMPETITORS (using get_top_competitors)")
    print("=" * 50)
    
    top_competitors = extractor.get_top_competitors(test_responses, top_n=5)
    for i, comp in enumerate(top_competitors, 1):
        print(f"{i}. {comp['name']}: {comp['mention_count']} mentions, score: {comp['mention_score']:.2f}")

if __name__ == "__main__":
    test_nike_competitor_discovery()