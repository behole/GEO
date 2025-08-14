from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import statistics
from datetime import datetime

from response_analyzer import ResponseAnalysis, Citation

@dataclass
class ScoreBreakdown:
    """Detailed breakdown of score calculation"""
    component_scores: Dict[str, float]
    raw_metrics: Dict[str, Any]
    weight_distribution: Dict[str, float]
    total_score: float
    confidence: float

@dataclass
class BaselineScores:
    """Complete set of baseline scores"""
    discovery_score: ScoreBreakdown
    context_score: ScoreBreakdown
    competitive_score: ScoreBreakdown
    overall_score: float
    calculation_timestamp: str
    data_quality_score: float

class DiscoveryScoreCalculator:
    """Calculator for Discovery Score (0-100)"""
    
    # Weight distribution for discovery score components
    WEIGHTS = {
        "citation_rate": 0.50,      # 50% - How often you're cited
        "position_quality": 0.30,   # 30% - Average position in citations
        "context_quality": 0.20     # 20% - Quality of citation context
    }
    
    @classmethod
    def calculate(cls, analyses: List[ResponseAnalysis]) -> ScoreBreakdown:
        """Calculate discovery score from response analyses"""
        if not analyses:
            return cls._create_empty_score()
        
        # Filter successful analyses
        successful_analyses = [a for a in analyses if a.response_text]
        total_queries = len(successful_analyses)
        
        if total_queries == 0:
            return cls._create_empty_score()
        
        # Component 1: Citation Rate (50%)
        your_brand_citations = sum(1 for a in successful_analyses if a.your_brand_mentioned)
        citation_rate = your_brand_citations / total_queries
        citation_rate_score = citation_rate * 100
        
        # Component 2: Position Quality (30%)
        your_brand_positions = []
        for analysis in successful_analyses:
            if analysis.your_brand_mentioned and analysis.citations:
                your_citations = [c for c in analysis.citations if c.brand == "your_brand"]
                if your_citations:
                    avg_position = statistics.mean(c.position for c in your_citations)
                    your_brand_positions.append(avg_position)
        
        if your_brand_positions:
            avg_position = statistics.mean(your_brand_positions)
            # Convert position to score (lower position = higher score)
            # Assuming max 10 positions, position 1 = 100%, position 10+ = 0%
            position_quality_score = max(0, (11 - avg_position) * 10)
        else:
            position_quality_score = 0
        
        # Component 3: Context Quality (20%)
        positive_contexts = 0
        total_contexts = 0
        
        for analysis in successful_analyses:
            if analysis.your_brand_mentioned:
                your_citations = [c for c in analysis.citations if c.brand == "your_brand"]
                for citation in your_citations:
                    total_contexts += 1
                    if citation.sentiment == "positive":
                        positive_contexts += 1
        
        if total_contexts > 0:
            context_quality_score = (positive_contexts / total_contexts) * 100
        else:
            context_quality_score = 0
        
        # Calculate weighted final score
        final_score = (
            citation_rate_score * cls.WEIGHTS["citation_rate"] +
            position_quality_score * cls.WEIGHTS["position_quality"] +
            context_quality_score * cls.WEIGHTS["context_quality"]
        )
        
        # Calculate confidence based on data volume
        confidence = min(1.0, total_queries / 50)  # Full confidence at 50+ queries
        
        return ScoreBreakdown(
            component_scores={
                "citation_rate": citation_rate_score,
                "position_quality": position_quality_score,
                "context_quality": context_quality_score
            },
            raw_metrics={
                "total_queries": total_queries,
                "your_brand_citations": your_brand_citations,
                "citation_rate": citation_rate,
                "avg_position": statistics.mean(your_brand_positions) if your_brand_positions else None,
                "positive_contexts": positive_contexts,
                "total_contexts": total_contexts
            },
            weight_distribution=cls.WEIGHTS,
            total_score=final_score,
            confidence=confidence
        )
    
    @classmethod
    def _create_empty_score(cls) -> ScoreBreakdown:
        """Create empty score for no data scenarios"""
        return ScoreBreakdown(
            component_scores={k: 0.0 for k in cls.WEIGHTS.keys()},
            raw_metrics={},
            weight_distribution=cls.WEIGHTS,
            total_score=0.0,
            confidence=0.0
        )

