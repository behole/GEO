#!/usr/bin/env python3
"""
Export Manager for Terminal Dashboard
Handles PDF, HTML, and other format exports for sharing with partners
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import asdict

logger = logging.getLogger(__name__)

class DashboardExportManager:
    """Manages export of terminal dashboard to various formats for sharing"""
    
    def __init__(self, dashboard_instance, output_dir: str = "dashboard_exports"):
        self.dashboard = dashboard_instance
        self.data = dashboard_instance.data
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create timestamped export directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.export_dir = self.output_dir / f"geo_dashboard_{timestamp}"
        self.export_dir.mkdir(exist_ok=True)
        
        logger.info(f"Export manager initialized: {self.export_dir}")
    
    def export_all_formats(self) -> Dict[str, str]:
        """Export dashboard to all available formats"""
        exports = {}
        
        try:
            # Terminal text (colored)
            exports['terminal_colored'] = self.export_terminal_text(colored=True)
            
            # Terminal text (plain)
            exports['terminal_plain'] = self.export_terminal_text(colored=False)
            
            # HTML version
            exports['html'] = self.export_html()
            
            # JSON data
            exports['json'] = self.export_json_data()
            
            # Executive summary
            exports['executive_summary'] = self.export_executive_summary()
            
            # Try PDF export (may fail if dependencies missing)
            try:
                exports['pdf'] = self.export_pdf()
            except Exception as e:
                logger.warning(f"PDF export failed: {str(e)}")
                exports['pdf'] = f"PDF export failed: {str(e)}"
            
            # Create export manifest
            exports['manifest'] = self.create_export_manifest(exports)
            
            logger.info(f"Exported dashboard to {len(exports)} formats")
            return exports
            
        except Exception as e:
            logger.error(f"Error during export: {str(e)}")
            raise
    
    def export_terminal_text(self, colored: bool = True) -> str:
        """Export terminal dashboard as text file"""
        filename = "geo_dashboard_terminal.txt" if not colored else "geo_dashboard_terminal_colored.txt"
        filepath = self.export_dir / filename
        
        if colored:
            # Get colored terminal output
            dashboard_text = self.dashboard.generate_complete_dashboard()
        else:
            # Get plain text version
            dashboard_text = self._get_plain_text_dashboard()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(dashboard_text)
        
        logger.info(f"Terminal text exported: {filepath}")
        return str(filepath)
    
    def export_html(self) -> str:
        """Export dashboard as HTML for web viewing"""
        filename = "geo_dashboard.html"
        filepath = self.export_dir / filename
        
        html_content = self._generate_html_dashboard()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML dashboard exported: {filepath}")
        return str(filepath)
    
    def export_pdf(self) -> str:
        """Export dashboard as PDF (requires additional dependencies)"""
        try:
            # Try to import PDF generation libraries
            from weasyprint import HTML, CSS
            from io import StringIO
            
            filename = "geo_dashboard.pdf"
            filepath = self.export_dir / filename
            
            # Generate HTML content
            html_content = self._generate_pdf_optimized_html()
            
            # Convert to PDF
            HTML(string=html_content).write_pdf(str(filepath))
            
            logger.info(f"PDF dashboard exported: {filepath}")
            return str(filepath)
            
        except ImportError:
            # Fallback: create a simple text-based PDF using reportlab
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.fonts import addMapping
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
                
                filename = "geo_dashboard.pdf"
                filepath = self.export_dir / filename
                
                # Create PDF document
                doc = SimpleDocTemplate(str(filepath), pagesize=letter)
                styles = getSampleStyleSheet()
                
                # Create content
                story = []
                
                # Title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=16,
                    spaceAfter=30,
                    alignment=1  # Center alignment
                )
                
                story.append(Paragraph("Brush on Block - GEO Audit Dashboard", title_style))
                story.append(Spacer(1, 20))
                
                # Add dashboard sections
                plain_dashboard = self._get_plain_text_dashboard()
                
                # Split into sections and add each
                sections = plain_dashboard.split('\\n\\n')
                for section in sections:
                    if section.strip():
                        # Use preformatted text to preserve ASCII formatting
                        story.append(Preformatted(section, styles['Code']))
                        story.append(Spacer(1, 12))
                
                # Build PDF
                doc.build(story)
                
                logger.info(f"PDF dashboard exported (reportlab): {filepath}")
                return str(filepath)
                
            except ImportError:
                raise Exception("PDF export requires 'weasyprint' or 'reportlab' package. Install with: pip install weasyprint reportlab")
    
    def export_json_data(self) -> str:
        """Export raw data as JSON for API integration"""
        filename = "geo_dashboard_data.json"
        filepath = self.export_dir / filename
        
        # Prepare data for JSON export
        export_data = {
            "dashboard_metadata": {
                "brand_name": self.data.brand_name,
                "generated_at": self.data.analysis_timestamp,
                "version": "1.0"
            },
            "scores": asdict(self.data.scores),
            "roi_projection": asdict(self.data.roi_projection),
            "market_position": self.data.market_position,
            "competitors": [asdict(comp) for comp in self.data.competitors],
            "opportunities": [asdict(opp) for opp in self.data.opportunities],
            "key_insights": self.data.key_insights,
            "recommendations": self.data.recommendations,
            "dashboard_metrics": self.dashboard.get_dashboard_metrics()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        logger.info(f"JSON data exported: {filepath}")
        return str(filepath)
    
    def export_executive_summary(self) -> str:
        """Export one-page executive summary"""
        filename = "EXECUTIVE_SUMMARY.md"
        filepath = self.export_dir / filename
        
        summary = self._generate_executive_summary_markdown()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"Executive summary exported: {filepath}")
        return str(filepath)
    
    def create_export_manifest(self, exports: Dict[str, str]) -> str:
        """Create manifest file listing all exports"""
        filename = "EXPORT_MANIFEST.md"
        filepath = self.export_dir / filename
        
        manifest = f"""# GEO Dashboard Export Manifest
        
