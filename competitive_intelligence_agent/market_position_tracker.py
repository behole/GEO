import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
import statistics

from .config import get_config, CompetitorConfig, QueryExtensionConfig

logger = logging.getLogger(__name__)

@dataclass
class QueryPerformanceMetric:
    """Performance metrics for a specific query"""
    query: str
    competitor: str
    citation_rank: int
    citation_frequency: float
    context_quality_score: float
    response_dominance: float  # % of AI response dedicated to this competitor
    sentiment_score: float
    timestamp: str

@dataclass
class CompetitorQueryDominance:
    """Query territory analysis for competitors"""
    competitor: str
    dominated_queries: List[str]  # Queries where competitor ranks #1
    strong_presence_queries: List[str]  # Queries where competitor ranks 2-3
    weak_presence_queries: List[str]  # Queries where competitor ranks 4+
    query_territory_score: float
    seasonal_performance_trends: Dict[str, float]

@dataclass
class MarketGapOpportunity:
    """Identified content/market gap opportunity"""
    gap_type: str  # "underserved_query", "seasonal_gap", "content_format_gap"
    query_cluster: List[str]
    competitor_weakness_analysis: Dict[str, float]
    opportunity_score: float
    effort_level: str  # "low", "medium", "high"
    expected_citation_potential: float
    recommended_content_format: str
    target_keywords: List[str]

@dataclass
class CompetitiveRankingChange:
    """Tracking competitive ranking changes over time"""
    competitor: str
    query: str
    previous_rank: int
    current_rank: int
    rank_change: int
    citation_frequency_change: float
    factors_contributing_to_change: List[str]
    trend_direction: str  # "improving", "declining", "stable"

@dataclass
class MarketPositionIntelligence:
    """Complete market position intelligence analysis"""
    analysis_timestamp: str
    query_matrix_size: int
    baseline_queries: int
    expanded_queries: int
    competitor_dominance_analysis: List[CompetitorQueryDominance]
    market_gap_opportunities: List[MarketGapOpportunity]
    ranking_changes: List[CompetitiveRankingChange]
    seasonal_trends: Dict[str, Any]
    query_expansion_impact: Dict[str, Any]

