# Agent 3: Competitive Intelligence Agent - Technical Specification

## Agent Overview
The Competitive Intelligence Agent monitors and analyzes how competitors perform in AI-powered search results, identifying content strategies and market positioning opportunities that drive better GEO performance.

## Core Architecture

### Integration with Previous Agents
```python
# Data flow integration
discovery_baseline = load_agent1_results()  # Citation performance data
content_analysis = load_agent2_results()    # Content gap analysis
competitor_list = discovery_baseline.top_competitors  # EltaMD, Supergoop, CeraVe, etc.
```

### Primary Functions

#### 1. Competitor Content Strategy Analysis
- **Deep-dive content analysis** of top competitors from Agent 1
- **Content type mapping**: What content formats do AI engines prefer to cite?
- **Authority signal analysis**: How do competitors establish credibility?
- **Citation pattern recognition**: Which content gets cited most frequently?

#### 2. Market Position Tracking
- **Competitive ranking changes** over time in AI responses
- **Market share trends** in AI citations
- **Seasonal performance patterns**
- **Query territory mapping** (which competitors own which query types)

#### 3. Content Strategy Intelligence
- **Content gap opportunities**: Queries where no strong competitor exists
- **Content format preferences**: Lists vs paragraphs vs tables that AI engines favor
- **Authority building tactics**: How competitors earn credible citations
- **Link building and mention strategies**

## Technical Implementation

### Data Sources
```python
# Primary data sources
competitor_websites = extract_from_agent2()
ai_engine_responses = enhance_agent1_queries()
competitor_citations = analyze_citation_context()
content_freshness = track_content_updates()

# Additional intelligence sources
social_mentions = scrape_social_signals()
backlink_profiles = analyze_authority_signals() 
press_mentions = track_media_coverage()
```

### Analysis Algorithms

#### Content Strategy Scoring
```python
def analyze_competitor_content_strategy(competitor):
    return {
        "content_depth_score": calculate_content_depth(),
        "authority_signal_score": measure_credibility_markers(),
        "ai_optimization_score": evaluate_geo_practices(),
        "citation_worthiness_score": assess_quotability(),
        "content_freshness_score": track_update_frequency()
    }
```

#### Market Positioning Analysis
```python
def calculate_competitive_position(competitor):
    return {
        "query_dominance": map_query_territory(),
        "citation_velocity": track_mention_growth(),
        "authority_momentum": measure_credibility_trends(),
        "content_gap_exploitation": identify_opportunities()
    }
```

### Query Enhancement Strategy
- **Expand beyond 50 base queries** from Agent 1
- **Add competitor-specific queries**: "Brand X vs alternatives"
- **Include long-tail variations**: More specific, intent-driven searches
- **Seasonal query adaptation**: Time-sensitive optimization opportunities

## Output Schema

### Competitive Intelligence Report
```json
{
  "analysis_date": "2025-08-14",
  "baseline_period": "30_days",
  "competitive_landscape": {
    "market_leaders": [
      {
        "competitor": "eltamd",
        "market_share": 16.1,
        "citation_velocity": "+12% vs last month",
        "content_strategies": ["expert_endorsements", "clinical_studies", "ingredient_transparency"],
        "ai_optimization_score": 87
      }
    ],
    "emerging_threats": [...],
    "market_opportunities": [...]
  },
  "content_strategy_insights": {
    "high_performing_content_types": ["ingredient_guides", "dermatologist_recommendations"],
    "citation_patterns": {...},
    "authority_building_tactics": [...]
  },
  "actionable_recommendations": [
    {
      "priority": "high",
      "category": "content_creation",
      "recommendation": "Create dermatologist-endorsed ingredient comparison charts",
      "expected_impact": "15-25% citation increase",
      "effort_level": "medium"
    }
  ]
}
```

## Integration Points for Modular Architecture

### Sector Configuration
```yaml
# sector_configs/beauty_sunscreen_competitive.yaml
competitive_analysis:
  focus_competitors: 5
  content_types_to_analyze:
    - "ingredient_pages"
    - "product_comparisons" 
    - "expert_testimonials"
    - "how_to_guides"
  
  authority_signals:
    - "dermatologist_endorsements"
    - "clinical_study_citations"
    - "ingredient_certifications"
    - "award_mentions"
  
  query_extensions:
    - "vs_alternatives"
    - "expert_recommendations"
    - "clinical_studies"
    - "ingredient_comparisons"
```

## Success Metrics

### Intelligence Quality Metrics
- **Insight Actionability**: 90%+ recommendations lead to measurable improvements
- **Competitive Accuracy**: 95%+ accurate competitor performance tracking
- **Opportunity Identification**: Identify 10+ actionable content gaps per analysis

### Business Impact Metrics
- **Market Share Growth**: Track improvement in AI citation market share
- **Competitive Response Time**: Identify competitor moves within 48 hours
- **Strategy Effectiveness**: ROI tracking for implemented recommendations

## Technical Requirements

### Performance Specifications
- **Analysis Depth**: Full competitive analysis in <45 minutes
- **Data Freshness**: Real-time competitive intelligence updates
- **Scalability**: Handle 20+ competitors simultaneously

### Claude Code Integration
```python
# Entry point for orchestration
async def run_competitive_intelligence():
    """
    Main function for Claude Code integration
    Returns: Competitive intelligence insights + strategic recommendations
    """
    
async def analyze_competitor_content_strategies()
async def track_market_position_changes()
async def identify_content_opportunities()
async def generate_strategic_recommendations()
```

## Output for Dashboard Integration

### Key Visualizations
- **Competitive Position Matrix**: Market share vs authority score
- **Content Gap Heatmap**: Opportunities by query category
- **Citation Trend Analysis**: Performance over time
- **Strategy Effectiveness Tracking**: ROI of implemented recommendations

---

*Ready for implementation after Agent 2 completion*
