import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import statistics

from .config import get_config
from .competitor_strategy_analyzer import CompetitiveContentIntelligence, ContentStrategyScore, AuthorityAnalysis
from .market_position_tracker import MarketPositionIntelligence, MarketGapOpportunity

logger = logging.getLogger(__name__)

@dataclass
class ContentGapAnalysis:
    """Analysis of content gaps vs competitors"""
    content_area: str
    brand_current_coverage: float  # 0-100
    competitor_average_coverage: float  # 0-100
    coverage_gap: float  # Negative = behind, Positive = ahead
    top_competitor_in_area: str
    improvement_potential: float
    required_content_pieces: int

@dataclass
class TacticalRecommendation:
    """Specific tactical recommendation for competitive improvement"""
    priority: str  # "critical", "high", "medium", "low"
    category: str  # "content_creation", "authority_building", "optimization", "competitive_response"
    recommendation: str
    rationale: str
    competitor_benchmark: str
    expected_impact: str
    effort_level: str  # "low", "medium", "high"
    timeline: str  # "immediate", "short_term", "long_term"
    success_metrics: List[str]
    implementation_steps: List[str]

@dataclass
class CompetitorThreatAnalysis:
    """Analysis of competitive threats and responses"""
    threat_type: str  # "content_leadership", "authority_building", "market_expansion"
    threatening_competitor: str
    threat_description: str
    current_impact_level: str  # "low", "medium", "high", "critical"
    projected_impact: str
    recommended_response: str
    response_urgency: str

@dataclass
class StrategicOpportunityMap:
    """Strategic opportunity mapping"""
    opportunity_type: str  # "content_gap", "authority_gap", "seasonal_opportunity", "format_innovation"
    opportunity_description: str
    market_size_estimate: float
    competitive_difficulty: str  # "low", "medium", "high"
    resource_requirements: str
    expected_roi: str
    strategic_value: str

@dataclass
class StrategicInsightsReport:
    """Complete strategic insights and recommendations"""
    analysis_timestamp: str
    content_gap_analysis: List[ContentGapAnalysis]
    tactical_recommendations: List[TacticalRecommendation]
    threat_analysis: List[CompetitorThreatAnalysis]
    opportunity_map: List[StrategicOpportunityMap]
    executive_summary: Dict[str, Any]
    competitive_positioning_strategy: Dict[str, Any]
    investment_priorities: List[Dict[str, Any]]

