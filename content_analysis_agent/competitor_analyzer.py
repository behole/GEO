import asyncio
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import statistics
from collections import Counter, defaultdict

from .content_scraper import ContentScraper, SiteAnalysis, PageContent
from .content_scorer import ContentScorer, SiteScore
from .config import get_config, CompetitorConfig

logger = logging.getLogger(__name__)

@dataclass
class ContentGap:
    """Represents a content gap identified through competitor analysis"""
    gap_type: str  # missing_content_type, keyword_gap, feature_gap
    description: str
    competitor_examples: List[str]  # URLs where competitors have this content
    priority: str  # high, medium, low
    estimated_effort: str  # low, medium, high
    business_impact: str  # high, medium, low
    
@dataclass
class CompetitorContentAnalysis:
    """Analysis of competitor's content"""
    competitor_name: str
    website: str
    site_analysis: SiteAnalysis
    site_score: SiteScore
    content_types_found: Dict[str, int]  # content_type -> count
    keyword_coverage: Dict[str, int]  # keyword -> frequency
    unique_content_features: List[str]
    authority_metrics: Dict[str, float]
    
@dataclass
class ContentGapAnalysis:
    """Complete content gap analysis results"""
    brand_analysis: CompetitorContentAnalysis
    competitor_analyses: List[CompetitorContentAnalysis]
    identified_gaps: List[ContentGap]
    competitive_advantages: List[str]
    priority_recommendations: List[str]
    content_opportunity_matrix: Dict[str, Dict[str, Any]]
    analysis_timestamp: str

