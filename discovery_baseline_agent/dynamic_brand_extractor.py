#!/usr/bin/env python3
"""
Dynamic Brand Extractor for GEO System
Automatically discovers competitors and brands from AI responses for any industry
"""

import re
import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass
import logging
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

@dataclass
class BrandMention:
    """Represents a brand mention found in AI response"""
    name: str
    confidence: float
    context: str
    position: int
    mention_type: str  # direct, possessive, comparison
    
class DynamicBrandExtractor:
    """Dynamically extracts brand names from AI responses using NLP patterns"""
    
    # Common brand/company indicators
    BRAND_INDICATORS = {
        "company", "brand", "corporation", "corp", "inc", "incorporated", 
        "limited", "ltd", "llc", "co", "group", "enterprises", "systems",
        "technologies", "tech", "solutions", "services", "international",
        "global", "worldwide", "usa", "america", "labs", "laboratory"
    }
    
    # Business entity suffixes
    BUSINESS_SUFFIXES = {
        "inc", "corp", "corporation", "co", "company", "ltd", "limited", 
        "llc", "llp", "lp", "plc", "sa", "gmbh", "ag", "spa", "srl"
    }
    
    # Common possessive patterns for brands
    POSSESSIVE_PATTERNS = [
        r"(\w+(?:\s+\w+){0,2})'s\s+(?:products?|services?|platform|solution|technology)",
        r"(\w+(?:\s+\w+){0,2})'s\s+(?:new|latest|best|top)",
        r"by\s+(\w+(?:\s+\w+){0,2})",
        r"from\s+(\w+(?:\s+\w+){0,2})",
        r"made\s+by\s+(\w+(?:\s+\w+){0,2})"
    ]
    
    # Brand mention patterns
    BRAND_PATTERNS = [
        # Direct brand mentions
        r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b(?:\s+(?:' + '|'.join(BRAND_INDICATORS) + '))?',
        # Acronyms/abbreviations
        r'\b([A-Z]{2,6})\b',
        # Product-brand patterns
        r'\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\s+(?:shoes|sneakers|apparel|clothing|gear|equipment|products?)',
    ]
    
    # Common non-brand words to filter out
    EXCLUDE_WORDS = {
        "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", 
        "by", "from", "up", "about", "into", "through", "during", "before", 
        "after", "above", "below", "between", "among", "this", "that", "these", 
        "those", "i", "me", "my", "myself", "we", "us", "our", "ours", "ourselves",
        "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", 
        "himself", "she", "her", "hers", "herself", "it", "its", "itself", 
        "they", "them", "their", "theirs", "themselves", "what", "which", "who", 
        "whom", "this", "that", "these", "those", "am", "is", "are", "was", 
        "were", "be", "been", "being", "have", "has", "had", "having", "do", 
        "does", "did", "doing", "a", "an", "as", "able", "about", "across", 
        "after", "all", "almost", "also", "although", "always", "among", "any", 
        "are", "because", "been", "before", "being", "both", "but", "can", 
        "could", "did", "does", "either", "every", "far", "from", "get", "has", 
        "have", "how", "however", "its", "may", "might", "more", "most", "much", 
        "must", "neither", "now", "often", "other", "our", "own", "said", "say", 
        "she", "should", "since", "some", "than", "that", "their", "them", 
        "there", "they", "through", "too", "under", "until", "very", "was", 
        "way", "well", "were", "what", "where", "which", "while", "who", "will", 
        "with", "would", "your", "here", "there", "when", "where", "why", "how",
        "many", "much", "few", "several", "all", "some", "any", "each", "every",
        "good", "great", "best", "better", "top", "high", "low", "new", "old",
        "big", "small", "large", "little", "long", "short", "right", "left",
        "first", "last", "next", "previous", "same", "different", "similar",
        "such", "like", "just", "only", "also", "even", "still", "yet", "already"
    }
    
    # Industry-specific common words to exclude
    INDUSTRY_COMMON_WORDS = {
        "fitness": {"workout", "training", "fitness", "gym", "exercise", "sport", "sports", "athletic", "performance"},
        "beauty": {"beauty", "skincare", "makeup", "cosmetic", "skin", "face", "body", "hair"},
        "tech": {"software", "technology", "platform", "system", "app", "application", "service"},
        "generic": {"product", "service", "solution", "quality", "price", "value", "customer"}
    }
    
    def __init__(self, target_brand: str, industry: str = "generic"):
        self.target_brand = target_brand.lower()
        self.target_brand_variations = self._generate_brand_variations(target_brand)
        self.industry = industry
        self.discovered_brands = Counter()
        self.brand_contexts = defaultdict(list)
        
    def _generate_brand_variations(self, brand_name: str) -> Set[str]:
        """Generate variations of the target brand name"""
        variations = {brand_name.lower()}
        
        # Add common variations
        variations.add(brand_name.upper())
        variations.add(brand_name.replace(" ", "").lower())
        variations.add(brand_name.replace(" ", ""))
        
        # Add abbreviated forms
        if " " in brand_name:
            words = brand_name.split()
            if len(words) <= 4:  # Only for reasonable length
                abbreviation = "".join(word[0].upper() for word in words)
                variations.add(abbreviation)
                variations.add(abbreviation.lower())
        
        return variations
    
    def extract_brands_from_response(self, response_text: str, query: str = "") -> Dict[str, List[BrandMention]]:
        """Extract all potential brand mentions from AI response"""
        brands_found = defaultdict(list)
        
        # Clean and prepare text
        text = self._clean_text(response_text)
        sentences = self._split_into_sentences(text)
        
        for sentence_idx, sentence in enumerate(sentences):
            # Extract using different patterns
            mentions = []
            
            # 1. Use possessive patterns
            mentions.extend(self._extract_possessive_brands(sentence, sentence_idx))
            
            # 2. Use capitalized word patterns  
            mentions.extend(self._extract_capitalized_brands(sentence, sentence_idx))
            
            # 3. Use context-based extraction
            mentions.extend(self._extract_contextual_brands(sentence, sentence_idx, query))
            
            # Filter and validate mentions
            for mention in mentions:
                if self._is_valid_brand_mention(mention.name, sentence):
                    brands_found[mention.name.lower()].append(mention)
        
        # Post-process and rank brands
        return self._post_process_brands(brands_found, response_text)
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for brand extraction"""
        # Remove URLs, emails, and other noise
        text = re.sub(r'http[s]?://[^\s]+', '', text)
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _extract_possessive_brands(self, sentence: str, position: int) -> List[BrandMention]:
        """Extract brands using possessive patterns"""
        mentions = []
        
        for pattern in self.POSSESSIVE_PATTERNS:
            for match in re.finditer(pattern, sentence, re.IGNORECASE):
                brand_name = match.group(1).strip()
                if brand_name and len(brand_name.split()) <= 3:  # Reasonable brand length
                    mentions.append(BrandMention(
                        name=brand_name.title(),
                        confidence=0.8,
                        context=sentence,
                        position=position,
                        mention_type="possessive"
                    ))
        
        return mentions
    
    def _extract_capitalized_brands(self, sentence: str, position: int) -> List[BrandMention]:
        """Extract brands using capitalization patterns"""
        mentions = []
        
        # Look for capitalized sequences
        pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b'
        for match in re.finditer(pattern, sentence):
            brand_name = match.group(1).strip()
            
            # Additional validation for capitalized brands
            if self._is_likely_brand_name(brand_name, sentence):
                confidence = self._calculate_brand_confidence(brand_name, sentence)
                if confidence > 0.3:  # Minimum confidence threshold
                    mentions.append(BrandMention(
                        name=brand_name,
                        confidence=confidence,
                        context=sentence,
                        position=position,
                        mention_type="direct"
                    ))
        
        return mentions
    
    def _extract_contextual_brands(self, sentence: str, position: int, query: str = "") -> List[BrandMention]:
        """Extract brands using contextual clues"""
        mentions = []
        
        # Look for brands in comparison contexts
        comparison_patterns = [
            r'(?:better than|compared to|versus|vs\.?|against)\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+(?:is better|outperforms|beats)',
            r'(?:like|similar to|such as)\s+([A-Z][a-zA-Z\s]+)'
        ]
        
        for pattern in comparison_patterns:
            for match in re.finditer(pattern, sentence, re.IGNORECASE):
                brand_name = match.group(1).strip()
                if brand_name and self._is_likely_brand_name(brand_name, sentence):
                    mentions.append(BrandMention(
                        name=brand_name.title(),
                        confidence=0.6,
                        context=sentence,
                        position=position,
                        mention_type="comparison"
                    ))
        
        return mentions
    
    def _is_likely_brand_name(self, name: str, context: str) -> bool:
        """Determine if a name is likely a brand"""
        name_lower = name.lower()
        
        # Basic filters
        if len(name) < 2 or len(name.split()) > 4:
            return False
        
        if name_lower in self.EXCLUDE_WORDS:
            return False
        
        # Check against industry common words
        industry_words = self.INDUSTRY_COMMON_WORDS.get(self.industry, set())
        if name_lower in industry_words:
            return False
        
        # Look for brand indicators in context
        context_lower = context.lower()
        brand_context_indicators = [
            "brand", "company", "manufacturer", "makes", "produces", "offers",
            "sells", "available from", "by", "from", "choose", "prefer",
            "recommend", "suggests", "consider", "try", "use", "popular"
        ]
        
        has_brand_context = any(indicator in context_lower for indicator in brand_context_indicators)
        
        # Higher likelihood for proper nouns with brand context
        is_proper_noun = name[0].isupper() and not name.isupper()
        
        return has_brand_context or is_proper_noun
    
    def _calculate_brand_confidence(self, brand_name: str, context: str) -> float:
        """Calculate confidence score for brand mention"""
        confidence = 0.0
        context_lower = context.lower()
        name_lower = brand_name.lower()
        
        # Base confidence for proper capitalization
        if brand_name[0].isupper() and not brand_name.isupper():
            confidence += 0.4
        
        # Higher base confidence for known patterns
        if brand_name.isupper() and len(brand_name) >= 2:  # Acronyms
            confidence += 0.5
        
        # Boost for brand context indicators
        brand_indicators = ["brand", "company", "makes", "by", "from", "offers", "sells", "choose", "consider", "prefer"]
        for indicator in brand_indicators:
            if indicator in context_lower:
                confidence += 0.3
                break
        
        # Boost for comparison context (very strong indicator)
        comparison_words = ["versus", "vs", "compared", "better", "worse", "than", "like", "also", "however", "but"]
        if any(word in context_lower for word in comparison_words):
            confidence += 0.4
        
        # Boost for recommendation context
        recommendation_words = ["recommend", "suggest", "try", "consider", "check out", "look at"]
        if any(word in context_lower for word in recommendation_words):
            confidence += 0.3
        
        # Boost for industry-specific context
        if self.industry == "fitness":
            fitness_words = ["shoes", "sneakers", "apparel", "athletic", "sports", "gear", "performance", "training"]
            if any(word in context_lower for word in fitness_words):
                confidence += 0.2
        
        # Reduce confidence for common words
        if name_lower in self.EXCLUDE_WORDS:
            confidence -= 0.8
        
        # Reduce confidence for very short names (unless acronym)
        if len(brand_name) <= 2 and not brand_name.isupper():
            confidence -= 0.3
        
        return min(1.0, max(0.0, confidence))
    
    def _is_valid_brand_mention(self, brand_name: str, context: str) -> bool:
        """Final validation for brand mentions"""
        name_lower = brand_name.lower()
        
        # Skip target brand variations
        if name_lower in self.target_brand_variations:
            return False
        
        # Skip very common words
        if name_lower in self.EXCLUDE_WORDS:
            return False
        
        # Skip single characters
        if len(brand_name) <= 1:
            return False
        
        # Skip obvious non-brands
        non_brand_patterns = [
            r'^\d+$',  # Pure numbers
            r'^[a-z]+$',  # All lowercase (usually not brands)
            r'^(and|or|the|with|for|from|that)$'  # Common function words
        ]
        
        for pattern in non_brand_patterns:
            if re.match(pattern, brand_name, re.IGNORECASE):
                return False
        
        return True
    
    def _post_process_brands(self, brands_found: Dict[str, List[BrandMention]], full_text: str) -> Dict[str, List[BrandMention]]:
        """Post-process and clean up discovered brands"""
        processed_brands = {}
        
        # Merge similar brand names
        brand_groups = self._group_similar_brands(brands_found)
        
        for canonical_name, mentions in brand_groups.items():
            if len(mentions) >= 1:  # At least 1 mention
                # Calculate aggregate confidence
                avg_confidence = sum(m.confidence for m in mentions) / len(mentions)
                
                # Keep only if meets minimum confidence and frequency
                if avg_confidence >= 0.3 or len(mentions) >= 2:
                    processed_brands[canonical_name] = mentions
        
        return processed_brands
    
    def _group_similar_brands(self, brands_found: Dict[str, List[BrandMention]]) -> Dict[str, List[BrandMention]]:
        """Group similar brand variations together"""
        groups = {}
        processed = set()
        
        for brand_name, mentions in brands_found.items():
            if brand_name in processed:
                continue
                
            # Find similar brand names
            similar_brands = [brand_name]
            for other_brand in brands_found:
                if other_brand != brand_name and other_brand not in processed:
                    if self._are_similar_brands(brand_name, other_brand):
                        similar_brands.append(other_brand)
            
            # Use the most common/confident name as canonical
            canonical = max(similar_brands, key=lambda x: len(brands_found[x]))
            
            # Merge all mentions
            all_mentions = []
            for similar in similar_brands:
                all_mentions.extend(brands_found[similar])
                processed.add(similar)
            
            groups[canonical.title()] = all_mentions
        
        return groups
    
    def _are_similar_brands(self, brand1: str, brand2: str) -> bool:
        """Check if two brand names are similar variations"""
        # Simple similarity check
        b1, b2 = brand1.lower(), brand2.lower()
        
        # Exact match after normalization
        if b1.replace(" ", "") == b2.replace(" ", ""):
            return True
        
        # One is abbreviation of the other
        if " " in b1 and not " " in b2:
            abbrev = "".join(word[0] for word in b1.split())
            if abbrev.lower() == b2:
                return True
        
        if " " in b2 and not " " in b1:
            abbrev = "".join(word[0] for word in b2.split())
            if abbrev.lower() == b1:
                return True
        
        return False
    
    def get_top_competitors(self, response_analyses: List[Dict], top_n: int = 10) -> List[Dict[str, any]]:
        """Get top discovered competitors from multiple responses"""
        all_competitors = Counter()
        competitor_contexts = defaultdict(list)
        
        for analysis in response_analyses:
            if isinstance(analysis, dict) and 'response' in analysis:
                brands = self.extract_brands_from_response(analysis['response'], analysis.get('query', ''))
                
                for brand_name, mentions in brands.items():
                    if brand_name.lower() not in self.target_brand_variations:
                        # Weight by confidence and frequency
                        weight = sum(mention.confidence for mention in mentions)
                        all_competitors[brand_name] += weight
                        
                        # Store contexts for analysis
                        competitor_contexts[brand_name].extend([m.context for m in mentions])
        
        # Return top competitors with metadata
        top_competitors = []
        for brand, score in all_competitors.most_common(top_n):
            top_competitors.append({
                "name": brand.title(),
                "mention_score": score,
                "mention_count": len(competitor_contexts[brand]),
                "contexts": competitor_contexts[brand][:3],  # Sample contexts
                "confidence": score / len(response_analyses)  # Normalize by number of analyses
            })
        
        return top_competitors

# Example usage and testing
if __name__ == "__main__":
    # Test with Nike
    extractor = DynamicBrandExtractor("Nike", "fitness")
    
    test_response = """
    When it comes to athletic footwear, Nike is a top choice, but you should also consider Adidas, 
    which offers excellent performance shoes. Under Armour has been gaining popularity, and Puma 
    makes some great running shoes too. New Balance is known for their comfort, while Reebok 
    focuses on cross-training. Some people prefer Asics for long-distance running.
    """
    
    brands = extractor.extract_brands_from_response(test_response, "best running shoes")
    
    print("Discovered brands:")
    for brand, mentions in brands.items():
        print(f"  {brand}: {len(mentions)} mentions, avg confidence: {sum(m.confidence for m in mentions)/len(mentions):.2f}")
        for mention in mentions:
            print(f"    - {mention.mention_type}: '{mention.context[:50]}...' (conf: {mention.confidence:.2f})")