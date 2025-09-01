# GEO Optimization Reports

This directory contains the output from the GEO (Generative Engine Optimization) system's analysis agents.

## Directory Structure

The reports are organized by agent type and timestamp for easy navigation:

### Current Reports (Most Recent)

Use these symlinks to quickly access the latest reports:

- **`latest_discovery/`** → Latest Discovery Baseline Agent results
- **`latest_content_analysis/`** → Latest Content Analysis Agent results  
- **`latest_competitive_intelligence/`** → Latest Competitive Intelligence Agent results
- **`latest_monitoring/`** → Latest Monitoring & Alerting Agent results

### Historical Reports

Historical timestamped folders are kept for comparison:

- **`discovery_baseline_YYYYMMDD_HHMMSS/`** - Discovery baseline analysis results
- **`content_analysis_YYYYMMDD_HHMMSS/`** - Content analysis and recommendations
- **`competitive_intelligence_YYYYMMDD_HHMMSS/`** - Competitive intelligence reports
- **`monitoring_run_YYYYMMDD_HHMMSS/`** - Monitoring and alerting results

### Special Folders

- **`dashboards/`** - Interactive HTML dashboards and visualizations
- **`agent_feedback/`** - Agent performance feedback and metrics

### Database Files

- **`business_impact.db`** - Business impact tracking database
- **`monitoring_data.db`** - Monitoring system database

## Report Types

### Discovery Baseline Reports
- `complete_results.json` - Complete analysis results
- `summary_results.json` - Executive summary  
- `competitor_analysis.csv` - Competitor comparison data
- `scores_summary.csv` - Scoring breakdown
- `citations_detail.csv` - Citation analysis

### Content Analysis Reports  
- `EXECUTIVE_SUMMARY.md` - Executive summary report
- `brand_content_analysis.json` - Detailed content analysis
- `competitive_benchmarking.csv` - Competitive benchmarking data
- `action_plan_recommendations.csv` - Actionable recommendations
- `page_scores_detailed.csv` - Page-by-page scoring

### Competitive Intelligence Reports
- `COMPETITIVE_INTELLIGENCE_SUMMARY.md` - Executive summary
- `competitor_analysis_summary.json` - Competitor analysis data
- `market_opportunities_report.md` - Market opportunities
- `tactical_recommendations.csv` - Tactical recommendations

### Monitoring Reports
- `MONITORING_EXECUTIVE_SUMMARY.md` - Executive summary
- `monitoring_complete.json` - Complete monitoring data  
- `alerts_summary.csv` - Alerts and notifications

## Usage Tips

1. **Always start with the `latest_*` symlinks** to get the most recent data
2. **Check the EXECUTIVE_SUMMARY.md files** for quick overviews
3. **Use the CSV files** for data analysis and spreadsheet import
4. **Check timestamps** in folder names to understand when analyses were run
5. **Compare historical reports** to track progress over time

## Maintenance

The system includes automatic cleanup to:
- Keep only the 2 most recent reports of each type
- Remove reports older than 30 days automatically  
- Maintain symlinks to the latest reports
- Clean up obsolete database files

Run `python cleanup_reports.py --help` for manual cleanup options.

## Report Status

- ✅ **Fixed**: Brand names now correctly reflect the target brand instead of hardcoded defaults
- ✅ **Cleaned**: Old duplicate reports have been removed to reduce clutter
- ✅ **Organized**: Symlinks created for easy access to latest reports
- ✅ **Documented**: This README provides clear guidance for navigating reports

Last updated: 2025-08-31