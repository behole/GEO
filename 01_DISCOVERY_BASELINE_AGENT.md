# Discovery Baseline Agent - Technical Specification

## Agent Overview
The Discovery Baseline Agent establishes your current position in AI-powered search results by systematically querying multiple AI engines with relevant mineral sunscreen queries.

## Core Architecture

### API Integration Strategy
```python
# Async API clients for concurrent execution
- OpenAI Client (GPT-4, GPT-3.5)
- Anthropic Client (Claude)  
- Google AI Client (Gemini)
- Perplexity Client (if available)
```

### Query Execution Flow
1. **Load Query Matrix** → Structured list of 50+ queries
2. **Parallel API Calls** → Execute across all AI engines simultaneously
3. **Response Analysis** → Parse citations, context, competitor mentions
4. **Score Calculation** → Generate baseline metrics
5. **Data Export** → JSON/CSV for dashboard integration

## Query Matrix for Mineral Sunscreen

### Category 1: Direct Product Discovery (15 queries)
```
"best mineral sunscreen 2024"
"top rated zinc oxide sunscreen"
"mineral powder sunscreen recommendations"
"best reef safe sunscreen"
"dermatologist recommended mineral sunscreen"
"best mineral sunscreen for face"
"high SPF mineral sunscreen"
"mineral sunscreen for sensitive skin"
"best chemical free sunscreen"
"organic mineral sunscreen brands"
"luxury mineral sunscreen products"
"affordable mineral sunscreen options"
"travel size mineral sunscreen"
"waterproof mineral sunscreen"
"tinted mineral sunscreen powder"
```

### Category 2: Problem-Solution Queries (12 queries)
```
"mineral sunscreen that doesn't leave white cast"
"sunscreen for acne prone skin mineral"
"mineral sunscreen for dark skin tones"
"non greasy mineral sunscreen"
"mineral sunscreen for kids sensitive skin"
"sunscreen that won't clog pores mineral"
"mineral sunscreen for rosacea"
"hypoallergenic mineral sunscreen"
"fragrance free mineral sunscreen"
"mineral sunscreen for eczema"
"pregnancy safe mineral sunscreen"
"mineral sunscreen for oily skin"
```

### Category 3: Application & Usage (10 queries)
```
"how to apply powder sunscreen correctly"
"powder sunscreen over makeup tutorial"
"reapplying powder sunscreen during day"
"setting powder with SPF vs sunscreen"
"mineral sunscreen application tips"
"how much powder sunscreen to use"
"powder sunscreen for touch ups"
"layering mineral sunscreen with skincare"
"mineral sunscreen under foundation"
"best way to blend powder sunscreen"
```

### Category 4: Ingredient & Science (8 queries)
```
"zinc oxide vs titanium dioxide sunscreen"
"nano vs non nano mineral sunscreen"
"mineral sunscreen ingredients to avoid"
"how does zinc oxide sunscreen work"
"titanium dioxide safety in sunscreen"
"mineral sunscreen chemical composition"
"SPF ratings mineral vs chemical"
"UV protection mineral sunscreen science"
```

### Category 5: Comparison Shopping (5 queries)
```
"mineral vs chemical sunscreen pros cons"
"powder vs cream mineral sunscreen"
"drugstore vs luxury mineral sunscreen"
"Korean vs American mineral sunscreen"
"mineral sunscreen vs BB cream SPF"
```

## Data Collection Schema

### Response Analysis Structure
```json
{
  "query": "best mineral sunscreen 2024",
  "ai_engine": "gpt-4",
  "timestamp": "2024-08-14T10:30:00Z",
  "response_text": "...",
  "citations": [
    {
      "brand": "your_brand",
      "product": "mineral powder sunscreen",
      "context": "recommended for sensitive skin",
      "position": 2,
      "sentiment": "positive"
    }
  ],
  "competitors_mentioned": ["brand_a", "brand_b"],
  "total_brands_mentioned": 5,
  "your_brand_mentioned": true,
  "mention_context": "positive_recommendation"
}
```

### Scoring Algorithms

#### Discovery Score (0-100)
```python
discovery_score = (
    (queries_with_citations / total_queries) * 50 +
    (average_citation_position / total_citations) * 30 +
    (positive_context_ratio) * 20
)
```

#### Context Quality Score (0-100)
```python
context_score = (
    (positive_mentions / total_mentions) * 60 +
    (product_specific_mentions / brand_mentions) * 25 +
    (detailed_mentions / brief_mentions) * 15
)
```

#### Competitive Position Score (0-100)
```python
competitive_score = (
    (queries_where_youre_first / queries_with_citations) * 50 +
    (your_mentions / total_competitor_mentions) * 30 +
    (unique_queries_only_you / total_queries) * 20
)
```

## Technical Implementation

### Claude Code Integration Points
```python
# Entry point for Claude Code orchestration
async def run_discovery_baseline():
    """
    Main function called by Claude Code orchestrator
    Returns: Discovery baseline results + scores
    """
    
# Modular functions for specific tasks
async def query_all_engines(query_matrix)
async def analyze_responses(raw_responses)  
async def calculate_baseline_scores(analyzed_data)
async def generate_report(scores, insights)
```

### Error Handling Strategy
- **API Rate Limits:** Exponential backoff with jitter
- **Failed Queries:** Retry up to 3 times, then skip
- **Partial Failures:** Continue execution, report missing data
- **Data Validation:** Schema validation for all API responses

### Performance Optimization
- **Concurrent Execution:** Max 5 simultaneous API calls per engine
- **Caching:** Store responses locally to avoid re-querying
- **Batching:** Group similar queries for efficiency
- **Timeouts:** 30-second timeout per API call

## Output Format

### JSON Export
```json
{
  "baseline_date": "2024-08-14",
  "query_matrix_size": 50,
  "engines_tested": ["gpt-4", "claude", "gemini"],
  "overall_scores": {
    "discovery_score": 23,
    "context_score": 67,
    "competitive_position": 15
  },
  "detailed_results": [...],
  "recommendations": [...]
}
```

### Dashboard Integration
- **CSV Export:** For spreadsheet analysis
- **API Endpoint:** For real-time dashboard updates
- **Slack Alerts:** For significant changes/insights

## Success Criteria
- **Execution Time:** Complete 50 queries across 3 engines in <10 minutes
- **Data Quality:** 95%+ successful API response rate
- **Actionability:** Clear next steps for content optimization
- **Repeatability:** Consistent results for baseline comparison

---

*Ready for implementation with Claude Code orchestration*