class CompetitorAnalyzer:
    """Comprehensive competitor content analysis for gap identification"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.scraper = ContentScraper(self.config)
        self.scorer = ContentScorer(self.config)
        self.brand_config = self.config.get_brand_config()
        self.competitors = self.config.get_competitors()
        self.keywords = self.config.get_keywords()
        
    async def analyze_competitive_landscape(self, max_pages_per_site: int = 50) -> ContentGapAnalysis:
        """Perform comprehensive competitive content analysis"""
        logger.info("Starting competitive landscape analysis")
        
        # Analyze brand content first
        brand_analysis = await self._analyze_single_competitor(
            self.brand_config.name, 
            self.brand_config.website, 
            max_pages_per_site,
            is_brand=True
        )
        
        # Analyze competitors
        competitor_analyses = []
        for competitor in self.competitors:
            if competitor.priority in ['high', 'medium']:  # Focus on primary competitors
                try:
                    analysis = await self._analyze_single_competitor(
                        competitor.name, 
                        competitor.website, 
                        max_pages_per_site
                    )
                    competitor_analyses.append(analysis)
                    logger.info(f"Completed analysis for {competitor.name}")
                    
                    # Add delay between competitor analyses
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Failed to analyze {competitor.name}: {str(e)}")
                    continue
        
        # Perform gap analysis
        identified_gaps = self._identify_content_gaps(brand_analysis, competitor_analyses)
        
        # Identify competitive advantages
        competitive_advantages = self._identify_competitive_advantages(brand_analysis, competitor_analyses)
        
        # Generate priority recommendations
        priority_recommendations = self._generate_competitive_recommendations(
            brand_analysis, competitor_analyses, identified_gaps
        )
        
        # Create content opportunity matrix
        opportunity_matrix = self._create_opportunity_matrix(brand_analysis, competitor_analyses, identified_gaps)
        
        return ContentGapAnalysis(
            brand_analysis=brand_analysis,
            competitor_analyses=competitor_analyses,
            identified_gaps=identified_gaps,
            competitive_advantages=competitive_advantages,
            priority_recommendations=priority_recommendations,
            content_opportunity_matrix=opportunity_matrix,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    async def _analyze_single_competitor(self, name: str, website: str, max_pages: int, 
                                       is_brand: bool = False) -> CompetitorContentAnalysis:
        """Analyze a single competitor's content"""
        logger.info(f"Analyzing {name} ({website})")
        
        async with self.scraper:
            # Scrape website
            site_analysis = await self.scraper.scrape_website(website, max_pages)
            
            # Score content
            site_score = self.scorer.score_site(site_analysis)
            
            # Analyze content types
            content_types = self._analyze_content_types(site_analysis.pages)
            
            # Analyze keyword coverage
            keyword_coverage = self._analyze_keyword_coverage(site_analysis.pages)
            
            # Identify unique content features
            unique_features = self._identify_unique_features(site_analysis.pages, name)
            
            # Calculate authority metrics
            authority_metrics = self._calculate_authority_metrics(site_analysis.pages, site_score)
            
            return CompetitorContentAnalysis(
                competitor_name=name,
                website=website,
                site_analysis=site_analysis,
                site_score=site_score,
                content_types_found=content_types,
                keyword_coverage=keyword_coverage,
                unique_content_features=unique_features,
                authority_metrics=authority_metrics
            )
    
    def _analyze_content_types(self, pages: List[PageContent]) -> Dict[str, int]:
        """Analyze distribution of content types"""
        content_types = Counter()
        
        for page in pages:
            if page.scrape_success and page.word_count > 100:
                content_types[page.content_type] += 1
        
        return dict(content_types)
    
    def _analyze_keyword_coverage(self, pages: List[PageContent]) -> Dict[str, int]:
        """Analyze keyword coverage across content"""
        keyword_coverage = defaultdict(int)
        all_keywords = []
        
        # Collect all keywords
        for keyword_type in ['primary', 'secondary', 'long_tail']:
            all_keywords.extend(self.keywords.get(keyword_type, []))
        
        # Count keyword occurrences across all pages
        for page in pages:
            if page.scrape_success and page.clean_text:
                text_lower = page.clean_text.lower()
                for keyword in all_keywords:
                    if keyword.lower() in text_lower:
                        keyword_coverage[keyword] += text_lower.count(keyword.lower())
        
        return dict(keyword_coverage)
    
    def _identify_unique_features(self, pages: List[PageContent], competitor_name: str) -> List[str]:
        """Identify unique content features for this competitor"""
        features = []
        
        # Analyze content patterns across pages
        total_pages = len([p for p in pages if p.scrape_success])
        if total_pages == 0:
            return features
        
        # Check for common content features
        pages_with_videos = len([p for p in pages if 'video' in p.clean_text.lower()])
        pages_with_quizzes = len([p for p in pages if any(word in p.clean_text.lower() 
                                                        for word in ['quiz', 'questionnaire', 'assessment'])])
        pages_with_calculators = len([p for p in pages if any(word in p.clean_text.lower() 
                                                            for word in ['calculator', 'tool', 'estimator'])])
        pages_with_comparisons = len([p for p in pages if 'vs' in p.clean_text.lower() or 'comparison' in p.clean_text.lower()])
        
        # Identify significant features (present in >20% of pages)
        threshold = total_pages * 0.2
        
        if pages_with_videos > threshold:
            features.append("Extensive video content integration")
        if pages_with_quizzes > threshold:
            features.append("Interactive quizzes and assessments")
        if pages_with_calculators > threshold:
            features.append("Interactive tools and calculators")
        if pages_with_comparisons > threshold:
            features.append("Comprehensive product comparisons")
        
        # Check for specific sunscreen-related features
        ingredient_focus = len([p for p in pages if any(ingredient in p.clean_text.lower() 
                                                      for ingredient in ['zinc oxide', 'titanium dioxide', 'avobenzone'])])
        if ingredient_focus > threshold:
            features.append("Detailed ingredient analysis")
        
        # Check for application guides
        application_content = len([p for p in pages if any(word in p.clean_text.lower() 
                                                         for word in ['how to apply', 'application', 'reapply'])])
        if application_content > threshold:
            features.append("Comprehensive application guidance")
        
        # Check for skin type content
        skin_type_content = len([p for p in pages if any(word in p.clean_text.lower() 
                                                       for word in ['sensitive skin', 'oily skin', 'dry skin', 'acne prone'])])
        if skin_type_content > threshold:
            features.append("Skin type specific recommendations")
        
        return features
    
    def _calculate_authority_metrics(self, pages: List[PageContent], site_score: SiteScore) -> Dict[str, float]:
        """Calculate authority-related metrics"""
        if not site_score.page_scores:
            return {}
        
        metrics = {
            'avg_authority_score': statistics.mean([page.authority_signals.total_score for page in site_score.page_scores]),
            'pages_with_external_links': len([page for page in site_score.page_scores 
                                            if page.authority_signals.details.get('authority_domains_linked', 0) > 0]),
            'avg_expertise_indicators': statistics.mean([page.authority_signals.details.get('expertise_keywords', 0) 
                                                       for page in site_score.page_scores]),
            'pages_with_author_info': len([page for page in site_score.page_scores 
                                         if page.authority_signals.details.get('has_author_info', False)]),
            'avg_word_count': statistics.mean([len(page.clean_text.split()) for page in pages 
                                             if page.scrape_success and page.clean_text])
        }
        
        return metrics
    
    def _identify_content_gaps(self, brand_analysis: CompetitorContentAnalysis, 
                              competitor_analyses: List[CompetitorContentAnalysis]) -> List[ContentGap]:
        """Identify content gaps by comparing brand against competitors"""
        gaps = []
        
        # Content type gaps
        gaps.extend(self._identify_content_type_gaps(brand_analysis, competitor_analyses))
        
        # Keyword coverage gaps
        gaps.extend(self._identify_keyword_gaps(brand_analysis, competitor_analyses))
        
        # Feature gaps
        gaps.extend(self._identify_feature_gaps(brand_analysis, competitor_analyses))
        
        # Quality gaps
        gaps.extend(self._identify_quality_gaps(brand_analysis, competitor_analyses))
        
        # Prioritize gaps
        gaps = self._prioritize_gaps(gaps)
        
        return gaps
    
    def _identify_content_type_gaps(self, brand_analysis: CompetitorContentAnalysis, 
                                   competitor_analyses: List[CompetitorContentAnalysis]) -> List[ContentGap]:
        """Identify missing content types"""
        gaps = []
        brand_types = set(brand_analysis.content_types_found.keys())
        
        # Find content types that competitors have but brand doesn't
        competitor_types = set()
        for analysis in competitor_analyses:
            competitor_types.update(analysis.content_types_found.keys())
        
        missing_types = competitor_types - brand_types
        
        for content_type in missing_types:
            # Count how many competitors have this type
            competitor_count = sum(1 for analysis in competitor_analyses 
                                 if content_type in analysis.content_types_found)
            
            if competitor_count >= 2:  # At least 2 competitors have this
                competitor_examples = [
                    f"{analysis.competitor_name}: {analysis.website}"
                    for analysis in competitor_analyses
                    if content_type in analysis.content_types_found
                ][:3]  # Limit to 3 examples
                
                priority = "high" if competitor_count >= 3 else "medium"
                
                gaps.append(ContentGap(
                    gap_type="missing_content_type",
                    description=f"Missing {content_type.replace('_', ' ')} content",
                    competitor_examples=competitor_examples,
                    priority=priority,
                    estimated_effort=self._estimate_content_effort(content_type),
                    business_impact=self._estimate_business_impact(content_type)
                ))
        
        return gaps
    
    def _identify_keyword_gaps(self, brand_analysis: CompetitorContentAnalysis, 
                              competitor_analyses: List[CompetitorContentAnalysis]) -> List[ContentGap]:
        """Identify keyword coverage gaps"""
        gaps = []
        brand_keywords = brand_analysis.keyword_coverage
        
        # Analyze competitor keyword coverage
        competitor_keyword_totals = defaultdict(int)
        competitor_keyword_presence = defaultdict(int)
        
        for analysis in competitor_analyses:
            for keyword, count in analysis.keyword_coverage.items():
                if count > 0:
                    competitor_keyword_totals[keyword] += count
                    competitor_keyword_presence[keyword] += 1
        
        # Find keywords with significant competitor coverage but low brand coverage
        for keyword in competitor_keyword_totals:
            brand_count = brand_keywords.get(keyword, 0)
            competitor_avg = competitor_keyword_totals[keyword] / len(competitor_analyses)
            competitor_presence = competitor_keyword_presence[keyword]
            
            # Gap criteria: competitors use it significantly more and multiple competitors have it
            if competitor_avg > brand_count * 2 and competitor_presence >= 2:
                priority = "high" if competitor_presence >= 3 and competitor_avg > 10 else "medium"
                
                competitor_examples = [
                    f"{analysis.competitor_name}: {analysis.keyword_coverage.get(keyword, 0)} mentions"
                    for analysis in competitor_analyses
                    if analysis.keyword_coverage.get(keyword, 0) > 0
                ][:3]
                
                gaps.append(ContentGap(
                    gap_type="keyword_gap",
                    description=f"Underutilized keyword: '{keyword}' (brand: {brand_count}, competitors avg: {competitor_avg:.1f})",
                    competitor_examples=competitor_examples,
                    priority=priority,
                    estimated_effort="low",
                    business_impact="medium"
                ))
        
        return gaps
    
    def _identify_feature_gaps(self, brand_analysis: CompetitorContentAnalysis, 
                              competitor_analyses: List[CompetitorContentAnalysis]) -> List[ContentGap]:
        """Identify unique feature gaps"""
        gaps = []
        brand_features = set(brand_analysis.unique_content_features)
        
        # Find features that multiple competitors have but brand doesn't
        competitor_features = defaultdict(list)
        for analysis in competitor_analyses:
            for feature in analysis.unique_content_features:
                competitor_features[feature].append(analysis.competitor_name)
        
        for feature, competitors in competitor_features.items():
            if len(competitors) >= 2 and feature not in brand_features:
                priority = "high" if len(competitors) >= 3 else "medium"
                
                competitor_examples = [f"{comp}: {feature}" for comp in competitors[:3]]
                
                gaps.append(ContentGap(
                    gap_type="feature_gap",
                    description=f"Missing content feature: {feature}",
                    competitor_examples=competitor_examples,
                    priority=priority,
                    estimated_effort=self._estimate_feature_effort(feature),
                    business_impact=self._estimate_feature_impact(feature)
                ))
        
        return gaps
    
    def _identify_quality_gaps(self, brand_analysis: CompetitorContentAnalysis, 
                              competitor_analyses: List[CompetitorContentAnalysis]) -> List[ContentGap]:
        """Identify content quality gaps"""
        gaps = []
        
        if not competitor_analyses:
            return gaps
        
        # Compare authority scores
        brand_authority = brand_analysis.authority_metrics.get('avg_authority_score', 0)
        competitor_authority_scores = [
            analysis.authority_metrics.get('avg_authority_score', 0)
            for analysis in competitor_analyses
        ]
        avg_competitor_authority = statistics.mean(competitor_authority_scores)
        
        if avg_competitor_authority > brand_authority + 15:  # Significant gap
            top_performers = [
                analysis.competitor_name 
                for analysis in competitor_analyses
                if analysis.authority_metrics.get('avg_authority_score', 0) > brand_authority + 10
            ]
            
            gaps.append(ContentGap(
                gap_type="quality_gap",
                description=f"Authority signal gap: Brand ({brand_authority:.1f}) vs competitors ({avg_competitor_authority:.1f})",
                competitor_examples=[f"{comp}: Higher authority signals" for comp in top_performers[:3]],
                priority="high",
                estimated_effort="high",
                business_impact="high"
            ))
        
        # Compare content depth (word count)
        brand_word_count = brand_analysis.authority_metrics.get('avg_word_count', 0)
        competitor_word_counts = [
            analysis.authority_metrics.get('avg_word_count', 0)
            for analysis in competitor_analyses
        ]
        avg_competitor_words = statistics.mean(competitor_word_counts)
        
        if avg_competitor_words > brand_word_count * 1.5:  # Significantly longer content
            gaps.append(ContentGap(
                gap_type="quality_gap",
                description=f"Content depth gap: Brand ({brand_word_count:.0f} words) vs competitors ({avg_competitor_words:.0f} words)",
                competitor_examples=[f"Competitors have {avg_competitor_words/brand_word_count:.1f}x longer content"],
                priority="medium",
                estimated_effort="medium",
                business_impact="medium"
            ))
        
        return gaps
    
    def _prioritize_gaps(self, gaps: List[ContentGap]) -> List[ContentGap]:
        """Prioritize gaps based on impact and effort"""
        
        def gap_priority_score(gap: ContentGap) -> int:
            """Calculate priority score for sorting"""
            impact_scores = {"high": 3, "medium": 2, "low": 1}
            effort_scores = {"low": 3, "medium": 2, "high": 1}  # Lower effort = higher score
            priority_scores = {"high": 3, "medium": 2, "low": 1}
            
            return (
                impact_scores.get(gap.business_impact, 1) * 3 +
                effort_scores.get(gap.estimated_effort, 1) * 2 +
                priority_scores.get(gap.priority, 1) * 2
            )
        
        return sorted(gaps, key=gap_priority_score, reverse=True)
    
    def _estimate_content_effort(self, content_type: str) -> str:
        """Estimate effort required to create content type"""
        effort_map = {
            "product_page": "medium",
            "faq_page": "low",
            "blog_post": "medium",
            "ingredient_guide": "high",
            "application_guide": "medium",
            "comparison_content": "high",
            "general_page": "low"
        }
        return effort_map.get(content_type, "medium")
    
    def _estimate_business_impact(self, content_type: str) -> str:
        """Estimate business impact of content type"""
        impact_map = {
            "product_page": "high",
            "faq_page": "medium",
            "blog_post": "medium",
            "ingredient_guide": "high",
            "application_guide": "high",
            "comparison_content": "high",
            "general_page": "low"
        }
        return impact_map.get(content_type, "medium")
    
    def _estimate_feature_effort(self, feature: str) -> str:
        """Estimate effort to implement feature"""
        if "video" in feature.lower():
            return "high"
        elif "interactive" in feature.lower() or "calculator" in feature.lower():
            return "high"
        elif "quiz" in feature.lower() or "assessment" in feature.lower():
            return "medium"
        else:
            return "low"
    
    def _estimate_feature_impact(self, feature: str) -> str:
        """Estimate business impact of feature"""
        if "interactive" in feature.lower() or "calculator" in feature.lower():
            return "high"
        elif "video" in feature.lower() or "comparison" in feature.lower():
            return "high"
        else:
            return "medium"
    
    def _identify_competitive_advantages(self, brand_analysis: CompetitorContentAnalysis, 
                                       competitor_analyses: List[CompetitorContentAnalysis]) -> List[str]:
        """Identify areas where brand outperforms competitors"""
        advantages = []
        
        if not competitor_analyses:
            return advantages
        
        # Compare overall scores
        brand_score = brand_analysis.site_score.aggregate_scores.get('overall_score', 0)
        competitor_scores = [
            analysis.site_score.aggregate_scores.get('overall_score', 0)
            for analysis in competitor_analyses
        ]
        avg_competitor_score = statistics.mean(competitor_scores)
        
        if brand_score > avg_competitor_score + 10:
            advantages.append(f"Superior overall content quality ({brand_score:.1f} vs {avg_competitor_score:.1f})")
        
        # Compare content types
        brand_types = set(brand_analysis.content_types_found.keys())
        for analysis in competitor_analyses:
            competitor_types = set(analysis.content_types_found.keys())
            unique_to_brand = brand_types - competitor_types
            
            if unique_to_brand:
                advantages.extend([f"Unique content type: {content_type.replace('_', ' ')}" for content_type in unique_to_brand])
        
        # Compare features
        brand_features = set(brand_analysis.unique_content_features)
        all_competitor_features = set()
        for analysis in competitor_analyses:
            all_competitor_features.update(analysis.unique_content_features)
        
        unique_brand_features = brand_features - all_competitor_features
        if unique_brand_features:
            advantages.extend([f"Unique feature: {feature}" for feature in unique_brand_features])
        
        return list(set(advantages))  # Remove duplicates
    
    def _generate_competitive_recommendations(self, brand_analysis: CompetitorContentAnalysis,
                                            competitor_analyses: List[CompetitorContentAnalysis],
                                            gaps: List[ContentGap]) -> List[str]:
        """Generate priority recommendations based on competitive analysis"""
        recommendations = []
        
        # Top priority gaps
        high_priority_gaps = [gap for gap in gaps if gap.priority == "high"][:3]
        for gap in high_priority_gaps:
            recommendations.append(f"HIGH PRIORITY: {gap.description}")
        
        # Best performing competitor insights
        if competitor_analyses:
            best_competitor = max(competitor_analyses, 
                                key=lambda x: x.site_score.aggregate_scores.get('overall_score', 0))
            
            recommendations.append(f"Study {best_competitor.competitor_name}'s content strategy - highest scoring competitor")
        
        # Quick wins
        low_effort_gaps = [gap for gap in gaps if gap.estimated_effort == "low"][:2]
        for gap in low_effort_gaps:
            recommendations.append(f"QUICK WIN: {gap.description}")
        
        return recommendations
    
    def _create_opportunity_matrix(self, brand_analysis: CompetitorContentAnalysis,
                                 competitor_analyses: List[CompetitorContentAnalysis],
                                 gaps: List[ContentGap]) -> Dict[str, Dict[str, Any]]:
        """Create content opportunity matrix"""
        matrix = {
            "high_impact_low_effort": [],
            "high_impact_high_effort": [],
            "low_impact_low_effort": [],
            "competitive_benchmarks": {},
            "content_type_gaps": {},
            "keyword_opportunities": {}
        }
        
        # Categorize gaps by impact/effort
        for gap in gaps:
            category = f"{gap.business_impact}_impact_{gap.estimated_effort}_effort"
            if category not in matrix:
                matrix[category] = []
            matrix[category].append({
                "description": gap.description,
                "gap_type": gap.gap_type,
                "priority": gap.priority
            })
        
        # Add competitive benchmarks
        if competitor_analyses:
            for analysis in competitor_analyses:
                matrix["competitive_benchmarks"][analysis.competitor_name] = {
                    "overall_score": analysis.site_score.aggregate_scores.get('overall_score', 0),
                    "content_types": len(analysis.content_types_found),
                    "unique_features": analysis.unique_content_features,
                    "authority_score": analysis.authority_metrics.get('avg_authority_score', 0)
                }
        
        return matrix