class ContextScoreCalculator:
    """Calculator for Context Quality Score (0-100)"""
    
    # Weight distribution for context score components
    WEIGHTS = {
        "sentiment_ratio": 0.60,        # 60% - Positive vs negative mentions
        "specificity_score": 0.25,      # 25% - Specific product mentions vs brand only
        "detail_richness": 0.15         # 15% - Detailed vs brief mentions
    }
    
    @classmethod
    def calculate(cls, analyses: List[ResponseAnalysis]) -> ScoreBreakdown:
        """Calculate context quality score from response analyses"""
        if not analyses:
            return cls._create_empty_score()
        
        # Get all your brand citations
        your_citations = []
        for analysis in analyses:
            your_citations.extend([c for c in analysis.citations if c.brand == "your_brand"])
        
        if not your_citations:
            return cls._create_empty_score()
        
        # Component 1: Sentiment Ratio (60%)
        positive_mentions = sum(1 for c in your_citations if c.sentiment == "positive")
        negative_mentions = sum(1 for c in your_citations if c.sentiment == "negative")
        neutral_mentions = sum(1 for c in your_citations if c.sentiment == "neutral")
        total_mentions = len(your_citations)
        
        # Calculate sentiment score (positive weight higher, negative penalized)
        sentiment_score = ((positive_mentions * 1.0) + (neutral_mentions * 0.5) + (negative_mentions * 0.0)) / total_mentions * 100
        
        # Component 2: Specificity Score (25%)
        product_specific_mentions = sum(1 for c in your_citations if c.product is not None)
        specificity_score = (product_specific_mentions / total_mentions) * 100
        
        # Component 3: Detail Richness (15%)
        detailed_mentions = sum(1 for c in your_citations if len(c.context) > 50)  # Arbitrary threshold
        detail_score = (detailed_mentions / total_mentions) * 100
        
        # Calculate weighted final score
        final_score = (
            sentiment_score * cls.WEIGHTS["sentiment_ratio"] +
            specificity_score * cls.WEIGHTS["specificity_score"] +
            detail_score * cls.WEIGHTS["detail_richness"]
        )
        
        # Calculate confidence based on citation volume
        confidence = min(1.0, total_mentions / 20)  # Full confidence at 20+ citations
        
        return ScoreBreakdown(
            component_scores={
                "sentiment_ratio": sentiment_score,
                "specificity_score": specificity_score,
                "detail_richness": detail_score
            },
            raw_metrics={
                "total_mentions": total_mentions,
                "positive_mentions": positive_mentions,
                "negative_mentions": negative_mentions,
                "neutral_mentions": neutral_mentions,
                "product_specific_mentions": product_specific_mentions,
                "detailed_mentions": detailed_mentions
            },
            weight_distribution=cls.WEIGHTS,
            total_score=final_score,
            confidence=confidence
        )
    
    @classmethod
    def _create_empty_score(cls) -> ScoreBreakdown:
        """Create empty score for no data scenarios"""
        return ScoreBreakdown(
            component_scores={k: 0.0 for k in cls.WEIGHTS.keys()},
            raw_metrics={},
            weight_distribution=cls.WEIGHTS,
            total_score=0.0,
            confidence=0.0
        )

