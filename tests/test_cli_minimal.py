#!/usr/bin/env python3
"""
Minimal test for CLI architecture
Tests only the structure without external dependencies
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_base_command():
    """Test BaseCommand abstract class"""
    print("Testing BaseCommand...")
    
    try:
        from cli.base_command import BaseCommand
        print("✓ BaseCommand imported")
        
        # Test that it's abstract
        import abc
        if abc.ABCMeta in BaseCommand.__bases__:
            print("✓ BaseCommand is abstract")
        else:
            print("✗ BaseCommand should be abstract")
            return False
        
        return True
    except Exception as e:
        print(f"✗ BaseCommand test failed: {e}")
        return False

def test_command_structure():
    """Test command class structure"""
    print("\nTesting command structure...")
    
    try:
        from cli.commands import ScrapeCommand, ValidateCommand
        
        # Test that commands inherit from BaseCommand
        from cli.base_command import BaseCommand
        
        if issubclass(ScrapeCommand, BaseCommand):
            print("✓ ScrapeCommand inherits from BaseCommand")
        else:
            print("✗ ScrapeCommand should inherit from BaseCommand")
            return False
        
        if issubclass(ValidateCommand, BaseCommand):
            print("✓ ValidateCommand inherits from BaseCommand")
        else:
            print("✗ ValidateCommand should inherit from BaseCommand")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Command structure test failed: {e}")
        return False

def test_command_properties():
    """Test command properties"""
    print("\nTesting command properties...")
    
    try:
        from cli.commands import ScrapeCommand, ValidateCommand
        
        scrape = ScrapeCommand()
        validate = ValidateCommand()
        
        # Test required properties exist
        required_props = ['name', 'description']
        for cmd, cmd_name in [(scrape, 'ScrapeCommand'), (validate, 'ValidateCommand')]:
            for prop in required_props:
                if hasattr(cmd, prop):
                    value = getattr(cmd, prop)
                    print(f"✓ {cmd_name}.{prop} = '{value}'")
                else:
                    print(f"✗ {cmd_name} missing {prop} property")
                    return False
        
        return True
    except Exception as e:
        print(f"✗ Command properties test failed: {e}")
        return False

def test_cli_manager_structure():
    """Test CLI manager structure"""
    print("\nTesting CLI manager structure...")
    
    try:
        from cli.cli_main import CLIManager
        
        # Test that CLIManager can be created
        cli = CLIManager()
        print("✓ CLIManager created")
        
        # Test that it has expected methods
        expected_methods = ['get_command', 'get_available_commands', 'create_parser']
        for method in expected_methods:
            if hasattr(cli, method):
                print(f"✓ CLIManager has {method} method")
            else:
                print(f"✗ CLIManager missing {method} method")
                return False
        
        return True
    except Exception as e:
        print(f"✗ CLI manager structure test failed: {e}")
        return False

def main():
    """Run minimal tests"""
    print("=== CLI Architecture Minimal Test ===")
    
    tests = [
        test_base_command,
        test_command_structure,
        test_command_properties,
        test_cli_manager_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"=== Test Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("✓ All minimal tests passed! CLI architecture structure is correct.")
        return 0
    else:
        print("✗ Some minimal tests failed. CLI architecture needs fixes.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 