class MarketPositionTracker:
    """Advanced market position intelligence and tracking system"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.competitors = self.config.get_competitors()
        self.query_extensions = self.config.get_query_extensions()
        self.market_intelligence_config = self.config.get_market_intelligence_config()
        
        # Load Agent 1 results for baseline
        self.agent1_results = self.config.load_agent1_results()
        self.agent2_results = self.config.load_agent2_results()
        
        # Query matrix expansion tracking
        self.base_queries = []
        self.expanded_queries = []
        self.competitor_specific_queries = []
        
    async def analyze_market_position_intelligence(self) -> MarketPositionIntelligence:
        """Comprehensive market position intelligence analysis"""
        logger.info("Starting market position intelligence analysis")
        
        # Build expanded query matrix
        query_matrix = await self._build_expanded_query_matrix()
        
        # Analyze competitor query dominance
        dominance_analysis = await self._analyze_competitor_query_dominance(query_matrix)
        
        # Identify market gap opportunities
        market_gaps = await self._identify_market_gap_opportunities(query_matrix, dominance_analysis)
        
        # Track competitive ranking changes
        ranking_changes = await self._track_competitive_ranking_changes(query_matrix)
        
        # Analyze seasonal performance patterns
        seasonal_trends = await self._analyze_seasonal_performance_patterns(query_matrix)
        
        # Calculate query expansion impact
        expansion_impact = self._calculate_query_expansion_impact(query_matrix)
        
        return MarketPositionIntelligence(
            analysis_timestamp=datetime.now().isoformat(),
            query_matrix_size=len(query_matrix),
            baseline_queries=len(self.base_queries),
            expanded_queries=len(self.expanded_queries),
            competitor_dominance_analysis=dominance_analysis,
            market_gap_opportunities=market_gaps,
            ranking_changes=ranking_changes,
            seasonal_trends=seasonal_trends,
            query_expansion_impact=expansion_impact
        )
    
    async def _build_expanded_query_matrix(self) -> List[str]:
        """Build expanded query matrix beyond Agent 1's baseline"""
        
        # Start with Agent 1 baseline queries
        self.base_queries = self._extract_baseline_queries()
        
        # Add base competitive queries
        base_competitive_queries = self.query_extensions.base_queries
        
        # Generate competitor-specific queries
        competitor_specific = self._generate_competitor_specific_queries()
        
        # Add long-tail variations
        long_tail_queries = self._generate_long_tail_variations()
        
        # Add seasonal queries
        seasonal_queries = self._generate_seasonal_queries()
        
        # Combine all query types
        all_queries = []
        all_queries.extend(self.base_queries)
        all_queries.extend(base_competitive_queries)
        all_queries.extend(competitor_specific)
        all_queries.extend(long_tail_queries)
        all_queries.extend(seasonal_queries)
        
        # Remove duplicates while preserving order
        query_matrix = list(dict.fromkeys(all_queries))
        
        # Track expansion components
        self.expanded_queries = [q for q in query_matrix if q not in self.base_queries]
        self.competitor_specific_queries = competitor_specific
        
        logger.info(f"Built query matrix: {len(self.base_queries)} baseline + {len(self.expanded_queries)} expanded = {len(query_matrix)} total")
        
        return query_matrix
    
    def _extract_baseline_queries(self) -> List[str]:
        """Extract baseline queries from Agent 1 results"""
        if not self.agent1_results:
            return [
                "mineral sunscreen",
                "zinc oxide sunscreen", 
                "dermatologist recommended sunscreen",
                "reef safe sunscreen",
                "powder sunscreen application"
            ]
        
        # Extract queries from Agent 1 results
        queries = []
        
        # Look for query data in various possible structures
        if 'queries' in self.agent1_results:
            queries.extend(self.agent1_results['queries'])
        elif 'query_results' in self.agent1_results:
            for result in self.agent1_results['query_results']:
                if 'query' in result:
                    queries.append(result['query'])
        elif 'baseline_queries' in self.agent1_results:
            queries.extend(self.agent1_results['baseline_queries'])
        
        return queries[:50] if queries else []  # Cap at 50 as mentioned in spec
    
    def _generate_competitor_specific_queries(self) -> List[str]:
        """Generate competitor-specific query variations"""
        competitor_queries = []
        brand_name = self.config.BRAND_NAME
        
        for competitor in self.competitors:
            if competitor.priority in ['high', 'medium']:
                # Direct comparison queries
                competitor_queries.extend([
                    f"{competitor.name} vs {brand_name}",
                    f"{competitor.name} vs {brand_name} sunscreen",
                    f"is {competitor.name} better than {brand_name}",
                    f"{competitor.name} or {brand_name} which is better"
                ])
                
                # Competitor analysis queries
                competitor_queries.extend([
                    f"{competitor.name} sunscreen ingredients",
                    f"{competitor.name} dermatologist reviews",
                    f"{competitor.name} clinical studies",
                    f"{competitor.name} sunscreen pros and cons"
                ])
                
                # Focus area specific queries
                for focus_area in competitor.focus_areas:
                    if focus_area == "dermatologist_endorsements":
                        competitor_queries.append(f"{competitor.name} dermatologist recommended")
                    elif focus_area == "clinical_studies":
                        competitor_queries.append(f"{competitor.name} clinical research")
                    elif focus_area == "ingredient_transparency":
                        competitor_queries.append(f"{competitor.name} ingredient list")
        
        return competitor_queries
    
    def _generate_long_tail_variations(self) -> List[str]:
        """Generate long-tail query variations"""
        long_tail_base = self.query_extensions.long_tail_variations
        
        # Add additional long-tail variations based on competitive intelligence
        additional_long_tail = [
            "best mineral sunscreen for oily acne prone sensitive skin",
            "dermatologist recommended powder sunscreen for daily use",
            "reef safe zinc oxide sunscreen without white cast",
            "non-comedogenic mineral sunscreen for face under makeup",
            "hypoallergenic sunscreen powder for children sensitive skin"
        ]
        
        return long_tail_base + additional_long_tail
    
    def _generate_seasonal_queries(self) -> List[str]:
        """Generate seasonal query variations"""
        seasonal_base = self.query_extensions.seasonal_queries
        
        # Add time-sensitive variations
        current_month = datetime.now().month
        
        seasonal_additions = []
        if 5 <= current_month <= 8:  # Summer months
            seasonal_additions.extend([
                "best sunscreen for beach vacation 2025",
                "waterproof sunscreen for swimming",
                "sunscreen for outdoor sports summer"
            ])
        elif 9 <= current_month <= 11:  # Fall months
            seasonal_additions.extend([
                "daily sunscreen for school year",
                "sunscreen for fall outdoor activities"
            ])
        elif 12 <= current_month <= 2:  # Winter months
            seasonal_additions.extend([
                "winter sunscreen for skiing",
                "daily sunscreen winter skincare routine"
            ])
        else:  # Spring months
            seasonal_additions.extend([
                "spring skincare sunscreen routine",
                "sunscreen for spring break"
            ])
        
        return seasonal_base + seasonal_additions
    
    async def _analyze_competitor_query_dominance(self, query_matrix: List[str]) -> List[CompetitorQueryDominance]:
        """Analyze which competitors dominate which query territories"""
        dominance_analysis = []
        
        for competitor in self.competitors:
            if competitor.priority in ['high', 'medium']:
                # Simulate query performance analysis (would integrate with actual AI engine testing)
                dominated_queries = []
                strong_presence_queries = []
                weak_presence_queries = []
                
                # Analyze competitor strength by focus areas
                for query in query_matrix:
                    performance_score = self._estimate_competitor_query_performance(competitor, query)
                    
                    if performance_score >= 0.8:
                        dominated_queries.append(query)
                    elif performance_score >= 0.5:
                        strong_presence_queries.append(query)
                    else:
                        weak_presence_queries.append(query)
                
                # Calculate query territory score
                territory_score = (
                    len(dominated_queries) * 3 + 
                    len(strong_presence_queries) * 1.5
                ) / len(query_matrix) * 100
                
                # Generate seasonal trends (simplified for demo)
                seasonal_trends = {
                    "summer": territory_score * 1.2,
                    "fall": territory_score * 0.9,
                    "winter": territory_score * 0.7,
                    "spring": territory_score * 1.1
                }
                
                dominance_analysis.append(CompetitorQueryDominance(
                    competitor=competitor.name,
                    dominated_queries=dominated_queries[:10],  # Top 10 for readability
                    strong_presence_queries=strong_presence_queries[:15],
                    weak_presence_queries=weak_presence_queries[:5],
                    query_territory_score=territory_score,
                    seasonal_performance_trends=seasonal_trends
                ))
        
        return sorted(dominance_analysis, key=lambda x: x.query_territory_score, reverse=True)
    
    def _estimate_competitor_query_performance(self, competitor: CompetitorConfig, query: str) -> float:
        """Estimate competitor performance on a specific query"""
        base_performance = competitor.market_share_estimate / 100
        
        # Boost performance for queries matching competitor's focus areas
        for focus_area in competitor.focus_areas:
            if focus_area == "dermatologist_endorsements" and any(term in query.lower() for term in ["dermatologist", "doctor", "expert"]):
                base_performance *= 1.5
            elif focus_area == "clinical_studies" and any(term in query.lower() for term in ["clinical", "study", "research", "proven"]):
                base_performance *= 1.4
            elif focus_area == "ingredient_transparency" and any(term in query.lower() for term in ["ingredient", "formula", "zinc", "titanium"]):
                base_performance *= 1.3
        
        # Boost for competitor-specific queries
        if competitor.name.lower() in query.lower():
            base_performance *= 1.8
        
        return min(1.0, base_performance)
    
    async def _identify_market_gap_opportunities(self, query_matrix: List[str], 
                                               dominance_analysis: List[CompetitorQueryDominance]) -> List[MarketGapOpportunity]:
        """Identify content gap opportunities where no competitor dominates"""
        opportunities = []
        
        # Create competitor query coverage map
        competitor_coverage = defaultdict(list)
        for analysis in dominance_analysis:
            for query in analysis.dominated_queries + analysis.strong_presence_queries:
                competitor_coverage[query].append(analysis.competitor)
        
        # Find underserved queries
        underserved_queries = []
        for query in query_matrix:
            if len(competitor_coverage.get(query, [])) <= 1:  # 0-1 competitors have strong presence
                underserved_queries.append(query)
        
        # Group related underserved queries into opportunities
        query_clusters = self._cluster_related_queries(underserved_queries)
        
        for cluster_queries in query_clusters:
            if len(cluster_queries) >= 2:  # Meaningful cluster size
                # Analyze why competitors are weak in this area
                weakness_analysis = {}
                for analysis in dominance_analysis:
                    weak_count = sum(1 for q in cluster_queries if q in analysis.weak_presence_queries)
                    weakness_analysis[analysis.competitor] = weak_count / len(cluster_queries)
                
                # Calculate opportunity score
                opportunity_score = self._calculate_opportunity_score(cluster_queries, weakness_analysis)
                
                # Determine content format and keywords
                content_format = self._recommend_content_format(cluster_queries)
                target_keywords = self._extract_target_keywords(cluster_queries)
                
                opportunities.append(MarketGapOpportunity(
                    gap_type="underserved_query",
                    query_cluster=cluster_queries,
                    competitor_weakness_analysis=weakness_analysis,
                    opportunity_score=opportunity_score,
                    effort_level=self._estimate_effort_level(cluster_queries, content_format),
                    expected_citation_potential=opportunity_score * 0.15,  # 15% of opportunity score
                    recommended_content_format=content_format,
                    target_keywords=target_keywords
                ))
        
        # Add seasonal gap opportunities
        seasonal_gaps = self._identify_seasonal_gaps(query_matrix, dominance_analysis)
        opportunities.extend(seasonal_gaps)
        
        # Add content format gaps
        format_gaps = self._identify_content_format_gaps()
        opportunities.extend(format_gaps)
        
        return sorted(opportunities, key=lambda x: x.opportunity_score, reverse=True)[:20]  # Top 20
    
    def _cluster_related_queries(self, queries: List[str]) -> List[List[str]]:
        """Cluster related queries together for opportunity identification"""
        clusters = []
        processed_queries = set()
        
        for query in queries:
            if query in processed_queries:
                continue
                
            # Find related queries using keyword overlap
            cluster = [query]
            query_words = set(query.lower().split())
            
            for other_query in queries:
                if other_query != query and other_query not in processed_queries:
                    other_words = set(other_query.lower().split())
                    overlap = len(query_words & other_words) / len(query_words | other_words)
                    
                    if overlap >= 0.4:  # 40% word overlap threshold
                        cluster.append(other_query)
                        processed_queries.add(other_query)
            
            processed_queries.add(query)
            clusters.append(cluster)
        
        return [cluster for cluster in clusters if len(cluster) >= 2]
    
    def _calculate_opportunity_score(self, cluster_queries: List[str], weakness_analysis: Dict[str, float]) -> float:
        """Calculate opportunity score for a query cluster"""
        # Base score from cluster size
        cluster_size_score = min(50, len(cluster_queries) * 8)
        
        # Weakness score (higher weakness = higher opportunity)
        avg_weakness = statistics.mean(weakness_analysis.values()) if weakness_analysis else 0.5
        weakness_score = avg_weakness * 30
        
        # Query importance score (based on keywords)
        importance_keywords = ["dermatologist", "best", "recommended", "safe", "clinical"]
        importance_score = 0
        for query in cluster_queries:
            importance_score += sum(2 for keyword in importance_keywords if keyword in query.lower())
        importance_score = min(20, importance_score)
        
        return cluster_size_score + weakness_score + importance_score
    
    def _recommend_content_format(self, cluster_queries: List[str]) -> str:
        """Recommend content format for addressing query cluster"""
        query_text = " ".join(cluster_queries).lower()
        
        if any(term in query_text for term in ["vs", "versus", "compare", "comparison"]):
            return "comparison_table"
        elif any(term in query_text for term in ["how", "guide", "steps", "apply"]):
            return "how_to_guide"
        elif any(term in query_text for term in ["best", "top", "recommended"]):
            return "ranked_list"
        elif any(term in query_text for term in ["ingredient", "contains", "formula"]):
            return "ingredient_breakdown"
        else:
            return "comprehensive_article"
    
    def _extract_target_keywords(self, cluster_queries: List[str]) -> List[str]:
        """Extract target keywords from query cluster"""
        all_words = []
        for query in cluster_queries:
            all_words.extend(query.lower().split())
        
        # Count word frequency and filter meaningful keywords
        word_counts = Counter(all_words)
        
        # Filter out common words
        stop_words = {"for", "the", "and", "or", "of", "in", "to", "a", "an", "is", "best", "good"}
        keywords = [word for word, count in word_counts.most_common(10) 
                   if word not in stop_words and len(word) > 3]
        
        return keywords[:5]  # Top 5 keywords
    
    def _estimate_effort_level(self, cluster_queries: List[str], content_format: str) -> str:
        """Estimate effort level for addressing opportunity"""
        if content_format == "comparison_table":
            return "medium"
        elif content_format == "how_to_guide":
            return "medium"
        elif len(cluster_queries) >= 5:
            return "high"
        else:
            return "low"
    
    def _identify_seasonal_gaps(self, query_matrix: List[str], 
                              dominance_analysis: List[CompetitorQueryDominance]) -> List[MarketGapOpportunity]:
        """Identify seasonal performance gaps"""
        seasonal_gaps = []
        
        # Analyze seasonal query performance
        seasonal_queries = [q for q in query_matrix if any(season in q.lower() 
                           for season in ["summer", "winter", "beach", "ski", "vacation"])]
        
        if seasonal_queries:
            # Calculate seasonal weakness
            weakness_analysis = {}
            for analysis in dominance_analysis:
                seasonal_weakness = 0
                for season, performance in analysis.seasonal_performance_trends.items():
                    if performance < 30:  # Below 30% territory score
                        seasonal_weakness += 1
                weakness_analysis[analysis.competitor] = seasonal_weakness / 4
            
            if statistics.mean(weakness_analysis.values()) > 0.3:  # General seasonal weakness
                seasonal_gaps.append(MarketGapOpportunity(
                    gap_type="seasonal_gap",
                    query_cluster=seasonal_queries,
                    competitor_weakness_analysis=weakness_analysis,
                    opportunity_score=65.0,
                    effort_level="medium",
                    expected_citation_potential=9.75,
                    recommended_content_format="seasonal_content_series",
                    target_keywords=["seasonal", "summer", "winter", "vacation", "outdoor"]
                ))
        
        return seasonal_gaps
    
    def _identify_content_format_gaps(self) -> List[MarketGapOpportunity]:
        """Identify content format gaps from Agent 2 analysis"""
        format_gaps = []
        
        if self.agent2_results:
            # Look for format gaps in Agent 2 results
            content_gaps = self.agent2_results.get('competitive_gap_analysis', {}).get('content_gaps', [])
            
            for gap in content_gaps:
                if gap.get('gap_type') == 'format_gap':
                    format_gaps.append(MarketGapOpportunity(
                        gap_type="content_format_gap",
                        query_cluster=gap.get('related_queries', []),
                        competitor_weakness_analysis=gap.get('competitor_analysis', {}),
                        opportunity_score=gap.get('opportunity_score', 50.0),
                        effort_level=gap.get('effort_level', 'medium'),
                        expected_citation_potential=gap.get('opportunity_score', 50.0) * 0.12,
                        recommended_content_format=gap.get('recommended_format', 'comprehensive_article'),
                        target_keywords=gap.get('target_keywords', [])
                    ))
        
        return format_gaps
    
    async def _track_competitive_ranking_changes(self, query_matrix: List[str]) -> List[CompetitiveRankingChange]:
        """Track competitive ranking changes over time (simulated for demo)"""
        ranking_changes = []
        
        # This would integrate with historical data in a full implementation
        # For demonstration, we'll simulate some ranking change scenarios
        
        for competitor in self.competitors[:3]:  # Top 3 competitors
            for query in query_matrix[:10]:  # Sample queries
                # Simulate ranking change detection
                if competitor.name.lower() in query.lower():
                    # Competitor-specific queries likely improved
                    ranking_changes.append(CompetitiveRankingChange(
                        competitor=competitor.name,
                        query=query,
                        previous_rank=3,
                        current_rank=1,
                        rank_change=-2,
                        citation_frequency_change=+0.15,
                        factors_contributing_to_change=["Brand-specific content optimization", "Increased authority signals"],
                        trend_direction="improving"
                    ))
                elif any(focus in query.lower() for focus in competitor.focus_areas):
                    # Queries in competitor's focus area
                    ranking_changes.append(CompetitiveRankingChange(
                        competitor=competitor.name,
                        query=query,
                        previous_rank=2,
                        current_rank=1,
                        rank_change=-1,
                        citation_frequency_change=+0.08,
                        factors_contributing_to_change=["Focus area expertise", "Content depth improvement"],
                        trend_direction="improving"
                    ))
        
        return ranking_changes
    
    async def _analyze_seasonal_performance_patterns(self, query_matrix: List[str]) -> Dict[str, Any]:
        """Analyze seasonal performance patterns"""
        seasonal_analysis = {
            "seasonal_query_performance": {},
            "peak_seasons": {},
            "opportunity_seasons": {},
            "year_over_year_trends": {}
        }
        
        # Analyze seasonal queries
        seasonal_queries = {
            "summer": [q for q in query_matrix if any(term in q.lower() for term in ["summer", "beach", "vacation", "swimming"])],
            "winter": [q for q in query_matrix if any(term in q.lower() for term in ["winter", "ski", "snow"])],
            "spring": [q for q in query_matrix if any(term in q.lower() for term in ["spring"])],
            "fall": [q for q in query_matrix if any(term in q.lower() for term in ["fall", "school"])]
        }
        
        # Calculate seasonal performance (simplified)
        for season, queries in seasonal_queries.items():
            if queries:
                seasonal_analysis["seasonal_query_performance"][season] = {
                    "query_count": len(queries),
                    "avg_competitiveness": 0.6,  # Simulated
                    "opportunity_score": len(queries) * 15
                }
        
        # Identify peak and opportunity seasons
        seasonal_analysis["peak_seasons"] = ["summer", "spring"]
        seasonal_analysis["opportunity_seasons"] = ["winter", "fall"]
        
        return seasonal_analysis
    
    def _calculate_query_expansion_impact(self, query_matrix: List[str]) -> Dict[str, Any]:
        """Calculate impact of query matrix expansion"""
        expansion_impact = {
            "total_queries": len(query_matrix),
            "baseline_queries": len(self.base_queries),
            "expanded_queries": len(self.expanded_queries),
            "competitor_specific_queries": len(self.competitor_specific_queries),
            "expansion_ratio": len(self.expanded_queries) / max(1, len(self.base_queries)),
            "coverage_improvement": {
                "long_tail_coverage": len([q for q in self.expanded_queries if len(q.split()) >= 6]),
                "competitor_analysis_coverage": len(self.competitor_specific_queries),
                "seasonal_coverage": len([q for q in self.expanded_queries if any(season in q.lower() 
                                        for season in ["summer", "winter", "spring", "fall"])])
            },
            "strategic_value": "High - Comprehensive competitive landscape coverage"
        }
        
        return expansion_impact