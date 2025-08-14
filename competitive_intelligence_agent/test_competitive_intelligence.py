import asyncio
import pytest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from config import get_config, CompetitiveIntelligenceConfig
from competitive_intelligence_agent import CompetitiveIntelligenceAgent
from competitor_strategy_analyzer import CompetitorStrategyAnalyzer, ContentStrategyScore
from market_position_tracker import MarketPositionTracker, MarketGapOpportunity
from strategic_insights_generator import StrategicInsightsGenerator, TacticalRecommendation

class TestCompetitiveIntelligenceConfig:
    """Test configuration and setup"""
    
    def test_config_initialization(self):
        """Test configuration initializes correctly"""
        config = CompetitiveIntelligenceConfig()
        
        assert config.BRAND_NAME == "Brush on Block"
        assert config.MAX_CONCURRENT_REQUESTS > 0
        assert config.REQUEST_TIMEOUT > 0
        assert config.sector_config is not None
    
    def test_competitor_loading(self):
        """Test competitor configuration loading"""
        config = CompetitiveIntelligenceConfig()
        competitors = config.get_competitors()
        
        assert len(competitors) > 0
        assert all(hasattr(comp, 'name') for comp in competitors)
        assert all(hasattr(comp, 'priority') for comp in competitors)
        assert all(comp.priority in ['high', 'medium', 'low'] for comp in competitors)
    
    def test_analysis_weights_sum_to_one(self):
        """Test analysis weights sum to 1.0"""
        config = CompetitiveIntelligenceConfig()
        weights = config.get_analysis_weights()
        
        total_weight = (
            weights.content_depth + 
            weights.authority_signals + 
            weights.ai_optimization + 
            weights.citation_worthiness + 
            weights.content_freshness
        )
        
        assert abs(total_weight - 1.0) < 0.01
    
    def test_configuration_validation(self):
        """Test configuration validation"""
        config = CompetitiveIntelligenceConfig()
        validation = config.validate_configuration()
        
        assert 'valid' in validation
        assert 'issues' in validation
        assert 'competitors_configured' in validation
        assert 'integration_status' in validation

