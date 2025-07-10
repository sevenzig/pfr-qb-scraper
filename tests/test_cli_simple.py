#!/usr/bin/env python3
"""
Simple test script for CLI architecture
Tests basic functionality without complex dependencies
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """Test basic imports work"""
    print("Testing basic imports...")
    
    try:
        from cli.base_command import BaseCommand
        print("✓ BaseCommand imported successfully")
    except Exception as e:
        print(f"✗ Failed to import BaseCommand: {e}")
        return False
    
    try:
        from cli.commands import ScrapeCommand, ValidateCommand
        print("✓ Command classes imported successfully")
    except Exception as e:
        print(f"✗ Failed to import command classes: {e}")
        return False
    
    return True

def test_cli_manager():
    """Test CLI manager creation"""
    print("\nTesting CLI manager...")
    
    try:
        from cli.cli_main import CLIManager
        cli = CLIManager()
        print("✓ CLI manager created successfully")
        
        # Test command registration
        commands = cli.get_available_commands()
        expected = {'scrape', 'validate', 'monitor', 'health', 'cleanup'}
        if set(commands) == expected:
            print("✓ All commands registered correctly")
        else:
            print(f"✗ Command registration mismatch. Expected: {expected}, Got: {set(commands)}")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Failed to create CLI manager: {e}")
        return False

def test_command_creation():
    """Test individual command creation"""
    print("\nTesting command creation...")
    
    try:
        from cli.commands import ScrapeCommand, ValidateCommand, MonitorCommand, HealthCommand, CleanupCommand
        
        commands = [
            ScrapeCommand(),
            ValidateCommand(),
            MonitorCommand(),
            HealthCommand(),
            CleanupCommand()
        ]
        
        for cmd in commands:
            print(f"✓ Created {cmd.name} command")
        
        return True
    except Exception as e:
        print(f"✗ Failed to create commands: {e}")
        return False

def test_help_system():
    """Test help system"""
    print("\nTesting help system...")
    
    try:
        from cli.cli_main import CLIManager
        cli = CLIManager()
        
        # Test that help doesn't crash
        result = cli.run(['--help'])
        if result == 0:
            print("✓ Help system works")
            return True
        else:
            print(f"✗ Help system failed with exit code {result}")
            return False
    except Exception as e:
        print(f"✗ Help system crashed: {e}")
        return False

def main():
    """Run all tests"""
    print("=== CLI Architecture Phase 1 Test ===")
    
    tests = [
        test_basic_imports,
        test_cli_manager,
        test_command_creation,
        test_help_system
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("✓ All tests passed! CLI architecture is working correctly.")
        return 0
    else:
        print("✗ Some tests failed. CLI architecture needs fixes.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 