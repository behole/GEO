#!/usr/bin/env python3
"""
Dynamic Configuration Manager for GEO System
Handles brand and sector overrides from command line arguments
"""

import os
import yaml
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

class DynamicConfigManager:
    """Manages dynamic brand and sector configuration"""
    
    def __init__(self):
        self.base_config_dir = Path(__file__).parent / "sector_configs"
        self.temp_configs = []
    
    def create_brand_config(
        self,
        brand_name: str,
        website: str,
        sector: str = "generic",
        competitors: Optional[List[str]] = None
    ) -> str:
        """
        Create a temporary configuration file for a specific brand
        
        Args:
            brand_name: Name of the brand to analyze
            website: Brand website URL
            sector: Sector template to use (default: generic)
            competitors: Optional list of competitor websites
            
        Returns:
            Path to the temporary config file
        """
        
        # Load base sector configuration
        sector_config_path = self.base_config_dir / f"{sector}.yaml"
        if not sector_config_path.exists():
            logger.warning(f"Sector config {sector}.yaml not found, using generic.yaml")
            sector_config_path = self.base_config_dir / "generic.yaml"
        
        # Load the base configuration
        with open(sector_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Override brand information
        config["brand"] = {
            "name": brand_name,
            "website": website,
            "variations": self._generate_brand_variations(brand_name)
        }
        
        # Override competitors if provided
        if competitors:
            config["competitors"] = self._create_competitor_config(competitors)
        
        # Update keywords to be more generic if using generic sector
        if sector == "generic":
            config["keywords"] = self._generate_generic_keywords(brand_name, website)
        
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.yaml', 
            delete=False, 
            encoding='utf-8'
        )
        
        yaml.dump(config, temp_file, default_flow_style=False, allow_unicode=True)
        temp_file.flush()
        
        # Store for cleanup
        self.temp_configs.append(temp_file.name)
        
        logger.info(f"Created dynamic config for {brand_name} at {temp_file.name}")
        return temp_file.name
    
    def _generate_brand_variations(self, brand_name: str) -> List[str]:
        """Generate common variations of the brand name"""
        variations = [
            brand_name,
            brand_name.lower(),
            brand_name.upper(),
            brand_name.replace(" ", ""),
            brand_name.replace(" ", "").lower()
        ]
        
        # Add variations with common suffixes/prefixes
        base_name = brand_name.lower()
        if " " in brand_name:
            # For multi-word brands, add acronym
            acronym = "".join(word[0].upper() for word in brand_name.split())
            variations.extend([acronym, acronym.lower()])
        
        # Remove duplicates and return
        return list(set(variations))
    
    def _create_competitor_config(self, competitor_urls: List[str]) -> Dict[str, Any]:
        """Create competitor configuration from URLs"""
        competitors = {"primary": [], "secondary": []}
        
        for i, url in enumerate(competitor_urls[:10]):  # Limit to 10 competitors
            domain = urlparse(url).netloc.replace("www.", "")
            name = domain.split(".")[0].title()
            
            priority = "high" if i < 3 else "medium" if i < 6 else "low"
            category = "primary" if i < 5 else "secondary"
            
            competitors[category].append({
                "name": name,
                "website": url if url.startswith("http") else f"https://{url}",
                "priority": priority
            })
        
        return competitors
    
    def _generate_generic_keywords(self, brand_name: str, website: str) -> Dict[str, List[str]]:
        """Generate generic keywords for any brand"""
        domain = urlparse(website).netloc.replace("www.", "")
        base_name = brand_name.lower()
        
        return {
            "primary": [
                base_name,
                f"{base_name} products",
                f"{base_name} services",
                domain,
                f"{base_name} reviews"
            ],
            "secondary": [
                f"{base_name} company",
                f"{base_name} official",
                f"{base_name} website",
                f"about {base_name}",
                f"{base_name} information"
            ],
            "long_tail": [
                f"what is {base_name}",
                f"best {base_name} products",
                f"{base_name} vs competitors",
                f"how to use {base_name}",
                f"{base_name} customer reviews"
            ]
        }
    
    def cleanup(self):
        """Clean up temporary configuration files"""
        for config_path in self.temp_configs:
            try:
                os.unlink(config_path)
                logger.debug(f"Cleaned up temporary config: {config_path}")
            except OSError:
                pass
        self.temp_configs.clear()
    
    def list_available_sectors(self) -> List[str]:
        """List available sector configurations"""
        sectors = []
        for config_file in self.base_config_dir.glob("*.yaml"):
            sectors.append(config_file.stem)
        return sorted(sectors)
    
    def validate_brand_config(self, brand_name: str, website: str) -> Dict[str, Any]:
        """Validate brand configuration parameters"""
        issues = []
        
        if not brand_name or not brand_name.strip():
            issues.append("Brand name cannot be empty")
        
        if not website or not website.strip():
            issues.append("Website URL cannot be empty")
        
        # Basic URL validation
        if website and not website.startswith(('http://', 'https://')):
            if not website.startswith('www.'):
                website = f"https://{website}"
            else:
                website = f"https://{website}"
        
        try:
            parsed = urlparse(website)
            if not parsed.netloc:
                issues.append("Invalid website URL format")
        except Exception as e:
            issues.append(f"URL parsing error: {str(e)}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "normalized_website": website,
            "brand_variations": self._generate_brand_variations(brand_name) if brand_name else []
        }

# Global instance
_config_manager = None

def get_config_manager() -> DynamicConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = DynamicConfigManager()
    return _config_manager

def create_dynamic_config(
    brand_name: str,
    website: str,
    sector: str = "generic",
    competitors: Optional[List[str]] = None
) -> str:
    """Convenience function to create dynamic configuration"""
    manager = get_config_manager()
    return manager.create_brand_config(brand_name, website, sector, competitors)

def cleanup_dynamic_configs():
    """Clean up all temporary configurations"""
    manager = get_config_manager()
    manager.cleanup()

if __name__ == "__main__":
    # Test the dynamic configuration system
    import argparse
    
    parser = argparse.ArgumentParser(description="Test Dynamic Configuration Manager")
    parser.add_argument("--brand", required=True, help="Brand name")
    parser.add_argument("--website", required=True, help="Brand website")
    parser.add_argument("--sector", default="generic", help="Sector template")
    parser.add_argument("--competitors", nargs="*", help="Competitor websites")
    
    args = parser.parse_args()
    
    manager = DynamicConfigManager()
    
    # Validate configuration
    validation = manager.validate_brand_config(args.brand, args.website)
    print("Validation Result:", validation)
    
    if validation["valid"]:
        # Create configuration
        config_path = manager.create_brand_config(
            args.brand,
            validation["normalized_website"],
            args.sector,
            args.competitors
        )
        
        print(f"Created configuration: {config_path}")
        
        # Show the configuration
        with open(config_path, 'r') as f:
            print("\nGenerated Configuration:")
            print(f.read())
        
        # Cleanup
        manager.cleanup()
    else:
        print("Configuration validation failed!")
        for issue in validation["issues"]:
            print(f"  - {issue}")