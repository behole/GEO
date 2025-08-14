# Content Analysis Agent (Agent 2)

## Overview

The Content Analysis Agent is a comprehensive content audit and optimization system designed for Generative Engine Optimization (GEO). It analyzes website content against GEO best practices, performs competitive gap analysis, and provides actionable recommendations for improving AI engine visibility and citation rates.

## Key Features

### 🔍 **Comprehensive Content Analysis**
- **Website Content Scraping**: Intelligent scraping with sitemap parsing, robots.txt analysis, and content prioritization
- **Multi-Dimensional Scoring**: Evaluates content across 4 key dimensions:
  - Content Structure (paragraph/sentence length, heading hierarchy, readability)
  - Citation Worthiness (fact density, source citations, expert authority)
  - Authority Signals (author credentials, publication freshness, external links)
  - AI Consumption Optimization (answer formatting, structured data, voice search)

### 🏆 **Competitive Gap Analysis**
- **Competitor Benchmarking**: Analyzes top competitors' content strategies
- **Gap Identification**: Identifies missing content types, keyword gaps, and feature gaps
- **Opportunity Matrix**: Prioritizes improvements by impact vs effort
- **Market Positioning**: Assesses competitive advantages and disadvantages

### 📊 **Actionable Recommendations**
- **Prioritized Action Plan**: 30-day, 90-day, and annual goals
- **ROI Estimates**: High-impact, low-effort opportunities identification
- **Success Metrics**: Measurable targets and KPI tracking
- **Integration with Agent 1**: Cross-references with baseline discovery results

### 🔧 **Modular Architecture**
- **Sector-Specific Configuration**: YAML-based configuration for different industries
- **Plugin System**: Extensible architecture for new content types and scoring methods
- **Multi-Format Export**: JSON, CSV, and Markdown outputs for different stakeholders

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup
```bash
# Clone or navigate to the content analysis agent directory
cd "/Users/jjoosshhmbpm1/GEO OPT/content_analysis_agent"

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit configuration as needed
nano .env
```

### Configuration

#### Environment Variables (.env)
```bash
# Target Brand Configuration
BRAND_NAME=Brush on Block
BRAND_WEBSITE=https://brushonblock.com
BRAND_VARIATIONS=Brush on Block,Brush On Block,BrushOnBlock,BOB

# Analysis Settings
MAX_CONCURRENT_REQUESTS=5
REQUEST_TIMEOUT=30
MAX_PAGES_PER_SITE=100

# Output Settings
OUTPUT_DIR=./results
ENABLE_SCREENSHOTS=false
SAVE_HTML_CONTENT=true

# Integration with Agent 1
AGENT1_RESULTS_PATH=../discovery_baseline_agent/results/latest/
```

#### Sector Configuration
The agent uses YAML configuration files for sector-specific analysis. The default configuration is for beauty/sunscreen sector:

```yaml
sector: "beauty"
product_type: "mineral_sunscreen"

brand:
  name: "Brush on Block"
  website: "https://brushonblock.com"
  variations: ["Brush on Block", "BOB", "brushonblock"]

competitors:
  primary:
    - name: "EltaMD"
      website: "https://eltamd.com"
      priority: "high"
    - name: "Supergoop"
      website: "https://supergoop.com"
      priority: "high"
```

## Usage

### Command Line Interface

#### Basic Analysis
```bash
# Run full analysis with default settings
python main.py

# Specify maximum pages per site
python main.py --max-pages 50

# Use custom configuration
python main.py --config sector_configs/custom_sector.yaml

# Export specific format
python main.py --export-format json
python main.py --export-format csv
python main.py --export-format both
```

#### Advanced Options
```bash
# Custom output directory
python main.py --output-dir /path/to/results

# Full command with all options
python main.py \
  --config sector_configs/beauty_sunscreen.yaml \
  --max-pages 100 \
  --output-dir ./custom_results \
  --export-format both
```

### Python Integration
```python
from content_analysis_agent.main import ContentAnalysisAgent
import asyncio

async def run_analysis():
    # Initialize agent
    agent = ContentAnalysisAgent()
    
    # Run full analysis
    results = await agent.run_full_analysis(max_pages_per_site=50)
    
    print(f"Overall content health: {results['summary']['overall_content_health']}")
    print(f"Competitive position: {results['summary']['competitive_position']}")
    
    return results

# Run analysis
results = asyncio.run(run_analysis())
```

## Architecture

### Core Components

#### 1. **ContentScraper** (`content_scraper.py`)
- **Async web scraping** with rate limiting and retry logic
- **Intelligent URL discovery** via sitemaps and crawling
- **Content extraction** with multiple parsing strategies
- **Structured data extraction** (JSON-LD, microdata)

#### 2. **ContentScorer** (`content_scorer.py`)
- **Multi-dimensional scoring** against GEO best practices
- **Readability analysis** using multiple metrics
- **Authority signal detection** and quantification
- **AI consumption optimization** scoring

#### 3. **CompetitorAnalyzer** (`competitor_analyzer.py`)
- **Competitive landscape analysis** across multiple dimensions
- **Content gap identification** with priority scoring
- **Feature comparison** and unique capability detection
- **Market positioning** assessment

#### 4. **ExportManager** (`export_manager.py`)
- **Multi-format export** (JSON, CSV, Markdown)
- **Executive summaries** for stakeholder communication
- **Detailed technical reports** for implementation teams

