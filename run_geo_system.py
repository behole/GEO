#!/usr/bin/env python3
"""
GEO Optimization System - Umbrella Command
Main entry point for running the complete GEO optimization system

Usage:
    python run_geo_system.py --mode [full|discovery|content|competitive|monitoring]
    python run_geo_system.py --continuous --interval 6
    python run_geo_system.py --status
"""

import asyncio
import argparse
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
import atexit

from dynamic_config import get_config_manager, cleanup_dynamic_configs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Ensure cleanup on exit
atexit.register(cleanup_dynamic_configs)

async def run_agent_1(config_path: Optional[str] = None):
    """Run Agent 1 - Discovery Baseline Agent"""
    try:
        from discovery_baseline_agent.main import run_discovery_baseline
        logger.info("🔍 Running Agent 1 - Discovery Baseline Agent")
        result = await run_discovery_baseline()
        logger.info("✅ Agent 1 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Agent 1 failed: {str(e)}")
        return None

async def run_agent_2(config_path: Optional[str] = None):
    """Run Agent 2 - Content Analysis Agent"""
    try:
        from content_analysis_agent.main import run_content_analysis
        logger.info("📝 Running Agent 2 - Content Analysis Agent")
        result = await run_content_analysis(config_path)
        logger.info("✅ Agent 2 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Agent 2 failed: {str(e)}")
        return None

async def run_agent_3(config_path: Optional[str] = None):
    """Run Agent 3 - Competitive Intelligence Agent"""
    try:
        from competitive_intelligence_agent.competitive_intelligence_agent import run_competitive_intelligence
        logger.info("🏆 Running Agent 3 - Competitive Intelligence Agent")
        result = await run_competitive_intelligence()
        logger.info("✅ Agent 3 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Agent 3 failed: {str(e)}")
        return None

async def run_agent_4(monitoring_type="full", test_mode=False):
    """Run Agent 4 - Monitoring & Alerting Agent"""
    try:
        from monitoring_alerting_agent.monitoring_alerting_agent import run_monitoring_agent
        logger.info("📊 Running Agent 4 - Monitoring & Alerting Agent")
        result = await run_monitoring_agent(monitoring_type, test_mode=test_mode)
        logger.info("✅ Agent 4 completed successfully")
        return result
    except Exception as e:
        logger.error(f"❌ Agent 4 failed: {str(e)}")
        # If it fails due to missing agent results, run in test mode
        if "No agent results available" in str(e):
            logger.info("🔄 Retrying Agent 4 in test mode (no prior agent results)")
            try:
                result = await run_monitoring_agent(monitoring_type, test_mode=True)
                logger.info("✅ Agent 4 completed successfully in test mode")
                return result
            except Exception as e2:
                logger.error(f"❌ Agent 4 failed even in test mode: {str(e2)}")
        return None

async def run_full_system(config_path: Optional[str] = None):
    """Run the complete GEO optimization system (all agents in sequence)"""
    logger.info("🚀 Starting Complete GEO Optimization System")
    if config_path:
        logger.info(f"📋 Using dynamic configuration: {config_path}")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    results = {}
    
    # Run agents in sequence
    results['agent_1'] = await run_agent_1(config_path)
    results['agent_2'] = await run_agent_2(config_path)
    results['agent_3'] = await run_agent_3(config_path)
    results['agent_4'] = await run_agent_4()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Summary
    logger.info("=" * 60)
    logger.info("🎯 GEO System Execution Summary")
    logger.info(f"⏱️ Total Duration: {duration}")
    
    successful_agents = [name for name, result in results.items() if result is not None]
    failed_agents = [name for name, result in results.items() if result is None]
    
    logger.info(f"✅ Successful Agents: {len(successful_agents)}/4")
    logger.info(f"❌ Failed Agents: {len(failed_agents)}/4")
    
    if successful_agents:
        logger.info(f"✅ Completed: {', '.join(successful_agents)}")
    if failed_agents:
        logger.info(f"❌ Failed: {', '.join(failed_agents)}")
    
    return results

async def start_continuous_monitoring(interval_hours=6):
    """Start continuous monitoring system"""
    try:
        from monitoring_alerting_agent.monitoring_alerting_agent import start_continuous_monitoring
        logger.info(f"🔄 Starting continuous monitoring (every {interval_hours} hours)")
        result = await start_continuous_monitoring(interval_hours)
        logger.info("✅ Continuous monitoring started successfully")
        logger.info(f"📅 Next run: {result.get('next_run', 'Unknown')}")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to start continuous monitoring: {str(e)}")
        return None

def get_system_status():
    """Get current system status"""
    try:
        from monitoring_alerting_agent.monitoring_alerting_agent import get_monitoring_status
        logger.info("📊 Checking GEO System Status")
        status = get_monitoring_status()
        
        logger.info("=" * 40)
        logger.info("🎯 GEO System Status")
        logger.info("=" * 40)
        logger.info(f"Monitoring Active: {status['monitoring_active']}")
        logger.info(f"System Health: {status['system_health']}")
        logger.info(f"Last Run: {status.get('last_run', 'Never')}")
        logger.info(f"Next Run: {status.get('next_scheduled_run', 'Not scheduled')}")
        
        config = status.get('configuration', {})
        logger.info(f"Interval: {config.get('interval_hours', 'Unknown')} hours")
        logger.info(f"Real-time: {config.get('real_time_enabled', False)}")
        logger.info(f"Alert Sensitivity: {config.get('alert_sensitivity', 'Unknown')}")
        
        integration = status.get('integration_status', {})
        logger.info(f"Agents Tracked: {integration.get('total_agents', 0)}")
        logger.info(f"Healthy Integrations: {integration.get('healthy_integrations', 0)}")
        
        return status
    except Exception as e:
        logger.error(f"❌ Failed to get system status: {str(e)}")
        return None