class TestCompetitorStrategyAnalyzer:
    """Test competitor strategy analysis"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for testing"""
        config = get_config()
        return CompetitorStrategyAnalyzer(config)
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initializes correctly"""
        assert analyzer.config is not None
        assert len(analyzer.competitors) > 0
        assert analyzer.authority_signals is not None
    
    def test_content_depth_scoring(self, analyzer):
        """Test content depth scoring logic"""
        mock_content_data = {
            'content_types_found': {'product_page': 10, 'ingredient_guide': 5, 'faq_page': 3},
            'unique_features': ['Expert endorsements', 'Clinical studies', 'Video content']
        }
        
        score = analyzer._score_content_depth(mock_content_data)
        
        assert 0 <= score <= 100
        assert isinstance(score, (int, float))
    
    def test_authority_signals_scoring(self, analyzer):
        """Test authority signals scoring"""
        mock_content_data = {
            'authority_metrics': {'avg_authority_score': 75.0, 'pages_with_author_info': 8},
            'unique_features': ['Expert endorsements', 'Clinical studies']
        }
        
        score = analyzer._score_authority_signals(mock_content_data)
        
        assert 0 <= score <= 100
        assert score > 50  # Should be high with good authority metrics
    
    def test_ai_optimization_scoring(self, analyzer):
        """Test AI optimization scoring"""
        mock_content_data = {
            'unique_features': ['FAQ sections', 'How-to guides', 'Structured data'],
            'content_types_found': {'faq_page': 5, 'guide_page': 3, 'product_page': 10}
        }
        
        score = analyzer._score_ai_optimization(mock_content_data)
        
        assert 0 <= score <= 100
    
    @pytest.mark.asyncio
    async def test_competitive_analysis_execution(self, analyzer):
        """Test full competitive analysis execution"""
        # Mock the data retrieval
        with patch.object(analyzer, '_get_competitor_content_data') as mock_data:
            mock_data.return_value = {
                'content_types_found': {'product_page': 10, 'ingredient_guide': 5},
                'unique_features': ['Expert endorsements'],
                'authority_metrics': {'avg_authority_score': 60.0, 'pages_with_author_info': 5},
                'keyword_coverage_top10': {'mineral sunscreen': 15}
            }
            
            result = await analyzer.analyze_competitive_content_strategies()
            
            assert hasattr(result, 'analysis_timestamp')
            assert hasattr(result, 'competitors_analyzed')
            assert hasattr(result, 'strategy_scores')
            assert len(result.strategy_scores) > 0

class TestMarketPositionTracker:
    """Test market position tracking and intelligence"""
    
    @pytest.fixture
    def tracker(self):
        """Create tracker instance for testing"""
        config = get_config()
        return MarketPositionTracker(config)
    
    def test_tracker_initialization(self, tracker):
        """Test tracker initializes correctly"""
        assert tracker.config is not None
        assert len(tracker.competitors) > 0
        assert tracker.query_extensions is not None
    
    @pytest.mark.asyncio
    async def test_query_matrix_expansion(self, tracker):
        """Test query matrix expansion"""
        query_matrix = await tracker._build_expanded_query_matrix()
        
        assert len(query_matrix) > len(tracker.base_queries)
        assert len(tracker.expanded_queries) > 0
        assert len(tracker.competitor_specific_queries) > 0
    
    def test_competitor_query_performance_estimation(self, tracker):
        """Test competitor query performance estimation"""
        competitor = tracker.competitors[0]
        query = "dermatologist recommended sunscreen"
        
        performance = tracker._estimate_competitor_query_performance(competitor, query)
        
        assert 0 <= performance <= 1.0
    
    def test_opportunity_score_calculation(self, tracker):
        """Test opportunity score calculation"""
        cluster_queries = ["best sunscreen for sensitive skin", "gentle sunscreen for face"]
        weakness_analysis = {"EltaMD": 0.3, "Supergoop": 0.4}
        
        score = tracker._calculate_opportunity_score(cluster_queries, weakness_analysis)
        
        assert score > 0
        assert isinstance(score, (int, float))
    
    @pytest.mark.asyncio
    async def test_market_position_analysis(self, tracker):
        """Test full market position analysis"""
        with patch.object(tracker, '_extract_baseline_queries') as mock_baseline:
            mock_baseline.return_value = ["mineral sunscreen", "zinc oxide sunscreen"]
            
            result = await tracker.analyze_market_position_intelligence()
            
            assert hasattr(result, 'analysis_timestamp')
            assert hasattr(result, 'query_matrix_size')
            assert hasattr(result, 'market_gap_opportunities')
            assert result.query_matrix_size > 0

class TestStrategicInsightsGenerator:
    """Test strategic insights generation"""
    
    @pytest.fixture
    def generator(self):
        """Create generator instance for testing"""
        config = get_config()
        return StrategicInsightsGenerator(config)
    
    def test_generator_initialization(self, generator):
        """Test generator initializes correctly"""
        assert generator.config is not None
        assert generator.brand_name is not None
    
    def test_content_gap_coverage_calculation(self, generator):
        """Test content gap coverage calculation"""
        mock_brand_analysis = {
            'ingredient_coverage': 60,
            'clinical_references': 30,
            'authority_score': 45
        }
        
        coverage = generator._calculate_brand_coverage(mock_brand_analysis, "ingredient_education")
        
        assert 0 <= coverage <= 100
        assert isinstance(coverage, (int, float))
    
    def test_tactical_recommendation_generation(self, generator):
        """Test tactical recommendation logic"""
        # This would test the logic for generating recommendations
        # based on competitive analysis results
        assert True  # Placeholder for more complex testing
    
    @pytest.mark.asyncio
    async def test_strategic_insights_generation(self, generator):
        """Test full strategic insights generation"""
        # Create mock inputs
        mock_competitive_intel = Mock()
        mock_competitive_intel.strategy_scores = []
        mock_competitive_intel.citation_patterns = []
        mock_competitive_intel.authority_analyses = []
        
        mock_market_intel = Mock()
        mock_market_intel.market_gap_opportunities = []
        mock_market_intel.seasonal_trends = {}
        mock_market_intel.baseline_queries = 50
        mock_market_intel.query_matrix_size = 150
        
        with patch.object(generator, '_analyze_content_gaps_vs_competitors') as mock_gaps:
            mock_gaps.return_value = []
            
            result = await generator.generate_strategic_insights(
                mock_competitive_intel, mock_market_intel)
            
            assert hasattr(result, 'analysis_timestamp')
            assert hasattr(result, 'tactical_recommendations')
            assert hasattr(result, 'executive_summary')

class TestCompetitiveIntelligenceAgent:
    """Test main agent orchestration"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def agent(self, temp_dir):
        """Create agent instance for testing"""
        config = get_config()
        config.OUTPUT_DIR = str(temp_dir)
        return CompetitiveIntelligenceAgent(config)
    
    def test_agent_initialization(self, agent):
        """Test agent initializes correctly"""
        assert agent.version is not None
        assert agent.brand_name is not None
        assert agent.competitor_analyzer is not None
        assert agent.market_tracker is not None
        assert agent.insights_generator is not None
    
    @pytest.mark.asyncio
    async def test_configuration_validation(self, agent):
        """Test configuration and integration validation"""
        # This should not raise an exception
        await agent._validate_configuration_and_integration()
    
    @pytest.mark.asyncio
    async def test_report_creation(self, agent):
        """Test comprehensive report creation"""
        # Create mock analysis results
        mock_competitive_intel = Mock()
        mock_competitive_intel.analysis_timestamp = datetime.now().isoformat()
        mock_competitive_intel.competitors_analyzed = ["EltaMD", "Supergoop"]
        mock_competitive_intel.strategy_scores = []
        mock_competitive_intel.citation_patterns = []
        mock_competitive_intel.authority_analyses = []
        mock_competitive_intel.content_gap_opportunities = []
        mock_competitive_intel.strategic_insights = []
        mock_competitive_intel.competitive_positioning = {}
        
        mock_market_intel = Mock()
        mock_market_intel.analysis_timestamp = datetime.now().isoformat()
        mock_market_intel.query_matrix_size = 150
        mock_market_intel.baseline_queries = 50
        mock_market_intel.expanded_queries = 100
        mock_market_intel.competitor_dominance_analysis = []
        mock_market_intel.market_gap_opportunities = []
        mock_market_intel.ranking_changes = []
        mock_market_intel.seasonal_trends = {}
        mock_market_intel.query_expansion_impact = {}
        
        mock_strategic_insights = Mock()
        mock_strategic_insights.analysis_timestamp = datetime.now().isoformat()
        mock_strategic_insights.content_gap_analysis = []
        mock_strategic_insights.tactical_recommendations = []
        mock_strategic_insights.threat_analysis = []
        mock_strategic_insights.opportunity_map = []
        mock_strategic_insights.executive_summary = {
            'competitive_landscape_summary': 'Test summary',
            'brand_position_assessment': 'Test assessment',
            'expected_outcomes': 'Test outcomes'
        }
        mock_strategic_insights.competitive_positioning_strategy = {}
        mock_strategic_insights.investment_priorities = []
        
        report = await agent._create_comprehensive_report(
            mock_competitive_intel, mock_market_intel, mock_strategic_insights)
        
        assert 'agent_info' in report
        assert 'configuration' in report
        assert 'executive_summary' in report
        assert 'competitive_intelligence_analysis' in report
        assert 'cross_agent_integration' in report
        assert 'key_findings' in report
        assert 'actionable_recommendations' in report
        assert 'performance_metrics' in report
    
    @pytest.mark.asyncio 
    async def test_results_saving(self, agent, temp_dir):
        """Test results saving functionality"""
        # Create a minimal report for testing
        test_report = {
            'agent_info': {
                'agent_name': 'Competitive Intelligence Agent',
                'agent_version': '1.0.0',
                'brand_name': 'Test Brand',
                'analysis_timestamp': datetime.now().isoformat()
            },
            'configuration': {'competitors_analyzed': 3},
            'executive_summary': {
                'competitive_landscape': {'competitors_analyzed': 3},
                'strategic_position': {'competitive_landscape_summary': 'Test'}
            },
            'actionable_recommendations': {
                'critical_priority': [],
                'high_priority': [],
                'investment_roadmap': []
            },
            'competitive_intelligence_analysis': {
                'competitor_content_strategies': {
                    'strategy_scores': [],
                    'authority_analyses': [],
                    'citation_patterns': []
                },
                'market_position_intelligence': {
                    'baseline_queries': 50,
                    'query_matrix_size': 150,
                    'market_gap_opportunities': [],
                    'ranking_changes': [],
                    'seasonal_trends': {}
                },
                'strategic_insights_report': {
                    'tactical_recommendations': []
                }
            },
            'key_findings': {
                'content_strategy_leaders': [],
                'authority_signal_leaders': []
            }
        }
        
        await agent._save_results(test_report)
        
        # Check that files were created
        result_files = list(temp_dir.glob("competitive_intelligence_*/*.json"))
        assert len(result_files) > 0
        
        # Check that latest symlink was created
        latest_link = temp_dir / "latest"
        assert latest_link.exists()
        assert latest_link.is_symlink()

