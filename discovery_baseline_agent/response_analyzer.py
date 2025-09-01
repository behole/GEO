import re
import json
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

from .dynamic_brand_extractor import DynamicBrandExtractor

logger = logging.getLogger(__name__)

@dataclass
class Citation:
    """Represents a brand/product citation found in AI response"""
    brand: str
    product: Optional[str]
    context: str
    position: int
    sentiment: str  # positive, negative, neutral
    mention_type: str  # direct, indirect, comparison
    confidence: float  # 0.0 to 1.0

@dataclass
class ResponseAnalysis:
    """Complete analysis of an AI response"""
    query: str
    ai_engine: str
    model: str
    timestamp: str
    response_text: str
    citations: List[Citation]
    competitors_mentioned: List[str]
    total_brands_mentioned: int
    your_brand_mentioned: bool
    mention_context: Optional[str]
    response_quality: float
    response_length: int
    contains_recommendations: bool
    contains_specific_products: bool

class BrandDatabase:
    """Database of known sunscreen brands and competitors"""
    
    # Major sunscreen brands to track
    MAJOR_BRANDS = {
        "neutrogena", "coppertone", "blue lizard", "eltamd", "cerave", 
        "la roche posay", "eucerin", "aveeno", "banana boat", "hawaiian tropic",
        "badger", "thinkbaby", "alba botanica", "dermalogica", "drunk elephant",
        "supergoop", "coola", "sun bum", "bare republic", "mineral fusion",
        "kiss my face", "goddess garden", "all good", "stream2sea", "thinksport"
    }
    
    # Your brand variations (to be customized)
    YOUR_BRAND_VARIATIONS = {
        "Brush on Block", 
        "Brush On Block", 
        "BrushOnBlock", 
        "Brush-On-Block",
        "brush on block",  # lowercase variations
        "brushonblock",
        "Brush on Block sunscreen",
        "Brush On Block mineral sunscreen",
        "BOB",  # if commonly abbreviated
        "Brush-on-Block"  
    }
    
    # Common product indicators
    PRODUCT_INDICATORS = {
        "spf", "sunscreen", "lotion", "cream", "spray", "stick", "powder",
        "zinc", "titanium", "mineral", "broad spectrum", "water resistant"
    }
    
    @classmethod
    def is_sunscreen_brand(cls, text: str) -> bool:
        """Check if text contains a known sunscreen brand"""
        text_lower = text.lower()
        return any(brand in text_lower for brand in cls.MAJOR_BRANDS)
    
    @classmethod
    def is_your_brand(cls, text: str) -> bool:
        """Check if text mentions your brand"""
        text_lower = text.lower()
        return any(brand in text_lower for brand in cls.YOUR_BRAND_VARIATIONS)
    
    @classmethod
    def extract_brands(cls, text: str) -> Set[str]:
        """Extract all known brands from text"""
        text_lower = text.lower()
        found_brands = set()
        
        for brand in cls.MAJOR_BRANDS:
            if brand in text_lower:
                found_brands.add(brand)
        
        for brand in cls.YOUR_BRAND_VARIATIONS:
            if brand in text_lower:
                found_brands.add("your_brand")  # Normalize to single identifier
        
        return found_brands
    
    @classmethod
    def extract_brands_dynamic(cls, text: str, target_brand: str = "Brush on Block", industry: str = "generic") -> Set[str]:
        """Extract brands dynamically using AI-powered detection"""
        # First try traditional method
        traditional_brands = cls.extract_brands(text)
        
        # If we found brands or this is the sunscreen industry, use traditional method
        if traditional_brands or industry == "beauty":
            return traditional_brands
        
        # Otherwise use dynamic extraction
        try:
            extractor = DynamicBrandExtractor(target_brand, industry)
            dynamic_brands = extractor.extract_brands_from_response(text)
            
            # Convert to set of brand names
            brand_names = set()
            for brand_name, mentions in dynamic_brands.items():
                if mentions:  # Only include brands with valid mentions
                    # Use confidence threshold
                    avg_confidence = sum(m.confidence for m in mentions) / len(mentions)
                    if avg_confidence >= 0.4:
                        brand_names.add(brand_name.lower())
            
            # Check for target brand
            target_variations = extractor.target_brand_variations
            if any(var in text.lower() for var in target_variations):
                brand_names.add("your_brand")
            
            return brand_names
        except Exception as e:
            logger.warning(f"Dynamic brand extraction failed: {str(e)}")
            return traditional_brands

