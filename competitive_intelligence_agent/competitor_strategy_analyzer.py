import asyncio
import logging
import re
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import statistics
from collections import Counter, defaultdict
import json

from .config import get_config, CompetitorConfig, AuthoritySignalConfig

logger = logging.getLogger(__name__)

@dataclass
class ContentStrategyScore:
    """Comprehensive content strategy scoring for a competitor"""
    competitor: str
    content_depth_score: float
    authority_signal_score: float
    ai_optimization_score: float
    citation_worthiness_score: float
    content_freshness_score: float
    overall_strategy_score: float
    strategy_strengths: List[str]
    strategy_weaknesses: List[str]
    content_patterns: Dict[str, Any]
    authority_indicators: Dict[str, int]

@dataclass
class CitationPattern:
    """Analysis of how competitors get cited by AI engines"""
    competitor: str
    content_type: str
    citation_frequency: float
    citation_context: List[str]
    citation_quality_score: float
    ai_engine_preferences: Dict[str, float]  # openai, anthropic, google
    common_citation_triggers: List[str]

@dataclass
class AuthorityAnalysis:
    """Authority signal analysis for competitors"""
    competitor: str
    expert_endorsements: int
    clinical_study_references: int
    certification_count: int
    award_mentions: int
    authority_building_tactics: List[str]
    credibility_score: float
    trust_indicators: Dict[str, int]

@dataclass
class CompetitiveContentIntelligence:
    """Complete competitive content intelligence analysis"""
    analysis_timestamp: str
    competitors_analyzed: List[str]
    strategy_scores: List[ContentStrategyScore]
    citation_patterns: List[CitationPattern] 
    authority_analyses: List[AuthorityAnalysis]
    content_gap_opportunities: List[Dict[str, Any]]
    strategic_insights: List[str]
    competitive_positioning: Dict[str, Any]

