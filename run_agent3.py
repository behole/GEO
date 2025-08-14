#!/usr/bin/env python3
"""
Agent 3: Competitive Intelligence Agent - Execution Script

Run this script to execute the complete competitive intelligence analysis.
"""

import asyncio
import sys
from pathlib import Path

async def main():
    """Execute competitive intelligence analysis"""
    
    print("🚀 Starting Agent 3: Competitive Intelligence Analysis")
    print("=" * 60)
    print()
    
    try:
        # Import the competitive intelligence agent
        from competitive_intelligence_agent import run_competitive_intelligence
        
        print("⚡ Initializing competitive intelligence analysis...")
        print("   - Analyzing competitor content strategies")
        print("   - Tracking market position intelligence") 
        print("   - Generating strategic insights")
        print("   - Creating actionable recommendations")
        print()
        
        # Run the complete analysis
        print("🔍 Running comprehensive competitive intelligence analysis...")
        results = await run_competitive_intelligence()
        
        print()
        print("✅ Competitive Intelligence Analysis Complete!")
        print("=" * 60)
        print()
        
        # Display key results
        executive_summary = results.get('executive_summary', {})
        competitive_landscape = executive_summary.get('competitive_landscape', {})
        
        print("📊 KEY RESULTS:")
        print(f"   • Competitors Analyzed: {competitive_landscape.get('competitors_analyzed', 'N/A')}")
        print(f"   • Market Leaders: {competitive_landscape.get('market_leaders_identified', 'N/A')}")
        print(f"   • Significant Threats: {competitive_landscape.get('significant_threats', 'N/A')}")
        print(f"   • High Priority Opportunities: {competitive_landscape.get('high_priority_opportunities', 'N/A')}")
        
        print()
        print("📁 RESULTS SAVED TO:")
        print(f"   • Main Report: {Path('./intelligence_results/latest/competitive_intelligence_complete.json').absolute()}")
        print(f"   • Executive Summary: {Path('./intelligence_results/latest/COMPETITIVE_INTELLIGENCE_SUMMARY.md').absolute()}")
        print(f"   • Recommendations: {Path('./intelligence_results/latest/tactical_recommendations.csv').absolute()}")
        
        print()
        print("🎯 NEXT STEPS:")
        critical_recs = results.get('actionable_recommendations', {}).get('critical_priority', [])
        if critical_recs:
            print(f"   • Review {len(critical_recs)} critical priority recommendations")
            print("   • Implement immediate actions within 30 days")
            print("   • Monitor competitive response")
        else:
            print("   • Review detailed analysis in generated reports")
            print("   • Prioritize high-value opportunities")
            print("   • Schedule quarterly competitive analysis")
        
        print()
        print("✨ Competitive intelligence analysis ready for strategic planning!")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during competitive intelligence analysis: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # Run the competitive intelligence analysis
    results = asyncio.run(main())