class SentimentAnalyzer:
    """Simple sentiment analysis for brand mentions"""
    
    POSITIVE_INDICATORS = {
        "best", "excellent", "great", "amazing", "fantastic", "recommended", 
        "top rated", "highly rated", "love", "favorite", "outstanding",
        "effective", "gentle", "lightweight", "non-greasy", "perfect"
    }
    
    NEGATIVE_INDICATORS = {
        "worst", "terrible", "bad", "awful", "disappointing", "avoid",
        "not recommended", "poor", "heavy", "greasy", "irritating",
        "expensive", "overpriced", "chalky", "white cast"
    }
    
    @classmethod
    def analyze_sentiment(cls, text: str, brand_context: str = "") -> str:
        """Analyze sentiment of brand mention in context"""
        context_text = f"{text} {brand_context}".lower()
        
        positive_count = sum(1 for word in cls.POSITIVE_INDICATORS if word in context_text)
        negative_count = sum(1 for word in cls.NEGATIVE_INDICATORS if word in context_text)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

class CitationExtractor:
    """Extracts structured citations from AI responses"""
    
    @staticmethod
    def extract_citations(response_text: str, query: str) -> List[Citation]:
        """Extract brand citations from response text"""
        citations = []
        brands_found = BrandDatabase.extract_brands(response_text)
        
        # Split response into sentences for position analysis
        sentences = re.split(r'[.!?]+', response_text)
        
        for i, sentence in enumerate(sentences):
            sentence_brands = BrandDatabase.extract_brands(sentence)
            
            for brand in sentence_brands:
                # Extract product information
                product = CitationExtractor._extract_product_from_sentence(sentence, brand)
                
                # Determine mention type
                mention_type = CitationExtractor._classify_mention_type(sentence, brand)
                
                # Analyze sentiment
                sentiment = SentimentAnalyzer.analyze_sentiment(sentence, brand)
                
                # Calculate confidence based on specificity
                confidence = CitationExtractor._calculate_confidence(sentence, brand, product)
                
                citation = Citation(
                    brand=brand,
                    product=product,
                    context=sentence.strip(),
                    position=i + 1,
                    sentiment=sentiment,
                    mention_type=mention_type,
                    confidence=confidence
                )
                
                citations.append(citation)
        
        return citations
    
    @staticmethod
    def _extract_product_from_sentence(sentence: str, brand: str) -> Optional[str]:
        """Extract specific product name from sentence"""
        # Look for product patterns near brand mention
        sentence_lower = sentence.lower()
        brand_lower = brand.lower()
        
        # Find brand position
        brand_pos = sentence_lower.find(brand_lower)
        if brand_pos == -1:
            return None
        
        # Look for product indicators in nearby text
        context_window = sentence_lower[max(0, brand_pos-50):brand_pos+100]
        
        # Extract potential product names (simplified approach)
        product_patterns = [
            r'(\w+\s+)?spf\s+\d+',
            r'\w+\s+sunscreen',
            r'\w+\s+lotion',
            r'\w+\s+cream'
        ]
        
        for pattern in product_patterns:
            matches = re.findall(pattern, context_window)
            if matches:
                return matches[0].strip()
        
        return None
    
    @staticmethod
    def _classify_mention_type(sentence: str, brand: str) -> str:
        """Classify the type of brand mention"""
        sentence_lower = sentence.lower()
        
        comparison_indicators = ["vs", "versus", "compared to", "better than", "worse than"]
        if any(indicator in sentence_lower for indicator in comparison_indicators):
            return "comparison"
        
        direct_indicators = ["recommend", "suggest", "try", "use", "choose"]
        if any(indicator in sentence_lower for indicator in direct_indicators):
            return "direct"
        
        return "indirect"
    
    @staticmethod
    def _calculate_confidence(sentence: str, brand: str, product: Optional[str]) -> float:
        """Calculate confidence score for citation"""
        confidence = 0.5  # Base confidence
        
        # Boost for specific product mention
        if product:
            confidence += 0.3
        
        # Boost for specific recommendations
        if any(word in sentence.lower() for word in ["recommend", "best", "top"]):
            confidence += 0.2
        
        # Reduce for vague mentions
        if any(word in sentence.lower() for word in ["some", "various", "many", "several"]):
            confidence -= 0.1
        
        return max(0.1, min(1.0, confidence))

