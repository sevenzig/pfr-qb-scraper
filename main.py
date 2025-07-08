#!/usr/bin/env python3
"""
Main entry point for NFL QB Data Scraping System
Provides easy access to all functionality through command-line interface
"""

import sys
import os
import logging
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from cli.scraper_cli import main as cli_main

def setup_logging():
    """Setup basic logging configuration"""
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/main.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """Main entry point"""
    setup_logging()
    
    try:
        # Delegate to CLI main function
        cli_main()
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 