class CompetitiveScoreCalculator:
    """Calculator for Competitive Position Score (0-100)"""
    
    # Weight distribution for competitive score components
    WEIGHTS = {
        "first_position_rate": 0.50,    # 50% - How often you're mentioned first
        "market_share": 0.30,           # 30% - Your mentions vs competitor mentions
        "unique_visibility": 0.20       # 20% - Queries where only you appear
    }
    
    @classmethod
    def calculate(cls, analyses: List[ResponseAnalysis]) -> ScoreBreakdown:
        """Calculate competitive position score from response analyses"""
        if not analyses:
            return cls._create_empty_score()
        
        # Filter successful analyses with citations
        analyses_with_citations = [a for a in analyses if a.citations]
        total_query_opportunities = len(analyses_with_citations)
        
        if total_query_opportunities == 0:
            return cls._create_empty_score()
        
        # Component 1: First Position Rate (50%)
        first_position_count = 0
        your_brand_in_results = 0
        
        for analysis in analyses_with_citations:
            your_citations = [c for c in analysis.citations if c.brand == "your_brand"]
            if your_citations:
                your_brand_in_results += 1
                # Check if you have the earliest position
                your_min_position = min(c.position for c in your_citations)
                all_min_position = min(c.position for c in analysis.citations)
                if your_min_position == all_min_position:
                    first_position_count += 1
        
        first_position_rate = (first_position_count / your_brand_in_results) * 100 if your_brand_in_results > 0 else 0
        
        # Component 2: Market Share (30%)
        total_your_mentions = sum(len([c for c in a.citations if c.brand == "your_brand"]) for a in analyses)
        total_competitor_mentions = sum(len([c for c in a.citations if c.brand != "your_brand"]) for a in analyses)
        total_mentions = total_your_mentions + total_competitor_mentions
        
        market_share_score = (total_your_mentions / total_mentions) * 100 if total_mentions > 0 else 0
        
        # Component 3: Unique Visibility (20%)
        unique_queries = 0
        
        for analysis in analyses:
            your_mentioned = any(c.brand == "your_brand" for c in analysis.citations)
            competitors_mentioned = any(c.brand != "your_brand" for c in analysis.citations)
            
            if your_mentioned and not competitors_mentioned:
                unique_queries += 1
        
        unique_visibility_score = (unique_queries / len(analyses)) * 100
        
        # Calculate weighted final score
        final_score = (
            first_position_rate * cls.WEIGHTS["first_position_rate"] +
            market_share_score * cls.WEIGHTS["market_share"] +
            unique_visibility_score * cls.WEIGHTS["unique_visibility"]
        )
        
        # Calculate confidence based on competitive data volume
        confidence = min(1.0, your_brand_in_results / 10)  # Full confidence at 10+ competitive appearances
        
        return ScoreBreakdown(
            component_scores={
                "first_position_rate": first_position_rate,
                "market_share": market_share_score,
                "unique_visibility": unique_visibility_score
            },
            raw_metrics={
                "total_query_opportunities": total_query_opportunities,
                "your_brand_in_results": your_brand_in_results,
                "first_position_count": first_position_count,
                "total_your_mentions": total_your_mentions,
                "total_competitor_mentions": total_competitor_mentions,
                "unique_queries": unique_queries
            },
            weight_distribution=cls.WEIGHTS,
            total_score=final_score,
            confidence=confidence
        )
    
    @classmethod
    def _create_empty_score(cls) -> ScoreBreakdown:
        """Create empty score for no data scenarios"""
        return ScoreBreakdown(
            component_scores={k: 0.0 for k in cls.WEIGHTS.keys()},
            raw_metrics={},
            weight_distribution=cls.WEIGHTS,
            total_score=0.0,
            confidence=0.0
        )

class DataQualityCalculator:
    """Calculator for overall data quality score"""
    
    @classmethod
    def calculate(cls, analyses: List[ResponseAnalysis]) -> float:
        """Calculate data quality score based on response completeness and richness"""
        if not analyses:
            return 0.0
        
        total_responses = len(analyses)
        successful_responses = len([a for a in analyses if a.response_text])
        responses_with_citations = len([a for a in analyses if a.citations])
        responses_with_recommendations = len([a for a in analyses if a.contains_recommendations])
        
        # Calculate individual quality metrics
        success_rate = successful_responses / total_responses
        citation_rate = responses_with_citations / total_responses
        recommendation_rate = responses_with_recommendations / total_responses
        
        # Average response quality
        avg_response_quality = statistics.mean(a.response_quality for a in analyses if a.response_text) if successful_responses > 0 else 0
        
        # Weighted data quality score
        data_quality = (
            success_rate * 0.40 +           # 40% - API success rate
            citation_rate * 0.30 +          # 30% - Citation richness
            recommendation_rate * 0.20 +    # 20% - Recommendation presence
            avg_response_quality * 0.10     # 10% - Response quality
        )
        
        return data_quality * 100

