from typing import Dict, List
import json

class QueryMatrix:
    """Structured query matrix for mineral sunscreen discovery baseline"""
    
    # Base prompt for all AI engines
    BASE_PROMPT = """
    You are a helpful assistant providing comprehensive information about sunscreen products. 
    Please provide detailed recommendations including specific brand names, product names, 
    and reasons for recommendations. Include information about ingredients, SPF levels, 
    skin types, and any specific benefits. If possible, mention multiple brands and products 
    to give users comprehensive options.
    """
    
    # Query categories with structured queries
    QUERY_CATEGORIES = {
        "direct_product_discovery": {
            "description": "Direct product recommendations and discovery",
            "queries": [
                "best mineral sunscreen 2024",
                "top rated zinc oxide sunscreen",
                "mineral powder sunscreen recommendations",
                "best reef safe sunscreen",
                "dermatologist recommended mineral sunscreen",
                "best mineral sunscreen for face",
                "high SPF mineral sunscreen",
                "mineral sunscreen for sensitive skin",
                "best chemical free sunscreen",
                "organic mineral sunscreen brands",
                "luxury mineral sunscreen products",
                "affordable mineral sunscreen options",
                "travel size mineral sunscreen",
                "waterproof mineral sunscreen",
                "tinted mineral sunscreen powder"
            ]
        },
        "problem_solution": {
            "description": "Problem-focused queries for specific skin concerns",
            "queries": [
                "mineral sunscreen that doesn't leave white cast",
                "sunscreen for acne prone skin mineral",
                "mineral sunscreen for dark skin tones",
                "non greasy mineral sunscreen",
                "mineral sunscreen for kids sensitive skin",
                "sunscreen that won't clog pores mineral",
                "mineral sunscreen for rosacea",
                "hypoallergenic mineral sunscreen",
                "fragrance free mineral sunscreen",
                "mineral sunscreen for eczema",
                "pregnancy safe mineral sunscreen",
                "mineral sunscreen for oily skin"
            ]
        },
        "application_usage": {
            "description": "Application techniques and usage guidance",
            "queries": [
                "how to apply powder sunscreen correctly",
                "powder sunscreen over makeup tutorial",
                "reapplying powder sunscreen during day",
                "setting powder with SPF vs sunscreen",
                "mineral sunscreen application tips",
                "how much powder sunscreen to use",
                "powder sunscreen for touch ups",
                "layering mineral sunscreen with skincare",
                "mineral sunscreen under foundation",
                "best way to blend powder sunscreen"
            ]
        },
        "ingredient_science": {
            "description": "Scientific and ingredient-focused queries",
            "queries": [
                "zinc oxide vs titanium dioxide sunscreen",
                "nano vs non nano mineral sunscreen",
                "mineral sunscreen ingredients to avoid",
                "how does zinc oxide sunscreen work",
                "titanium dioxide safety in sunscreen",
                "mineral sunscreen chemical composition",
                "SPF ratings mineral vs chemical",
                "UV protection mineral sunscreen science"
            ]
        },
        "comparison_shopping": {
            "description": "Comparative analysis and shopping guidance",
            "queries": [
                "mineral vs chemical sunscreen pros cons",
                "powder vs cream mineral sunscreen",
                "drugstore vs luxury mineral sunscreen",
                "Korean vs American mineral sunscreen",
                "mineral sunscreen vs BB cream SPF"
            ]
        }
    }
    
    @classmethod
    def get_all_queries(cls) -> List[str]:
        """Get all queries as a flat list"""
        all_queries = []
        for category in cls.QUERY_CATEGORIES.values():
            all_queries.extend(category["queries"])
        return all_queries
    
    @classmethod
    def get_queries_by_category(cls, category_name: str) -> List[str]:
        """Get queries for a specific category"""
        if category_name in cls.QUERY_CATEGORIES:
            return cls.QUERY_CATEGORIES[category_name]["queries"]
        return []
    
    @classmethod
    def get_category_info(cls) -> Dict[str, Dict]:
        """Get information about all categories"""
        return {
            name: {
                "description": category["description"],
                "query_count": len(category["queries"])
            }
            for name, category in cls.QUERY_CATEGORIES.items()
        }
    
    @classmethod
    def get_total_query_count(cls) -> int:
        """Get total number of queries"""
        return len(cls.get_all_queries())
    
    @classmethod
    def get_structured_queries(cls) -> Dict[str, List[str]]:
        """Get queries organized by category"""
        return {
            category_name: category["queries"]
            for category_name, category in cls.QUERY_CATEGORIES.items()
        }
    
    @classmethod
    def export_to_json(cls, filepath: str) -> None:
        """Export query matrix to JSON file"""
        data = {
            "meta": {
                "total_queries": cls.get_total_query_count(),
                "categories": cls.get_category_info(),
                "base_prompt": cls.BASE_PROMPT
            },
            "queries": {
                "by_category": cls.get_structured_queries(),
                "flat_list": cls.get_all_queries()
            }
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    @classmethod
    def validate_queries(cls) -> Dict[str, any]:
        """Validate query matrix and return statistics"""
        all_queries = cls.get_all_queries()
        unique_queries = set(all_queries)
        
        # Check for duplicates
        duplicates = []
        seen = set()
        for query in all_queries:
            if query in seen:
                duplicates.append(query)
            seen.add(query)
        
        # Length analysis
        query_lengths = [len(query) for query in all_queries]
        
        return {
            "total_queries": len(all_queries),
            "unique_queries": len(unique_queries),
            "duplicates": duplicates,
            "duplicate_count": len(duplicates),
            "categories": len(cls.QUERY_CATEGORIES),
            "length_stats": {
                "min": min(query_lengths),
                "max": max(query_lengths),
                "avg": sum(query_lengths) / len(query_lengths)
            },
            "valid": len(duplicates) == 0 and len(all_queries) >= 50
        }

# Additional specialized query sets for testing
class SpecializedQueries:
    """Additional specialized query sets for focused testing"""
    
    COMPETITOR_FOCUSED = [
        "EltaMD mineral sunscreen review",
        "Blue Lizard sunscreen vs mineral alternatives",
        "Neutrogena mineral sunscreen comparison",
        "CeraVe mineral sunscreen ingredients",
        "La Roche Posay mineral sunscreen recommendations"
    ]
    
    BRAND_AWARENESS = [
        "new mineral sunscreen brands 2024",
        "indie mineral sunscreen companies",
        "clean beauty mineral sunscreen brands",
        "sustainable mineral sunscreen options",
        "mineral sunscreen startup brands"
    ]
    
    SEASONAL_TRENDING = [
        "summer mineral sunscreen must-haves",
        "winter mineral sunscreen protection",
        "beach vacation mineral sunscreen",
        "ski trip mineral sunscreen recommendations",
        "daily commute mineral sunscreen"
    ]
    
    @classmethod
    def get_all_specialized(cls) -> Dict[str, List[str]]:
        """Get all specialized query sets"""
        return {
            "competitor_focused": cls.COMPETITOR_FOCUSED,
            "brand_awareness": cls.BRAND_AWARENESS,
            "seasonal_trending": cls.SEASONAL_TRENDING
        }

if __name__ == "__main__":
    # Validate and display query matrix stats
    stats = QueryMatrix.validate_queries()
    print("Query Matrix Validation:")
    print(f"Total queries: {stats['total_queries']}")
    print(f"Unique queries: {stats['unique_queries']}")
    print(f"Categories: {stats['categories']}")
    print(f"Valid: {stats['valid']}")
    
    if stats['duplicates']:
        print(f"Duplicates found: {stats['duplicate_count']}")
        for dup in stats['duplicates']:
            print(f"  - {dup}")
    
    # Export to JSON
    QueryMatrix.export_to_json("query_matrix.json")
    print("\nQuery matrix exported to query_matrix.json")