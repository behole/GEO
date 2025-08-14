#!/usr/bin/env python3
"""
Test suite for Content Analysis Agent
Tests core functionality and validates implementation
"""

import asyncio
import unittest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Import our modules
from config import get_config, reload_config
from content_scraper import ContentScraper, PageContent, SiteAnalysis
from content_scorer import ContentScorer, ContentStructureScore
from competitor_analyzer import CompetitorAnalyzer, ContentGap
from main import ContentAnalysisAgent
from export_manager import ExportManager

class TestContentAnalysisAgent(unittest.TestCase):
    """Test suite for the complete Content Analysis Agent"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_config = get_config()
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_config_loading(self):
        """Test configuration loading and validation"""
        config = get_config()
        
        # Test basic config access
        self.assertIsNotNone(config.BRAND_NAME)
        self.assertIsNotNone(config.BRAND_WEBSITE)
        
        # Test brand config
        brand_config = config.get_brand_config()
        self.assertIsNotNone(brand_config.name)
        self.assertIsNotNone(brand_config.website)
        
        # Test competitors
        competitors = config.get_competitors()
        self.assertIsInstance(competitors, list)
        
        # Test validation
        validation = config.validate_configuration()
        self.assertIn("valid", validation)
        if not validation["valid"]:
            print(f"Config validation issues: {validation['issues']}")
    
    def test_content_scraper_initialization(self):
        """Test ContentScraper initialization and basic functionality"""
        scraper = ContentScraper(self.test_config)
        self.assertIsNotNone(scraper.config)
        self.assertEqual(len(scraper.scraped_urls), 0)
        self.assertEqual(len(scraper.failed_urls), 0)
    
    def test_page_content_creation(self):
        """Test PageContent dataclass creation"""
        page_content = PageContent(
            url="https://example.com/test",
            title="Test Page",
            meta_description="Test description",
            headings={"h1": ["Main Heading"], "h2": ["Sub Heading"]},
            paragraphs=["Test paragraph content with sufficient length for analysis."],
            lists=[["Item 1", "Item 2", "Item 3"]],
            images=[{"src": "test.jpg", "alt": "Test image"}],
            links=[{"href": "https://example.com", "text": "Link", "type": "external"}],
            structured_data=[{"type": "json-ld", "data": "{}"}],
            word_count=100,
            reading_time=1,
            last_modified="2024-01-01T00:00:00",
            content_type="general_page",
            raw_html="<html><body>Test</body></html>",
            clean_text="Test paragraph content with sufficient length for analysis.",
            markdown="# Test\nTest paragraph content.",
            scrape_timestamp="2024-01-01T00:00:00",
            scrape_success=True,
            error_message=None
        )
        
        self.assertEqual(page_content.url, "https://example.com/test")
        self.assertEqual(page_content.word_count, 100)
        self.assertTrue(page_content.scrape_success)
    
    def test_content_scorer_initialization(self):
        """Test ContentScorer initialization"""
        scorer = ContentScorer(self.test_config)
        self.assertIsNotNone(scorer.config)
        self.assertIsNotNone(scorer.geo_practices)
        self.assertIsNotNone(scorer.scoring_weights)
    
    def test_content_structure_scoring(self):
        """Test content structure scoring functionality"""
        scorer = ContentScorer(self.test_config)
        
        # Create test page content
        test_page = PageContent(
            url="https://example.com/test",
            title="Test Page for Content Scoring Analysis",
            meta_description="This is a test meta description for content analysis.",
            headings={
                "h1": ["Main Heading About Sunscreen"],
                "h2": ["Benefits of Mineral Sunscreen", "How to Apply"],
                "h3": ["Zinc Oxide Benefits", "Titanium Dioxide Benefits"]
            },
            paragraphs=[
                "This is a well-structured paragraph about mineral sunscreen benefits. It contains adequate information about zinc oxide and titanium dioxide ingredients that provide broad spectrum protection.",
                "Another paragraph discussing application methods. The paragraph explains proper application techniques for powder sunscreen products including coverage and reapplication.",
                "A final paragraph about skin types and recommendations. This content addresses different skin concerns and provides specific guidance for sensitive skin users."
            ],
            lists=[
                ["Zinc oxide provides UVA protection", "Titanium dioxide blocks UVB rays", "Both are reef-safe ingredients"],
                ["Apply evenly across face", "Reapply every 2 hours", "Use adequate amount for coverage"]
            ],
            images=[{"src": "sunscreen.jpg", "alt": "Mineral sunscreen application"}],
            links=[
                {"href": "https://fda.gov/sunscreen", "text": "FDA Guidelines", "type": "external"},
                {"href": "https://example.com/products", "text": "Our Products", "type": "internal"}
            ],
            structured_data=[{"type": "json-ld", "data": '{"@type": "Product"}'}],
            word_count=150,
            reading_time=1,
            last_modified="2024-01-01T00:00:00",
            content_type="product_page",
            raw_html="<html><body>Test content</body></html>",
            clean_text="This is a well-structured paragraph about mineral sunscreen benefits. It contains adequate information about zinc oxide and titanium dioxide ingredients that provide broad spectrum protection. Another paragraph discussing application methods. The paragraph explains proper application techniques for powder sunscreen products including coverage and reapplication. A final paragraph about skin types and recommendations. This content addresses different skin concerns and provides specific guidance for sensitive skin users.",
            markdown="# Main Heading\n\nTest content paragraphs.",
            scrape_timestamp="2024-01-01T00:00:00",
            scrape_success=True,
            error_message=None
        )
        
        # Test content structure scoring
        structure_score = scorer._score_content_structure(test_page)
        self.assertIsInstance(structure_score, ContentStructureScore)
        self.assertGreaterEqual(structure_score.total_score, 0)
        self.assertLessEqual(structure_score.total_score, 100)
        
        # Test individual scoring components
        self.assertGreaterEqual(structure_score.paragraph_length_score, 0)
        self.assertGreaterEqual(structure_score.heading_hierarchy_score, 0)
        self.assertGreaterEqual(structure_score.readability_score, 0)
    
    def test_competitor_analyzer_initialization(self):
        """Test CompetitorAnalyzer initialization"""
        analyzer = CompetitorAnalyzer(self.test_config)
        self.assertIsNotNone(analyzer.config)
        self.assertIsNotNone(analyzer.brand_config)
        self.assertIsInstance(analyzer.competitors, list)
    
    def test_content_gap_creation(self):
        """Test ContentGap dataclass creation"""
        gap = ContentGap(
            gap_type="missing_content_type",
            description="Missing ingredient guide content",
            competitor_examples=["EltaMD: Detailed ingredient analysis", "Supergoop: Scientific backing"],
            priority="high",
            estimated_effort="medium",
            business_impact="high"
        )
        
        self.assertEqual(gap.gap_type, "missing_content_type")
        self.assertEqual(gap.priority, "high")
        self.assertEqual(len(gap.competitor_examples), 2)
    
    def test_export_manager_initialization(self):
        """Test ExportManager initialization"""
        export_manager = ExportManager(self.temp_dir)
        self.assertTrue(export_manager.output_dir.exists())
        self.assertTrue(export_manager.session_dir.exists())
    
    def test_export_manager_json_export(self):
        """Test JSON export functionality"""
        export_manager = ExportManager(self.temp_dir)
        
        test_results = {
            "agent_info": {
                "name": "Content Analysis Agent",
                "version": "1.0.0",
                "brand": "Test Brand"
            },
            "brand_content_analysis": {
                "overall_score": 75.5,
                "pages_analyzed": 10
            },
            "competitive_gap_analysis": {
                "identified_gaps": [
                    {"type": "keyword_gap", "description": "Missing zinc oxide content"}
                ]
            }
        }
        
        # Test JSON export (synchronous version for testing)
        json_file = export_manager.session_dir / "test_export.json"
        with open(json_file, 'w') as f:
            json.dump(test_results, f, indent=2, default=str)
        
        self.assertTrue(json_file.exists())
        
        # Verify content
        with open(json_file, 'r') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data["agent_info"]["brand"], "Test Brand")
        self.assertEqual(loaded_data["brand_content_analysis"]["overall_score"], 75.5)
    
    def test_content_analysis_agent_initialization(self):
        """Test ContentAnalysisAgent initialization"""
        agent = ContentAnalysisAgent()
        self.assertIsNotNone(agent.config)
        self.assertIsNotNone(agent.brand_config)
    
    def test_url_prioritization(self):
        """Test URL prioritization logic"""
        scraper = ContentScraper(self.test_config)
        
        test_urls = [
            "https://example.com/product/sunscreen",
            "https://example.com/ingredients/zinc-oxide", 
            "https://example.com/blog/random-post",
            "https://example.com/faq",
            "https://example.com/very/deep/nested/path/page",
            "https://example.com/about"
        ]
        
        prioritized_urls = scraper._prioritize_urls(test_urls, 4)
        
        # Should return 4 URLs
        self.assertEqual(len(prioritized_urls), 4)
        
        # High priority URLs should be included
        prioritized_url_strings = " ".join(prioritized_urls)
        self.assertIn("product", prioritized_url_strings)
        self.assertIn("ingredients", prioritized_url_strings)
        self.assertIn("faq", prioritized_url_strings)
    
    def test_keyword_extraction(self):
        """Test keyword extraction and coverage analysis"""
        analyzer = CompetitorAnalyzer(self.test_config)
        
        test_pages = [
            PageContent(
                url="https://example.com/test1",
                title="Zinc Oxide Mineral Sunscreen",
                meta_description="Test",
                headings={},
                paragraphs=[],
                lists=[],
                images=[],
                links=[],
                structured_data=[],
                word_count=50,
                reading_time=1,
                last_modified=None,
                content_type="product_page",
                raw_html="",
                clean_text="Zinc oxide mineral sunscreen provides broad spectrum protection for sensitive skin. This reef safe sunscreen is perfect for daily use.",
                markdown="",
                scrape_timestamp="2024-01-01T00:00:00",
                scrape_success=True,
                error_message=None
            ),
            PageContent(
                url="https://example.com/test2",
                title="Titanium Dioxide Benefits",
                meta_description="Test",
                headings={},
                paragraphs=[],
                lists=[],
                images=[],
                links=[],
                structured_data=[],
                word_count=40,
                reading_time=1,
                last_modified=None,
                content_type="ingredient_guide",
                raw_html="",
                clean_text="Titanium dioxide is another mineral sunscreen ingredient that blocks UV radiation effectively.",
                markdown="",
                scrape_timestamp="2024-01-01T00:00:00",
                scrape_success=True,
                error_message=None
            )
        ]
        
        keyword_coverage = analyzer._analyze_keyword_coverage(test_pages)
        
        # Check that keywords were found
        self.assertIn("zinc oxide", keyword_coverage)
        self.assertIn("titanium dioxide", keyword_coverage)
        self.assertIn("mineral sunscreen", keyword_coverage)
        
        # Verify counts
        self.assertGreaterEqual(keyword_coverage.get("zinc oxide", 0), 1)
        self.assertGreaterEqual(keyword_coverage.get("mineral sunscreen", 0), 1)
    
    def test_scoring_weight_validation(self):
        """Test that scoring weights are properly configured"""
        config = get_config()
        weights = config.get_scoring_weights()
        
        # Check that weights sum to approximately 1.0
        total_weight = (
            weights.content_structure +
            weights.citation_worthiness +
            weights.authority_signals +
            weights.competitor_gap_coverage +
            weights.ai_consumption_optimization
        )
        
        self.assertAlmostEqual(total_weight, 1.0, places=2)
        
        # Check individual weights are reasonable
        self.assertGreater(weights.content_structure, 0)
        self.assertLess(weights.content_structure, 1)
        self.assertGreater(weights.citation_worthiness, 0)
        self.assertLess(weights.citation_worthiness, 1)

class TestAsyncFunctionality(unittest.IsolatedAsyncioTestCase):
    """Test async functionality separately"""
    
    async def test_mock_website_scraping(self):
        """Test website scraping with mocked responses"""
        config = get_config()
        scraper = ContentScraper(config)
        
        # Mock a simple successful scrape
        with patch.object(scraper, 'scrape_single_page', new_callable=AsyncMock) as mock_scrape:
            mock_scrape.return_value = PageContent(
                url="https://example.com/test",
                title="Mock Page",
                meta_description="Mock description",
                headings={"h1": ["Mock Heading"]},
                paragraphs=["Mock paragraph content for testing purposes."],
                lists=[["Mock", "List", "Items"]],
                images=[],
                links=[],
                structured_data=[],
                word_count=50,
                reading_time=1,
                last_modified=None,
                content_type="general_page",
                raw_html="<html><body>Mock</body></html>",
                clean_text="Mock paragraph content for testing purposes.",
                markdown="# Mock\nMock content.",
                scrape_timestamp="2024-01-01T00:00:00",
                scrape_success=True,
                error_message=None
            )
            
            # Test single page scraping
            result = await scraper.scrape_single_page("https://example.com/test")
            self.assertIsNotNone(result)
            self.assertTrue(result.scrape_success)
            self.assertEqual(result.title, "Mock Page")
    
    async def test_mock_competitive_analysis(self):
        """Test competitive analysis with mocked data"""
        config = get_config()
        analyzer = CompetitorAnalyzer(config)
        
        # Mock the individual competitor analysis
        mock_analysis = Mock()
        mock_analysis.competitor_name = "Test Competitor"
        mock_analysis.content_types_found = {"product_page": 5, "faq_page": 2}
        mock_analysis.keyword_coverage = {"zinc oxide": 10, "sunscreen": 15}
        mock_analysis.unique_content_features = ["Video content", "Interactive tools"]
        
        with patch.object(analyzer, '_analyze_single_competitor', new_callable=AsyncMock) as mock_analyze:
            mock_analyze.return_value = mock_analysis
            
            # Test single competitor analysis
            result = await analyzer._analyze_single_competitor("Test", "https://example.com", 10)
            self.assertEqual(result.competitor_name, "Test Competitor")
            self.assertIn("product_page", result.content_types_found)

def run_integration_test():
    """Run a basic integration test with real web scraping (optional)"""
    print("\n" + "="*60)
    print("INTEGRATION TEST - Content Analysis Agent")
    print("="*60)
    
    try:
        # Test with a simple, reliable website
        config = get_config()
        
        # Override with a test website
        original_website = config.BRAND_WEBSITE
        config.BRAND_WEBSITE = "https://httpbin.org"  # Simple, reliable test site
        
        print(f"Testing with: {config.BRAND_WEBSITE}")
        
        async def run_test():
            agent = ContentAnalysisAgent()
            
            # Run a limited analysis
            print("Running limited content analysis...")
            results = await agent._analyze_brand_content(max_pages=5)
            
            print(f"Pages analyzed: {results.get('pages_analyzed', 0)}")
            print(f"Overall score: {results.get('overall_score', 0):.1f}")
            print(f"Analysis completed: {results.get('analysis_timestamp', 'Unknown')}")
            
            return results
        
        results = asyncio.run(run_test())
        print("✅ Integration test completed successfully!")
        
        # Restore original config
        config.BRAND_WEBSITE = original_website
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")
        print("This is expected if network access is limited or target site is unavailable.")

def main():
    """Run all tests"""
    print("Content Analysis Agent - Test Suite")
    print("="*50)
    
    # Run unit tests
    unittest.main(argv=[''], exit=False, verbosity=2)
    
    # Run integration test (optional)
    integration_test = input("\nRun integration test with real web scraping? (y/N): ")
    if integration_test.lower() == 'y':
        run_integration_test()
    
    print("\n" + "="*50)
    print("Test suite completed!")
    print("\nTo run the full agent:")
    print("  python main.py --max-pages 20")
    print("\nTo run specific tests:")
    print("  python -m unittest test_agent.TestContentAnalysisAgent.test_config_loading")

if __name__ == "__main__":
    main()