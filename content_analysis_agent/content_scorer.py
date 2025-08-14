import re
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging
import textstat
import nltk
from collections import Counter

from content_scraper import PageContent, SiteAnalysis
from config import get_config

# Download required NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except Exception:
    pass  # Continue if NLTK download fails

logger = logging.getLogger(__name__)

@dataclass
class ContentStructureScore:
    """Content structure scoring results"""
    paragraph_length_score: float
    sentence_length_score: float
    heading_hierarchy_score: float
    list_optimization_score: float
    readability_score: float
    total_score: float
    details: Dict[str, Any]

@dataclass
class CitationWorthinessScore:
    """Citation worthiness scoring results"""
    fact_density_score: float
    source_citation_score: float
    expert_authority_score: float
    data_visualization_score: float
    specificity_score: float
    total_score: float
    details: Dict[str, Any]

@dataclass
class AuthoritySignalsScore:
    """Authority signals scoring results"""
    author_credentials_score: float
    publication_freshness_score: float
    update_frequency_score: float
    external_authority_links_score: float
    expertise_indicators_score: float
    total_score: float
    details: Dict[str, Any]

@dataclass
class AIConsumptionScore:
    """AI consumption optimization scoring results"""
    answer_format_score: float
    question_addressing_score: float
    structured_data_score: float
    snippet_optimization_score: float
    voice_search_readiness_score: float
    total_score: float
    details: Dict[str, Any]

@dataclass
class PageScore:
    """Complete scoring for a single page"""
    url: str
    page_type: str
    content_structure: ContentStructureScore
    citation_worthiness: CitationWorthinessScore
    authority_signals: AuthoritySignalsScore
    ai_consumption: AIConsumptionScore
    overall_score: float
    recommendations: List[str]
    scoring_timestamp: str

@dataclass
class SiteScore:
    """Complete scoring for entire site"""
    domain: str
    page_scores: List[PageScore]
    aggregate_scores: Dict[str, float]
    content_gaps: List[str]
    priority_recommendations: List[str]
    site_level_issues: List[str]
    scoring_timestamp: str