class CompetitorStrategyAnalyzer:
    """Advanced analyzer for competitor content strategies and positioning"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.competitors = self.config.get_competitors()
        self.authority_signals = self.config.get_authority_signals()
        self.content_focus_areas = self.config.get_content_analysis_focus()
        self.analysis_weights = self.config.get_analysis_weights()
        
        # Load Agent 2 results for content comparison
        self.agent2_results = self.config.load_agent2_results()
        self.agent1_results = self.config.load_agent1_results()
        
    async def analyze_competitive_content_strategies(self) -> CompetitiveContentIntelligence:
        """Comprehensive analysis of competitor content strategies"""
        logger.info("Starting competitive content strategy analysis")
        
        strategy_scores = []
        citation_patterns = []
        authority_analyses = []
        
        # Analyze each competitor's content strategy
        for competitor in self.competitors:
            if competitor.priority in ['high', 'medium']:
                try:
                    logger.info(f"Analyzing content strategy for {competitor.name}")
                    
                    # Get competitor content data from Agent 2 integration
                    competitor_content = await self._get_competitor_content_data(competitor)
                    
                    if competitor_content:
                        # Strategy scoring
                        strategy_score = self._analyze_content_strategy(competitor, competitor_content)
                        strategy_scores.append(strategy_score)
                        
                        # Citation pattern analysis
                        citation_pattern = await self._analyze_citation_patterns(competitor, competitor_content)
                        citation_patterns.append(citation_pattern)
                        
                        # Authority signal analysis
                        authority_analysis = self._analyze_authority_signals(competitor, competitor_content)
                        authority_analyses.append(authority_analysis)
                        
                        logger.info(f"Completed analysis for {competitor.name}")
                    else:
                        logger.warning(f"No content data available for {competitor.name}")
                        
                except Exception as e:
                    logger.error(f"Error analyzing {competitor.name}: {str(e)}")
                    continue
        
        # Generate strategic insights
        strategic_insights = self._generate_strategic_insights(strategy_scores, citation_patterns, authority_analyses)
        
        # Identify content gap opportunities
        content_gaps = self._identify_content_gap_opportunities(strategy_scores, authority_analyses)
        
        # Analyze competitive positioning
        competitive_positioning = self._analyze_competitive_positioning(strategy_scores, citation_patterns)
        
        return CompetitiveContentIntelligence(
            analysis_timestamp=datetime.now().isoformat(),
            competitors_analyzed=[comp.name for comp in self.competitors if comp.priority in ['high', 'medium']],
            strategy_scores=strategy_scores,
            citation_patterns=citation_patterns,
            authority_analyses=authority_analyses,
            content_gap_opportunities=content_gaps,
            strategic_insights=strategic_insights,
            competitive_positioning=competitive_positioning
        )
    
    async def _get_competitor_content_data(self, competitor: CompetitorConfig) -> Optional[Dict[str, Any]]:
        """Retrieve competitor content data from Agent 2 results or scrape if needed"""
        
        # First, try to get data from Agent 2 results
        if self.agent2_results:
            competitor_insights = self.agent2_results.get('competitive_gap_analysis', {}).get('competitor_insights', {})
            if competitor.name in competitor_insights:
                return competitor_insights[competitor.name]
        
        # If not available, we would scrape here (simplified for this implementation)
        # For now, return mock data structure to demonstrate functionality
        
        return {
            'content_types_found': {'product_page': 10, 'ingredient_guide': 5, 'faq_page': 3},
            'unique_features': ['Expert endorsements', 'Clinical studies', 'Video content'],
            'authority_metrics': {'avg_authority_score': 75.0, 'pages_with_author_info': 8},
            'keyword_coverage_top10': {'mineral sunscreen': 15, 'zinc oxide': 12, 'dermatologist': 8}
        }
    
    def _analyze_content_strategy(self, competitor: CompetitorConfig, content_data: Dict[str, Any]) -> ContentStrategyScore:
        """Analyze individual competitor's content strategy"""
        
        # Content depth analysis
        content_depth_score = self._score_content_depth(content_data)
        
        # Authority signal scoring
        authority_signal_score = self._score_authority_signals(content_data)
        
        # AI optimization scoring
        ai_optimization_score = self._score_ai_optimization(content_data)
        
        # Citation worthiness scoring
        citation_worthiness_score = self._score_citation_worthiness(content_data)
        
        # Content freshness scoring (simplified for demo)
        content_freshness_score = 75.0  # Would analyze update patterns in full implementation
        
        # Calculate overall strategy score using configured weights
        weights = self.analysis_weights
        overall_score = (
            content_depth_score * weights.content_depth +
            authority_signal_score * weights.authority_signals +
            ai_optimization_score * weights.ai_optimization +
            citation_worthiness_score * weights.citation_worthiness +
            content_freshness_score * weights.content_freshness
        )
        
        # Identify strategy strengths and weaknesses
        strengths, weaknesses = self._identify_strategy_patterns(competitor, content_data)
        
        # Analyze content patterns
        content_patterns = self._analyze_content_patterns(content_data)
        
        # Count authority indicators
        authority_indicators = self._count_authority_indicators(content_data)
        
        return ContentStrategyScore(
            competitor=competitor.name,
            content_depth_score=content_depth_score,
            authority_signal_score=authority_signal_score,
            ai_optimization_score=ai_optimization_score,
            citation_worthiness_score=citation_worthiness_score,
            content_freshness_score=content_freshness_score,
            overall_strategy_score=overall_score,
            strategy_strengths=strengths,
            strategy_weaknesses=weaknesses,
            content_patterns=content_patterns,
            authority_indicators=authority_indicators
        )
    
    def _score_content_depth(self, content_data: Dict[str, Any]) -> float:
        """Score content depth and comprehensiveness"""
        content_types = content_data.get('content_types_found', {})
        unique_features = content_data.get('unique_features', [])
        
        # Base score from content type diversity
        type_diversity_score = min(100, len(content_types) * 15)
        
        # Bonus for comprehensive content
        comprehensive_indicators = [
            'ingredient_guide' in content_types,
            'faq_page' in content_types, 
            'product_page' in content_types,
            len(unique_features) >= 3
        ]
        comprehensiveness_bonus = sum(comprehensive_indicators) * 10
        
        return min(100, type_diversity_score + comprehensiveness_bonus)
    
    def _score_authority_signals(self, content_data: Dict[str, Any]) -> float:
        """Score authority signal implementation"""
        authority_metrics = content_data.get('authority_metrics', {})
        unique_features = content_data.get('unique_features', [])
        
        # Base score from authority metrics
        authority_score = authority_metrics.get('avg_authority_score', 0)
        
        # Bonus for authority features
        authority_features = [
            'Expert endorsements' in unique_features,
            'Clinical studies' in unique_features,
            'Dermatologist recommendations' in unique_features,
            authority_metrics.get('pages_with_author_info', 0) > 5
        ]
        
        authority_bonus = sum(authority_features) * 15
        
        return min(100, authority_score + authority_bonus)
    
    def _score_ai_optimization(self, content_data: Dict[str, Any]) -> float:
        """Score AI optimization implementation"""
        unique_features = content_data.get('unique_features', [])
        content_types = content_data.get('content_types_found', {})
        
        # AI-friendly content indicators
        ai_optimization_indicators = [
            'FAQ sections' in unique_features,
            'How-to guides' in unique_features,
            'Comparison content' in unique_features,
            'faq_page' in content_types,
            len(content_types) >= 4  # Content diversity
        ]
        
        base_score = sum(ai_optimization_indicators) * 20
        
        # Bonus for structured content
        if 'Structured data' in unique_features:
            base_score += 20
        
        return min(100, base_score)
    
    def _score_citation_worthiness(self, content_data: Dict[str, Any]) -> float:
        """Score content citation worthiness"""
        unique_features = content_data.get('unique_features', [])
        keyword_coverage = content_data.get('keyword_coverage_top10', {})
        
        # Citation-worthy content indicators
        citation_indicators = [
            'Clinical studies' in unique_features,
            'Expert endorsements' in unique_features,
            'Scientific backing' in unique_features,
            'Research data' in unique_features,
            len(keyword_coverage) >= 5  # Good keyword coverage
        ]
        
        base_score = sum(citation_indicators) * 20
        
        # Keyword usage bonus
        keyword_score = min(30, len(keyword_coverage) * 3)
        
        return min(100, base_score + keyword_score)
    
    def _identify_strategy_patterns(self, competitor: CompetitorConfig, content_data: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """Identify competitor's strategy strengths and weaknesses"""
        unique_features = content_data.get('unique_features', [])
        content_types = content_data.get('content_types_found', {})
        authority_metrics = content_data.get('authority_metrics', {})
        
        strengths = []
        weaknesses = []
        
        # Analyze based on competitor's focus areas
        for focus_area in competitor.focus_areas:
            if focus_area == "dermatologist_endorsements":
                if 'Expert endorsements' in unique_features:
                    strengths.append("Strong dermatologist endorsement strategy")
                else:
                    weaknesses.append("Lacks dermatologist endorsement content")
                    
            elif focus_area == "clinical_studies":
                if 'Clinical studies' in unique_features:
                    strengths.append("Evidence-based content with clinical backing")
                else:
                    weaknesses.append("Missing clinical study references")
                    
            elif focus_area == "ingredient_transparency":
                if 'ingredient_guide' in content_types:
                    strengths.append("Comprehensive ingredient education")
                else:
                    weaknesses.append("Limited ingredient transparency content")
        
        # General content strategy analysis
        if len(content_types) >= 5:
            strengths.append("Diverse content portfolio")
        elif len(content_types) <= 2:
            weaknesses.append("Limited content type diversity")
        
        if authority_metrics.get('avg_authority_score', 0) >= 70:
            strengths.append("High authority signal implementation")
        elif authority_metrics.get('avg_authority_score', 0) <= 40:
            weaknesses.append("Low authority signal presence")
        
        return strengths, weaknesses
    
    def _analyze_content_patterns(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze competitor's content patterns"""
        return {
            'content_type_distribution': content_data.get('content_types_found', {}),
            'unique_feature_count': len(content_data.get('unique_features', [])),
            'authority_presence': content_data.get('authority_metrics', {}).get('avg_authority_score', 0) > 50,
            'keyword_focus_areas': list(content_data.get('keyword_coverage_top10', {}).keys())[:5]
        }
    
    def _count_authority_indicators(self, content_data: Dict[str, Any]) -> Dict[str, int]:
        """Count different types of authority indicators"""
        unique_features = content_data.get('unique_features', [])
        
        return {
            'expert_endorsements': 1 if 'Expert endorsements' in unique_features else 0,
            'clinical_studies': 1 if 'Clinical studies' in unique_features else 0,
            'certifications': 1 if 'Certifications' in unique_features else 0,
            'awards': 1 if 'Awards' in unique_features else 0,
            'author_credentials': content_data.get('authority_metrics', {}).get('pages_with_author_info', 0)
        }
    
    async def _analyze_citation_patterns(self, competitor: CompetitorConfig, content_data: Dict[str, Any]) -> CitationPattern:
        """Analyze how competitor content gets cited by AI engines"""
        
        # This would integrate with Agent 1 results in full implementation
        # For now, creating representative analysis
        
        citation_frequency = self._estimate_citation_frequency(competitor, content_data)
        citation_contexts = self._identify_citation_contexts(competitor)
        citation_quality = self._assess_citation_quality(content_data)
        
        # AI engine preference analysis (would be based on Agent 1 results)
        ai_preferences = {
            'openai': citation_frequency * 0.9,  # Slight preference variation
            'anthropic': citation_frequency * 1.1,
            'google': citation_frequency * 0.8
        }
        
        # Common citation triggers
        citation_triggers = self._identify_citation_triggers(content_data)
        
        return CitationPattern(
            competitor=competitor.name,
            content_type="mixed",  # Would analyze specific content types
            citation_frequency=citation_frequency,
            citation_context=citation_contexts,
            citation_quality_score=citation_quality,
            ai_engine_preferences=ai_preferences,
            common_citation_triggers=citation_triggers
        )
    
    def _estimate_citation_frequency(self, competitor: CompetitorConfig, content_data: Dict[str, Any]) -> float:
        """Estimate citation frequency based on content quality indicators"""
        
        # Base frequency from market share
        base_frequency = competitor.market_share_estimate
        
        # Adjustments based on content quality
        authority_score = content_data.get('authority_metrics', {}).get('avg_authority_score', 0)
        unique_features = len(content_data.get('unique_features', []))
        
        # Quality multipliers
        authority_multiplier = 1 + (authority_score - 50) / 100  # Higher authority = higher citations
        feature_multiplier = 1 + (unique_features * 0.1)  # More features = more citation opportunities
        
        estimated_frequency = base_frequency * authority_multiplier * feature_multiplier
        
        return min(50, max(1, estimated_frequency))  # Cap between 1-50%
    
    def _identify_citation_contexts(self, competitor: CompetitorConfig) -> List[str]:
        """Identify common contexts where competitor gets cited"""
        contexts = []
        
        for focus_area in competitor.focus_areas:
            if focus_area == "dermatologist_endorsements":
                contexts.append("Expert recommendation queries")
            elif focus_area == "clinical_studies":
                contexts.append("Scientific evidence discussions")
            elif focus_area == "ingredient_transparency":
                contexts.append("Ingredient comparison queries")
        
        # Add general contexts
        contexts.extend([
            "Product comparison discussions",
            "Best-of-category recommendations"
        ])
        
        return contexts
    
    def _assess_citation_quality(self, content_data: Dict[str, Any]) -> float:
        """Assess quality of citations competitor receives"""
        unique_features = content_data.get('unique_features', [])
        authority_score = content_data.get('authority_metrics', {}).get('avg_authority_score', 0)
        
        # Quality indicators
        quality_indicators = [
            'Clinical studies' in unique_features,
            'Expert endorsements' in unique_features,
            authority_score >= 60,
            len(content_data.get('content_types_found', {})) >= 4
        ]
        
        base_quality = sum(quality_indicators) * 20
        authority_bonus = min(20, authority_score / 5)
        
        return min(100, base_quality + authority_bonus)
    
    def _identify_citation_triggers(self, content_data: Dict[str, Any]) -> List[str]:
        """Identify what triggers AI engines to cite this competitor"""
        triggers = []
        unique_features = content_data.get('unique_features', [])
        
        if 'Clinical studies' in unique_features:
            triggers.append("Clinical evidence mentions")
        if 'Expert endorsements' in unique_features:
            triggers.append("Professional recommendations")
        if 'ingredient_guide' in content_data.get('content_types_found', {}):
            triggers.append("Ingredient education queries")
        
        # Always add common triggers
        triggers.extend([
            "Brand comparison requests",
            "Product recommendation queries"
        ])
        
        return triggers
    
    def _analyze_authority_signals(self, competitor: CompetitorConfig, content_data: Dict[str, Any]) -> AuthorityAnalysis:
        """Comprehensive authority signal analysis"""
        unique_features = content_data.get('unique_features', [])
        authority_metrics = content_data.get('authority_metrics', {})
        
        # Count different authority types
        expert_endorsements = 1 if 'Expert endorsements' in unique_features else 0
        clinical_studies = 1 if 'Clinical studies' in unique_features else 0
        certifications = 1 if 'Certifications' in unique_features else 0
        awards = 1 if 'Awards' in unique_features else 0
        
        # Authority building tactics
        tactics = []
        for focus_area in competitor.focus_areas:
            if focus_area == "dermatologist_endorsements":
                tactics.append("Dermatologist partnership strategy")
            elif focus_area == "clinical_studies":
                tactics.append("Evidence-based marketing approach")
            elif focus_area == "ingredient_transparency":
                tactics.append("Educational authority positioning")
        
        # Calculate credibility score
        credibility_components = [
            expert_endorsements * 25,
            clinical_studies * 30,
            certifications * 20,
            awards * 15,
            min(10, authority_metrics.get('pages_with_author_info', 0))
        ]
        credibility_score = sum(credibility_components)
        
        # Trust indicators
        trust_indicators = {
            'expert_backing': expert_endorsements,
            'scientific_evidence': clinical_studies,
            'third_party_validation': certifications + awards,
            'transparency_signals': 1 if authority_metrics.get('pages_with_author_info', 0) > 0 else 0
        }
        
        return AuthorityAnalysis(
            competitor=competitor.name,
            expert_endorsements=expert_endorsements,
            clinical_study_references=clinical_studies,
            certification_count=certifications,
            award_mentions=awards,
            authority_building_tactics=tactics,
            credibility_score=min(100, credibility_score),
            trust_indicators=trust_indicators
        )
    
    def _generate_strategic_insights(self, strategy_scores: List[ContentStrategyScore], 
                                   citation_patterns: List[CitationPattern],
                                   authority_analyses: List[AuthorityAnalysis]) -> List[str]:
        """Generate strategic insights from competitive analysis"""
        insights = []
        
        if not strategy_scores:
            return ["No competitor data available for strategic analysis"]
        
        # Identify top performer
        top_performer = max(strategy_scores, key=lambda x: x.overall_strategy_score)
        insights.append(f"{top_performer.competitor} leads with overall strategy score of {top_performer.overall_strategy_score:.1f}")
        
        # Authority signal analysis
        avg_authority_score = statistics.mean([score.authority_signal_score for score in strategy_scores])
        high_authority_competitors = [score.competitor for score in strategy_scores if score.authority_signal_score > avg_authority_score + 10]
        
        if high_authority_competitors:
            insights.append(f"Authority leaders: {', '.join(high_authority_competitors)} excel in credibility signals")
        
        # Content depth analysis
        content_leaders = [score.competitor for score in strategy_scores if score.content_depth_score >= 80]
        if content_leaders:
            insights.append(f"Content depth leaders: {', '.join(content_leaders)} provide comprehensive coverage")
        
        # Citation frequency insights
        if citation_patterns:
            avg_citation_freq = statistics.mean([pattern.citation_frequency for pattern in citation_patterns])
            top_cited = [pattern.competitor for pattern in citation_patterns if pattern.citation_frequency > avg_citation_freq]
            
            if top_cited:
                insights.append(f"High citation frequency: {', '.join(top_cited)} get referenced more often by AI engines")
        
        # Common success patterns
        all_strengths = []
        for score in strategy_scores:
            all_strengths.extend(score.strategy_strengths)
        
        common_strengths = [strength for strength, count in Counter(all_strengths).items() if count >= 2]
        if common_strengths:
            insights.append(f"Common success patterns: {', '.join(common_strengths[:3])}")
        
        return insights
    
    def _identify_content_gap_opportunities(self, strategy_scores: List[ContentStrategyScore],
                                          authority_analyses: List[AuthorityAnalysis]) -> List[Dict[str, Any]]:
        """Identify content gap opportunities based on competitor analysis"""
        opportunities = []
        
        if not strategy_scores:
            return opportunities
        
        # Analyze common weaknesses
        all_weaknesses = []
        for score in strategy_scores:
            all_weaknesses.extend(score.strategy_weaknesses)
        
        common_weaknesses = Counter(all_weaknesses)
        
        for weakness, count in common_weaknesses.most_common(5):
            if count >= 2:  # Multiple competitors have this weakness
                opportunities.append({
                    "gap_type": "market_weakness",
                    "description": weakness,
                    "competitors_affected": count,
                    "opportunity_score": count * 20,
                    "recommendation": f"Address '{weakness}' to gain competitive advantage"
                })
        
        # Authority signal gaps
        low_authority_competitors = [score.competitor for score in strategy_scores if score.authority_signal_score < 50]
        if len(low_authority_competitors) >= 2:
            opportunities.append({
                "gap_type": "authority_gap",
                "description": "Low authority signal presence across multiple competitors",
                "competitors_affected": len(low_authority_competitors),
                "opportunity_score": 85,
                "recommendation": "Invest heavily in authority building - clinical studies, expert partnerships"
            })
        
        # Content depth opportunities
        shallow_content_competitors = [score.competitor for score in strategy_scores if score.content_depth_score < 60]
        if len(shallow_content_competitors) >= 2:
            opportunities.append({
                "gap_type": "content_depth",
                "description": "Opportunity for comprehensive content leadership",
                "competitors_affected": len(shallow_content_competitors),
                "opportunity_score": 70,
                "recommendation": "Create most comprehensive ingredient and application guides in market"
            })
        
        return sorted(opportunities, key=lambda x: x["opportunity_score"], reverse=True)
    
    def _analyze_competitive_positioning(self, strategy_scores: List[ContentStrategyScore],
                                       citation_patterns: List[CitationPattern]) -> Dict[str, Any]:
        """Analyze overall competitive positioning landscape"""
        
        if not strategy_scores:
            return {"error": "No strategy scores available for positioning analysis"}
        
        # Market leaders by different dimensions
        positioning = {
            "content_depth_leader": max(strategy_scores, key=lambda x: x.content_depth_score).competitor,
            "authority_leader": max(strategy_scores, key=lambda x: x.authority_signal_score).competitor,
            "ai_optimization_leader": max(strategy_scores, key=lambda x: x.ai_optimization_score).competitor,
            "overall_leader": max(strategy_scores, key=lambda x: x.overall_strategy_score).competitor
        }
        
        # Market positioning matrix
        positioning["competitive_matrix"] = []
        for score in strategy_scores:
            positioning["competitive_matrix"].append({
                "competitor": score.competitor,
                "authority_signals": score.authority_signal_score,
                "content_depth": score.content_depth_score,
                "overall_score": score.overall_strategy_score,
                "market_position": self._determine_market_position(score)
            })
        
        # Citation dominance
        if citation_patterns:
            citation_leader = max(citation_patterns, key=lambda x: x.citation_frequency)
            positioning["citation_leader"] = citation_leader.competitor
            positioning["avg_citation_frequency"] = statistics.mean([p.citation_frequency for p in citation_patterns])
        
        # Competitive gaps and opportunities
        avg_overall_score = statistics.mean([score.overall_strategy_score for score in strategy_scores])
        positioning["market_average_score"] = avg_overall_score
        positioning["underperformers"] = [score.competitor for score in strategy_scores if score.overall_strategy_score < avg_overall_score - 10]
        positioning["leaders"] = [score.competitor for score in strategy_scores if score.overall_strategy_score > avg_overall_score + 10]
        
        return positioning
    
    def _determine_market_position(self, strategy_score: ContentStrategyScore) -> str:
        """Determine competitive market position based on strategy score"""
        overall = strategy_score.overall_strategy_score
        authority = strategy_score.authority_signal_score
        content = strategy_score.content_depth_score
        
        if overall >= 80:
            return "Market Leader"
        elif overall >= 65 and authority >= 70:
            return "Authority Challenger"
        elif overall >= 65 and content >= 75:
            return "Content Leader"
        elif overall >= 50:
            return "Competitive Contender"
        else:
            return "Market Follower"