class ResponseAnalyzer:
    """Main response analyzer orchestrating all analysis components"""
    
    def __init__(self, target_brand: str = "Brush on Block", industry: str = "beauty"):
        self.citation_extractor = CitationExtractor()
        self.brand_database = BrandDatabase()
        self.sentiment_analyzer = SentimentAnalyzer()
        self.target_brand = target_brand
        self.industry = industry
        # Initialize dynamic extractor for non-sunscreen industries
        if industry != "beauty":
            self.dynamic_extractor = DynamicBrandExtractor(target_brand, industry)
    
    def analyze_response(self, response_data: Dict[str, Any]) -> ResponseAnalysis:
        """Analyze a complete AI response"""
        if not response_data.get("success") or not response_data.get("response"):
            return self._create_failed_analysis(response_data)
        
        response_text = response_data["response"]
        query = response_data["query"]
        
        # Extract citations
        citations = self.citation_extractor.extract_citations(response_text, query)
        
        # Analyze competitors (use dynamic extraction for non-beauty industries)
        if self.industry == "beauty":
            all_brands = self.brand_database.extract_brands(response_text)
        else:
            all_brands = self.brand_database.extract_brands_dynamic(response_text, self.target_brand, self.industry)
        
        competitors = [brand for brand in all_brands if brand != "your_brand"]
        
        # Check for your brand mention
        your_brand_mentioned = self.brand_database.is_your_brand(response_text)
        mention_context = self._extract_your_brand_context(response_text) if your_brand_mentioned else None
        
        # Quality metrics
        response_quality = self._calculate_response_quality(response_text, citations)
        contains_recommendations = self._contains_recommendations(response_text)
        contains_specific_products = self._contains_specific_products(response_text)
        
        return ResponseAnalysis(
            query=query,
            ai_engine=response_data.get("engine", "unknown"),
            model=response_data.get("model", "unknown"),
            timestamp=response_data.get("timestamp", datetime.utcnow().isoformat()),
            response_text=response_text,
            citations=citations,
            competitors_mentioned=list(competitors),
            total_brands_mentioned=len(all_brands),
            your_brand_mentioned=your_brand_mentioned,
            mention_context=mention_context,
            response_quality=response_quality,
            response_length=len(response_text),
            contains_recommendations=contains_recommendations,
            contains_specific_products=contains_specific_products
        )
    
    def _create_failed_analysis(self, response_data: Dict[str, Any]) -> ResponseAnalysis:
        """Create analysis for failed API responses"""
        return ResponseAnalysis(
            query=response_data.get("query", "unknown"),
            ai_engine=response_data.get("engine", "unknown"),
            model=response_data.get("model", "unknown"),
            timestamp=response_data.get("timestamp", datetime.utcnow().isoformat()),
            response_text="",
            citations=[],
            competitors_mentioned=[],
            total_brands_mentioned=0,
            your_brand_mentioned=False,
            mention_context=None,
            response_quality=0.0,
            response_length=0,
            contains_recommendations=False,
            contains_specific_products=False
        )
    
    def _extract_your_brand_context(self, response_text: str) -> str:
        """Extract context around your brand mentions"""
        sentences = re.split(r'[.!?]+', response_text)
        
        for sentence in sentences:
            if self.brand_database.is_your_brand(sentence):
                return sentence.strip()
        
        return ""
    
    def _calculate_response_quality(self, response_text: str, citations: List[Citation]) -> float:
        """Calculate overall response quality score"""
        quality = 0.0
        
        # Length factor (optimal range 200-1000 characters)
        length = len(response_text)
        if 200 <= length <= 1000:
            quality += 0.3
        elif length > 1000:
            quality += 0.2
        else:
            quality += 0.1
        
        # Citation factor
        if citations:
            quality += min(0.4, len(citations) * 0.1)
        
        # Specificity factor
        specific_terms = ["spf", "zinc oxide", "titanium dioxide", "broad spectrum"]
        specificity_score = sum(1 for term in specific_terms if term.lower() in response_text.lower())
        quality += min(0.3, specificity_score * 0.1)
        
        return min(1.0, quality)
    
    def _contains_recommendations(self, response_text: str) -> bool:
        """Check if response contains product recommendations"""
        recommendation_indicators = [
            "recommend", "suggest", "best", "top", "highly rated", 
            "favorite", "try", "consider", "choose"
        ]
        text_lower = response_text.lower()
        return any(indicator in text_lower for indicator in recommendation_indicators)
    
    def _contains_specific_products(self, response_text: str) -> bool:
        """Check if response mentions specific products"""
        return bool(re.search(r'spf\s+\d+|[A-Z][a-z]+\s+(sunscreen|lotion|cream)', response_text))