class ContentScorer:
    """Advanced content scorer for GEO optimization"""
    
    def __init__(self, config=None):
        self.config = config or get_config()
        self.geo_practices = self.config.get_geo_best_practices()
        self.quality_benchmarks = self.config.get_quality_benchmarks()
        self.scoring_weights = self.config.get_scoring_weights()
        
    def score_site(self, site_analysis: SiteAnalysis) -> SiteScore:
        """Score entire site based on scraped content"""
        logger.info(f"Scoring site: {site_analysis.domain}")
        
        page_scores = []
        for page in site_analysis.pages:
            if page.scrape_success and page.word_count > 50:  # Only score substantial pages
                page_score = self.score_page(page)
                page_scores.append(page_score)
        
        # Calculate aggregate scores
        aggregate_scores = self._calculate_aggregate_scores(page_scores)
        
        # Identify content gaps
        content_gaps = self._identify_content_gaps(site_analysis, page_scores)
        
        # Generate priority recommendations
        priority_recommendations = self._generate_priority_recommendations(page_scores, content_gaps)
        
        # Identify site-level issues
        site_issues = self._identify_site_level_issues(site_analysis, page_scores)
        
        return SiteScore(
            domain=site_analysis.domain,
            page_scores=page_scores,
            aggregate_scores=aggregate_scores,
            content_gaps=content_gaps,
            priority_recommendations=priority_recommendations,
            site_level_issues=site_issues,
            scoring_timestamp=datetime.now().isoformat()
        )
    
    def score_page(self, page: PageContent) -> PageScore:
        """Score a single page against GEO best practices"""
        logger.debug(f"Scoring page: {page.url}")
        
        # Score each dimension
        content_structure = self._score_content_structure(page)
        citation_worthiness = self._score_citation_worthiness(page)
        authority_signals = self._score_authority_signals(page)
        ai_consumption = self._score_ai_consumption(page)
        
        # Calculate overall score using configured weights
        weights = self.scoring_weights
        overall_score = (
            content_structure.total_score * weights.content_structure +
            citation_worthiness.total_score * weights.citation_worthiness +
            authority_signals.total_score * weights.authority_signals +
            ai_consumption.total_score * weights.ai_consumption_optimization
        )
        
        # Generate page-specific recommendations
        recommendations = self._generate_page_recommendations(
            page, content_structure, citation_worthiness, authority_signals, ai_consumption
        )
        
        return PageScore(
            url=page.url,
            page_type=page.content_type,
            content_structure=content_structure,
            citation_worthiness=citation_worthiness,
            authority_signals=authority_signals,
            ai_consumption=ai_consumption,
            overall_score=overall_score,
            recommendations=recommendations,
            scoring_timestamp=datetime.now().isoformat()
        )
    
    def _score_content_structure(self, page: PageContent) -> ContentStructureScore:
        """Score content structure against GEO best practices"""
        practices = self.geo_practices.get('content_structure', {})
        
        # Paragraph length scoring
        paragraph_score = self._score_paragraph_length(page.paragraphs, practices.get('optimal_paragraph_length', [50, 150]))
        
        # Sentence length scoring
        sentence_score = self._score_sentence_length(page.clean_text, practices.get('optimal_sentence_length', [15, 25]))
        
        # Heading hierarchy scoring
        heading_score = self._score_heading_hierarchy(page.headings, practices.get('heading_hierarchy_depth', [2, 4]))
        
        # List optimization scoring
        list_score = self._score_list_optimization(page.lists, practices.get('list_item_optimal', [3, 7]))
        
        # Readability scoring
        readability_score = self._score_readability(page.clean_text)
        
        # Calculate total structure score
        total_score = statistics.mean([paragraph_score, sentence_score, heading_score, list_score, readability_score])
        
        details = {
            'paragraph_count': len(page.paragraphs),
            'avg_paragraph_length': statistics.mean([len(p.split()) for p in page.paragraphs]) if page.paragraphs else 0,
            'sentence_count': len(nltk.sent_tokenize(page.clean_text)) if page.clean_text else 0,
            'heading_levels': len([k for k, v in page.headings.items() if v]),
            'list_count': len(page.lists),
            'flesch_reading_ease': textstat.flesch_reading_ease(page.clean_text) if page.clean_text else 0
        }
        
        return ContentStructureScore(
            paragraph_length_score=paragraph_score,
            sentence_length_score=sentence_score,
            heading_hierarchy_score=heading_score,
            list_optimization_score=list_score,
            readability_score=readability_score,
            total_score=total_score,
            details=details
        )
    
    def _score_citation_worthiness(self, page: PageContent) -> CitationWorthinessScore:
        """Score content for citation worthiness by AI engines"""
        practices = self.geo_practices.get('citation_worthiness', {})
        
        # Fact density scoring
        fact_score = self._score_fact_density(page.clean_text, practices.get('fact_density_score', 0.3))
        
        # Source citation scoring
        citation_score = self._score_source_citations(page.clean_text, page.links, practices.get('source_citation_rate', 0.2))
        
        # Expert authority scoring
        expert_score = self._score_expert_authority(page.clean_text, practices.get('expert_quote_frequency', 0.1))
        
        # Data visualization scoring
        viz_score = self._score_data_visualization(page.images, page.clean_text, practices.get('data_visualization_ratio', 0.15))
        
        # Specificity scoring
        specificity_score = self._score_content_specificity(page.clean_text, page.content_type)
        
        # Calculate total citation worthiness score
        total_score = statistics.mean([fact_score, citation_score, expert_score, viz_score, specificity_score])
        
        details = {
            'numerical_facts_count': len(re.findall(r'\b\d+(?:\.\d+)?(?:%|percent|mg|ml|spf|minutes?|hours?)\b', page.clean_text.lower())),
            'external_links_count': len([link for link in page.links if link['type'] == 'external']),
            'authority_indicators': self._count_authority_indicators(page.clean_text),
            'images_with_data': len([img for img in page.images if any(word in img.get('alt', '').lower() for word in ['chart', 'graph', 'data', 'study'])]),
            'specificity_keywords': len(self._extract_specific_keywords(page.clean_text, page.content_type))
        }
        
        return CitationWorthinessScore(
            fact_density_score=fact_score,
            source_citation_score=citation_score,
            expert_authority_score=expert_score,
            data_visualization_score=viz_score,
            specificity_score=specificity_score,
            total_score=total_score,
            details=details
        )
    
    def _score_authority_signals(self, page: PageContent) -> AuthoritySignalsScore:
        """Score authority signals for AI trust"""
        practices = self.geo_practices.get('authority_signals', {})
        
        # Author credentials scoring
        credentials_score = self._score_author_credentials(page.clean_text, page.structured_data)
        
        # Publication freshness scoring
        freshness_score = self._score_publication_freshness(page.last_modified)
        
        # Update frequency scoring (estimated from content)
        update_score = self._score_update_frequency(page.clean_text, page.last_modified)
        
        # External authority links scoring
        authority_links_score = self._score_authority_links(page.links)
        
        # Expertise indicators scoring
        expertise_score = self._score_expertise_indicators(page.clean_text, page.content_type)
        
        # Calculate total authority score
        total_score = statistics.mean([credentials_score, freshness_score, update_score, authority_links_score, expertise_score])
        
        details = {
            'has_author_info': self._has_author_info(page.clean_text, page.structured_data),
            'last_modified_date': page.last_modified,
            'authority_domains_linked': self._count_authority_domains(page.links),
            'expertise_keywords': len(self._extract_expertise_keywords(page.clean_text)),
            'scientific_terms_count': len(self._extract_scientific_terms(page.clean_text))
        }
        
        return AuthoritySignalsScore(
            author_credentials_score=credentials_score,
            publication_freshness_score=freshness_score,
            update_frequency_score=update_score,
            external_authority_links_score=authority_links_score,
            expertise_indicators_score=expertise_score,
            total_score=total_score,
            details=details
        )
    
    def _score_ai_consumption(self, page: PageContent) -> AIConsumptionScore:
        """Score content for AI consumption optimization"""
        
        # Answer format scoring
        answer_score = self._score_answer_format(page.clean_text, page.headings, page.lists)
        
        # Question addressing scoring
        question_score = self._score_question_addressing(page.clean_text, page.headings)
        
        # Structured data scoring
        structured_score = self._score_structured_data(page.structured_data, page.content_type)
        
        # Snippet optimization scoring
        snippet_score = self._score_snippet_optimization(page.title, page.meta_description, page.headings)
        
        # Voice search readiness scoring
        voice_score = self._score_voice_search_readiness(page.clean_text, page.headings)
        
        # Calculate total AI consumption score
        total_score = statistics.mean([answer_score, question_score, structured_score, snippet_score, voice_score])
        
        details = {
            'direct_answer_patterns': len(re.findall(r'\b(?:is|are|can|will|should|does|how|what|when|where|why)\b.*?\?', page.clean_text.lower())),
            'structured_data_types': [data['type'] for data in page.structured_data],
            'faq_format_detected': page.content_type == 'faq_page' or page.clean_text.lower().count('?') > 5,
            'conversational_phrases': len(re.findall(r'\b(?:you should|you can|you need|you might|we recommend)\b', page.clean_text.lower())),
            'step_by_step_content': len(re.findall(r'\b(?:step \d+|first,|second,|next,|finally,)\b', page.clean_text.lower()))
        }
        
        return AIConsumptionScore(
            answer_format_score=answer_score,
            question_addressing_score=question_score,
            structured_data_score=structured_score,
            snippet_optimization_score=snippet_score,
            voice_search_readiness_score=voice_score,
            total_score=total_score,
            details=details
        )
    
    # Detailed scoring methods
    def _score_paragraph_length(self, paragraphs: List[str], optimal_range: List[int]) -> float:
        """Score paragraph lengths against optimal range"""
        if not paragraphs:
            return 0.0
        
        min_optimal, max_optimal = optimal_range
        scores = []
        
        for paragraph in paragraphs:
            word_count = len(paragraph.split())
            if min_optimal <= word_count <= max_optimal:
                scores.append(1.0)
            elif word_count < min_optimal:
                # Penalize short paragraphs
                scores.append(max(0.3, word_count / min_optimal))
            else:
                # Penalize long paragraphs
                penalty = min(0.7, (word_count - max_optimal) / max_optimal)
                scores.append(max(0.2, 1.0 - penalty))
        
        return statistics.mean(scores) * 100
    
    def _score_sentence_length(self, text: str, optimal_range: List[int]) -> float:
        """Score sentence lengths against optimal range"""
        if not text:
            return 0.0
        
        sentences = nltk.sent_tokenize(text)
        if not sentences:
            return 0.0
        
        min_optimal, max_optimal = optimal_range
        scores = []
        
        for sentence in sentences:
            word_count = len(sentence.split())
            if min_optimal <= word_count <= max_optimal:
                scores.append(1.0)
            elif word_count < min_optimal:
                scores.append(max(0.4, word_count / min_optimal))
            else:
                penalty = min(0.6, (word_count - max_optimal) / max_optimal)
                scores.append(max(0.3, 1.0 - penalty))
        
        return statistics.mean(scores) * 100
    
    def _score_heading_hierarchy(self, headings: Dict[str, List[str]], optimal_range: List[int]) -> float:
        """Score heading hierarchy depth and structure"""
        if not headings:
            return 0.0
        
        # Count heading levels with content
        levels_with_content = len([k for k, v in headings.items() if v])
        
        if not levels_with_content:
            return 0.0
        
        min_levels, max_levels = optimal_range
        
        # Score based on optimal range
        if min_levels <= levels_with_content <= max_levels:
            base_score = 1.0
        elif levels_with_content < min_levels:
            base_score = max(0.4, levels_with_content / min_levels)
        else:
            base_score = max(0.5, 1.0 - (levels_with_content - max_levels) * 0.1)
        
        # Bonus for proper H1 usage
        h1_count = len(headings.get('h1', []))
        if h1_count == 1:
            base_score += 0.1
        elif h1_count == 0:
            base_score -= 0.2
        elif h1_count > 1:
            base_score -= 0.1
        
        return min(100, max(0, base_score * 100))
    
    def _score_list_optimization(self, lists: List[List[str]], optimal_range: List[int]) -> float:
        """Score list usage and optimization"""
        if not lists:
            return 50.0  # Neutral score for no lists
        
        min_items, max_items = optimal_range
        scores = []
        
        for list_items in lists:
            item_count = len(list_items)
            if min_items <= item_count <= max_items:
                scores.append(1.0)
            elif item_count < min_items:
                scores.append(max(0.5, item_count / min_items))
            else:
                penalty = min(0.4, (item_count - max_items) / max_items)
                scores.append(max(0.4, 1.0 - penalty))
        
        return statistics.mean(scores) * 100
    
    def _score_readability(self, text: str) -> float:
        """Score readability using multiple metrics"""
        if not text or len(text) < 100:
            return 0.0
        
        try:
            # Multiple readability scores
            flesch_score = textstat.flesch_reading_ease(text)
            flesch_grade = textstat.flesch_kincaid_grade(text)
            
            # Convert Flesch Reading Ease to 0-100 score
            # 90-100 = Very Easy (5th grade)
            # 80-90 = Easy (6th grade)
            # 70-80 = Fairly Easy (7th grade)
            # 60-70 = Standard (8th-9th grade)
            # 50-60 = Fairly Difficult (10th-12th grade)
            
            # Optimal range for general audience is 60-80
            if 60 <= flesch_score <= 80:
                readability_score = 100
            elif flesch_score > 80:
                # Too easy might lack depth
                readability_score = max(70, 100 - (flesch_score - 80) * 2)
            else:
                # Too difficult
                readability_score = max(20, flesch_score)
            
            # Consider grade level (optimal 8-12th grade)
            if 8 <= flesch_grade <= 12:
                grade_bonus = 10
            elif flesch_grade < 8:
                grade_bonus = max(-20, (flesch_grade - 8) * 2)
            else:
                grade_bonus = max(-30, (12 - flesch_grade) * 2)
            
            final_score = min(100, max(0, readability_score + grade_bonus))
            return final_score
            
        except Exception as e:
            logger.warning(f"Error calculating readability: {str(e)}")
            return 50.0  # Neutral score on error
    
    def _score_fact_density(self, text: str, target_density: float) -> float:
        """Score fact density in content"""
        if not text:
            return 0.0
        
        # Count factual elements (numbers, percentages, specific claims)
        numerical_facts = len(re.findall(r'\b\d+(?:\.\d+)?(?:%|percent|mg|ml|spf|minutes?|hours?|years?|studies?|research)\b', text.lower()))
        specific_claims = len(re.findall(r'\b(?:proven|clinically|scientifically|research shows|studies show|dermatologist|fda approved)\b', text.lower()))
        
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        actual_density = (numerical_facts + specific_claims) / (word_count / 100)  # per 100 words
        
        # Score based on how close to target density
        if actual_density >= target_density:
            return min(100, (actual_density / target_density) * 80 + 20)
        else:
            return (actual_density / target_density) * 100
    
    def _score_source_citations(self, text: str, links: List[Dict], target_rate: float) -> float:
        """Score source citations and external links"""
        if not text:
            return 0.0
        
        # Count external authority links
        authority_domains = {'ncbi.nlm.nih.gov', 'pubmed.ncbi.nlm.nih.gov', 'fda.gov', 'aad.org', 'cancer.org', 'who.int'}
        authority_links = len([link for link in links if any(domain in link['href'] for domain in authority_domains)])
        
        # Count citation patterns in text
        citation_patterns = len(re.findall(r'\[(.*?)\]|\(.*?20\d{2}.*?\)|according to|source:', text))
        
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        actual_rate = (authority_links + citation_patterns) / (word_count / 100)  # per 100 words
        
        if actual_rate >= target_rate:
            return 100
        else:
            return (actual_rate / target_rate) * 100
    
    def _score_expert_authority(self, text: str, target_frequency: float) -> float:
        """Score expert quotes and authority indicators"""
        if not text:
            return 0.0
        
        # Count expert indicators
        expert_patterns = len(re.findall(r'\b(?:dr\.|doctor|dermatologist|researcher|expert|professor|scientist|md|phd)\b', text.lower()))
        quote_patterns = len(re.findall(r'"[^"]*"', text))
        
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        actual_frequency = (expert_patterns + quote_patterns * 0.5) / (word_count / 100)
        
        if actual_frequency >= target_frequency:
            return 100
        else:
            return (actual_frequency / target_frequency) * 100
    
    def _score_data_visualization(self, images: List[Dict], text: str, target_ratio: float) -> float:
        """Score data visualization elements"""
        if not text:
            return 0.0
        
        # Count images that might contain data
        data_images = len([
            img for img in images 
            if any(word in img.get('alt', '').lower() + img.get('title', '').lower() 
                  for word in ['chart', 'graph', 'data', 'study', 'result', 'comparison', 'before', 'after'])
        ])
        
        # Count references to visual data in text
        visual_references = len(re.findall(r'\b(?:chart|graph|figure|table|image|photo|shows|demonstrates)\b', text.lower()))
        
        word_count = len(text.split())
        if word_count == 0:
            return 50.0  # Neutral for empty content
        
        actual_ratio = (data_images + visual_references * 0.3) / (word_count / 100)
        
        if actual_ratio >= target_ratio:
            return 100
        else:
            return (actual_ratio / target_ratio) * 100
    
    def _score_content_specificity(self, text: str, content_type: str) -> float:
        """Score content specificity based on type"""
        if not text:
            return 0.0
        
        # Get sector-specific keywords
        keywords = self.config.get_keywords()
        primary_keywords = keywords.get('primary', [])
        secondary_keywords = keywords.get('secondary', [])
        long_tail_keywords = keywords.get('long_tail', [])
        
        text_lower = text.lower()
        
        # Count keyword usage
        primary_count = sum(1 for keyword in primary_keywords if keyword.lower() in text_lower)
        secondary_count = sum(1 for keyword in secondary_keywords if keyword.lower() in text_lower)
        long_tail_count = sum(1 for keyword in long_tail_keywords if keyword.lower() in text_lower)
        
        # Weight different keyword types
        specificity_score = (
            primary_count * 3 +      # Primary keywords worth more
            secondary_count * 2 +    # Secondary keywords worth less
            long_tail_count * 4      # Long tail keywords worth most
        )
        
        # Normalize based on content length
        word_count = len(text.split())
        normalized_score = (specificity_score / (word_count / 100)) * 10  # Scale factor
        
        return min(100, normalized_score)
    
    # Authority scoring methods
    def _count_authority_indicators(self, text: str) -> int:
        """Count authority indicators in text"""
        authority_patterns = [
            r'\bclinically proven\b', r'\bfda approved\b', r'\bdermatologist tested\b',
            r'\bresearch shows\b', r'\bstudies show\b', r'\bpeer.reviewed\b',
            r'\buniversity\b', r'\bhospital\b', r'\binstitute\b'
        ]
        
        count = 0
        text_lower = text.lower()
        for pattern in authority_patterns:
            count += len(re.findall(pattern, text_lower))
        
        return count
    
    def _extract_specific_keywords(self, text: str, content_type: str) -> List[str]:
        """Extract sector-specific keywords from text"""
        keywords = self.config.get_keywords()
        all_keywords = keywords.get('primary', []) + keywords.get('secondary', []) + keywords.get('long_tail', [])
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in all_keywords:
            if keyword.lower() in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _has_author_info(self, text: str, structured_data: List[Dict]) -> bool:
        """Check if page has author information"""
        # Check structured data first
        for data in structured_data:
            if 'author' in str(data).lower():
                return True
        
        # Check text patterns
        author_patterns = [
            r'\bby\s+[A-Z][a-z]+\s+[A-Z][a-z]+\b',
            r'\bauthor:\s*[A-Z][a-z]+',
            r'\bwritten by\b',
            r'\bdr\.\s+[A-Z][a-z]+',
            r'\bmd\b'
        ]
        
        for pattern in author_patterns:
            if re.search(pattern, text):
                return True
        
        return False
    
    def _count_authority_domains(self, links: List[Dict]) -> int:
        """Count links to authority domains"""
        authority_domains = {
            'ncbi.nlm.nih.gov', 'pubmed.ncbi.nlm.nih.gov', 'fda.gov',
            'aad.org', 'cancer.org', 'who.int', 'mayo clinic.org',
            'harvard.edu', 'stanford.edu', 'nih.gov'
        }
        
        count = 0
        for link in links:
            if link['type'] == 'external':
                for domain in authority_domains:
                    if domain in link['href']:
                        count += 1
                        break
        
        return count
    
    def _extract_expertise_keywords(self, text: str) -> List[str]:
        """Extract expertise-indicating keywords"""
        expertise_keywords = [
            'clinical', 'research', 'study', 'studies', 'trial', 'tested',
            'dermatologist', 'scientist', 'expert', 'professional',
            'peer-reviewed', 'published', 'journal', 'medical'
        ]
        
        found = []
        text_lower = text.lower()
        
        for keyword in expertise_keywords:
            if keyword in text_lower:
                found.append(keyword)
        
        return found
    
    def _extract_scientific_terms(self, text: str) -> List[str]:
        """Extract scientific terminology"""
        scientific_terms = [
            'zinc oxide', 'titanium dioxide', 'uv radiation', 'broad spectrum',
            'spf', 'photoprotection', 'melanin', 'epidermis', 'dermal',
            'photoaging', 'photodamage', 'carcinogenic', 'antioxidant'
        ]
        
        found = []
        text_lower = text.lower()
        
        for term in scientific_terms:
            if term in text_lower:
                found.append(term)
        
        return found
    
    # AI consumption scoring methods
    def _score_answer_format(self, text: str, headings: Dict, lists: List) -> float:
        """Score content for direct answer formatting"""
        if not text:
            return 0.0
        
        score = 50  # Base score
        
        # Check for direct answer patterns
        answer_patterns = [
            r'\byes,?\s', r'\bno,?\s', r'\bthe answer is\b',
            r'\bin short,?\b', r'\bsimply put,?\b', r'\bthe key is\b'
        ]
        
        for pattern in answer_patterns:
            if re.search(pattern, text.lower()):
                score += 10
        
        # Bonus for numbered lists (step-by-step answers)
        if any(len(lst) >= 3 for lst in lists):
            score += 15
        
        # Bonus for FAQ-style headings
        question_headings = 0
        for heading_list in headings.values():
            for heading in heading_list:
                if heading.strip().endswith('?'):
                    question_headings += 1
        
        if question_headings > 0:
            score += min(20, question_headings * 5)
        
        return min(100, score)
    
    def _score_question_addressing(self, text: str, headings: Dict) -> float:
        """Score how well content addresses common questions"""
        if not text:
            return 0.0
        
        # Common question patterns
        question_patterns = [
            r'\bhow\s+(?:to|do|does|can)\b', r'\bwhat\s+(?:is|are|does)\b',
            r'\bwhen\s+(?:to|should|do)\b', r'\bwhere\s+(?:to|can|should)\b',
            r'\bwhy\s+(?:is|are|do|should)\b', r'\bwhich\s+(?:is|are|one)\b'
        ]
        
        question_count = 0
        text_lower = text.lower()
        
        for pattern in question_patterns:
            question_count += len(re.findall(pattern, text_lower))
        
        # Also check headings for question format
        for heading_list in headings.values():
            for heading in heading_list:
                if any(word in heading.lower() for word in ['how', 'what', 'when', 'where', 'why', 'which']):
                    question_count += 2  # Headings worth more
        
        # Score based on question density
        word_count = len(text.split())
        if word_count > 0:
            question_density = (question_count / (word_count / 100))  # per 100 words
            return min(100, question_density * 25)
        
        return 0
    
    def _score_structured_data(self, structured_data: List[Dict], content_type: str) -> float:
        """Score structured data implementation"""
        if not structured_data:
            return 0.0
        
        score = 0
        data_types = [data.get('type', '') for data in structured_data]
        
        # Score based on structured data types
        if 'json-ld' in data_types:
            score += 40
        if 'microdata' in data_types:
            score += 20
        
        # Content-specific structured data bonuses
        if content_type == 'product_page':
            if any('Product' in str(data) for data in structured_data):
                score += 30
        elif content_type == 'faq_page':
            if any('FAQPage' in str(data) for data in structured_data):
                score += 30
        elif content_type == 'blog_post':
            if any('Article' in str(data) for data in structured_data):
                score += 30
        
        # Bonus for comprehensive structured data
        if len(structured_data) > 2:
            score += 10
        
        return min(100, score)
    
    def _score_snippet_optimization(self, title: str, meta_description: str, headings: Dict) -> float:
        """Score content for search snippet optimization"""
        score = 0
        
        # Title scoring
        if title:
            if 30 <= len(title) <= 60:  # Optimal title length
                score += 25
            elif len(title) > 0:
                score += 15
        
        # Meta description scoring
        if meta_description:
            if 120 <= len(meta_description) <= 160:  # Optimal meta description length
                score += 25
            elif len(meta_description) > 0:
                score += 15
        
        # H1 scoring
        h1_headings = headings.get('h1', [])
        if len(h1_headings) == 1:  # Exactly one H1
            score += 25
        elif len(h1_headings) > 0:
            score += 15
        
        # H2/H3 structure scoring
        h2_count = len(headings.get('h2', []))
        if h2_count >= 2:
            score += 25
        elif h2_count >= 1:
            score += 15
        
        return min(100, score)
    
    def _score_voice_search_readiness(self, text: str, headings: Dict) -> float:
        """Score content for voice search optimization"""
        if not text:
            return 0.0
        
        score = 0
        text_lower = text.lower()
        
        # Conversational language patterns
        conversational_patterns = [
            r'\byou\s+(?:can|should|need|might|will)\b',
            r'\bwe\s+(?:recommend|suggest|advise)\b',
            r'\bit\'s\s+(?:important|best|better)\b',
            r'\bhere\'s\s+(?:how|what|why)\b'
        ]
        
        for pattern in conversational_patterns:
            score += min(15, len(re.findall(pattern, text_lower)) * 3)
        
        # Question-based headings (good for voice search)
        question_headings = 0
        for heading_list in headings.values():
            for heading in heading_list:
                if any(word in heading.lower() for word in ['how', 'what', 'when', 'where', 'why']):
                    question_headings += 1
        
        score += min(30, question_headings * 5)
        
        # Local language patterns
        local_patterns = ['near me', 'best for', 'recommended for', 'perfect for']
        for pattern in local_patterns:
            if pattern in text_lower:
                score += 5
        
        return min(100, score)
    
    # Additional scoring methods
    def _score_publication_freshness(self, last_modified: Optional[str]) -> float:
        """Score publication freshness"""
        if not last_modified:
            return 30  # Neutral score for missing date
        
        try:
            # Parse date and calculate age
            # This is simplified - in production, you'd want better date parsing
            import dateutil.parser
            modified_date = dateutil.parser.parse(last_modified)
            age_days = (datetime.utcnow() - modified_date.replace(tzinfo=None)).days
            
            # Score based on age (fresher is better)
            if age_days <= 30:    # Very fresh
                return 100
            elif age_days <= 90:  # Fresh
                return 90
            elif age_days <= 180: # Somewhat fresh
                return 75
            elif age_days <= 365: # Acceptable
                return 60
            else:                 # Old
                return max(20, 60 - (age_days - 365) // 30)
        
        except Exception:
            return 30  # Neutral score on parsing error
    
    def _score_update_frequency(self, text: str, last_modified: Optional[str]) -> float:
        """Estimate update frequency scoring"""
        # This is a simplified estimation based on content patterns
        score = 50  # Base score
        
        # Look for update indicators in text
        update_patterns = [
            r'updated\s+(?:on|in)\s+20\d{2}',
            r'revised\s+(?:on|in)\s+20\d{2}',
            r'last\s+(?:updated|modified|reviewed)',
            r'as\s+of\s+20\d{2}'
        ]
        
        text_lower = text.lower()
        for pattern in update_patterns:
            if re.search(pattern, text_lower):
                score += 15
                break  # Only count once
        
        # Bonus if we have a recent last_modified date
        if last_modified:
            try:
                import dateutil.parser
                modified_date = dateutil.parser.parse(last_modified)
                age_days = (datetime.utcnow() - modified_date.replace(tzinfo=None)).days
                if age_days <= 90:
                    score += 20
                elif age_days <= 180:
                    score += 10
            except Exception:
                pass
        
        return min(100, score)
    
    # Site-level analysis methods
    def _calculate_aggregate_scores(self, page_scores: List[PageScore]) -> Dict[str, float]:
        """Calculate aggregate scores across all pages"""
        if not page_scores:
            return {}
        
        aggregate = {
            'overall_score': statistics.mean([page.overall_score for page in page_scores]),
            'content_structure_avg': statistics.mean([page.content_structure.total_score for page in page_scores]),
            'citation_worthiness_avg': statistics.mean([page.citation_worthiness.total_score for page in page_scores]),
            'authority_signals_avg': statistics.mean([page.authority_signals.total_score for page in page_scores]),
            'ai_consumption_avg': statistics.mean([page.ai_consumption.total_score for page in page_scores]),
            'pages_analyzed': len(page_scores),
            'top_scoring_pages': len([page for page in page_scores if page.overall_score >= 75]),
            'needs_improvement_pages': len([page for page in page_scores if page.overall_score < 50])
        }
        
        # Calculate content type breakdown
        content_types = {}
        for page in page_scores:
            if page.page_type not in content_types:
                content_types[page.page_type] = []
            content_types[page.page_type].append(page.overall_score)
        
        for content_type, scores in content_types.items():
            aggregate[f'{content_type}_avg_score'] = statistics.mean(scores)
            aggregate[f'{content_type}_count'] = len(scores)
        
        return aggregate
    
    def _identify_content_gaps(self, site_analysis: SiteAnalysis, page_scores: List[PageScore]) -> List[str]:
        """Identify content gaps based on configured content types"""
        content_types = self.config.get_content_types()
        found_content_types = set(page.page_type for page in page_scores)
        
        gaps = []
        
        for content_type, config in content_types.items():
            # Convert config names to match our classification
            expected_type = content_type.replace('_', '_')
            
            if expected_type not in found_content_types:
                gaps.append(f"Missing {content_type.replace('_', ' ')} content")
            else:
                # Check if content type has sufficient coverage
                type_pages = [page for page in page_scores if page.page_type == expected_type]
                if len(type_pages) == 1 and content_type in ['product_pages', 'ingredient_guides']:
                    gaps.append(f"Limited {content_type.replace('_', ' ')} content - consider expanding")
        
        # Check for specific content elements
        all_text = ' '.join([page.url for page in site_analysis.pages if page.scrape_success])
        
        # Sector-specific gap analysis
        keywords = self.config.get_keywords()
        primary_keywords = keywords.get('primary', [])
        
        missing_topics = []
        for keyword in primary_keywords[:5]:  # Check top 5 primary keywords
            if keyword.lower() not in all_text.lower():
                missing_topics.append(f"No content found for '{keyword}'")
        
        gaps.extend(missing_topics[:3])  # Limit to top 3 missing topics
        
        return gaps
    
    def _generate_priority_recommendations(self, page_scores: List[PageScore], content_gaps: List[str]) -> List[str]:
        """Generate priority recommendations based on analysis"""
        recommendations = []
        
        if not page_scores:
            recommendations.append("No pages successfully analyzed - check website accessibility")
            return recommendations
        
        # Analyze overall performance
        avg_score = statistics.mean([page.overall_score for page in page_scores])
        
        if avg_score < 40:
            recommendations.append("CRITICAL: Overall content quality is poor - comprehensive content audit recommended")
        elif avg_score < 60:
            recommendations.append("IMPORTANT: Content quality needs significant improvement across multiple areas")
        
        # Identify biggest opportunity areas
        structure_scores = [page.content_structure.total_score for page in page_scores]
        citation_scores = [page.citation_worthiness.total_score for page in page_scores]
        authority_scores = [page.authority_signals.total_score for page in page_scores]
        ai_scores = [page.ai_consumption.total_score for page in page_scores]
        
        avg_structure = statistics.mean(structure_scores)
        avg_citation = statistics.mean(citation_scores)
        avg_authority = statistics.mean(authority_scores)
        avg_ai = statistics.mean(ai_scores)
        
        # Prioritize improvements
        improvement_areas = [
            ('Content Structure', avg_structure),
            ('Citation Worthiness', avg_citation),
            ('Authority Signals', avg_authority),
            ('AI Consumption', avg_ai)
        ]
        
        improvement_areas.sort(key=lambda x: x[1])  # Sort by score (lowest first)
        
        for area, score in improvement_areas[:2]:  # Focus on top 2 problem areas
            if score < 50:
                recommendations.append(f"Priority: Improve {area} (current score: {score:.1f}/100)")
        
        # Add content gap recommendations
        for gap in content_gaps[:3]:  # Top 3 gaps
            recommendations.append(f"Content Gap: {gap}")
        
        # Add specific page recommendations
        low_scoring_pages = [page for page in page_scores if page.overall_score < 40]
        if low_scoring_pages:
            recommendations.append(f"Immediate attention: {len(low_scoring_pages)} pages scoring below 40/100")
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _identify_site_level_issues(self, site_analysis: SiteAnalysis, page_scores: List[PageScore]) -> List[str]:
        """Identify site-level issues"""
        issues = []
        
        # Check scraping success rate
        if site_analysis.successful_scrapes / site_analysis.total_pages < 0.8:
            issues.append(f"High scraping failure rate: {site_analysis.failed_scrapes}/{site_analysis.total_pages} pages failed")
        
        # Check for consistent H1 usage
        h1_issues = 0
        for page in page_scores:
            heading_levels = page.content_structure.details.get('heading_levels', 0)
            # Handle both dict and int cases for heading_levels
            if isinstance(heading_levels, dict):
                h1_count = len(heading_levels.get('h1', []))
            else:
                # If it's just a count, we can't determine H1 specifically
                h1_count = 1 if heading_levels > 0 else 0
            
            if h1_count != 1:
                h1_issues += 1
        
        if h1_issues > len(page_scores) * 0.5:
            issues.append("Inconsistent H1 tag usage across pages")
        
        # Check for structured data implementation
        pages_with_structured_data = len([page for page in page_scores if page.ai_consumption.details.get('structured_data_types')])
        if pages_with_structured_data / len(page_scores) < 0.3:
            issues.append("Low structured data implementation across site")
        
        # Check for authority link patterns
        total_authority_links = sum(score.authority_signals.details.get('authority_domains_linked', 0) for score in page_scores)
        if total_authority_links < len(page_scores) * 0.5:
            issues.append("Insufficient external authority links across content")
        
        return issues
    
    def _generate_page_recommendations(self, page: PageContent, structure: ContentStructureScore, 
                                     citation: CitationWorthinessScore, authority: AuthoritySignalsScore, 
                                     ai_consumption: AIConsumptionScore) -> List[str]:
        """Generate specific recommendations for a single page"""
        recommendations = []
        
        # Structure recommendations
        if structure.paragraph_length_score < 60:
            recommendations.append("Optimize paragraph length (aim for 50-150 words per paragraph)")
        
        if structure.sentence_length_score < 60:
            recommendations.append("Shorten sentences for better readability (aim for 15-25 words)")
        
        if structure.heading_hierarchy_score < 60:
            recommendations.append("Improve heading structure with proper H1-H4 hierarchy")
        
        if structure.readability_score < 60:
            recommendations.append("Improve readability - content may be too complex")
        
        # Citation recommendations
        if citation.fact_density_score < 60:
            recommendations.append("Add more specific facts, statistics, and numerical data")
        
        if citation.source_citation_score < 60:
            recommendations.append("Include more external authority links and source citations")
        
        # Authority recommendations
        if authority.author_credentials_score < 60:
            recommendations.append("Add author credentials and expertise information")
        
        if authority.external_authority_links_score < 60:
            recommendations.append("Link to more authoritative external sources")
        
        # AI consumption recommendations
        if ai_consumption.structured_data_score < 60:
            recommendations.append("Implement structured data markup (JSON-LD, Schema.org)")
        
        if ai_consumption.answer_format_score < 60:
            recommendations.append("Format content to directly answer common questions")
        
        return recommendations[:5]  # Limit to top 5 recommendations per page
    
    # Missing scoring methods
    def _score_author_credentials(self, text: str, structured_data: List[Dict]) -> float:
        """Score author credentials and expertise"""
        if self._has_author_info(text, structured_data):
            return 85.0
        return 25.0
    
    def _score_authority_links(self, links: List[Dict]) -> float:
        """Score external authority links"""
        authority_count = self._count_authority_domains(links)
        total_external = len([link for link in links if link['type'] == 'external'])
        
        if total_external == 0:
            return 20.0
        
        authority_ratio = authority_count / total_external
        return min(100, authority_ratio * 100 + 30)
    
    def _score_expertise_indicators(self, text: str, content_type: str) -> float:
        """Score expertise indicators in content"""
        expertise_keywords = self._extract_expertise_keywords(text)
        scientific_terms = self._extract_scientific_terms(text)
        
        word_count = len(text.split())
        if word_count == 0:
            return 0.0
        
        expertise_density = (len(expertise_keywords) + len(scientific_terms)) / (word_count / 100)
        return min(100, expertise_density * 20)