class StrategicInsightsGenerator:
    """Advanced strategic insights generation from competitive intelligence"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.brand_name = self.config.BRAND_NAME
        
        # Load previous analysis results
        self.agent1_results = self.config.load_agent1_results()
        self.agent2_results = self.config.load_agent2_results()
        
    async def generate_strategic_insights(self, 
                                        competitive_intelligence: CompetitiveContentIntelligence,
                                        market_position_intel: MarketPositionIntelligence) -> StrategicInsightsReport:
        """Generate comprehensive strategic insights and recommendations"""
        logger.info("Generating strategic insights from competitive analysis")
        
        # Analyze content gaps vs competitors
        content_gaps = await self._analyze_content_gaps_vs_competitors(competitive_intelligence)
        
        # Generate tactical recommendations
        tactical_recommendations = await self._generate_tactical_recommendations(
            competitive_intelligence, market_position_intel, content_gaps)
        
        # Analyze competitive threats
        threat_analysis = await self._analyze_competitive_threats(competitive_intelligence)
        
        # Map strategic opportunities
        opportunity_map = await self._map_strategic_opportunities(
            market_position_intel, content_gaps)
        
        # Create executive summary
        executive_summary = self._create_executive_summary(
            competitive_intelligence, content_gaps, tactical_recommendations)
        
        # Develop competitive positioning strategy
        positioning_strategy = await self._develop_positioning_strategy(
            competitive_intelligence, market_position_intel)
        
        # Prioritize investment areas
        investment_priorities = self._prioritize_investments(
            tactical_recommendations, opportunity_map)
        
        return StrategicInsightsReport(
            analysis_timestamp=datetime.now().isoformat(),
            content_gap_analysis=content_gaps,
            tactical_recommendations=tactical_recommendations,
            threat_analysis=threat_analysis,
            opportunity_map=opportunity_map,
            executive_summary=executive_summary,
            competitive_positioning_strategy=positioning_strategy,
            investment_priorities=investment_priorities
        )
    
    async def _analyze_content_gaps_vs_competitors(self, 
                                                 competitive_intelligence: CompetitiveContentIntelligence) -> List[ContentGapAnalysis]:
        """Compare brand content depth vs competitors"""
        content_gaps = []
        
        # Extract brand content data from Agent 2 results
        brand_content_analysis = self._extract_brand_content_analysis()
        
        if not brand_content_analysis:
            logger.warning("No Agent 2 results available for brand content comparison")
            return []
        
        # Define content areas to analyze
        content_areas = [
            "ingredient_education",
            "application_guides", 
            "clinical_evidence",
            "expert_endorsements",
            "comparison_content",
            "faq_coverage",
            "product_specifications",
            "authority_signals"
        ]
        
        for area in content_areas:
            # Get brand coverage in this area
            brand_coverage = self._calculate_brand_coverage(brand_content_analysis, area)
            
            # Calculate competitor average
            competitor_scores = []
            top_competitor = None
            top_score = 0
            
            for strategy_score in competitive_intelligence.strategy_scores:
                competitor_coverage = self._calculate_competitor_coverage(strategy_score, area)
                competitor_scores.append(competitor_coverage)
                
                if competitor_coverage > top_score:
                    top_score = competitor_coverage
                    top_competitor = strategy_score.competitor
            
            competitor_average = statistics.mean(competitor_scores) if competitor_scores else 0
            coverage_gap = brand_coverage - competitor_average
            
            # Calculate improvement potential
            improvement_potential = max(0, top_score - brand_coverage)
            
            # Estimate required content pieces
            required_pieces = max(0, int(improvement_potential / 10))  # Rough estimate
            
            content_gaps.append(ContentGapAnalysis(
                content_area=area,
                brand_current_coverage=brand_coverage,
                competitor_average_coverage=competitor_average,
                coverage_gap=coverage_gap,
                top_competitor_in_area=top_competitor or "Unknown",
                improvement_potential=improvement_potential,
                required_content_pieces=required_pieces
            ))
        
        return sorted(content_gaps, key=lambda x: abs(x.coverage_gap), reverse=True)
    
    def _extract_brand_content_analysis(self) -> Optional[Dict[str, Any]]:
        """Extract brand content analysis from Agent 2 results"""
        if not self.agent2_results:
            return None
        
        # Look for content analysis data
        if 'content_analysis' in self.agent2_results:
            return self.agent2_results['content_analysis']
        elif 'brand_content_analysis' in self.agent2_results:
            return self.agent2_results['brand_content_analysis']
        else:
            return self.agent2_results  # Fallback to full results
    
    def _calculate_brand_coverage(self, brand_analysis: Dict[str, Any], content_area: str) -> float:
        """Calculate brand coverage score for specific content area"""
        
        # Map content areas to Agent 2 analysis fields
        area_mapping = {
            "ingredient_education": ["ingredient_coverage", "educational_content_score"],
            "application_guides": ["how_to_content", "application_guides"],
            "clinical_evidence": ["clinical_references", "scientific_backing"],
            "expert_endorsements": ["expert_testimonials", "authority_signals"],
            "comparison_content": ["comparison_tables", "competitive_content"],
            "faq_coverage": ["faq_content", "question_answering"],
            "product_specifications": ["product_details", "specification_completeness"],
            "authority_signals": ["authority_score", "credibility_signals"]
        }
        
        relevant_fields = area_mapping.get(content_area, [content_area])
        scores = []
        
        for field in relevant_fields:
            if field in brand_analysis:
                value = brand_analysis[field]
                if isinstance(value, (int, float)):
                    scores.append(value)
                elif isinstance(value, dict) and 'score' in value:
                    scores.append(value['score'])
        
        if scores:
            return statistics.mean(scores)
        else:
            # Fallback to overall content scores if specific fields not found
            overall_score = brand_analysis.get('overall_content_score', 50)
            return overall_score * 0.6  # Conservative estimate for specific area
    
    def _calculate_competitor_coverage(self, strategy_score: ContentStrategyScore, content_area: str) -> float:
        """Calculate competitor coverage for specific content area"""
        
        # Map content areas to strategy score components
        if content_area == "clinical_evidence":
            return strategy_score.authority_signal_score
        elif content_area == "expert_endorsements":
            return strategy_score.authority_signal_score * 1.1
        elif content_area == "ingredient_education":
            return strategy_score.content_depth_score
        elif content_area == "application_guides":
            return strategy_score.ai_optimization_score
        elif content_area == "comparison_content":
            return strategy_score.citation_worthiness_score
        elif content_area == "authority_signals":
            return strategy_score.authority_signal_score
        else:
            # General coverage estimate
            return (strategy_score.content_depth_score + strategy_score.ai_optimization_score) / 2
    
    async def _generate_tactical_recommendations(self, 
                                               competitive_intelligence: CompetitiveContentIntelligence,
                                               market_position_intel: MarketPositionIntelligence,
                                               content_gaps: List[ContentGapAnalysis]) -> List[TacticalRecommendation]:
        """Generate specific tactical recommendations"""
        recommendations = []
        
        # Critical content gap recommendations
        for gap in content_gaps:
            if gap.coverage_gap < -20:  # Significantly behind
                recommendations.append(TacticalRecommendation(
                    priority="critical",
                    category="content_creation",
                    recommendation=f"Create comprehensive {gap.content_area.replace('_', ' ')} content to close competitive gap",
                    rationale=f"Brand is {abs(gap.coverage_gap):.1f} points behind competitor average in {gap.content_area}",
                    competitor_benchmark=f"{gap.top_competitor_in_area} leads this area",
                    expected_impact=f"Close {gap.improvement_potential:.1f}% coverage gap, improve citations by 15-25%",
                    effort_level="high",
                    timeline="short_term",
                    success_metrics=[
                        f"Increase {gap.content_area} coverage to {gap.competitor_average_coverage + 10:.1f}%",
                        "Achieve parity with top competitor within 90 days"
                    ],
                    implementation_steps=[
                        f"Audit {gap.top_competitor_in_area}'s {gap.content_area} content",
                        f"Create {gap.required_content_pieces} new content pieces",
                        "Optimize for AI consumption and citation",
                        "Monitor competitive response"
                    ]
                ))
        
        # Authority building recommendations
        authority_leaders = [score for score in competitive_intelligence.strategy_scores 
                           if score.authority_signal_score > 70]
        
        if authority_leaders:
            top_authority = max(authority_leaders, key=lambda x: x.authority_signal_score)
            
            recommendations.append(TacticalRecommendation(
                priority="high",
                category="authority_building",
                recommendation="Implement systematic authority building program",
                rationale=f"{top_authority.competitor} leads with {top_authority.authority_signal_score:.1f}% authority score",
                competitor_benchmark=f"Match {top_authority.competitor}'s authority tactics: {', '.join(top_authority.strategy_strengths[:3])}",
                expected_impact="25-35% improvement in credibility signals, higher citation frequency",
                effort_level="medium",
                timeline="long_term",
                success_metrics=[
                    "Achieve 70%+ authority signal score",
                    "Secure 3+ expert endorsements",
                    "Publish 2+ clinical studies"
                ],
                implementation_steps=[
                    "Identify key industry experts for partnerships",
                    "Develop clinical study program",
                    "Create expert interview content series",
                    "Implement author credentials across all content"
                ]
            ))
        
        # Market gap opportunity recommendations
        high_opportunity_gaps = [gap for gap in market_position_intel.market_gap_opportunities 
                               if gap.opportunity_score > 70]
        
        for gap in high_opportunity_gaps[:3]:  # Top 3 opportunities
            recommendations.append(TacticalRecommendation(
                priority="high" if gap.effort_level == "low" else "medium",
                category="competitive_response",
                recommendation=f"Capture {gap.gap_type.replace('_', ' ')} opportunity",
                rationale=f"Market gap identified with {gap.opportunity_score:.1f}% opportunity score",
                competitor_benchmark=f"Competitors show weakness: {max(gap.competitor_weakness_analysis.values()) * 100:.1f}% average weakness",
                expected_impact=f"{gap.expected_citation_potential:.1f}% citation potential increase",
                effort_level=gap.effort_level,
                timeline="short_term" if gap.effort_level == "low" else "medium_term",
                success_metrics=[
                    f"Capture 60%+ of queries in cluster: {len(gap.query_cluster)} queries",
                    f"Achieve top 3 ranking in {gap.recommended_content_format} searches"
                ],
                implementation_steps=[
                    f"Create {gap.recommended_content_format} addressing query cluster",
                    f"Optimize for target keywords: {', '.join(gap.target_keywords[:3])}",
                    "Monitor competitor response and adjust strategy",
                    "Scale successful approach to related queries"
                ]
            ))
        
        # AI optimization recommendations
        ai_optimization_leaders = [score for score in competitive_intelligence.strategy_scores 
                                 if score.ai_optimization_score > 75]
        
        if ai_optimization_leaders and len(ai_optimization_leaders) < len(competitive_intelligence.strategy_scores):
            # Not everyone is optimized - opportunity exists
            recommendations.append(TacticalRecommendation(
                priority="medium",
                category="optimization",
                recommendation="Implement advanced AI consumption optimization",
                rationale="Competitors showing mixed AI optimization - opportunity to lead",
                competitor_benchmark="Exceed current leader's AI optimization approach",
                expected_impact="20-30% improvement in AI engine preference and citation frequency",
                effort_level="medium",
                timeline="immediate",
                success_metrics=[
                    "Achieve 80%+ AI optimization score",
                    "Improve structured content coverage by 50%"
                ],
                implementation_steps=[
                    "Audit all content for AI consumption patterns",
                    "Implement structured data markup",
                    "Create FAQ-style content sections",
                    "Optimize content hierarchy and formatting"
                ]
            ))
        
        return sorted(recommendations, key=lambda x: {"critical": 4, "high": 3, "medium": 2, "low": 1}[x.priority], reverse=True)
    
    async def _analyze_competitive_threats(self, competitive_intelligence: CompetitiveContentIntelligence) -> List[CompetitorThreatAnalysis]:
        """Analyze competitive threats requiring response"""
        threats = []
        
        # Content leadership threats
        content_leaders = [score for score in competitive_intelligence.strategy_scores 
                          if score.content_depth_score > 80]
        
        for leader in content_leaders:
            threats.append(CompetitorThreatAnalysis(
                threat_type="content_leadership",
                threatening_competitor=leader.competitor,
                threat_description=f"{leader.competitor} demonstrates superior content depth ({leader.content_depth_score:.1f}%) with strengths in: {', '.join(leader.strategy_strengths[:3])}",
                current_impact_level="high",
                projected_impact="Continued citation dominance in content-heavy queries",
                recommended_response="Accelerated content development program focusing on depth and comprehensiveness",
                response_urgency="high"
            ))
        
        # Authority building threats
        authority_leaders = [score for score in competitive_intelligence.strategy_scores 
                           if score.authority_signal_score > 75]
        
        for leader in authority_leaders:
            threats.append(CompetitorThreatAnalysis(
                threat_type="authority_building",
                threatening_competitor=leader.competitor,
                threat_description=f"{leader.competitor} building strong authority position ({leader.authority_signal_score:.1f}%) through systematic credibility development",
                current_impact_level="medium",
                projected_impact="Increased credibility-based citations and expert recommendation queries",
                recommended_response="Implement comprehensive authority building program with expert partnerships",
                response_urgency="medium"
            ))
        
        # Market expansion threats (based on citation patterns)
        high_citation_competitors = []
        for pattern in competitive_intelligence.citation_patterns:
            if pattern.citation_frequency > 15:  # High citation frequency
                high_citation_competitors.append(pattern.competitor)
        
        for competitor in set(high_citation_competitors):
            threats.append(CompetitorThreatAnalysis(
                threat_type="market_expansion",
                threatening_competitor=competitor,
                threat_description=f"{competitor} showing high citation velocity and market expansion potential",
                current_impact_level="medium",
                projected_impact="Potential market share erosion in key query territories",
                recommended_response="Defensive content creation in competitor's strong areas + offensive expansion into gaps",
                response_urgency="medium"
            ))
        
        return threats
    
    async def _map_strategic_opportunities(self, market_position_intel: MarketPositionIntelligence, 
                                         content_gaps: List[ContentGapAnalysis]) -> List[StrategicOpportunityMap]:
        """Map strategic opportunities for competitive advantage"""
        opportunities = []
        
        # Content gap opportunities
        significant_gaps = [gap for gap in content_gaps if gap.improvement_potential > 25]
        
        for gap in significant_gaps[:3]:  # Top 3 content opportunities
            opportunities.append(StrategicOpportunityMap(
                opportunity_type="content_gap",
                opportunity_description=f"Leadership opportunity in {gap.content_area.replace('_', ' ')}: {gap.improvement_potential:.1f}% improvement potential",
                market_size_estimate=gap.improvement_potential * 2,  # Rough market size estimate
                competitive_difficulty="medium",
                resource_requirements=f"{gap.required_content_pieces} content pieces, specialized expertise",
                expected_roi="High - direct impact on citation frequency",
                strategic_value="Establishes thought leadership in key content area"
            ))
        
        # Market gap opportunities
        for gap in market_position_intel.market_gap_opportunities[:5]:  # Top 5 market gaps
            opportunities.append(StrategicOpportunityMap(
                opportunity_type=gap.gap_type,
                opportunity_description=f"Market gap in {len(gap.query_cluster)} related queries with {gap.opportunity_score:.1f}% opportunity score",
                market_size_estimate=gap.expected_citation_potential * 10,
                competitive_difficulty=gap.effort_level,
                resource_requirements=f"{gap.recommended_content_format} creation, keyword optimization",
                expected_roi=f"Medium-High - {gap.expected_citation_potential:.1f}% citation increase potential",
                strategic_value="First-mover advantage in underserved query territory"
            ))
        
        # Seasonal opportunities
        if market_position_intel.seasonal_trends.get("opportunity_seasons"):
            opportunities.append(StrategicOpportunityMap(
                opportunity_type="seasonal_opportunity", 
                opportunity_description="Seasonal content gaps during off-peak periods",
                market_size_estimate=30.0,
                competitive_difficulty="low",
                resource_requirements="Seasonal content calendar, time-sensitive production",
                expected_roi="High - reduced competition during off-peak seasons",
                strategic_value="Year-round market presence, seasonal market capture"
            ))
        
        return opportunities
    
    def _create_executive_summary(self, competitive_intelligence: CompetitiveContentIntelligence,
                                content_gaps: List[ContentGapAnalysis],
                                tactical_recommendations: List[TacticalRecommendation]) -> Dict[str, Any]:
        """Create executive summary of strategic insights"""
        
        # Calculate key metrics
        avg_competitor_score = statistics.mean([score.overall_strategy_score 
                                              for score in competitive_intelligence.strategy_scores])
        
        critical_recommendations = [rec for rec in tactical_recommendations if rec.priority == "critical"]
        high_recommendations = [rec for rec in tactical_recommendations if rec.priority == "high"]
        
        significant_gaps = [gap for gap in content_gaps if abs(gap.coverage_gap) > 15]
        
        return {
            "competitive_landscape_summary": f"Analyzed {len(competitive_intelligence.strategy_scores)} competitors with average strategy score of {avg_competitor_score:.1f}%",
            "brand_position_assessment": "Significant improvement opportunities identified across multiple content areas",
            "priority_action_items": len(critical_recommendations) + len(high_recommendations),
            "critical_gaps_identified": len(significant_gaps),
            "investment_recommendation": "Medium to high investment in content and authority building for competitive parity",
            "timeline_urgency": "Immediate action recommended for critical gaps, 90-day timeline for competitive parity",
            "expected_outcomes": "25-40% improvement in competitive positioning within 6 months with proper execution",
            "key_focus_areas": [
                "Content depth improvement",
                "Authority signal development", 
                "Market gap capture",
                "AI optimization enhancement"
            ]
        }
    
    async def _develop_positioning_strategy(self, competitive_intelligence: CompetitiveContentIntelligence,
                                          market_position_intel: MarketPositionIntelligence) -> Dict[str, Any]:
        """Develop competitive positioning strategy"""
        
        # Analyze competitive positioning matrix
        top_performer = max(competitive_intelligence.strategy_scores, 
                           key=lambda x: x.overall_strategy_score)
        
        positioning_strategy = {
            "current_market_position": "Challenger - significant upside potential",
            "target_position": "Content and Authority Leader",
            "differentiation_strategy": {
                "primary_differentiator": "Comprehensive educational content with strong authority backing",
                "secondary_differentiators": [
                    "AI-optimized content structure",
                    "Clinical evidence integration", 
                    "Expert partnership program"
                ]
            },
            "competitive_response_strategy": {
                "defensive_actions": [
                    "Protect existing content strength areas",
                    "Monitor competitor content launches",
                    "Maintain citation frequency in core queries"
                ],
                "offensive_actions": [
                    "Capture identified market gaps",
                    "Accelerate authority building",
                    "Expand into competitor weak areas"
                ]
            },
            "market_expansion_approach": {
                "query_territory_expansion": f"Expand from {market_position_intel.baseline_queries} to {market_position_intel.query_matrix_size} queries",
                "content_format_diversification": "Add comparison tables, how-to guides, clinical summaries",
                "seasonal_optimization": "Year-round content calendar with seasonal focus areas"
            },
            "success_benchmarks": {
                "6_month_targets": [
                    f"Achieve parity with {top_performer.competitor} ({top_performer.overall_strategy_score:.1f}%)",
                    "Capture 3+ market gap opportunities",
                    "Establish authority in 2+ content areas"
                ],
                "12_month_targets": [
                    "Achieve top 3 competitive position",
                    "Lead in 2+ content categories",
                    "Maintain 15%+ citation frequency"
                ]
            }
        }
        
        return positioning_strategy
    
    def _prioritize_investments(self, tactical_recommendations: List[TacticalRecommendation],
                              opportunity_map: List[StrategicOpportunityMap]) -> List[Dict[str, Any]]:
        """Prioritize investment areas based on impact and effort"""
        
        investments = []
        
        # Critical recommendations get top priority
        critical_recs = [rec for rec in tactical_recommendations if rec.priority == "critical"]
        if critical_recs:
            investments.append({
                "investment_area": "Critical Content Gaps",
                "priority_level": "immediate",
                "resource_allocation": "40% of available resources",
                "expected_timeline": "30-60 days",
                "key_initiatives": [rec.recommendation for rec in critical_recs[:3]],
                "success_metrics": "Close critical competitive gaps, achieve content parity",
                "roi_expectation": "High - immediate competitive positioning improvement"
            })
        
        # High-impact, low-effort opportunities
        quick_wins = [rec for rec in tactical_recommendations 
                     if rec.priority == "high" and rec.effort_level == "low"]
        if quick_wins:
            investments.append({
                "investment_area": "Quick Wins & Market Gaps",
                "priority_level": "immediate",
                "resource_allocation": "25% of available resources", 
                "expected_timeline": "15-45 days",
                "key_initiatives": [rec.recommendation for rec in quick_wins],
                "success_metrics": "Capture low-competition opportunities, improve citation velocity",
                "roi_expectation": "Very High - maximum impact for minimal investment"
            })
        
        # Authority building (long-term strategic)
        authority_recs = [rec for rec in tactical_recommendations if rec.category == "authority_building"]
        if authority_recs:
            investments.append({
                "investment_area": "Authority Building Program",
                "priority_level": "strategic",
                "resource_allocation": "20% of available resources",
                "expected_timeline": "3-12 months",
                "key_initiatives": [rec.recommendation for rec in authority_recs],
                "success_metrics": "Establish expert partnerships, publish clinical evidence",
                "roi_expectation": "High - long-term competitive moat"
            })
        
        # Technology and optimization
        tech_recs = [rec for rec in tactical_recommendations if rec.category == "optimization"]
        if tech_recs:
            investments.append({
                "investment_area": "AI Optimization & Technology",
                "priority_level": "supporting",
                "resource_allocation": "15% of available resources",
                "expected_timeline": "30-90 days",
                "key_initiatives": [rec.recommendation for rec in tech_recs],
                "success_metrics": "Improve AI consumption scores, enhance citation frequency",
                "roi_expectation": "Medium-High - multiplier effect on all content"
            })
        
        return investments