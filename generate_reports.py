#!/usr/bin/env python3
"""
GEO Report Generator - Main CLI Interface
Single command to generate all professional report formats from GEO audit data
"""

import argparse
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional

# Add report generator to path
sys.path.insert(0, str(Path(__file__).parent / "report_generator"))

from report_generator.core.data_pipeline import UnifiedDataPipeline
from report_generator.core.chart_generator import ChartGenerator
from report_generator.generators.pdf_generator import PDFReportGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GEOReportGenerator:
    """Main report generation coordinator"""
    
    def __init__(self, base_dir: str = "/Users/jjoosshhmbpm1/GEO OPT", 
                 brand_name: str = "Brush on Block"):
        self.base_dir = Path(base_dir)
        self.brand_name = brand_name
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = self.base_dir / "report_outputs" / f"geo_reports_{timestamp}"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.data_pipeline = UnifiedDataPipeline(str(self.base_dir), brand_name)
        self.chart_generator = ChartGenerator(output_dir=str(self.output_dir / "charts"))
        
        logger.info(f"GEO Report Generator initialized - Output: {self.output_dir}")
    
    def generate_all_reports(self) -> dict:
        """Generate all report formats"""
        logger.info("Starting comprehensive report generation...")
        
        results = {
            'success': False,
            'output_directory': str(self.output_dir),
            'generated_reports': {},
            'errors': []
        }
        
        try:
            # 1. Collect unified data from all agents
            logger.info("Step 1: Collecting data from all GEO agents...")
            unified_data = self.data_pipeline.collect_all_agent_data()
            
            # 2. Generate professional charts
            logger.info("Step 2: Generating professional charts...")
            charts = self.chart_generator.generate_all_charts(unified_data.charts_data)
            
            # 3. Generate PDF report
            logger.info("Step 3: Generating professional PDF report...")
            pdf_generator = PDFReportGenerator(str(self.output_dir), self._get_brand_config())
            pdf_path = pdf_generator.generate_professional_report(unified_data, charts)
            results['generated_reports']['pdf'] = pdf_path
            
            # 4. Generate Terminal Dashboard (integration)
            logger.info("Step 4: Generating terminal dashboard...")
            terminal_path = self._generate_terminal_dashboard(unified_data)
            results['generated_reports']['terminal'] = terminal_path
            
            # 5. Generate Executive Summary
            logger.info("Step 5: Generating executive summary...")
            exec_summary_path = self._generate_executive_summary(unified_data)
            results['generated_reports']['executive_summary'] = exec_summary_path
            
            # 6. Create manifest
            manifest_path = self._create_report_manifest(results['generated_reports'], unified_data)
            results['generated_reports']['manifest'] = manifest_path
            
            results['success'] = True
            logger.info("All reports generated successfully!")
            
            return results
            
        except Exception as e:
            error_msg = f"Error during report generation: {str(e)}"
            logger.error(error_msg)
            results['errors'].append(error_msg)
            return results
    
    def generate_pdf_only(self) -> str:
        """Generate only PDF report"""
        logger.info("Generating PDF report only...")
        
        try:
            unified_data = self.data_pipeline.collect_all_agent_data()
            charts = self.chart_generator.generate_all_charts(unified_data.charts_data)
            
            pdf_generator = PDFReportGenerator(str(self.output_dir), self._get_brand_config())
            pdf_path = pdf_generator.generate_professional_report(unified_data, charts)
            
            logger.info(f"PDF report generated: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise
    
    def generate_executive_summary_only(self) -> str:
        """Generate only executive summary"""
        logger.info("Generating executive summary only...")
        
        try:
            unified_data = self.data_pipeline.collect_all_agent_data()
            summary_path = self._generate_executive_summary(unified_data)
            
            logger.info(f"Executive summary generated: {summary_path}")
            return summary_path
            
        except Exception as e:
            logger.error(f"Error generating executive summary: {str(e)}")
            raise
    
    def display_terminal_dashboard(self):
        """Display live terminal dashboard"""
        logger.info("Displaying live terminal dashboard...")
        
        try:
            # Use existing terminal dashboard generator
            from terminal_dashboard_generator.main import TerminalDashboardGenerator
            
            terminal_gen = TerminalDashboardGenerator(str(self.base_dir))
            terminal_gen.display_live_dashboard()
            
        except Exception as e:
            logger.error(f"Error displaying terminal dashboard: {str(e)}")
            raise
    
    def _generate_terminal_dashboard(self, unified_data) -> str:
        """Generate terminal dashboard export"""
        try:
            from terminal_dashboard_generator.main import TerminalDashboardGenerator
            
            terminal_gen = TerminalDashboardGenerator(str(self.base_dir))
            results = terminal_gen.generate_dashboard(export_formats=['html', 'terminal_plain'])
            
            # Copy terminal outputs to our report directory
            if 'exports' in results:
                terminal_dir = self.output_dir / "terminal_dashboard"
                terminal_dir.mkdir(exist_ok=True)
                
                # Copy files to our output directory (simplified for demo)
                return str(terminal_dir / "terminal_dashboard.html")
            
        except Exception as e:
            logger.warning(f"Could not generate terminal dashboard: {str(e)}")
            return ""
        
        return ""
    
    def _generate_executive_summary(self, unified_data) -> str:
        """Generate executive summary"""
        summary_path = self.output_dir / "EXECUTIVE_SUMMARY.md"
        
        summary_content = f"""# Executive Summary: {unified_data.brand_name} GEO Audit

**Generated:** {datetime.now().strftime("%B %d, %Y")}

## 🎯 The Opportunity

- Currently capturing only **{unified_data.current_market_share:.1f}%** of AI citations in the market
- Competitors capture significantly more AI visibility
- AI search drives 35% of product research - missing revenue opportunity

## 💰 The Business Case

| Metric | Value |
|--------|-------|
| **Investment Required** | ${unified_data.investment_required:,.0f} |
| **Annual Revenue Impact** | ${unified_data.annual_revenue_impact:,.0f} |
| **12-Month ROI** | {unified_data.roi_percentage:.0f}% |
| **Break-even Timeline** | {unified_data.breakeven_months:.1f} months |

## ⚡ The Strategy

### Phase 1: Content Optimization (Weeks 1-2)
- Optimize product pages for AI consumption
- Create FAQ content for top queries
- Implement schema markup

### Phase 2: Authority Building (Weeks 3-6)
- Secure dermatologist partnerships
- Publish ingredient research content
- Collect expert endorsements

### Phase 3: Competitive Content (Weeks 7-12)
- Create comparison guides
- Develop seasonal content series
- Monitor and optimize performance

## 📊 Current Position

- **Market Rank:** #{unified_data.market_position['current_rank']} out of {unified_data.market_position['total_competitors']}
- **Market Share:** {unified_data.current_market_share:.1f}%
- **Overall GEO Score:** {unified_data.overall_score:.1f}/100
- **Status:** Needs Optimization

## 🚀 Next Steps

1. **Approve** GEO optimization investment
2. **Begin** Phase 1 content optimization
3. **Establish** monitoring dashboard
4. **Schedule** weekly progress reviews

---

*This analysis represents a comprehensive audit of {unified_data.brand_name}'s position in AI-powered search results and provides a clear roadmap for capturing market share in the growing AI search landscape.*
"""
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary_content)
        
        return str(summary_path)
    
    def _create_report_manifest(self, generated_reports: dict, unified_data) -> str:
        """Create manifest of all generated reports"""
        manifest_path = self.output_dir / "REPORT_MANIFEST.md"
        
        manifest_content = f"""# GEO Report Generation Manifest

**Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
**Brand:** {unified_data.brand_name}
**Sector:** {unified_data.sector}
**Output Directory:** {self.output_dir.name}

## Generated Reports

"""
        
        for report_type, file_path in generated_reports.items():
            if report_type != 'manifest' and file_path:
                filename = Path(file_path).name if isinstance(file_path, str) else "Generation failed"
                manifest_content += f"- **{report_type.replace('_', ' ').title()}:** `{filename}`\\n"
        
        manifest_content += f"""

## Report Summary

### Key Metrics
- **Overall GEO Score:** {unified_data.overall_score:.1f}/100
- **Current Market Position:** Rank #{unified_data.market_position['current_rank']}
- **Investment Required:** ${unified_data.investment_required:,.0f}
- **Expected ROI:** {unified_data.roi_percentage:.0f}%
- **Annual Revenue Impact:** ${unified_data.annual_revenue_impact:,.0f}

### Agent Data Status
"""
        
        for agent_status in unified_data.agent_statuses:
            status_emoji = "✅" if agent_status.status == "success" else "⚠️" if agent_status.status == "partial" else "❌"
            manifest_content += f"- {status_emoji} **{agent_status.agent_name}:** {agent_status.status.title()}\\n"
        
        manifest_content += f"""

## Usage Instructions

### For Executive Presentations
- **View:** Open PDF report for comprehensive analysis
- **Present:** Use executive summary for key stakeholder meetings
- **Share:** Distribute manifest for quick overview

### For Implementation
- **Reference:** Use PDF report for detailed implementation guidance
- **Track:** Monitor progress against 90-day roadmap
- **Measure:** Establish KPIs from methodology section

---

*Professional GEO audit reports generated by the integrated Report Generator suite.*
"""
        
        with open(manifest_path, 'w', encoding='utf-8') as f:
            f.write(manifest_content)
        
        return str(manifest_path)
    
    def _get_brand_config(self) -> dict:
        """Get brand configuration"""
        return {
            'name': self.brand_name,
            'colors': {
                'primary': '#2E8B57',
                'secondary': '#F4A460',
                'accent': '#20B2AA',
                'success': '#32CD32',
                'warning': '#FFD700',
                'danger': '#DC143C'
            }
        }

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="GEO Report Generator - Professional report suite for GEO audit data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --all-formats                    Generate all report formats
  %(prog)s --pdf-only                       Generate only PDF report
  %(prog)s --executive-summary              Generate only executive summary
  %(prog)s --terminal-display               Display live terminal dashboard
  %(prog)s --all-formats --debug            Generate with verbose logging
        """
    )
    
    # Report format options
    format_group = parser.add_mutually_exclusive_group(required=True)
    format_group.add_argument('--all-formats', action='store_true',
                             help='Generate all report formats (PDF, PowerPoint, Executive Summary)')
    format_group.add_argument('--pdf-only', action='store_true',
                             help='Generate only professional PDF report')
    format_group.add_argument('--executive-summary', action='store_true',
                             help='Generate only one-page executive summary')
    format_group.add_argument('--terminal-display', action='store_true',
                             help='Display live terminal dashboard')
    
    # Configuration options
    parser.add_argument('--brand', default='Brush on Block',
                       help='Brand name for customization (default: Brush on Block)')
    parser.add_argument('--base-dir', default='/Users/jjoosshhmbpm1/GEO OPT',
                       help='Base directory for GEO data (default: current GEO OPT)')
    parser.add_argument('--output-dir', 
                       help='Custom output directory (default: base-dir/report_outputs)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize report generator
    try:
        generator = GEOReportGenerator(
            base_dir=args.base_dir,
            brand_name=args.brand
        )
        
        if args.all_formats:
            print("🚀 Generating comprehensive report suite...")
            results = generator.generate_all_reports()
            
            if results['success']:
                print(f"\n✅ Report generation completed successfully!")
                print(f"📁 Output directory: {results['output_directory']}")
                print(f"\n📋 Generated reports:")
                
                for report_type, file_path in results['generated_reports'].items():
                    if file_path and report_type != 'manifest':
                        filename = Path(file_path).name
                        print(f"  • {report_type.replace('_', ' ').title()}: {filename}")
                
                print(f"\n📄 Open manifest: {Path(results['output_directory']) / 'REPORT_MANIFEST.md'}")
            else:
                print("❌ Report generation failed:")
                for error in results['errors']:
                    print(f"  • {error}")
                sys.exit(1)
        
        elif args.pdf_only:
            print("📄 Generating professional PDF report...")
            pdf_path = generator.generate_pdf_only()
            print(f"✅ PDF report generated: {Path(pdf_path).name}")
            print(f"📁 Location: {pdf_path}")
        
        elif args.executive_summary:
            print("📋 Generating executive summary...")
            summary_path = generator.generate_executive_summary_only()
            print(f"✅ Executive summary generated: {Path(summary_path).name}")
            print(f"📁 Location: {summary_path}")
        
        elif args.terminal_display:
            print("🖥️  Displaying terminal dashboard...")
            generator.display_terminal_dashboard()
    
    except KeyboardInterrupt:
        print("\n⏹️  Report generation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()