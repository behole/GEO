# Report Generator Architecture Plan

## Integration Strategy

### Current Architecture
```
GEO OPT/
├── discovery_baseline_agent/      # Agent 1
├── content_analysis_agent/        # Agent 2  
├── competitive_intelligence_agent/ # Agent 3
├── monitoring_alerting_agent/     # Agent 4
└── terminal_dashboard_generator/  # Terminal Reports
```

### New Architecture with Report Generator
```
GEO OPT/
├── discovery_baseline_agent/      # Agent 1
├── content_analysis_agent/        # Agent 2
├── competitive_intelligence_agent/ # Agent 3
├── monitoring_alerting_agent/     # Agent 4
├── terminal_dashboard_generator/  # Terminal Reports
├── report_generator/              # NEW: Professional Report Suite
│   ├── __init__.py
│   ├── main.py                    # CLI entry point
│   ├── config/                    # Brand & sector configurations
│   │   ├── brands/
│   │   │   ├── brush_on_block.yaml
│   │   │   ├── default.yaml
│   │   │   └── template.yaml
│   │   └── sectors/
│   │       ├── beauty_sunscreen.yaml
│   │       ├── healthcare.yaml
│   │       └── default.yaml
│   ├── core/                      # Core report generation
│   │   ├── __init__.py
│   │   ├── data_pipeline.py       # Unified data aggregation
│   │   ├── chart_generator.py     # Professional charts/graphs
│   │   ├── template_engine.py     # Brand/sector templating
│   │   └── export_coordinator.py  # Multi-format exports
│   ├── generators/                # Format-specific generators
│   │   ├── __init__.py
│   │   ├── pdf_generator.py       # Professional 12-page PDF
│   │   ├── powerpoint_generator.py # 8-10 slide presentations
│   │   ├── executive_summary.py   # One-page summaries
│   │   └── terminal_integration.py # Terminal dashboard wrapper
│   ├── templates/                 # Report templates
│   │   ├── pdf/
│   │   │   ├── default_template.html
│   │   │   └── brand_templates/
│   │   ├── powerpoint/
│   │   │   ├── default_template.pptx
│   │   │   └── brand_templates/
│   │   └── executive/
│   │       ├── default_summary.md
│   │       └── brand_templates/
│   └── outputs/                   # Generated reports directory
│       └── [timestamped_folders]/
└── generate_reports.py            # NEW: Main CLI interface
```

## Report Generator Components

### 1. Data Pipeline (`core/data_pipeline.py`)
- **Unified Agent Integration**: Single interface to all 4 agents
- **Data Validation**: Ensures data quality and completeness
- **Fallback Handling**: Graceful degradation when agent data missing
- **Caching**: Avoid re-processing during multi-format generation

### 2. Chart Generator (`core/chart_generator.py`)
- **Professional Charts**: matplotlib/plotly integration
- **GEO Score Visualizations**: Progress bars, radar charts
- **Competitive Analysis**: Market share pie charts, ranking tables
- **ROI Projections**: Timeline charts, financial projections
- **Brand Consistency**: Configurable colors, fonts, styling

### 3. Template Engine (`core/template_engine.py`)
- **Brand Customization**: Logo, colors, fonts, messaging
- **Sector Adaptation**: Industry-specific terminology and benchmarks
- **Multi-language Support**: Template localization capability
- **Dynamic Content**: Data-driven section generation

### 4. Export Coordinator (`core/export_coordinator.py`)
- **Format Orchestration**: Single command → all formats
- **Dependency Management**: Handle missing libraries gracefully
- **Output Organization**: Consistent directory structure
- **Manifest Generation**: Track all generated files

## Report Formats

### 1. Professional PDF Report (12 pages)
```
Page 1:  Executive Summary & Key Metrics
Page 2:  Current GEO Position Analysis
Page 3:  Competitive Landscape Overview
Page 4:  Market Opportunities Matrix
Page 5:  ROI Projections & Business Case
Page 6:  Implementation Roadmap
Page 7:  Agent 1 - Discovery Baseline Details
Page 8:  Agent 2 - Content Analysis Details  
Page 9:  Agent 3 - Competitive Intelligence Details
Page 10: Agent 4 - Monitoring & Alerts Details
Page 11: Technical Methodology & Data Sources
Page 12: Appendix & Next Steps
```

### 2. PowerPoint Presentation (8-10 slides)
```
Slide 1: Title & Executive Summary
Slide 2: The Opportunity (Market Position)
Slide 3: Competitive Analysis
Slide 4: ROI Projection & Business Case
Slide 5: Strategic Recommendations
Slide 6: Implementation Timeline
Slide 7: Success Metrics & KPIs
Slide 8: Next Steps & Approval Request
Slide 9: Appendix - Technical Details (optional)
Slide 10: Questions & Discussion (optional)
```

### 3. One-Page Executive Summary
- **Business Problem**: Current position vs opportunity
- **Recommended Solution**: 3-phase implementation strategy
- **Financial Impact**: Investment required vs expected returns
- **Timeline**: 90-day roadmap with key milestones
- **Success Metrics**: Measurable outcomes and KPIs

