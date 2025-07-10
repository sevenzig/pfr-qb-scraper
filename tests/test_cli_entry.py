#!/usr/bin/env python3
"""
Simple CLI entry point for testing
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Test CLI functionality"""
    try:
        print("Testing CLI imports...")
        
        # Test basic imports
        from cli.base_command import BaseCommand
        print("✓ BaseCommand imported")
        
        from cli.commands import ScrapeCommand, ValidateCommand
        print("✓ Command classes imported")
        
        from cli.cli_main import CLIManager
        print("✓ CLIManager imported")
        
        # Test CLI manager creation
        cli = CLIManager()
        print("✓ CLI manager created")
        
        # Test command registration
        commands = cli.get_available_commands()
        print(f"✓ Available commands: {commands}")
        
        # Test help
        print("\nTesting help system...")
        result = cli.run(['--help'])
        print(f"✓ Help system returned: {result}")
        
        print("\n=== CLI Architecture Test PASSED ===")
        return 0
        
    except Exception as e:
        print(f"\n✗ CLI test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 