class BaselineScoreCalculator:
    """Main calculator orchestrating all scoring components"""
    
    def __init__(self):
        self.discovery_calculator = DiscoveryScoreCalculator()
        self.context_calculator = ContextScoreCalculator()
        self.competitive_calculator = CompetitiveScoreCalculator()
        self.quality_calculator = DataQualityCalculator()
    
    def calculate_baseline_scores(self, analyses: List[ResponseAnalysis]) -> BaselineScores:
        """Calculate complete baseline scores from response analyses"""
        
        # Calculate individual score components
        discovery_score = self.discovery_calculator.calculate(analyses)
        context_score = self.context_calculator.calculate(analyses)
        competitive_score = self.competitive_calculator.calculate(analyses)
        data_quality_score = self.quality_calculator.calculate(analyses)
        
        # Calculate overall score (weighted average of main components)
        overall_weights = {
            "discovery": 0.40,      # 40% - How discoverable you are
            "context": 0.35,        # 35% - Quality of mentions
            "competitive": 0.25     # 25% - Competitive position
        }
        
        overall_score = (
            discovery_score.total_score * overall_weights["discovery"] +
            context_score.total_score * overall_weights["context"] +
            competitive_score.total_score * overall_weights["competitive"]
        )
        
        return BaselineScores(
            discovery_score=discovery_score,
            context_score=context_score,
            competitive_score=competitive_score,
            overall_score=overall_score,
            calculation_timestamp=datetime.utcnow().isoformat(),
            data_quality_score=data_quality_score
        )
    
    def generate_insights(self, baseline_scores: BaselineScores) -> Dict[str, Any]:
        """Generate actionable insights from baseline scores"""
        insights = {
            "overall_assessment": self._assess_overall_performance(baseline_scores.overall_score),
            "priority_areas": self._identify_priority_areas(baseline_scores),
            "strengths": self._identify_strengths(baseline_scores),
            "weaknesses": self._identify_weaknesses(baseline_scores),
            "recommendations": self._generate_recommendations(baseline_scores),
            "data_confidence": self._assess_data_confidence(baseline_scores)
        }
        
        return insights
    
    def _assess_overall_performance(self, overall_score: float) -> str:
        """Assess overall performance level"""
        if overall_score >= 80:
            return "Excellent - Strong market presence"
        elif overall_score >= 60:
            return "Good - Solid foundation with room for improvement"
        elif overall_score >= 40:
            return "Fair - Moderate visibility, significant opportunities"
        elif overall_score >= 20:
            return "Poor - Limited visibility, major improvements needed"
        else:
            return "Critical - Minimal presence, urgent action required"
    
    def _identify_priority_areas(self, scores: BaselineScores) -> List[str]:
        """Identify priority areas for improvement"""
        priorities = []
        
        if scores.discovery_score.total_score < 30:
            priorities.append("Discovery - Increase brand visibility in AI responses")
        
        if scores.context_score.total_score < 40:
            priorities.append("Context Quality - Improve sentiment and specificity of mentions")
        
        if scores.competitive_score.total_score < 25:
            priorities.append("Competitive Position - Strengthen position vs competitors")
        
        if scores.data_quality_score < 70:
            priorities.append("Data Foundation - Improve response completeness")
        
        return priorities
    
    def _identify_strengths(self, scores: BaselineScores) -> List[str]:
        """Identify current strengths"""
        strengths = []
        
        if scores.discovery_score.total_score >= 60:
            strengths.append("Strong brand discoverability")
        
        if scores.context_score.total_score >= 70:
            strengths.append("High-quality mention context")
        
        if scores.competitive_score.total_score >= 50:
            strengths.append("Competitive market position")
        
        return strengths
    
    def _identify_weaknesses(self, scores: BaselineScores) -> List[str]:
        """Identify current weaknesses"""
        weaknesses = []
        
        if scores.discovery_score.total_score < 40:
            weaknesses.append("Low brand discovery rate")
        
        if scores.context_score.total_score < 50:
            weaknesses.append("Poor mention context quality")
        
        if scores.competitive_score.total_score < 30:
            weaknesses.append("Weak competitive positioning")
        
        return weaknesses
    
    def _generate_recommendations(self, scores: BaselineScores) -> List[str]:
        """Generate specific recommendations"""
        recommendations = []
        
        # Discovery recommendations
        if scores.discovery_score.total_score < 50:
            recommendations.extend([
                "Increase content marketing focused on target queries",
                "Develop thought leadership content in mineral sunscreen space",
                "Optimize website content for AI training data inclusion"
            ])
        
        # Context recommendations
        if scores.context_score.total_score < 60:
            recommendations.extend([
                "Create detailed product specification content",
                "Develop comprehensive benefit-focused messaging",
                "Build authority through expert testimonials and reviews"
            ])
        
        # Competitive recommendations
        if scores.competitive_score.total_score < 40:
            recommendations.extend([
                "Analyze top competitor content strategies",
                "Develop unique positioning vs major brands",
                "Create comparative content highlighting advantages"
            ])
        
        return recommendations
    
    def _assess_data_confidence(self, scores: BaselineScores) -> Dict[str, Any]:
        """Assess confidence in the data and scores"""
        avg_confidence = statistics.mean([
            scores.discovery_score.confidence,
            scores.context_score.confidence,
            scores.competitive_score.confidence
        ])
        
        confidence_level = "High" if avg_confidence >= 0.8 else "Medium" if avg_confidence >= 0.5 else "Low"
        
        return {
            "average_confidence": avg_confidence,
            "confidence_level": confidence_level,
            "data_quality_score": scores.data_quality_score,
            "recommendation": "Increase query volume for higher confidence" if avg_confidence < 0.7 else "Sufficient data for reliable insights"
        }