class TestIntegrationScenarios:
    """Test cross-agent integration scenarios"""
    
    @pytest.mark.asyncio
    async def test_agent1_integration_available(self):
        """Test behavior when Agent 1 results are available"""
        config = get_config()
        
        # Mock Agent 1 results
        mock_agent1_results = {
            'queries': ['mineral sunscreen', 'zinc oxide sunscreen'],
            'competitors': ['EltaMD', 'Supergoop', 'CeraVe']
        }
        
        with patch.object(config, 'load_agent1_results', return_value=mock_agent1_results):
            tracker = MarketPositionTracker(config)
            baseline_queries = tracker._extract_baseline_queries()
            
            assert len(baseline_queries) > 0
            assert 'mineral sunscreen' in baseline_queries
    
    @pytest.mark.asyncio
    async def test_agent2_integration_available(self):
        """Test behavior when Agent 2 results are available"""
        config = get_config()
        
        # Mock Agent 2 results
        mock_agent2_results = {
            'content_analysis': {
                'overall_content_score': 65,
                'ingredient_coverage': 70,
                'clinical_references': 40
            },
            'competitive_gap_analysis': {
                'content_gaps': [
                    {
                        'gap_type': 'format_gap',
                        'related_queries': ['how to apply sunscreen'],
                        'opportunity_score': 75
                    }
                ]
            }
        }
        
        with patch.object(config, 'load_agent2_results', return_value=mock_agent2_results):
            generator = StrategicInsightsGenerator(config)
            brand_analysis = generator._extract_brand_content_analysis()
            
            assert brand_analysis is not None
            assert 'overall_content_score' in brand_analysis
    
    @pytest.mark.asyncio
    async def test_no_agent_integration_fallback(self):
        """Test fallback behavior when no agent results available"""
        config = get_config()
        
        with patch.object(config, 'load_agent1_results', return_value=None):
            with patch.object(config, 'load_agent2_results', return_value=None):
                tracker = MarketPositionTracker(config)
                baseline_queries = tracker._extract_baseline_queries()
                
                # Should still work with fallback queries
                assert len(baseline_queries) > 0

