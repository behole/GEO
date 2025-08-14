# GEO Audit Agent System - Master Plan

## Project Overview
Building a multi-agent system to audit and optimize mineral powder sunscreen e-commerce site for Generative Engine Optimization (GEO) - optimizing for AI-powered search engines and chatbots.

## Architecture: Multi-Agent System with Claude Code Orchestration

### Agent Structure
```
Master Orchestrator (Claude Code)
├── Agent 1: Discovery Baseline Agent
├── Agent 2: Content Analysis Agent  
├── Agent 3: Competitive Intelligence Agent
└── Agent 4: Monitoring & Alerting Agent
```

## Phase 1: Discovery Baseline Agent (CURRENT FOCUS)

### Purpose
Establish current baseline of how AI engines cite and recommend your mineral sunscreen products across relevant queries.

### Core Functions
1. **Query Matrix Execution**
   - Test 50+ relevant sunscreen queries across multiple AI engines
   - Track citation frequency, context, and positioning
   - Map current brand/product visibility

2. **AI Engine Coverage**
   - ChatGPT/OpenAI API
   - Claude API (Anthropic)
   - Perplexity API
   - Google Gemini API
   - (Optional) Local models via Ollama

3. **Data Collection Points**
   - Citation frequency per query
   - Context of mentions (positive/neutral/negative)
   - Competitor comparison presence
   - Product-specific vs brand-level mentions
   - Query category performance

### Technical Implementation for Claude Code
- **Language:** Python with async/await for concurrent API calls
- **Dependencies:** `aiohttp`, `anthropic`, `openai`, `google-generativeai`
- **Rate Limiting:** Built-in throttling for each API
- **Error Handling:** Retry logic with exponential backoff
- **Output:** JSON + CSV for easy dashboard integration

### Scoring Framework
- **Discovery Score (0-100):** Overall citation frequency across all queries
- **Context Score (0-100):** Quality and relevance of mentions
- **Coverage Score (0-100):** Breadth across different query types
- **Competitive Position (0-100):** Performance vs competitors

## Query Categories for Mineral Sunscreen

### Primary Categories (High Volume)
1. **Product Discovery**
   - "best mineral sunscreen 2024"
   - "zinc oxide sunscreen recommendations"
   - "powder sunscreen for sensitive skin"

2. **Problem-Solution**
   - "sunscreen that doesn't leave white cast"
   - "reef safe sunscreen options"
   - "mineral sunscreen for acne prone skin"

3. **Application & Usage**
   - "how to apply powder sunscreen"
   - "powder sunscreen over makeup"
   - "reapplying sunscreen throughout day"

4. **Ingredient Focused**
   - "zinc oxide vs titanium dioxide"
   - "non nano mineral sunscreen"
   - "chemical free sunscreen ingredients"

5. **Comparison Queries**
   - "mineral vs chemical sunscreen"
   - "powder vs cream sunscreen"
   - "best drugstore mineral sunscreen"

## Next Phase Preview

### Agent 2: Content Analysis Agent
- Analyze current product pages for GEO optimization
- Score content depth, structure, and citation-worthiness
- Identify content gaps and optimization opportunities

### Agent 3: Competitive Intelligence Agent
- Monitor competitor citations across same query set
- Track content strategies that AI engines prefer
- Identify market positioning opportunities

### Agent 4: Monitoring & Alerting Agent
- Continuous tracking post-optimization
- Alert system for ranking changes
- Performance trend analysis

## Success Metrics
- **Baseline:** Current citation frequency across query matrix
- **Target:** 40% increase in relevant AI citations within 90 days
- **Leading Indicators:** Content optimization scores, new query coverage
- **Business Impact:** AI-driven traffic → conversion tracking

## Timeline
- **Week 1:** Discovery Baseline Agent development & testing
- **Week 2:** Content Analysis Agent + initial baseline run
- **Week 3:** Competitive Intelligence Agent + master orchestrator
- **Week 4:** Monitoring system + dashboard setup
- **Ongoing:** Monthly optimization cycles

## Technical Stack
- **Orchestration:** Claude Code
- **Language:** Python 3.11+
- **APIs:** OpenAI, Anthropic, Google AI, Perplexity
- **Data Storage:** SQLite → PostgreSQL (as needed)
- **Dashboard:** Streamlit or FastAPI + React
- **Monitoring:** Custom alerts + Slack integration

---

*Next Steps: Implement Discovery Baseline Agent with detailed query matrix*