### Data Flow
1. **Configuration Loading**: Sector-specific settings and competitor lists
2. **Brand Analysis**: Comprehensive analysis of target brand's content
3. **Competitive Analysis**: Parallel analysis of top competitors
4. **Gap Identification**: Cross-analysis to identify content and feature gaps
5. **Recommendation Generation**: Prioritized action plans with ROI estimates
6. **Export and Reporting**: Multi-format outputs for different audiences

## Output Files

After running the analysis, you'll find several files in the results directory:

### Executive Level
- **`EXECUTIVE_SUMMARY.md`**: High-level findings and recommendations
- **`export_manifest.json`**: Guide to all generated files

### Technical Analysis
- **`content_analysis_complete.json`**: Complete analysis results
- **`brand_content_analysis.json`**: Brand-specific content analysis
- **`competitive_gap_analysis.json`**: Competitive analysis results
- **`comprehensive_recommendations.json`**: Detailed recommendations

### Actionable Data (CSV)
- **`page_scores_detailed.csv`**: Page-by-page scoring and recommendations
- **`content_gaps_analysis.csv`**: Prioritized content gaps
- **`competitive_benchmarking.csv`**: Competitor comparison data
- **`action_plan_recommendations.csv`**: Timeline-based action items

## Interpretation Guide

### Content Health Scores
- **75-100**: Excellent - Well-optimized for GEO
- **60-74**: Good - Some optimization opportunities
- **40-59**: Fair - Significant improvements needed
- **0-39**: Poor - Comprehensive overhaul required

### Competitive Position
- **Leading**: Outperforming most competitors (+15 points above average)
- **Competitive**: Above average performance
- **Lagging**: Below average but recoverable (-10 points or less)
- **Behind**: Major competitive disadvantage (-10+ points)

### Priority Levels
- **HIGH**: Critical gaps affecting AI visibility
- **MEDIUM**: Important improvements with good ROI
- **LOW**: Nice-to-have optimizations

### Effort Estimates
- **Low**: Can be completed in days with existing resources
- **Medium**: Requires weeks and moderate resource investment
- **High**: Strategic initiatives requiring months and significant resources

## Integration with Agent 1

When Agent 1 (Discovery Baseline Agent) results are available, Agent 2 automatically integrates the data to provide cross-agent insights:

- **Citation Correlation**: Connects content gaps with low citation rates
- **Query Category Analysis**: Identifies content needs based on AI engine performance
- **Integrated Recommendations**: Combines discovery and content insights

## Troubleshooting

### Common Issues

#### 1. **Scraping Failures**
```
Error: High scraping failure rate
Solution: Check robots.txt compliance, reduce MAX_CONCURRENT_REQUESTS, increase REQUEST_TIMEOUT
```

#### 2. **Memory Issues with Large Sites**
```
Error: Out of memory during analysis
Solution: Reduce MAX_PAGES_PER_SITE, disable SAVE_HTML_CONTENT
```

#### 3. **Missing Dependencies**
```
Error: ModuleNotFoundError
Solution: pip install -r requirements.txt
```

#### 4. **Configuration Errors**
```
Error: Sector configuration file not found
Solution: Check path to YAML config file, ensure proper format
```

### Debug Mode
Enable debug logging by setting log level:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Extending the Agent

### Adding New Content Types
1. Update `sector_configs/your_sector.yaml` with new content type
2. Add classification logic in `ContentScraper._classify_content_type()`
3. Update scoring weights and requirements

### Custom Scoring Methods
1. Extend `ContentScorer` class with new scoring methods
2. Update scoring dataclasses with new fields
3. Modify aggregate scoring calculations

### New Sector Configuration
1. Create new YAML file in `sector_configs/`
2. Define sector-specific competitors, keywords, and content types
3. Set appropriate scoring weights and quality benchmarks

## Performance Optimization

### For Large Sites
- Use `--max-pages` to limit analysis scope
- Set `SAVE_HTML_CONTENT=false` to reduce memory usage
- Increase `REQUEST_TIMEOUT` for slow sites

### For Multiple Competitors
- Prioritize competitors by setting `priority: high/medium/low`
- Run analysis during off-peak hours
- Consider running competitors separately for very large analyses

## API Reference

### ContentAnalysisAgent
Main orchestrator class for running complete content analysis.

**Methods:**
- `run_full_analysis(max_pages_per_site: int) -> Dict[str, Any]`
- `_analyze_brand_content(max_pages: int) -> Dict[str, Any]`
- `_run_competitive_analysis(max_pages: int) -> Dict[str, Any]`

### ContentScorer
Comprehensive content scoring against GEO best practices.

**Key Methods:**
- `score_site(site_analysis: SiteAnalysis) -> SiteScore`
- `score_page(page: PageContent) -> PageScore`

### CompetitorAnalyzer
Competitive analysis and gap identification.

**Key Methods:**
- `analyze_competitive_landscape(max_pages_per_site: int) -> ContentGapAnalysis`

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Add tests for new functionality
4. Commit changes (`git commit -am 'Add new feature'`)
5. Push to branch (`git push origin feature/new-feature`)
6. Create Pull Request

## License

This project is part of the GEO Optimization Suite. See main project license for details.

## Support

For issues, questions, or feature requests:
1. Check troubleshooting section above
2. Review existing issues in the project repository
3. Create new issue with detailed description and logs

---

*Content Analysis Agent v1.0.0 - Built for comprehensive GEO optimization and competitive content analysis.*