#!/usr/bin/env python3
"""
Tests for CLI architecture foundation
Tests the basic CLI structure and command registration
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch
from argparse import Namespace

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from cli.cli_main import CLIManager
from cli.base_command import BaseCommand
from cli.commands import ScrapeCommand, ValidateCommand, MonitorCommand, HealthCommand, CleanupCommand


class TestCLIArchitecture(unittest.TestCase):
    """Test CLI architecture foundation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cli_manager = CLIManager()
    
    def test_cli_manager_initialization(self):
        """Test that CLI manager initializes correctly"""
        # Should have registered all commands
        expected_commands = {
            'scrape', 'validate', 'monitor', 'health', 'cleanup',
            'batch', 'data', 'migrate', 'legacy', 'quality-validate'
        }
        self.assertEqual(set(self.cli_manager.commands.keys()), expected_commands)
        
        # Should have registered aliases
        expected_aliases = {
            's': 'scrape',
            'v': 'validate',
            'm': 'monitor',
            'h': 'health',
            'c': 'cleanup',
            'd': 'data',
            'b': 'batch'
        }
        self.assertEqual(self.cli_manager.aliases, expected_aliases)
    
    def test_get_command_by_name(self):
        """Test getting commands by name"""
        scrape_cmd = self.cli_manager.get_command('scrape')
        self.assertIsInstance(scrape_cmd, ScrapeCommand)
        
        validate_cmd = self.cli_manager.get_command('validate')
        self.assertIsInstance(validate_cmd, ValidateCommand)
    
    def test_get_command_by_alias(self):
        """Test getting commands by alias"""
        scrape_cmd = self.cli_manager.get_command('s')
        self.assertIsInstance(scrape_cmd, ScrapeCommand)
        
        validate_cmd = self.cli_manager.get_command('v')
        self.assertIsInstance(validate_cmd, ValidateCommand)
    
    def test_get_nonexistent_command(self):
        """Test getting non-existent command returns None"""
        result = self.cli_manager.get_command('nonexistent')
        self.assertIsNone(result)
    
    def test_get_available_commands(self):
        """Test getting list of available commands"""
        commands = self.cli_manager.get_available_commands()
        self.assertIn('scrape', commands)
        self.assertIn('validate', commands)
        self.assertIn('monitor', commands)
        self.assertIn('health', commands)
        self.assertIn('cleanup', commands)
    
    def test_create_parser(self):
        """Test creating argument parser"""
        parser = self.cli_manager.create_parser()
        self.assertIsNotNone(parser)
        
        # Test parser has global options
        # This is a basic test - full parsing would require more complex setup
        self.assertIsNotNone(parser)
    
    def test_help_functionality(self):
        """Test help functionality"""
        with patch('sys.stdout'), patch('sys.exit') as mock_exit:
            # Test that help doesn't raise an exception
            try:
                result = self.cli_manager.run(['--help'])
            except SystemExit:
                # Help exits with SystemExit, which is expected
                pass
            # Help should exit with code 0
            mock_exit.assert_called_with(0)


class TestBaseCommand(unittest.TestCase):
    """Test base command functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create a mock concrete command for testing
        class TestCommand(BaseCommand):
            @property
            def name(self):
                return "test"
            
            @property
            def description(self):
                return "Test command"
            
            def add_arguments(self, parser):
                parser.add_argument('--test-arg', help='Test argument')
            
            def run(self, args):
                return 0
        
        self.command = TestCommand()
    
    def test_command_properties(self):
        """Test command properties"""
        self.assertEqual(self.command.name, "test")
        self.assertEqual(self.command.description, "Test command")
        self.assertEqual(self.command.aliases, [])  # Default empty list
    
    def test_logging_setup(self):
        """Test logging setup"""
        # This should not raise an exception
        self.command.setup_logging(verbose=False)
        self.command.setup_logging(verbose=True)
    
    def test_error_handling(self):
        """Test error handling"""
        test_error = Exception("Test error")
        result = self.command.handle_error(test_error)
        self.assertEqual(result, 1)  # Should return non-zero exit code
        
        result = self.command.handle_error(test_error, "Custom message")
        self.assertEqual(result, 1)
    
    def test_validation_default(self):
        """Test default validation returns no errors"""
        args = Namespace()
        errors = self.command.validate_args(args)
        self.assertEqual(errors, [])
    
    def test_print_methods(self):
        """Test print methods don't raise exceptions"""
        with patch('builtins.print'):
            self.command.print_success("Test success")
            self.command.print_error("Test error")
            self.command.print_warning("Test warning")
            self.command.print_info("Test info")
            self.command.print_section_header("Test section")
    
    def test_cleanup(self):
        """Test cleanup method"""
        # Should not raise an exception
        self.command.cleanup()


