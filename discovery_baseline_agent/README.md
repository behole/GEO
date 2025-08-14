# Discovery Baseline Agent

A comprehensive AI-powered discovery baseline tool for GEO optimization in the mineral sunscreen market. This agent systematically queries multiple AI engines to establish your current position in AI-powered search results.

## Features

- **Multi-Engine Querying**: Supports OpenAI, Anthropic, and Google AI APIs
- **Comprehensive Query Matrix**: 50+ targeted mineral sunscreen queries across 5 categories
- **Advanced Response Analysis**: Citation extraction, competitor detection, sentiment analysis
- **Scoring Algorithms**: Discovery, Context Quality, and Competitive Position scores
- **Export Capabilities**: JSON and CSV outputs for analysis and dashboard integration
- **Async Execution**: Optimized for concurrent API calls with rate limiting
- **Error Handling**: Robust retry logic and graceful failure handling

## Quick Start

### 1. Installation

```bash
# Clone or navigate to the project directory
cd discovery_baseline_agent

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your API keys
nano .env
```

Required API keys:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key  
- `GOOGLE_AI_API_KEY`: Your Google AI API key

### 3. Test the Setup

```bash
# Run tests to verify installation
python test_agent.py

# Validate configuration
python main.py --validate-only
```

### 4. Run Discovery Baseline

```bash
# Quick test run (5 queries)
python main.py --max-queries 5

# Full baseline run
python main.py

# Specific categories only
python main.py --categories direct_product_discovery problem_solution
```

## Usage Examples

### Command Line Interface

```bash
# List available query categories
python main.py --list-queries

# Run with custom output directory
python main.py --output-dir ./custom_results

# Run with custom run ID
python main.py --run-id baseline_2024_q1

# Validate configuration only
python main.py --validate-only
```

### Programmatic Usage

```python
import asyncio
from main import run_discovery_baseline

async def main():
    # Run discovery baseline programmatically
    result = await run_discovery_baseline(
        query_categories=["direct_product_discovery"],
        max_queries=10,
        output_dir="./results"
    )
    
    if result["success"]:
        print(f"Overall Score: {result['baseline_scores'].overall_score:.1f}/100")
        print(f"Files created: {len(result['files_created'])}")
    else:
        print(f"Error: {result['error']}")

asyncio.run(main())
```

## Query Categories

The agent includes 50+ queries across 5 categories:

1. **Direct Product Discovery** (15 queries)
   - "best mineral sunscreen 2024"
   - "top rated zinc oxide sunscreen"
   - "dermatologist recommended mineral sunscreen"
   - etc.

2. **Problem-Solution** (12 queries)
   - "mineral sunscreen that doesn't leave white cast"
   - "sunscreen for acne prone skin mineral"
   - "mineral sunscreen for dark skin tones"
   - etc.

3. **Application & Usage** (10 queries)
   - "how to apply powder sunscreen correctly"
   - "powder sunscreen over makeup tutorial"
   - etc.

4. **Ingredient & Science** (8 queries)
   - "zinc oxide vs titanium dioxide sunscreen"
   - "nano vs non nano mineral sunscreen"
   - etc.

5. **Comparison Shopping** (5 queries)
   - "mineral vs chemical sunscreen pros cons"
   - "powder vs cream mineral sunscreen"
   - etc.

## Output Files

Each run creates multiple output files:

- `complete_results.json`: Full results with all data
- `summary_results.json`: Summary scores and insights only
- `analyses_summary.csv`: Response analysis summary
- `citations_detail.csv`: Detailed citation information
- `scores_summary.csv`: Score breakdowns
- `competitor_analysis.csv`: Competitor performance analysis
- `export_summary.txt`: Human-readable summary

## Scoring System

### Discovery Score (0-100)
- **Citation Rate** (50%): How often your brand is mentioned
- **Position Quality** (30%): Average position in citations
- **Context Quality** (20%): Positive vs negative mentions

### Context Score (0-100)
- **Sentiment Ratio** (60%): Positive vs negative context
- **Specificity Score** (25%): Product-specific vs brand-only mentions
- **Detail Richness** (15%): Detailed vs brief mentions

### Competitive Score (0-100)
- **First Position Rate** (50%): How often you're mentioned first
- **Market Share** (30%): Your mentions vs competitor mentions
- **Unique Visibility** (20%): Queries where only you appear

## Configuration Options

### Environment Variables

```bash
# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_AI_API_KEY=your_google_ai_key

# Performance Settings
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
RETRY_ATTEMPTS=3

# Output Settings
OUTPUT_DIR=./results
CACHE_RESPONSES=true
```

### Brand Configuration

Edit `response_analyzer.py` to customize brand detection:

```python
# Your brand variations (customize these)
YOUR_BRAND_VARIATIONS = {
    "your brand", "yourbrand", "your-brand"
}
```

## Performance Optimization

- **Concurrent Execution**: Max 5 simultaneous API calls per engine
- **Rate Limiting**: Built-in throttling and exponential backoff
- **Caching**: Optional response caching to avoid re-querying
- **Timeout Handling**: 30-second timeout per API call
- **Error Recovery**: Automatic retry with exponential backoff

## Troubleshooting

### Common Issues

1. **API Key Errors**
   ```bash
   # Verify API keys are set
   python main.py --validate-only
   ```

2. **Rate Limiting**
   - Reduce `MAX_CONCURRENT_REQUESTS` in .env
   - Increase `REQUEST_TIMEOUT` for slower responses

3. **Import Errors**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   ```

### Debug Mode

```bash
# Enable detailed logging
export PYTHONPATH=$PYTHONPATH:$(pwd)
python -c "import logging; logging.basicConfig(level=logging.DEBUG)" main.py
```

## Success Criteria

- **Execution Time**: Complete 50 queries across 3 engines in <10 minutes
- **Data Quality**: 95%+ successful API response rate
- **Actionability**: Clear next steps for content optimization
- **Repeatability**: Consistent results for baseline comparison

## Integration

### Dashboard Integration

The JSON exports are designed for dashboard integration:

```javascript
// Example dashboard integration
fetch('./results/summary_results.json')
  .then(response => response.json())
  .then(data => {
    updateScoreDashboard(data.scores);
    displayInsights(data.insights);
  });
```

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Run Discovery Baseline
  run: |
    python discovery_baseline_agent/main.py --max-queries 10
    # Upload results to dashboard
```

## Development

### Project Structure

```
discovery_baseline_agent/
├── main.py                 # Main orchestration
├── config.py              # Configuration management
├── api_clients.py         # AI API clients
├── query_matrix.py        # Query definitions
├── response_analyzer.py   # Response analysis
├── scoring_engine.py      # Scoring algorithms
├── export_manager.py      # Export functionality
├── test_agent.py          # Test suite
├── requirements.txt       # Dependencies
├── .env.example          # Environment template
└── README.md             # This file
```

### Testing

```bash
# Run test suite
python test_agent.py

# Test individual components
python -c "from query_matrix import QueryMatrix; print(QueryMatrix.validate_queries())"
```

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the test output: `python test_agent.py`
3. Validate configuration: `python main.py --validate-only`
4. Check logs in `discovery_baseline.log`

## License

This project is part of the GEO Optimization suite. See project documentation for licensing details.