**Generated:** {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
**Brand:** {self.data.brand_name}
**Export Directory:** {self.export_dir.name}

## Exported Files

"""
        
        for format_name, file_path in exports.items():
            if format_name != 'manifest':  # Don't include self-reference
                filename = Path(file_path).name if isinstance(file_path, str) else "Export failed"
                manifest += f"- **{format_name.replace('_', ' ').title()}:** `{filename}`\\n"
        
        manifest += f"""
## Usage Instructions

### For Executive Presentations
- **View:** Open `geo_dashboard.html` in web browser
- **Print:** Use `geo_dashboard.pdf` for hard copies
- **Share:** Send `EXECUTIVE_SUMMARY.md` for quick overview

### For Technical Integration
- **Data:** Use `geo_dashboard_data.json` for API integration
- **Terminal:** Use `geo_dashboard_terminal.txt` for CLI viewing

### For Partner Meetings
1. Open `geo_dashboard.html` for live presentation
2. Print `geo_dashboard.pdf` for handouts
3. Reference `EXECUTIVE_SUMMARY.md` for talking points

## Key Metrics Summary
- **Current Position:** Rank #{self.data.market_position['current_rank']} with {self.data.market_position['market_share_percentage']:.1f}% market share
- **Investment Required:** ${self.data.roi_projection.implementation_cost:,.0f}
- **Expected ROI:** {self.data.roi_projection.twelve_month_roi:.0f}% in 12 months
- **Revenue Impact:** ${self.data.roi_projection.annual_revenue_impact:,.0f} additional annual revenue
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(manifest)
        
        logger.info(f"Export manifest created: {filepath}")
        return str(filepath)
    
    def _get_plain_text_dashboard(self) -> str:
        """Get dashboard without ANSI color codes"""
        # Temporarily disable colors
        original_colors = self.dashboard._disable_colors()
        dashboard_text = self.dashboard.generate_complete_dashboard()
        self.dashboard._restore_colors(original_colors)
        return dashboard_text
    
    def _generate_html_dashboard(self) -> str:
        """Generate HTML version of the dashboard"""
        roi = self.data.roi_projection
        scores = self.data.scores
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.data.brand_name} - GEO Audit Dashboard</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background-color: #0a0a0a;
            color: #00ff00;
            margin: 0;
            padding: 20px;
            line-height: 1.4;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background-color: #1a1a1a;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }}
        .header {{
            text-align: center;
            border: 2px solid #00ff00;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 5px;
        }}
        .section {{
            margin-bottom: 30px;
            border: 1px solid #333;
            padding: 20px;
            border-radius: 5px;
            background-color: #111;
        }}
        .section-title {{
            color: #00ffff;
            font-weight: bold;
            font-size: 1.2em;
            margin-bottom: 15px;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }}
        .progress-bar {{
            background-color: #333;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin: 5px 0;
        }}
        .progress-fill {{
            height: 100%;
            transition: width 0.3s ease;
        }}
        .score-excellent {{ background-color: #00ff00; }}
        .score-good {{ background-color: #ffff00; }}
        .score-warning {{ background-color: #ff8800; }}
        .score-danger {{ background-color: #ff0000; }}
        .metric-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-item {{
            background-color: #222;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #00ff00;
        }}
        .roi-highlight {{
            background-color: #003300;
            border: 2px solid #00ff00;
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            text-align: center;
        }}
        .roi-value {{
            font-size: 2em;
            color: #00ff00;
            font-weight: bold;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 15px 0;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        th {{
            background-color: #333;
            color: #00ffff;
        }}
        .opportunity-high {{ color: #ff4444; }}
        .opportunity-medium {{ color: #ffaa00; }}
        .opportunity-low {{ color: #00ff00; }}
        .print-friendly {{
            background-color: white !important;
            color: black !important;
        }}
        @media print {{
            body {{ background-color: white; color: black; }}
            .container {{ background-color: white; box-shadow: none; }}
            .section {{ background-color: white; border-color: black; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{self.data.brand_name.upper()} - GEO AUDIT</h1>
            <h2>Intelligence Dashboard v1.0</h2>
            <p>Generated: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
        </div>
        
        <div class="section">
            <div class="section-title">CURRENT POSITION</div>
            <div class="metric-grid">
                <div class="metric-item">
                    <strong>Overall Score:</strong> {scores.overall:.1f}/100<br>
                    <div class="progress-bar">
                        <div class="progress-fill score-{'excellent' if scores.overall >= 80 else 'good' if scores.overall >= 60 else 'warning' if scores.overall >= 40 else 'danger'}" 
                             style="width: {scores.overall}%"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <strong>Discovery Score:</strong> {scores.discovery:.1f}/100<br>
                    <div class="progress-bar">
                        <div class="progress-fill score-{'excellent' if scores.discovery >= 80 else 'good' if scores.discovery >= 60 else 'warning' if scores.discovery >= 40 else 'danger'}" 
                             style="width: {scores.discovery}%"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <strong>Context Score:</strong> {scores.context:.1f}/100<br>
                    <div class="progress-bar">
                        <div class="progress-fill score-{'excellent' if scores.context >= 80 else 'good' if scores.context >= 60 else 'warning' if scores.context >= 40 else 'danger'}" 
                             style="width: {scores.context}%"></div>
                    </div>
                </div>
                <div class="metric-item">
                    <strong>Competitive Score:</strong> {scores.competitive:.1f}/100<br>
                    <div class="progress-bar">
                        <div class="progress-fill score-{'excellent' if scores.competitive >= 80 else 'good' if scores.competitive >= 60 else 'warning' if scores.competitive >= 40 else 'danger'}" 
                             style="width: {scores.competitive}%"></div>
                    </div>
                </div>
            </div>
            <p><strong>Market Share:</strong> {self.data.market_position['market_share_percentage']:.1f}% | 
               <strong>Rank:</strong> #{self.data.market_position['current_rank']} | 
               <strong>Status:</strong> ⚠️ NEEDS OPTIMIZATION</p>
        </div>
        
        <div class="roi-highlight">
            <h3>ROI PROJECTION</h3>
            <div class="roi-value">{roi.twelve_month_roi:.0f}% ROI</div>
            <p><strong>${roi.annual_revenue_impact:,.0f}</strong> additional annual revenue</p>
            <p>Investment: ${roi.implementation_cost:,.0f} | Break-even: {roi.breakeven_months:.1f} months</p>
        </div>
        
        <div class="section">
            <div class="section-title">COMPETITIVE LANDSCAPE</div>
            <table>
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>Competitor</th>
                        <th>Citations</th>
                        <th>Market Share</th>
                        <th>Trend</th>
                    </tr>
                </thead>
                <tbody>"""
        
        # Add competitor rows
        for comp in self.data.competitors[:6]:
            html += f"""
                    <tr>
                        <td>#{comp.rank}</td>
                        <td>{comp.name}</td>
                        <td>{comp.citations}</td>
                        <td>{comp.market_share:.1f}%</td>
                        <td>{'↗️' if comp.rank <= 2 else '→' if comp.rank <= 4 else '↘️'}</td>
                    </tr>"""
        
        html += """
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">MARKET OPPORTUNITIES</div>
            <table>
                <thead>
                    <tr>
                        <th>Priority</th>
                        <th>Opportunity</th>
                        <th>Impact</th>
                        <th>Effort</th>
                        <th>Citation Potential</th>
                    </tr>
                </thead>
                <tbody>"""
        
        # Add opportunity rows
        for opp in self.data.opportunities[:4]:
            effort_class = f"opportunity-{'high' if opp.effort_level == 'High' else 'medium' if opp.effort_level == 'Medium' else 'low'}"
            html += f"""
                    <tr>
                        <td>{opp.priority}</td>
                        <td>{opp.name}</td>
                        <td>{opp.impact_percentage:.0f}%</td>
                        <td class="{effort_class}">{opp.effort_level}</td>
                        <td>{opp.citation_potential:.1f}%</td>
                    </tr>"""
        
        html += f"""
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <div class="section-title">EXECUTIVE SUMMARY</div>
            <h4>🎯 THE OPPORTUNITY</h4>
            <ul>
                <li>Currently getting only 1.8% of AI citations in our market</li>
                <li>Competitors like EltaMD capture 8.7x more AI visibility</li>
                <li>AI search drives 35% of product research - missing revenue</li>
            </ul>
            
            <h4>💰 THE BUSINESS CASE</h4>
            <ul>
                <li>Investment: ${roi.implementation_cost:,.0f} in content optimization & authority building</li>
                <li>Expected Return: ${roi.annual_revenue_impact:,.0f} additional annual revenue ({roi.twelve_month_roi:.0f}% ROI)</li>
                <li>Timeline: {roi.breakeven_months:.1f} months to break even, ongoing competitive advantage</li>
            </ul>
            
            <h4>⚡ THE STRATEGY</h4>
            <ul>
                <li>Phase 1: Content optimization for AI consumption (Weeks 1-2)</li>
                <li>Phase 2: Authority building with expert partnerships (Weeks 3-6)</li>
                <li>Phase 3: Competitive content creation (Weeks 7-12)</li>
            </ul>
            
            <h4>🚀 NEXT STEPS</h4>
            <ol>
                <li>Approve GEO optimization investment</li>
                <li>Begin Phase 1 content optimization</li>
                <li>Establish monitoring dashboard</li>
                <li>Schedule weekly progress reviews</li>
            </ol>
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def _generate_pdf_optimized_html(self) -> str:
        """Generate HTML optimized for PDF conversion"""
        # Similar to HTML but with print-optimized styling
        html = self._generate_html_dashboard()
        
        # Add PDF-specific styles
        pdf_styles = """
        <style>
            @page { margin: 1in; }
            body { font-size: 12px; }
            .container { max-width: none; }
            .section { page-break-inside: avoid; }
        </style>
        """
        
        # Insert PDF styles before closing head tag
        html = html.replace('</head>', pdf_styles + '</head>')
        
        return html
    
    def _generate_executive_summary_markdown(self) -> str:
        """Generate executive summary in Markdown format"""
        roi = self.data.roi_projection
        
        summary = f"""# Executive Summary: {self.data.brand_name} GEO Audit

**Generated:** {datetime.now().strftime("%B %d, %Y")}

## 🎯 The Opportunity

- We're currently getting only **1.8%** of AI citations in our market
- Competitors like EltaMD capture **8.7x more** AI visibility
- AI search drives **35%** of product research - we're missing revenue

## 💰 The Business Case

| Metric | Value |
|--------|-------|
| **Investment Required** | ${roi.implementation_cost:,.0f} |
| **Annual Revenue Impact** | ${roi.annual_revenue_impact:,.0f} |
| **12-Month ROI** | {roi.twelve_month_roi:.0f}% |
| **Break-even Timeline** | {roi.breakeven_months:.1f} months |

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

- **Market Rank:** #{self.data.market_position['current_rank']} out of {self.data.market_position['total_competitors']}
- **Market Share:** {self.data.market_position['market_share_percentage']:.1f}%
- **Overall GEO Score:** {self.data.scores.overall:.1f}/100
- **Status:** Needs Optimization

## 🚀 Next Steps

1. **Approve** GEO optimization investment
2. **Begin** Phase 1 content optimization  
3. **Establish** monitoring dashboard
4. **Schedule** weekly progress reviews

---

*This analysis represents a comprehensive audit of {self.data.brand_name}'s position in AI-powered search results and provides a clear roadmap for capturing market share in the growing AI search landscape.*
"""
        
        return summary

# Export for easy importing
__all__ = ['DashboardExportManager']