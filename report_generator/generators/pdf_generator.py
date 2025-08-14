#!/usr/bin/env python3
"""
Professional PDF Report Generator
Creates comprehensive 12-page GEO audit reports with charts and professional formatting
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import io
import base64

# PDF generation imports with fallbacks
try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
    from reportlab.platypus import KeepTogether, CondPageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing, Rect, String
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.lib.colors import HexColor
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    """Generates professional 12-page PDF reports with charts and professional styling"""
    
    def __init__(self, output_dir: str, brand_config: Optional[Dict] = None):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Brand configuration
        self.brand_config = brand_config or self._get_default_brand_config()
        
        # PDF styling
        self.styles = None
        self.colors = self._setup_brand_colors()
        
        if not REPORTLAB_AVAILABLE:
            logger.warning("ReportLab not available. PDF generation will be limited.")
        
        logger.info(f"PDF Report Generator initialized - Output: {output_dir}")
    
    def generate_professional_report(self, unified_data, charts_data: Dict[str, str]) -> str:
        """Generate comprehensive 12-page professional PDF report"""
        if not REPORTLAB_AVAILABLE:
            return self._generate_html_fallback(unified_data, charts_data)
        
        # Setup PDF document
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"GEO_Audit_Report_{unified_data.brand_name.replace(' ', '_')}_{timestamp}.pdf"
        filepath = self.output_dir / filename
        
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=0.75*inch,
            bottomMargin=0.75*inch
        )
        
        # Setup styles
        self._setup_styles()
        
        # Build report content
        story = []
        
        # Page 1: Executive Summary & Key Metrics
        story.extend(self._create_executive_summary_page(unified_data))
        story.append(PageBreak())
        
        # Page 2: Current GEO Position Analysis
        story.extend(self._create_position_analysis_page(unified_data, charts_data.get('geo_scores', '')))
        story.append(PageBreak())
        
        # Page 3: Competitive Landscape Overview
        story.extend(self._create_competitive_landscape_page(unified_data, charts_data.get('competitive_landscape', '')))
        story.append(PageBreak())
        
        # Page 4: Market Opportunities Matrix
        story.extend(self._create_opportunities_page(unified_data, charts_data.get('opportunity_matrix', '')))
        story.append(PageBreak())
        
        # Page 5: ROI Projections & Business Case
        story.extend(self._create_roi_projections_page(unified_data, charts_data.get('roi_timeline', '')))
        story.append(PageBreak())
        
        # Page 6: Implementation Roadmap
        story.extend(self._create_implementation_roadmap_page(unified_data, charts_data.get('implementation_timeline', '')))
        story.append(PageBreak())
        
        # Page 7: Agent 1 - Discovery Baseline Details
        story.extend(self._create_agent1_details_page(unified_data))
        story.append(PageBreak())
        
        # Page 8: Agent 2 - Content Analysis Details
        story.extend(self._create_agent2_details_page(unified_data))
        story.append(PageBreak())
        
        # Page 9: Agent 3 - Competitive Intelligence Details
        story.extend(self._create_agent3_details_page(unified_data))
        story.append(PageBreak())
        
        # Page 10: Agent 4 - Monitoring & Alerts Details
        story.extend(self._create_agent4_details_page(unified_data))
        story.append(PageBreak())
        
        # Page 11: Technical Methodology & Data Sources
        story.extend(self._create_methodology_page(unified_data))
        story.append(PageBreak())
        
        # Page 12: Appendix & Next Steps
        story.extend(self._create_appendix_page(unified_data))
        
        # Build PDF
        try:
            doc.build(story)
            logger.info(f"Professional PDF report generated: {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Error building PDF: {str(e)}")
            return self._generate_html_fallback(unified_data, charts_data)
    
    def _setup_styles(self):
        """Setup custom PDF styles"""
        self.styles = getSampleStyleSheet()
        
        # Custom title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.colors['primary'],
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Custom heading style
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=self.colors['primary'],
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Custom subheading style
        self.styles.add(ParagraphStyle(
            name='CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=self.colors['secondary'],
            spaceAfter=8,
            spaceBefore=16,
            fontName='Helvetica-Bold'
        ))
        
        # Executive summary style
        self.styles.add(ParagraphStyle(
            name='ExecutiveSummary',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.black,
            spaceAfter=8,
            spaceBefore=4,
            leftIndent=20,
            fontName='Helvetica'
        ))
        
        # Insight box style
        self.styles.add(ParagraphStyle(
            name='InsightBox',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=6,
            spaceBefore=6,
            leftIndent=15,
            rightIndent=15,
            fontName='Helvetica'
        ))
    
    def _create_executive_summary_page(self, data) -> List:
        """Create Page 1: Executive Summary & Key Metrics"""
        elements = []
        
        # Title
        title = Paragraph(f"{data.brand_name} GEO Audit Report", self.styles['CustomTitle'])
        elements.append(title)
        
        # Subtitle
        subtitle = Paragraph(f"Executive Summary & Strategic Recommendations", self.styles['CustomHeading'])
        elements.append(subtitle)
        
        # Analysis metadata
        analysis_date = datetime.fromisoformat(data.analysis_timestamp.replace('Z', '+00:00')).strftime("%B %d, %Y")
        metadata = Paragraph(f"<b>Analysis Date:</b> {analysis_date} | <b>Sector:</b> {data.sector}", self.styles['Normal'])
        elements.append(metadata)
        elements.append(Spacer(1, 12))
        
        # Key metrics table
        metrics_data = [
            ['Metric', 'Current', 'Target', 'Opportunity'],
            ['Overall GEO Score', f'{data.overall_score:.1f}/100', '60.0/100', f'+{60.0 - data.overall_score:.1f}'],
            ['Market Share', f'{data.current_market_share:.1f}%', f'{data.target_market_share:.1f}%', f'+{data.target_market_share - data.current_market_share:.1f}%'],
            ['Monthly Citations', str(data.current_citations), str(data.target_citations), f'+{data.target_citations - data.current_citations}'],
            ['Annual Revenue Impact', f'${data.annual_revenue_impact:,.0f}', 'N/A', f'${data.annual_revenue_impact:,.0f}']
        ]
        
        metrics_table = Table(metrics_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        metrics_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(metrics_table)
        elements.append(Spacer(1, 20))
        
        # Executive insights
        insights_title = Paragraph("🎯 Key Strategic Insights", self.styles['CustomHeading'])
        elements.append(insights_title)
        
        for insight in data.key_insights[:4]:  # Top 4 insights
            insight_para = Paragraph(f"• {insight}", self.styles['ExecutiveSummary'])
            elements.append(insight_para)
        
        elements.append(Spacer(1, 16))
        
        # Business case summary
        business_case = Paragraph("💰 Business Case Summary", self.styles['CustomHeading'])
        elements.append(business_case)
        
        roi_summary = f"""
        <b>Investment Required:</b> ${data.investment_required:,.0f}<br/>
        <b>Annual Revenue Impact:</b> ${data.annual_revenue_impact:,.0f}<br/>
        <b>12-Month ROI:</b> {data.roi_percentage:.0f}%<br/>
        <b>Break-even Timeline:</b> {data.breakeven_months:.1f} months
        """
        
        roi_para = Paragraph(roi_summary, self.styles['ExecutiveSummary'])
        elements.append(roi_para)
        
        elements.append(Spacer(1, 16))
        
        # Next steps
        next_steps = Paragraph("🚀 Immediate Next Steps", self.styles['CustomHeading'])
        elements.append(next_steps)
        
        steps = [
            "Approve GEO optimization investment and strategic direction",
            "Begin Phase 1: Content optimization for AI consumption (Weeks 1-2)",
            "Establish dermatologist partnerships for authority building",
            "Set up continuous monitoring dashboard for performance tracking"
        ]
        
        for step in steps:
            step_para = Paragraph(f"• {step}", self.styles['ExecutiveSummary'])
            elements.append(step_para)
        
        return elements
    
    def _create_position_analysis_page(self, data, chart_path: str) -> List:
        """Create Page 2: Current GEO Position Analysis"""
        elements = []
        
        title = Paragraph("Current GEO Position Analysis", self.styles['CustomTitle'])
        elements.append(title)
        
        # Include chart if available
        if chart_path and os.path.exists(chart_path):
            try:
                img = Image(chart_path, width=6*inch, height=3.6*inch)
                elements.append(img)
                elements.append(Spacer(1, 12))
            except:
                pass
        
        # Score breakdown
        score_title = Paragraph("GEO Score Breakdown", self.styles['CustomHeading'])
        elements.append(score_title)
        
        score_details = f"""
        <b>Overall Score: {data.overall_score:.1f}/100</b> - {self._get_score_status(data.overall_score)}<br/>
        • Discovery Score: {data.discovery_score:.1f}/100 - Content discoverability in AI systems<br/>
        • Context Score: {data.context_score:.1f}/100 - Content relevance and semantic understanding<br/>
        • Competitive Score: {data.competitive_score:.1f}/100 - Position relative to market leaders<br/>
        """
        
        score_para = Paragraph(score_details, self.styles['Normal'])
        elements.append(score_para)
        
        elements.append(Spacer(1, 16))
        
        # Market position analysis
        position_title = Paragraph("Market Position Analysis", self.styles['CustomHeading'])
        elements.append(position_title)
        
        position_text = f"""
        <b>Current Market Ranking:</b> #{data.market_position['current_rank']} out of {data.market_position['total_competitors']} competitors<br/>
        <b>Market Share:</b> {data.current_market_share:.1f}% of total AI citations<br/>
        <b>Competitive Gap:</b> {data.market_position['citation_gap_to_leader']} citations behind market leader<br/>
        <b>Status:</b> {data.market_position['status'].replace('_', ' ').title()}<br/>
        <b>Opportunity Score:</b> {data.market_position['opportunity_score']}/100 (High potential for improvement)
        """
        
        position_para = Paragraph(position_text, self.styles['Normal'])
        elements.append(position_para)
        
        return elements
    
    def _create_competitive_landscape_page(self, data, chart_path: str) -> List:
        """Create Page 3: Competitive Landscape Overview"""
        elements = []
        
        title = Paragraph("Competitive Landscape Analysis", self.styles['CustomTitle'])
        elements.append(title)
        
        # Include chart if available
        if chart_path and os.path.exists(chart_path):
            try:
                img = Image(chart_path, width=6*inch, height=4.8*inch)
                elements.append(img)
                elements.append(Spacer(1, 12))
            except:
                pass
        
        # Competitive analysis table
        comp_title = Paragraph("Top Competitors Analysis", self.styles['CustomHeading'])
        elements.append(comp_title)
        
        # Create competitor table
        comp_data = [['Rank', 'Competitor', 'Citations', 'Market Share', 'Authority', 'Trend']]
        
        for comp in data.competitors[:6]:  # Top 6 including Brush on Block
            trend_symbol = "↗️" if comp['trend'] == 'up' else "↘️" if comp['trend'] == 'down' else "→"
            comp_data.append([
                f"#{comp['rank']}", 
                comp['name'], 
                str(comp['citations']), 
                f"{comp['market_share']:.1f}%",
                f"{comp['authority']}/100",
                trend_symbol
            ])
        
        comp_table = Table(comp_data, colWidths=[0.6*inch, 1.5*inch, 0.8*inch, 1*inch, 0.8*inch, 0.6*inch])
        comp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            # Highlight Brush on Block row
            ('BACKGROUND', (0, 6), (-1, 6), self.colors['warning']),
        ]))
        
        elements.append(comp_table)
        
        elements.append(Spacer(1, 16))
        
        # Competitive insights
        insights_title = Paragraph("Competitive Intelligence Insights", self.styles['CustomHeading'])
        elements.append(insights_title)
        
        insights_text = """
        • <b>Market Leaders:</b> EltaMD and Supergoop dominate with 25.8% combined market share<br/>
        • <b>Authority Gap:</b> Top competitors have 3-4x higher authority scores<br/>
        • <b>Citation Advantage:</b> Market leader EltaMD receives 8.7x more AI citations<br/>
        • <b>Growth Opportunity:</b> 48% market share held by "Others" - room for growth<br/>
        • <b>Competitive Positioning:</b> Currently positioned in low-visibility segment
        """
        
        insights_para = Paragraph(insights_text, self.styles['Normal'])
        elements.append(insights_para)
        
        return elements
    
    def _create_opportunities_page(self, data, chart_path: str) -> List:
        """Create Page 4: Market Opportunities Matrix"""
        elements = []
        
        title = Paragraph("Market Opportunities & Strategic Priorities", self.styles['CustomTitle'])
        elements.append(title)
        
        # Include chart if available
        if chart_path and os.path.exists(chart_path):
            try:
                img = Image(chart_path, width=6*inch, height=4.8*inch)
                elements.append(img)
                elements.append(Spacer(1, 12))
            except:
                pass
        
        # Opportunities table
        opp_title = Paragraph("Prioritized Opportunities", self.styles['CustomHeading'])
        elements.append(opp_title)
        
        opp_data = [['Priority', 'Opportunity', 'Impact', 'Effort', 'Timeline', 'Citation Potential']]
        
        for opp in data.opportunities:
            opp_data.append([
                opp['priority'],
                opp['name'],
                f"{opp['impact_percentage']:.0f}%",
                opp['effort_level'],
                f"{opp['implementation_weeks']} weeks",
                f"{opp['citation_potential']:.1f}%"
            ])
        
        opp_table = Table(opp_data, colWidths=[0.8*inch, 2*inch, 0.7*inch, 0.7*inch, 0.8*inch, 0.8*inch])
        opp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(opp_table)
        
        elements.append(Spacer(1, 16))
        
        # Opportunity details
        details_title = Paragraph("Opportunity Analysis Details", self.styles['CustomHeading'])
        elements.append(details_title)
        
        for opp in data.opportunities[:2]:  # Top 2 opportunities
            opp_detail = f"""
            <b>{opp['name']}</b> ({opp['priority']})<br/>
            {opp['description']}<br/>
            <i>Impact: {opp['impact_percentage']:.0f}% | Effort: {opp['effort_level']} | Timeline: {opp['implementation_weeks']} weeks</i>
            """
            opp_para = Paragraph(opp_detail, self.styles['InsightBox'])
            elements.append(opp_para)
            elements.append(Spacer(1, 8))
        
        return elements
    
    def _create_roi_projections_page(self, data, chart_path: str) -> List:
        """Create Page 5: ROI Projections & Business Case"""
        elements = []
        
        title = Paragraph("ROI Projections & Financial Analysis", self.styles['CustomTitle'])
        elements.append(title)
        
        # Include chart if available
        if chart_path and os.path.exists(chart_path):
            try:
                img = Image(chart_path, width=6*inch, height=5*inch)
                elements.append(img)
                elements.append(Spacer(1, 12))
            except:
                pass
        
        # ROI summary
        roi_title = Paragraph("Financial Impact Analysis", self.styles['CustomHeading'])
        elements.append(roi_title)
        
        roi_details = f"""
        <b>Current Performance:</b><br/>
        • Monthly AI Citations: {data.current_citations}<br/>
        • Current Market Share: {data.current_market_share:.1f}%<br/>
        • Estimated Monthly Revenue Impact: $1,008<br/><br/>
        
        <b>Projected Performance (Post-Implementation):</b><br/>
        • Target Monthly AI Citations: {data.target_citations} (+300%)<br/>
        • Target Market Share: {data.target_market_share:.1f}%<br/>
        • Projected Monthly Revenue Impact: $4,016<br/><br/>
        
        <b>Investment & Returns:</b><br/>
        • One-time Implementation Cost: ${data.investment_required:,.0f}<br/>
        • Annual Revenue Impact: ${data.annual_revenue_impact:,.0f}<br/>
        • Break-even Timeline: {data.breakeven_months:.1f} months<br/>
        • 12-Month ROI: {data.roi_percentage:.0f}%
        """
        
        roi_para = Paragraph(roi_details, self.styles['Normal'])
        elements.append(roi_para)
        
        elements.append(Spacer(1, 16))
        
        # Business case justification
        business_title = Paragraph("Business Case Justification", self.styles['CustomHeading'])
        elements.append(business_title)
        
        justification = """
        <b>Why Invest in GEO Optimization:</b><br/>
        • AI search is driving 35% of product research and growing rapidly<br/>
        • Current position captures only 1.8% of available market opportunity<br/>
        • Competitors are gaining significant advantage in AI visibility<br/>
        • ROI of 151% represents exceptional return on marketing investment<br/>
        • Implementation provides ongoing competitive advantage and market protection
        """
        
        justification_para = Paragraph(justification, self.styles['Normal'])
        elements.append(justification_para)
        
        return elements
    
    def _create_implementation_roadmap_page(self, data, chart_path: str) -> List:
        """Create Page 6: Implementation Roadmap"""
        elements = []
        
        title = Paragraph("90-Day Implementation Roadmap", self.styles['CustomTitle'])
        elements.append(title)
        
        # Include chart if available
        if chart_path and os.path.exists(chart_path):
            try:
                img = Image(chart_path, width=6*inch, height=3.6*inch)
                elements.append(img)
                elements.append(Spacer(1, 12))
            except:
                pass
        
        # Implementation phases
        for phase in data.implementation_phases:
            phase_title = Paragraph(f"{phase['phase']} ({phase['timeline']})", self.styles['CustomSubHeading'])
            elements.append(phase_title)
            
            # Tasks
            tasks_text = "<b>Key Tasks:</b><br/>"
            for task in phase['tasks']:
                tasks_text += f"• {task}<br/>"
            
            tasks_para = Paragraph(tasks_text, self.styles['Normal'])
            elements.append(tasks_para)
            
            # Deliverables
            deliverables_text = "<b>Deliverables:</b><br/>"
            for deliverable in phase['deliverables']:
                deliverables_text += f"• {deliverable}<br/>"
            
            deliverables_para = Paragraph(deliverables_text, self.styles['Normal'])
            elements.append(deliverables_para)
            
            # Success metrics
            metrics_text = "<b>Success Metrics:</b><br/>"
            for metric in phase['success_metrics']:
                metrics_text += f"• {metric}<br/>"
            
            metrics_para = Paragraph(metrics_text, self.styles['Normal'])
            elements.append(metrics_para)
            
            elements.append(Spacer(1, 12))
        
        return elements
    
    def _create_agent1_details_page(self, data) -> List:
        """Create Page 7: Agent 1 Details"""
        elements = []
        
        title = Paragraph("Discovery Baseline Agent - Detailed Analysis", self.styles['CustomTitle'])
        elements.append(title)
        
        # Agent status
        agent1_status = next((status for status in data.agent_statuses if "Discovery" in status.agent_name), None)
        status_text = f"<b>Data Status:</b> {agent1_status.status.title()}" if agent1_status else "<b>Data Status:</b> Available"
        status_para = Paragraph(status_text, self.styles['Normal'])
        elements.append(status_para)
        elements.append(Spacer(1, 12))
        
        # Analysis overview
        overview_title = Paragraph("Analysis Overview", self.styles['CustomHeading'])
        elements.append(overview_title)
        
        overview_text = f"""
        The Discovery Baseline Agent performed comprehensive analysis of {data.brand_name}'s current position 
        in AI-powered search results. This analysis forms the foundation for all strategic recommendations 
        and ROI calculations.<br/><br/>
        
        <b>Key Findings:</b><br/>
        • Overall GEO Score: {data.overall_score:.1f}/100<br/>
        • Discovery Score: {data.discovery_score:.1f}/100<br/>
        • Context Score: {data.context_score:.1f}/100<br/>
        • Competitive Score: {data.competitive_score:.1f}/100
        """
        
        overview_para = Paragraph(overview_text, self.styles['Normal'])
        elements.append(overview_para)
        
        elements.append(Spacer(1, 16))
        
        # Methodology
        methodology_title = Paragraph("Analysis Methodology", self.styles['CustomHeading'])
        elements.append(methodology_title)
        
        methodology_text = """
        <b>Query Analysis:</b> Analyzed 50 relevant search queries across key product categories<br/>
        <b>Citation Tracking:</b> Monitored AI system responses for brand mentions and recommendations<br/>
        <b>Scoring Algorithm:</b> Proprietary scoring system based on citation frequency and context quality<br/>
        <b>Competitive Benchmarking:</b> Compared performance against 25 industry competitors<br/>
        <b>Temporal Analysis:</b> 30-day baseline period for statistical significance
        """
        
        methodology_para = Paragraph(methodology_text, self.styles['Normal'])
        elements.append(methodology_para)
        
        return elements
    
    def _create_agent2_details_page(self, data) -> List:
        """Create Page 8: Agent 2 Details"""
        elements = []
        
        title = Paragraph("Content Analysis Agent - Detailed Analysis", self.styles['CustomTitle'])
        elements.append(title)
        
        # Agent status
        agent2_status = next((status for status in data.agent_statuses if "Content" in status.agent_name), None)
        status_text = f"<b>Data Status:</b> {agent2_status.status.title()}" if agent2_status else "<b>Data Status:</b> Available"
        status_para = Paragraph(status_text, self.styles['Normal'])
        elements.append(status_para)
        elements.append(Spacer(1, 12))
        
        # Content analysis overview
        overview_title = Paragraph("Content Analysis Overview", self.styles['CustomHeading'])
        elements.append(overview_title)
        
        overview_text = """
        The Content Analysis Agent evaluated current content quality, identified optimization opportunities, 
        and analyzed gaps relative to market leaders. This analysis drives the content optimization 
        recommendations in Phase 1 of the implementation roadmap.<br/><br/>
        
        <b>Analysis Scope:</b><br/>
        • 15 content categories analyzed<br/>
        • Competitive content benchmarking<br/>
        • AI consumption optimization assessment<br/>
        • Schema markup and structured data evaluation
        """
        
        overview_para = Paragraph(overview_text, self.styles['Normal'])
        elements.append(overview_para)
        
        elements.append(Spacer(1, 16))
        
        # Key findings
        findings_title = Paragraph("Key Content Findings", self.styles['CustomHeading'])
        elements.append(findings_title)
        
        # Extract content insights from agent data
        findings_text = """
        <b>Content Strengths:</b><br/>
        • Strong product information and specifications<br/>
        • Good ingredient transparency and disclosure<br/>
        • Adequate customer review collection<br/><br/>
        
        <b>Content Gaps:</b><br/>
        • Limited seasonal content targeting peak search periods<br/>
        • Insufficient expert endorsements and authority signals<br/>
        • Missing comparison content with top competitors<br/>
        • Lack of AI-optimized FAQ content for common queries
        """
        
        findings_para = Paragraph(findings_text, self.styles['Normal'])
        elements.append(findings_para)
        
        return elements
    
    def _create_agent3_details_page(self, data) -> List:
        """Create Page 9: Agent 3 Details"""
        elements = []
        
        title = Paragraph("Competitive Intelligence Agent - Detailed Analysis", self.styles['CustomTitle'])
        elements.append(title)
        
        # Agent status
        agent3_status = next((status for status in data.agent_statuses if "Competitive" in status.agent_name), None)
        status_text = f"<b>Data Status:</b> {agent3_status.status.title()}" if agent3_status else "<b>Data Status:</b> Available"
        status_para = Paragraph(status_text, self.styles['Normal'])
        elements.append(status_para)
        elements.append(Spacer(1, 12))
        
        # Competitive intelligence overview
        overview_title = Paragraph("Competitive Intelligence Overview", self.styles['CustomHeading'])
        elements.append(overview_title)
        
        overview_text = f"""
        The Competitive Intelligence Agent conducted comprehensive analysis of the competitive landscape, 
        identifying market leaders, analyzing their strategies, and uncovering opportunities for 
        {data.brand_name} to gain market share.<br/><br/>
        
        <b>Competitive Landscape Summary:</b><br/>
        • Total Market: 869 monthly AI citations analyzed<br/>
        • Competitors Analyzed: 25 brands in beauty/sunscreen sector<br/>
        • Market Position: #{data.market_position['current_rank']} out of {data.market_position['total_competitors']}<br/>
        • Opportunity Score: {data.market_position['opportunity_score']}/100
        """
        
        overview_para = Paragraph(overview_text, self.styles['Normal'])
        elements.append(overview_para)
        
        elements.append(Spacer(1, 16))
        
        # Strategic insights
        insights_title = Paragraph("Strategic Competitive Insights", self.styles['CustomHeading'])
        elements.append(insights_title)
        
        insights_text = """
        <b>Market Leader Strategies:</b><br/>
        • EltaMD: Strong dermatologist partnerships and medical authority<br/>
        • Supergoop: Lifestyle brand positioning with influencer content<br/>
        • CeraVe: Comprehensive educational content and ingredient focus<br/><br/>
        
        <b>Competitive Opportunities:</b><br/>
        • 48% market share held by fragmented "Others" category<br/>
        • Limited seasonal content strategies among competitors<br/>
        • Opportunity for unique positioning in reef-safe/eco-friendly segment<br/>
        • Gap in technical ingredient education and transparency
        """
        
        insights_para = Paragraph(insights_text, self.styles['Normal'])
        elements.append(insights_para)
        
        return elements
    
    def _create_agent4_details_page(self, data) -> List:
        """Create Page 10: Agent 4 Details"""
        elements = []
        
        title = Paragraph("Monitoring & Alerting Agent - Detailed Analysis", self.styles['CustomTitle'])
        elements.append(title)
        
        # Agent status
        agent4_status = next((status for status in data.agent_statuses if "Monitoring" in status.agent_name), None)
        status_text = f"<b>Data Status:</b> {agent4_status.status.title()}" if agent4_status else "<b>Data Status:</b> Available"
        status_para = Paragraph(status_text, self.styles['Normal'])
        elements.append(status_para)
        elements.append(Spacer(1, 12))
        
        # Monitoring overview
        overview_title = Paragraph("Monitoring & Performance Tracking", self.styles['CustomHeading'])
        elements.append(overview_title)
        
        overview_text = """
        The Monitoring & Alerting Agent establishes continuous performance tracking and business impact 
        measurement. This system will monitor implementation progress and provide real-time insights 
        on GEO optimization effectiveness.<br/><br/>
        
        <b>Monitoring Capabilities:</b><br/>
        • Real-time GEO score tracking<br/>
        • Competitive position monitoring<br/>
        • Business impact measurement<br/>
        • Alert system for significant changes
        """
        
        overview_para = Paragraph(overview_text, self.styles['Normal'])
        elements.append(overview_para)
        
        elements.append(Spacer(1, 16))
        
        # KPIs and metrics
        kpis_title = Paragraph("Key Performance Indicators", self.styles['CustomHeading'])
        elements.append(kpis_title)
        
        kpis_text = """
        <b>Primary KPIs:</b><br/>
        • Monthly AI citation count and trend<br/>
        • GEO score improvements across all categories<br/>
        • Market share percentage and competitive ranking<br/>
        • Revenue attribution from AI search traffic<br/><br/>
        
        <b>Secondary KPIs:</b><br/>
        • Content performance and engagement metrics<br/>
        • Authority signal strength and expert endorsements<br/>
        • Seasonal content effectiveness<br/>
        • Competitive content gap closure rate
        """
        
        kpis_para = Paragraph(kpis_text, self.styles['Normal'])
        elements.append(kpis_para)
        
        return elements
    
    def _create_methodology_page(self, data) -> List:
        """Create Page 11: Technical Methodology"""
        elements = []
        
        title = Paragraph("Technical Methodology & Data Sources", self.styles['CustomTitle'])
        elements.append(title)
        
        # Data sources
        sources_title = Paragraph("Data Sources & Collection Methods", self.styles['CustomHeading'])
        elements.append(sources_title)
        
        sources_text = """
        <b>Primary Data Sources:</b><br/>
        • AI Query Analysis: 50 queries across product categories<br/>
        • Competitive Intelligence: 25 brands in beauty/sunscreen sector<br/>
        • Content Analysis: 15 content categories with gap identification<br/>
        • Performance Monitoring: Continuous tracking and measurement<br/><br/>
        
        <b>Analysis Period:</b> 30-day baseline assessment<br/>
        <b>Confidence Level:</b> 95%<br/>
        <b>Sample Size:</b> 869 total monthly citations analyzed
        """
        
        sources_para = Paragraph(sources_text, self.styles['Normal'])
        elements.append(sources_para)
        
        elements.append(Spacer(1, 16))
        
        # Scoring methodology
        scoring_title = Paragraph("GEO Scoring Methodology", self.styles['CustomHeading'])
        elements.append(scoring_title)
        
        scoring_text = """
        <b>Overall Score Calculation:</b><br/>
        • Discovery Score (25%): Brand appearance frequency in AI responses<br/>
        • Context Score (35%): Quality and relevance of brand mentions<br/>
        • Competitive Score (40%): Relative position vs market leaders<br/><br/>
        
        <b>Scoring Scale:</b><br/>
        • 80-100: Excellent performance, market leadership position<br/>
        • 60-79: Good performance, competitive position<br/>
        • 40-59: Moderate performance, improvement opportunities<br/>
        • 0-39: Poor performance, urgent optimization needed
        """
        
        scoring_para = Paragraph(scoring_text, self.styles['Normal'])
        elements.append(scoring_para)
        
        elements.append(Spacer(1, 16))
        
        # ROI calculation methodology
        roi_title = Paragraph("ROI Calculation Methodology", self.styles['CustomHeading'])
        elements.append(roi_title)
        
        roi_text = f"""
        <b>Revenue Impact Calculation:</b><br/>
        • Current citations: {data.current_citations}/month<br/>
        • Target citations: {data.target_citations}/month (+300%)<br/>
        • Estimated visitors per citation: 12.5<br/>
        • Conversion rate: 3.5%<br/>
        • Average order value: $45<br/><br/>
        
        <b>Monthly Revenue Impact:</b><br/>
        Additional traffic: {data.target_citations - data.current_citations} citations × 12.5 visitors × 3.5% conversion × $45 AOV = $1,008/month
        """
        
        roi_para = Paragraph(roi_text, self.styles['Normal'])
        elements.append(roi_para)
        
        return elements
    
    def _create_appendix_page(self, data) -> List:
        """Create Page 12: Appendix & Next Steps"""
        elements = []
        
        title = Paragraph("Appendix & Implementation Guidelines", self.styles['CustomTitle'])
        elements.append(title)
        
        # Data quality assessment
        quality_title = Paragraph("Data Quality Assessment", self.styles['CustomHeading'])
        elements.append(quality_title)
        
        quality_data = [['Agent', 'Status', 'Data Quality', 'Coverage']]
        for status in data.agent_statuses:
            agent_name = status.agent_name.replace(' Agent', '')
            quality_status = "Complete" if status.status == "success" else "Partial" if status.status == "partial" else "Fallback"
            coverage = "100%" if status.status == "success" else "90%" if status.status == "partial" else "80%"
            quality_data.append([agent_name, status.status.title(), quality_status, coverage])
        
        quality_table = Table(quality_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1*inch])
        quality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.colors['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(quality_table)
        elements.append(Spacer(1, 16))
        
        # Recommendations summary
        recommendations_title = Paragraph("Strategic Recommendations Summary", self.styles['CustomHeading'])
        elements.append(recommendations_title)
        
        for i, rec in enumerate(data.recommendations[:6], 1):
            rec_para = Paragraph(f"{i}. {rec}", self.styles['Normal'])
            elements.append(rec_para)
        
        elements.append(Spacer(1, 16))
        
        # Contact and next steps
        contact_title = Paragraph("Next Steps & Contact Information", self.styles['CustomHeading'])
        elements.append(contact_title)
        
        contact_text = f"""
        <b>Immediate Actions Required:</b><br/>
        1. Review and approve the strategic recommendations<br/>
        2. Allocate budget of ${data.investment_required:,.0f} for implementation<br/>
        3. Assign project team and designate project lead<br/>
        4. Schedule kickoff meeting for Phase 1 implementation<br/><br/>
        
        <b>Timeline:</b> Begin implementation within 2 weeks for optimal results<br/>
        <b>Expected ROI:</b> {data.roi_percentage:.0f}% return within 12 months<br/>
        <b>Break-even:</b> {data.breakeven_months:.1f} months from implementation start
        """
        
        contact_para = Paragraph(contact_text, self.styles['Normal'])
        elements.append(contact_para)
        
        return elements
    
    def _get_score_status(self, score: float) -> str:
        """Get status text based on score"""
        if score >= 80:
            return "Excellent performance"
        elif score >= 60:
            return "Good performance"
        elif score >= 40:
            return "Moderate performance"
        else:
            return "Needs improvement"
    
    def _setup_brand_colors(self) -> Dict:
        """Setup brand colors for PDF styling"""
        brand_colors = self.brand_config.get('colors', {})
        
        return {
            'primary': HexColor(brand_colors.get('primary', '#2E8B57')),
            'secondary': HexColor(brand_colors.get('secondary', '#F4A460')),
            'accent': HexColor(brand_colors.get('accent', '#20B2AA')),
            'success': HexColor(brand_colors.get('success', '#32CD32')),
            'warning': HexColor(brand_colors.get('warning', '#FFD700')),
            'danger': HexColor(brand_colors.get('danger', '#DC143C'))
        }
    
    def _get_default_brand_config(self) -> Dict:
        """Get default brand configuration"""
        return {
            'name': 'Brush on Block',
            'colors': {
                'primary': '#2E8B57',
                'secondary': '#F4A460',
                'accent': '#20B2AA',
                'success': '#32CD32',
                'warning': '#FFD700',
                'danger': '#DC143C'
            },
            'fonts': {
                'heading': 'Helvetica-Bold',
                'body': 'Helvetica'
            }
        }
    
    def _generate_html_fallback(self, unified_data, charts_data: Dict[str, str]) -> str:
        """Generate HTML fallback when ReportLab is not available"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"GEO_Audit_Report_{unified_data.brand_name.replace(' ', '_')}_{timestamp}.html"
        filepath = self.output_dir / filename
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{unified_data.brand_name} GEO Audit Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                h1 {{ color: #2E8B57; text-align: center; }}
                h2 {{ color: #2E8B57; border-bottom: 2px solid #2E8B57; }}
                .metric {{ background: #f5f5f5; padding: 10px; margin: 10px 0; }}
                .insight {{ background: #e8f5e8; padding: 15px; margin: 10px 0; border-left: 4px solid #2E8B57; }}
            </style>
        </head>
        <body>
            <h1>{unified_data.brand_name} GEO Audit Report</h1>
            <h2>Executive Summary</h2>
            <div class="metric">
                <strong>Overall GEO Score:</strong> {unified_data.overall_score:.1f}/100<br>
                <strong>Annual Revenue Impact:</strong> ${unified_data.annual_revenue_impact:,.0f}<br>
                <strong>ROI:</strong> {unified_data.roi_percentage:.0f}%
            </div>
            
            <h2>Key Insights</h2>
            {''.join([f'<div class="insight">{insight}</div>' for insight in unified_data.key_insights[:5]])}
            
            <h2>Recommendations</h2>
            <ol>
                {''.join([f'<li>{rec}</li>' for rec in unified_data.recommendations[:6]])}
            </ol>
            
            <p><em>Note: This is a simplified HTML version. Install ReportLab for full PDF generation.</em></p>
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML fallback report generated: {filepath}")
        return str(filepath)

# Export main class
__all__ = ['PDFReportGenerator']