### 4. Terminal Dashboard
- **Live Display**: Real-time ASCII visualization
- **Multiple Exports**: Colored and plain text versions
- **Web Version**: HTML for sharing and browser viewing

## Configuration System

### Brand Configuration (`config/brands/`)
```yaml
# brush_on_block.yaml
brand:
  name: "Brush on Block"
  display_name: "Brush on Block"
  logo_path: "assets/logos/brush_on_block.png"
  
colors:
  primary: "#2E8B57"    # Sea Green
  secondary: "#F4A460"  # Sandy Brown
  accent: "#20B2AA"     # Light Sea Green
  danger: "#DC143C"     # Crimson
  warning: "#FFD700"    # Gold
  success: "#32CD32"    # Lime Green

fonts:
  heading: "Arial Bold"
  body: "Arial"
  monospace: "Courier New"

messaging:
  tagline: "Premium Sunscreen Protection"
  value_proposition: "AI-Powered GEO Optimization for Market Leadership"
  
business_metrics:
  current_aov: 45.0
  conversion_rate: 3.5
  target_growth: 300
```

### Sector Configuration (`config/sectors/`)
```yaml
# beauty_sunscreen.yaml
sector:
  name: "Beauty & Sunscreen"
  industry: "Consumer Goods"
  
benchmarks:
  excellent_score: 80
  good_score: 60
  warning_score: 40
  
terminology:
  citations: "AI Citations"
  queries: "Search Queries"
  competitors: "Brand Competitors"
  
kpis:
  primary: "AI Citation Share"
  secondary: "Market Visibility"
  business: "Revenue Impact"
  
competitive_context:
  market_leaders: ["EltaMD", "Supergoop", "CeraVe"]
  total_market_size: "869 monthly citations"
  growth_rate: "35% AI search adoption"
```

## Command Interface

### Single Command Generation
```bash
# Generate all report formats
python generate_reports.py --all-formats

# Generate specific formats
python generate_reports.py --pdf --powerpoint --executive-summary

# Custom brand and sector
python generate_reports.py --brand brush_on_block --sector beauty_sunscreen --all-formats

# Output to custom directory
python generate_reports.py --all-formats --output-dir /path/to/reports

# Live terminal display
python generate_reports.py --terminal-display

# Debug mode with verbose logging
python generate_reports.py --all-formats --debug
```

### API Integration
```python
from report_generator import ReportGenerator

# Initialize with custom configuration
generator = ReportGenerator(
    brand_config="brush_on_block",
    sector_config="beauty_sunscreen"
)

# Generate all formats
results = generator.generate_all_reports()

# Generate specific format
pdf_path = generator.generate_pdf_report()
ppt_path = generator.generate_powerpoint()
summary_path = generator.generate_executive_summary()
```

## Integration Points

### 1. Agent Data Pipeline
```python
class UnifiedDataPipeline:
    def collect_agent_data(self):
        return {
            'agent1': self.get_discovery_baseline_data(),
            'agent2': self.get_content_analysis_data(), 
            'agent3': self.get_competitive_intelligence_data(),
            'agent4': self.get_monitoring_data()
        }
```

### 2. Existing Terminal Dashboard
```python
# Integrate existing terminal dashboard
from terminal_dashboard_generator import TerminalDashboardGenerator
generator.include_terminal_dashboard = True
```

### 3. Agent Result Processing
```python
# Standardize agent output processing
class AgentResultProcessor:
    def process_agent1_results(self, results_path):
        # Process discovery baseline agent results
        pass
    
    def process_agent2_results(self, results_path):
        # Process content analysis agent results  
        pass
```

## Implementation Phases

### Phase 1: Core Infrastructure (Week 1)
- [ ] Create report_generator module structure
- [ ] Build unified data pipeline
- [ ] Implement configuration system
- [ ] Create chart generation framework

### Phase 2: Report Generators (Week 2)
- [ ] Professional PDF generator with charts
- [ ] PowerPoint presentation generator
- [ ] Enhanced executive summary generator
- [ ] Terminal dashboard integration

### Phase 3: Customization & Templates (Week 3)
- [ ] Brand customization system
- [ ] Sector-specific templates
- [ ] Multi-format template engine
- [ ] Asset management (logos, fonts)

### Phase 4: Integration & Testing (Week 4)
- [ ] CLI interface implementation
- [ ] Agent integration testing
- [ ] End-to-end report generation testing
- [ ] Documentation and examples

## Success Criteria

### Technical Requirements
- Generate all report formats from single command
- Process agent data automatically with fallbacks
- Maintain brand consistency across all formats
- Support multiple sectors and customization

### Business Requirements
- Professional presentation quality suitable for C-level
- Clear ROI justification and competitive positioning
- Actionable recommendations with implementation timeline
- Consistent messaging across all report formats

### Performance Requirements
- Complete report generation in under 2 minutes
- Handle missing agent data gracefully
- Support concurrent report generation
- Maintain data accuracy across all formats

---

*This architecture ensures seamless integration with existing agents while providing professional-grade report generation capabilities for multi-sector GEO audits.*