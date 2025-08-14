#!/usr/bin/env python3
"""
Terminal Dashboard Generator - Main Entry Point
Creates impressive executive presentations from GEO audit data
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional
import argparse

# Add the parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from terminal_dashboard_generator.data_aggregator import GEODataAggregator
from terminal_dashboard_generator.terminal_dashboard import TerminalDashboard
from terminal_dashboard_generator.export_manager import DashboardExportManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TerminalDashboardGenerator:
    """Main terminal dashboard generator for impressive executive presentations"""
    
    def __init__(self, base_dir: str = "/Users/jjoosshhmbpm1/GEO OPT"):
        self.base_dir = Path(base_dir)
        self.brand_name = "Brush on Block"
        
        logger.info(f"Terminal Dashboard Generator initialized for {self.brand_name}")
        
        # Initialize components
        self.data_aggregator = GEODataAggregator(str(self.base_dir))
        self.dashboard = None
        self.export_manager = None
    
    def generate_dashboard(self, export_formats: Optional[list] = None) -> dict:
        """Generate the complete terminal dashboard with optional exports"""
        logger.info("Starting terminal dashboard generation...")
        
        try:
            # 1. Aggregate data from all 4 agents
            logger.info("Aggregating data from all GEO agents...")
            aggregated_data = self.data_aggregator.aggregate_all_data()
            
            # 2. Create terminal dashboard
            logger.info("Creating terminal dashboard visualization...")
            self.dashboard = TerminalDashboard(aggregated_data)
            
            # 3. Generate live terminal dashboard
            dashboard_output = self.dashboard.generate_complete_dashboard()
            
            results = {
                'terminal_output': dashboard_output,
                'dashboard_metrics': self.dashboard.get_dashboard_metrics(),
                'brand_name': self.brand_name
            }
            
            # 4. Export to additional formats if requested
            if export_formats:
                logger.info(f"Exporting to formats: {export_formats}")
                self.export_manager = DashboardExportManager(self.dashboard)
                
                if 'all' in export_formats:
                    export_results = self.export_manager.export_all_formats()
                    results['exports'] = export_results
                    results['export_directory'] = str(self.export_manager.export_dir)
                else:
                    exports = {}
                    for fmt in export_formats:
                        if fmt == 'html':
                            exports['html'] = self.export_manager.export_html()
                        elif fmt == 'pdf':
                            exports['pdf'] = self.export_manager.export_pdf()
                        elif fmt == 'json':
                            exports['json'] = self.export_manager.export_json_data()
                        elif fmt == 'executive_summary':
                            exports['executive_summary'] = self.export_manager.export_executive_summary()
                    
                    results['exports'] = exports
                    results['export_directory'] = str(self.export_manager.export_dir)
            
            logger.info("Terminal dashboard generation completed successfully!")
            return results
            
        except Exception as e:
            logger.error(f"Error generating dashboard: {str(e)}")
            raise
    
    def display_live_dashboard(self):
        """Display the dashboard to terminal in real-time"""
        try:
            results = self.generate_dashboard()
            
            # Clear terminal
            os.system('clear' if os.name == 'posix' else 'cls')
            
            # Display the dashboard
            print(results['terminal_output'])
            
            # Show generation info
            print(f"\n🎯 Dashboard generated for {self.brand_name}")
            print(f"📊 Overall GEO Score: {results['dashboard_metrics']['overall_score']:.1f}/100")
            print(f"💰 Expected ROI: {results['dashboard_metrics']['expected_roi']}%")
            print(f"🚀 Investment Required: ${results['dashboard_metrics']['investment_required']:,}")
            
        except Exception as e:
            logger.error(f"Error displaying dashboard: {str(e)}")
            print(f"❌ Error: {str(e)}")
    
    def create_executive_presentation(self, output_dir: Optional[str] = None):
        """Create complete executive presentation package"""
        logger.info("Creating executive presentation package...")
        
        try:
            # Generate dashboard with all export formats
            results = self.generate_dashboard(export_formats=['all'])
            
            export_dir = results['export_directory']
            
            print(f"\n🎯 EXECUTIVE PRESENTATION GENERATED")
            print(f"📁 Location: {export_dir}")
            print(f"\n📋 Generated Files:")
            
            for format_name, file_path in results['exports'].items():
                if format_name != 'manifest' and isinstance(file_path, str):
                    filename = Path(file_path).name
                    print(f"  • {format_name.replace('_', ' ').title()}: {filename}")
            
            print(f"\n💼 Ready for partner presentation!")
            print(f"🔗 Open {export_dir}/geo_dashboard.html to view in browser")
            
            return results
            
        except Exception as e:
            logger.error(f"Error creating executive presentation: {str(e)}")
            raise

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description="Terminal Dashboard Generator for GEO Audit Results")
    parser.add_argument(
        '--mode', 
        choices=['display', 'export', 'presentation'], 
        default='display',
        help='Dashboard mode: display (live terminal), export (files), presentation (complete package)'
    )
    parser.add_argument(
        '--formats', 
        nargs='+', 
        choices=['html', 'pdf', 'json', 'executive_summary', 'all'],
        default=['html'],
        help='Export formats (for export mode)'
    )
    parser.add_argument(
        '--base-dir',
        default="/Users/jjoosshhmbpm1/GEO OPT",
        help='Base directory for GEO data'
    )
    
    args = parser.parse_args()
    
    # Initialize generator
    generator = TerminalDashboardGenerator(args.base_dir)
    
    try:
        if args.mode == 'display':
            generator.display_live_dashboard()
        
        elif args.mode == 'export':
            results = generator.generate_dashboard(export_formats=args.formats)
            if 'exports' in results:
                print(f"\n✅ Dashboard exported to: {results['export_directory']}")
                for fmt, path in results['exports'].items():
                    if isinstance(path, str):
                        print(f"  • {fmt}: {Path(path).name}")
        
        elif args.mode == 'presentation':
            generator.create_executive_presentation()
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()