class BatchAnalyzer:
    """Analyzer for processing batches of responses"""
    
    def __init__(self, target_brand: str = "Brush on Block", industry: str = "beauty"):
        self.analyzer = ResponseAnalyzer(target_brand, industry)
    
    def analyze_batch(self, response_batch: List[Dict[str, Any]]) -> List[ResponseAnalysis]:
        """Analyze a batch of responses"""
        analyses = []
        
        for response_data in response_batch:
            try:
                analysis = self.analyzer.analyze_response(response_data)
                analyses.append(analysis)
            except Exception as e:
                logger.error(f"Error analyzing response for query '{response_data.get('query', 'unknown')}': {str(e)}")
                # Create failed analysis
                analyses.append(self.analyzer._create_failed_analysis(response_data))
        
        return analyses
    
    def get_batch_summary(self, analyses: List[ResponseAnalysis]) -> Dict[str, Any]:
        """Generate summary statistics for a batch of analyses"""
        if not analyses:
            return {"error": "No analyses to summarize"}
        
        total_analyses = len(analyses)
        successful_analyses = [a for a in analyses if a.response_text]
        
        # Citation statistics
        total_citations = sum(len(a.citations) for a in analyses)
        your_brand_mentions = sum(1 for a in analyses if a.your_brand_mentioned)
        
        # Competitor analysis
        all_competitors = set()
        for analysis in analyses:
            all_competitors.update(analysis.competitors_mentioned)
        
        # Quality metrics
        avg_quality = sum(a.response_quality for a in successful_analyses) / len(successful_analyses) if successful_analyses else 0
        avg_length = sum(a.response_length for a in successful_analyses) / len(successful_analyses) if successful_analyses else 0
        
        return {
            "total_analyses": total_analyses,
            "successful_responses": len(successful_analyses),
            "success_rate": len(successful_analyses) / total_analyses if total_analyses > 0 else 0,
            "total_citations": total_citations,
            "your_brand_mentions": your_brand_mentions,
            "your_brand_mention_rate": your_brand_mentions / total_analyses if total_analyses > 0 else 0,
            "unique_competitors": len(all_competitors),
            "top_competitors": list(all_competitors)[:10],
            "avg_response_quality": avg_quality,
            "avg_response_length": avg_length,
            "responses_with_recommendations": sum(1 for a in analyses if a.contains_recommendations),
            "responses_with_specific_products": sum(1 for a in analyses if a.contains_specific_products)
        }