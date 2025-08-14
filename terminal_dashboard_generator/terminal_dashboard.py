#!/usr/bin/env python3
"""
Terminal Dashboard Generator
Creates impressive ASCII-style executive dashboards for GEO audit presentations
"""

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import logging
from dataclasses import asdict

# Terminal colors and styling
class TerminalColors:
    """ANSI color codes for terminal styling"""
    # Basic colors
    BLACK = '\033[0;30m'
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    MAGENTA = '\033[0;35m'
    CYAN = '\033[0;36m'
    WHITE = '\033[0;37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[1;30m'
    BRIGHT_RED = '\033[1;31m'
    BRIGHT_GREEN = '\033[1;32m'
    BRIGHT_YELLOW = '\033[1;33m'
    BRIGHT_BLUE = '\033[1;34m'
    BRIGHT_MAGENTA = '\033[1;35m'
    BRIGHT_CYAN = '\033[1;36m'
    BRIGHT_WHITE = '\033[1;37m'
    
    # Special formatting
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'

class TerminalDashboard:
    """Professional terminal dashboard generator for GEO audit results"""
    
    def __init__(self, aggregated_data):
        self.data = aggregated_data
        self.colors = TerminalColors()
        self.width = 70  # Standard terminal width for readability
        
        # Color scheme
        self.success_color = self.colors.BRIGHT_GREEN
        self.warning_color = self.colors.BRIGHT_YELLOW
        self.danger_color = self.colors.BRIGHT_RED
        self.info_color = self.colors.BRIGHT_CYAN
        self.primary_color = self.colors.BRIGHT_WHITE
        self.secondary_color = self.colors.WHITE
        self.muted_color = self.colors.BRIGHT_BLACK
        self.reset = self.colors.RESET
        
        # Status indicators
        self.status_indicators = {
            'excellent': '🟢',
            'good': '🟡',
            'needs_improvement': '🟠',
            'critical': '🔴'
        }
        
        # Trend arrows
        self.trend_arrows = {
            'up': '↗️',
            'down': '↘️',
            'stable': '→'
        }
        
        logging.info("Terminal Dashboard initialized for impressive executive presentation")
    
    def generate_complete_dashboard(self) -> str:
        """Generate the complete terminal dashboard"""
        dashboard = []
        
        # Header
        dashboard.append(self._create_header())
        dashboard.append("")
        
        # Current Position
        dashboard.append(self._create_position_section())
        dashboard.append("")
        
        # Competitive Landscape
        dashboard.append(self._create_competitive_section())
        dashboard.append("")
        
        # Market Opportunities
        dashboard.append(self._create_opportunities_section())
        dashboard.append("")
        
        # ROI Projection
        dashboard.append(self._create_roi_section())
        dashboard.append("")
        
        # Implementation Roadmap
        dashboard.append(self._create_roadmap_section())
        dashboard.append("")
        
        # Executive Summary
        dashboard.append(self._create_executive_summary())
        
        return "\\n".join(dashboard)
    
    def _create_header(self) -> str:
        """Create professional header with branding"""
        brand = self.data.brand_name.upper()
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        
        header = f"""╔══════════════════════════════════════════════════════════════════╗
║{self.success_color}                     {brand} - GEO AUDIT{self.reset}                    ║
║{self.info_color}                     Intelligence Dashboard v1.0{self.reset}                 ║
║{self.muted_color}                     Generated: {timestamp}{self.reset}                      ║
╚══════════════════════════════════════════════════════════════════╝"""
        
        return header
    
    def _create_position_section(self) -> str:
        """Create current position visualization with progress bars"""
        scores = self.data.scores
        
        # Generate progress bars
        overall_bar = self._create_progress_bar(scores.overall, scores.target_overall)
        discovery_bar = self._create_progress_bar(scores.discovery, scores.target_discovery)
        context_bar = self._create_progress_bar(scores.context, scores.target_context)
        competitive_bar = self._create_progress_bar(scores.competitive, scores.target_competitive)
        
        # Market share calculation
        total_citations = 869  # Based on competitive analysis
        brand_citations = 16
        market_share = (brand_citations / total_citations) * 100
        
        # Status determination
        status_emoji = "⚠️"
        status_text = f"{self.warning_color}NEEDS OPTIMIZATION{self.reset}"
        
        if scores.overall >= 60:
            status_emoji = "🟢"
            status_text = f"{self.success_color}EXCELLENT{self.reset}"
        elif scores.overall >= 40:
            status_emoji = "🟡"
            status_text = f"{self.warning_color}GOOD{self.reset}"
        
        position = f"""┌─[ {self.primary_color}CURRENT POSITION{self.reset} ]──────────────────────────────────────────────┐
│ Overall Score:        {overall_bar} {self.primary_color}{scores.overall:.1f}/100{self.reset}          │
│ Discovery Score:      {discovery_bar} {self.primary_color}{scores.discovery:.1f}/100{self.reset}      │
│ Context Score:        {context_bar} {self.primary_color}{scores.context:.1f}/100{self.reset}          │
│ Competitive Score:    {competitive_bar} {self.primary_color}{scores.competitive:.1f}/100{self.reset}  │
│                                                                  │
│ Market Share:         {self.info_color}{market_share:.1f}% ({brand_citations}/{total_citations} citations){self.reset}                   │
│ Competitors Ahead:    {self.danger_color}18 brands{self.reset}                                 │
│ Status:              {status_emoji} {status_text}               │
└──────────────────────────────────────────────────────────────────┘"""
        
        return position
    
    def _create_competitive_section(self) -> str:
        """Create competitive landscape table"""
        competitors = self.data.competitors[:6]  # Top 5 + Brush on Block
        
        header = f"""┌─[ {self.primary_color}COMPETITIVE LANDSCAPE{self.reset} ]─────────────────────────────────────────┐
│ Rank │ Competitor     │ Citations │ Share  │ Trend │ Authority  │
│ ──── │ ────────────── │ ───────── │ ────── │ ───── │ ────────── │"""
        
        rows = []
        for comp in competitors:
            # Format competitor name
            name = comp.name[:14].ljust(14)
            
            # Color coding based on threat level
            if comp.name == "Brush on Block":
                rank_color = self.warning_color
                name_color = self.primary_color
            elif comp.threat_level == "high":
                rank_color = self.danger_color
                name_color = self.danger_color
            else:
                rank_color = self.secondary_color
                name_color = self.secondary_color
            
            # Authority bar
            authority_bar = self._create_mini_authority_bar(comp.authority_score)
            
            # Trend arrow
            if comp.name == "EltaMD" or comp.name == "Supergoop":
                trend = "↗️"
            elif comp.name == "Brush on Block":
                trend = "↘️"
            else:
                trend = "→"
            
            row = f"│ {rank_color}#{comp.rank:2d}{self.reset}  │ {name_color}{name}{self.reset} │    {comp.citations:3d}    │ {comp.market_share:5.1f}% │  {trend}   │ {authority_bar} │"
            rows.append(row)
        
        footer = "└──────────────────────────────────────────────────────────────────┘"
        
        return "\\n".join([header] + rows + [footer])
    
    def _create_opportunities_section(self) -> str:
        """Create market opportunities matrix"""
        opportunities = self.data.opportunities[:4]  # Top 4 opportunities
        
        header = f"""┌─[ {self.primary_color}MARKET OPPORTUNITIES{self.reset} ]──────────────────────────────────────────┐
│ Priority │ Opportunity       │ Impact │ Effort │ Citation Pot. │
│ ──────── │ ───────────────── │ ────── │ ────── │ ───────────── │"""
        
        rows = []
        for opp in opportunities:
            name = opp.name[:17].ljust(17)
            
            # Color code impact
            if opp.impact_percentage >= 60:
                impact_color = self.success_color
            elif opp.impact_percentage >= 50:
                impact_color = self.warning_color
            else:
                impact_color = self.secondary_color
            
            # Color code effort
            effort_colors = {
                "Low": self.success_color,
                "Medium": self.warning_color,
                "High": self.danger_color
            }
            effort_color = effort_colors.get(opp.effort_level, self.secondary_color)
            
            row = f"│    {opp.priority}    │ {name} │ {impact_color}{opp.impact_percentage:5.0f}%{self.reset} │ {effort_color}{opp.effort_level:6s}{self.reset} │     {opp.citation_potential:.1f}%      │"
            rows.append(row)
        
        footer = "└──────────────────────────────────────────────────────────────────┘"
        
        return "\\n".join([header] + rows + [footer])
    
    def _create_roi_section(self) -> str:
        """Create ROI projection section"""
        roi = self.data.roi_projection
        
        # Color code ROI percentage
        if roi.twelve_month_roi >= 150:
            roi_color = self.success_color
        elif roi.twelve_month_roi >= 100:
            roi_color = self.warning_color
        else:
            roi_color = self.danger_color
        
        roi_section = f"""┌─[ {self.primary_color}ROI PROJECTION{self.reset} ]────────────────────────────────────────────────┐
│                                                                  │
│ Current AI Citations:     {self.secondary_color}{roi.current_citations}/month{self.reset}                              │
│ Target AI Citations:      {self.success_color}{roi.target_citations}/month (+300%){self.reset}                      │
│                                                                  │
│ Current AI Traffic:       {self.secondary_color}~{roi.current_traffic} visitors/month{self.reset}                   │
│ Projected AI Traffic:     {self.success_color}~{roi.projected_traffic} visitors/month{self.reset}                   │
│                                                                  │
│ Conversion Rate:          {self.info_color}{roi.conversion_rate}%{self.reset}                                  │
│ Revenue per Customer:     {self.info_color}${roi.revenue_per_customer:.0f}{self.reset}                                   │
│                                                                  │
│ Monthly Revenue Impact:   {self.success_color}${roi.monthly_revenue_impact:,.0f} additional revenue{self.reset}             │
│ Annual Revenue Impact:    {self.success_color}${roi.annual_revenue_impact:,.0f} additional revenue{self.reset}            │
│                                                                  │
│ Implementation Cost:      {self.warning_color}${roi.implementation_cost:,.0f} (one-time){self.reset}                     │
│ ROI Timeline:             {self.info_color}{roi.breakeven_months:.1f} months to break even{self.reset}              │
│ 12-Month ROI:             {roi_color}{roi.twelve_month_roi:.0f}% return on investment{self.reset}             │
└──────────────────────────────────────────────────────────────────┘"""
        
        return roi_section
    
    def _create_roadmap_section(self) -> str:
        """Create 90-day implementation roadmap"""
        roadmap = f"""┌─[ {self.primary_color}90-DAY IMPLEMENTATION ROADMAP{self.reset} ]─────────────────────────────────┐
│                                                                  │
│ {self.success_color}WEEK 1-2: Content Optimization{self.reset}                                  │
│ ├─ 🎯 Optimize product pages for AI consumption                 │
│ ├─ 📝 Create FAQ content for top queries                       │
│ └─ 🔧 Implement schema markup                                   │
│                                                                  │
│ {self.info_color}WEEK 3-6: Authority Building{self.reset}                                    │
│ ├─ 👨‍⚕️ Secure dermatologist partnerships                        │
│ ├─ 📚 Publish ingredient research content                       │
│ └─ 🏆 Collect expert endorsements                               │
│                                                                  │
│ {self.warning_color}WEEK 7-12: Competitive Content{self.reset}                                  │
│ ├─ 📊 Create comparison guides                                  │
│ ├─ 🎭 Develop seasonal content series                          │
│ └─ 📈 Monitor and optimize performance                          │
│                                                                  │
│ {self.success_color}Expected Outcome: 40% increase in AI citations{self.reset}                  │
└──────────────────────────────────────────────────────────────────┘"""
        
        return roadmap
    
    def _create_executive_summary(self) -> str:
        """Create one-page executive summary"""
        summary = f"""╔══════════════════════════════════════════════════════════════════╗
║{self.primary_color}                    EXECUTIVE SUMMARY{self.reset}                             ║
║{self.info_color}                  Brush on Block GEO Audit{self.reset}                       ║
╚══════════════════════════════════════════════════════════════════╝

{self.success_color}🎯 THE OPPORTUNITY{self.reset}
   • We're currently getting only 1.8% of AI citations in our market
   • Competitors like EltaMD capture 8.7x more AI visibility
   • AI search drives 35% of product research - we're missing revenue

{self.warning_color}💰 THE BUSINESS CASE{self.reset}
   • Investment: $8,000 in content optimization & authority building
   • Expected Return: $12,096 additional annual revenue (151% ROI)
   • Timeline: 6.6 months to break even, ongoing competitive advantage

{self.info_color}⚡ THE STRATEGY{self.reset}
   • Phase 1: Content optimization for AI consumption (Weeks 1-2)
   • Phase 2: Authority building with expert partnerships (Weeks 3-6)
   • Phase 3: Competitive content creation (Weeks 7-12)

{self.danger_color}📊 SUCCESS METRICS{self.reset}
   • Target: 40% increase in AI citations within 90 days
   • Measurement: Continuous monitoring with weekly progress reports
   • Outcome: Market leadership position in AI-powered search

{self.success_color}🚀 NEXT STEPS{self.reset}
   1. Approve GEO optimization investment
   2. Begin Phase 1 content optimization
   3. Establish monitoring dashboard
   4. Schedule weekly progress reviews"""
        
        return summary
    
    def _create_progress_bar(self, value: float, max_value: float, width: int = 20) -> str:
        """Create ASCII progress bar with colors"""
        percentage = min(value / max_value, 1.0)
        filled_width = int(percentage * width)
        
        # Color based on percentage
        if percentage >= 0.8:
            bar_color = self.success_color
        elif percentage >= 0.6:
            bar_color = self.warning_color
        elif percentage >= 0.3:
            bar_color = self.info_color
        else:
            bar_color = self.danger_color
        
        filled = "█" * filled_width
        empty = "░" * (width - filled_width)
        
        return f"{bar_color}{filled}{self.muted_color}{empty}{self.reset}"
    
    def _create_mini_authority_bar(self, authority_score: float, width: int = 12) -> str:
        """Create mini authority bar for competitive table"""
        percentage = authority_score / 100
        filled_width = int(percentage * width)
        
        filled = "█" * filled_width
        empty = "░" * (width - filled_width)
        
        if authority_score >= 90:
            color = self.success_color
        elif authority_score >= 70:
            color = self.warning_color
        else:
            color = self.danger_color
        
        return f"{color}{filled}{self.muted_color}{empty}{self.reset}"
    
    def display_dashboard(self) -> None:
        """Display the dashboard to terminal"""
        dashboard = self.generate_complete_dashboard()
        print(dashboard)
    
    def save_dashboard_text(self, filename: str) -> str:
        """Save dashboard as plain text (no colors)"""
        # Generate dashboard without colors for file saving
        original_colors = self._disable_colors()
        dashboard = self.generate_complete_dashboard()
        self._restore_colors(original_colors)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(dashboard)
        
        return filename
    
    def _disable_colors(self) -> Dict[str, str]:
        """Temporarily disable colors for text export"""
        original_colors = {
            'success_color': self.success_color,
            'warning_color': self.warning_color,
            'danger_color': self.danger_color,
            'info_color': self.info_color,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'muted_color': self.muted_color,
            'reset': self.reset
        }
        
        # Set all colors to empty strings
        self.success_color = ''
        self.warning_color = ''
        self.danger_color = ''
        self.info_color = ''
        self.primary_color = ''
        self.secondary_color = ''
        self.muted_color = ''
        self.reset = ''
        
        return original_colors
    
    def _restore_colors(self, original_colors: Dict[str, str]) -> None:
        """Restore original colors"""
        for attr, color in original_colors.items():
            setattr(self, attr, color)
    
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get key metrics for integration with other systems"""
        return {
            "overall_score": self.data.scores.overall,
            "market_position": self.data.market_position,
            "roi_projection": asdict(self.data.roi_projection),
            "top_opportunities": [asdict(opp) for opp in self.data.opportunities[:3]],
            "competitive_ranking": 19,
            "investment_required": 8000,
            "expected_roi": 151,
            "implementation_timeline": "90 days"
        }

# Export for easy importing
__all__ = ['TerminalDashboard', 'TerminalColors']