def stop_monitoring():
    """Stop continuous monitoring"""
    try:
        from monitoring_alerting_agent.monitoring_alerting_agent import stop_continuous_monitoring
        logger.info("🛑 Stopping continuous monitoring")
        result = stop_continuous_monitoring()
        logger.info("✅ Continuous monitoring stopped")
        return result
    except Exception as e:
        logger.error(f"❌ Failed to stop monitoring: {str(e)}")
        return None

async def main():
    """Main entry point"""
    config_manager = get_config_manager()
    available_sectors = config_manager.list_available_sectors()
    
    parser = argparse.ArgumentParser(
        description="GEO Optimization System - Complete Analysis Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Examples:
  # Run full analysis for default brand (Brush on Block)
  python run_geo_system.py --mode full
  
  # Run analysis for Nike with generic sector
  python run_geo_system.py --mode full --brand "Nike" --website "https://nike.com"
  
  # Run analysis with specific sector
  python run_geo_system.py --mode full --brand "Nike" --website "https://nike.com" --sector "fitness_supplements"
  
  # Run single agent with custom brand
  python run_geo_system.py --mode content --brand "Nike" --website "https://nike.com"
  
  # Include competitors
  python run_geo_system.py --mode full --brand "Nike" --website "https://nike.com" \\
    --competitors "https://adidas.com" "https://underarmour.com" "https://puma.com"
  
  # Other operations
  python run_geo_system.py --continuous --interval 6 # Start continuous monitoring
  python run_geo_system.py --status                 # Check system status
  python run_geo_system.py --stop                   # Stop continuous monitoring

Available sectors: {', '.join(available_sectors)}
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['full', 'discovery', 'content', 'competitive', 'monitoring'],
        default='full',
        help='Execution mode (default: full)'
    )
    
    parser.add_argument(
        '--continuous',
        action='store_true',
        help='Start continuous monitoring instead of one-time execution'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=6,
        help='Monitoring interval in hours (default: 6)'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current system status'
    )
    
    parser.add_argument(
        '--stop',
        action='store_true',
        help='Stop continuous monitoring'
    )
    
    # Brand configuration arguments
    parser.add_argument(
        '--brand',
        type=str,
        help='Brand name to analyze (e.g., "Nike", "Apple", "Tesla")'
    )
    
    parser.add_argument(
        '--website',
        type=str,
        help='Brand website URL (e.g., "https://nike.com", "apple.com")'
    )
    
    parser.add_argument(
        '--sector',
        choices=available_sectors,
        default='generic',
        help=f'Industry sector template to use (default: generic). Available: {", ".join(available_sectors)}'
    )
    
    parser.add_argument(
        '--competitors',
        nargs='*',
        help='List of competitor websites (e.g., "adidas.com" "puma.com")'
    )
    
    parser.add_argument(
        '--list-sectors',
        action='store_true',
        help='List all available sector configurations and exit'
    )
    
    args = parser.parse_args()
    
    # Handle list sectors
    if args.list_sectors:
        logger.info("📋 Available Sector Configurations:")
        for sector in available_sectors:
            logger.info(f"  - {sector}")
        return
    
    # Handle status check
    if args.status:
        get_system_status()
        return
    
    # Handle stop monitoring
    if args.stop:
        stop_monitoring()
        return
    
    # Create dynamic configuration if brand/website specified
    config_path = None
    if args.brand and args.website:
        logger.info(f"🔧 Creating dynamic configuration for {args.brand}")
        
        # Validate brand configuration
        validation = config_manager.validate_brand_config(args.brand, args.website)
        if not validation["valid"]:
            logger.error("❌ Brand configuration validation failed:")
            for issue in validation["issues"]:
                logger.error(f"  - {issue}")
            return
        
        # Create dynamic configuration
        config_path = config_manager.create_brand_config(
            args.brand,
            validation["normalized_website"],
            args.sector,
            args.competitors
        )
        
        logger.info(f"✅ Dynamic configuration created")
        logger.info(f"📋 Brand: {args.brand}")
        logger.info(f"🌐 Website: {validation['normalized_website']}")
        logger.info(f"🏢 Sector: {args.sector}")
        if args.competitors:
            logger.info(f"🏆 Competitors: {len(args.competitors)} specified")
    
    elif args.brand or args.website:
        logger.error("❌ Both --brand and --website must be specified together")
        return
    
    # Handle continuous monitoring
    if args.continuous:
        await start_continuous_monitoring(args.interval)
        logger.info("💡 Monitoring is now running in the background")
        logger.info("💡 Use --status to check status or --stop to stop monitoring")
        return
    
    # Handle individual agent execution
    if args.mode == 'discovery':
        await run_agent_1(config_path)
    elif args.mode == 'content':
        await run_agent_2(config_path)
    elif args.mode == 'competitive':
        await run_agent_3(config_path)
    elif args.mode == 'monitoring':
        await run_agent_4()
    elif args.mode == 'full':
        await run_full_system(config_path)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Unexpected error: {str(e)}")
        sys.exit(1)