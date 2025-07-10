#!/usr/bin/env python3
"""
Simple CLI Runner for NFL QB Scraper
Alternative entry point for running scraper commands
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the CLI manager
from cli.cli_main import CLIManager

def main():
    """Simple CLI runner"""
    cli = CLIManager()
    return cli.run()

if __name__ == "__main__":
    sys.exit(main()) 