# Test data generators
def create_mock_competitor_data():
    """Create mock competitor data for testing"""
    return {
        'content_types_found': {
            'product_page': 10,
            'ingredient_guide': 5,
            'faq_page': 3,
            'clinical_study_page': 2
        },
        'unique_features': [
            'Expert endorsements',
            'Clinical studies', 
            'Video content',
            'Ingredient transparency'
        ],
        'authority_metrics': {
            'avg_authority_score': 75.0,
            'pages_with_author_info': 8
        },
        'keyword_coverage_top10': {
            'mineral sunscreen': 15,
            'zinc oxide': 12,
            'dermatologist': 8,
            'reef safe': 6
        }
    }

def create_mock_competitive_intelligence():
    """Create mock competitive intelligence for testing"""
    return {
        'analysis_timestamp': datetime.now().isoformat(),
        'competitors_analyzed': ['EltaMD', 'Supergoop', 'CeraVe'],
        'strategy_scores': [
            {
                'competitor': 'EltaMD',
                'overall_strategy_score': 85.2,
                'content_depth_score': 82.0,
                'authority_signal_score': 90.0,
                'ai_optimization_score': 78.0,
                'strategy_strengths': ['Clinical studies', 'Expert endorsements'],
                'strategy_weaknesses': ['Limited FAQ content']
            }
        ],
        'strategic_insights': [
            'EltaMD leads in authority signals with clinical backing',
            'Market gap opportunity in application guides'
        ]
    }

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])