class TestScrapeCommand(unittest.TestCase):
    """Test scrape command specifically"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.command = ScrapeCommand()
    
    def test_command_properties(self):
        """Test scrape command properties"""
        self.assertEqual(self.command.name, "scrape")
        self.assertIn("scrape", self.command.description.lower())
        self.assertIn("s", self.command.aliases)
    
    def test_argument_validation(self):
        """Test argument validation"""
        # Test valid arguments
        args = Namespace(season=2024, rate_limit=3.0, players=None)
        errors = self.command.validate_args(args)
        self.assertEqual(errors, [])
        
        # Test invalid season
        args = Namespace(season=1900, rate_limit=3.0, players=None)
        errors = self.command.validate_args(args)
        self.assertTrue(len(errors) > 0)
        
        # Test invalid rate limit
        args = Namespace(season=2024, rate_limit=100.0, players=None)
        errors = self.command.validate_args(args)
        self.assertTrue(len(errors) > 0)


class TestValidateCommand(unittest.TestCase):
    """Test validate command specifically"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.command = ValidateCommand()
    
    def test_command_properties(self):
        """Test validate command properties"""
        self.assertEqual(self.command.name, "validate")
        self.assertIn("validate", self.command.description.lower())
        self.assertIn("v", self.command.aliases)


class TestMonitorCommand(unittest.TestCase):
    """Test monitor command specifically"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.command = MonitorCommand()
    
    def test_command_properties(self):
        """Test monitor command properties"""
        self.assertEqual(self.command.name, "monitor")
        self.assertIn("monitor", self.command.description.lower())
        self.assertIn("m", self.command.aliases)
    
    def test_argument_validation(self):
        """Test argument validation"""
        # Test valid arguments
        args = Namespace(hours=24, limit=20)
        errors = self.command.validate_args(args)
        self.assertEqual(errors, [])
        
        # Test invalid hours
        args = Namespace(hours=1000, limit=20)
        errors = self.command.validate_args(args)
        self.assertTrue(len(errors) > 0)


class TestHealthCommand(unittest.TestCase):
    """Test health command specifically"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.command = HealthCommand()
    
    def test_command_properties(self):
        """Test health command properties"""
        self.assertEqual(self.command.name, "health")
        self.assertIn("health", self.command.description.lower())
        self.assertIn("h", self.command.aliases)
    
    def test_argument_validation(self):
        """Test argument validation"""
        # Test valid arguments
        args = Namespace(timeout=30)
        errors = self.command.validate_args(args)
        self.assertEqual(errors, [])
        
        # Test invalid timeout
        args = Namespace(timeout=1000)
        errors = self.command.validate_args(args)
        self.assertTrue(len(errors) > 0)


class TestCleanupCommand(unittest.TestCase):
    """Test cleanup command specifically"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.command = CleanupCommand()
    
    def test_command_properties(self):
        """Test cleanup command properties"""
        self.assertEqual(self.command.name, "cleanup")
        self.assertIn("clean up", self.command.description.lower())
        self.assertIn("c", self.command.aliases)
    
    def test_argument_validation(self):
        """Test argument validation"""
        # Test valid arguments
        args = Namespace(days=30)
        errors = self.command.validate_args(args)
        self.assertEqual(errors, [])
        
        # Test invalid days
        args = Namespace(days=1000)
        errors = self.command.validate_args(args)
        self.assertTrue(len(errors) > 0)


if __name__ == '__main__':
    unittest.main() 