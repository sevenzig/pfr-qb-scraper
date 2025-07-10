"""
Command-line interface for NFL QB Data Scraping System
"""

# Avoid automatic imports to prevent circular dependencies during testing
# Import functions can be done explicitly when needed

__all__ = ['main', 'CLIManager']

def main():
    """Main entry point for legacy CLI"""
    from .scraper_cli import main as scraper_main
    return scraper_main()

def get_cli_manager():
    """Get CLI manager instance"""
    from .cli_main import CLIManager
    return CLIManager() 