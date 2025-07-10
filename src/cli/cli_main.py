#!/usr/bin/env python3
"""
Main CLI entry point for NFL QB Data Scraping System
Handles command registration, routing, and execution
"""

import sys
import os
import argparse
import logging
from typing import Dict, List, Type

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Handle relative imports when running as module
try:
    from .base_command import BaseCommand
except ImportError:
    # Fallback for direct execution
    from base_command import BaseCommand
try:
    from .commands import (
        ScrapeCommand,
        ValidateCommand,
        MonitorCommand,
        HealthCommand,
        CleanupCommand,
        DataCommand,
        BatchCommand
    )
    from .quality_commands import QualityValidateCommand
    from .legacy_commands import LegacyCommand, MigrateCommand
except ImportError:
    # Fallback for direct execution
    from commands import (
        ScrapeCommand,
        ValidateCommand,
        MonitorCommand,
        HealthCommand,
        CleanupCommand,
        DataCommand,
        BatchCommand
    )
    from quality_commands import QualityValidateCommand
    from legacy_commands import LegacyCommand, MigrateCommand
# Use try/except for optional imports
try:
    from config.config import config
except ImportError:
    try:
        from src.config.config import config
    except ImportError:
        # Fallback for testing
        config = None

logger = logging.getLogger(__name__)


class CLIManager:
    """Main CLI manager for command registration and execution"""
    
    def __init__(self):
        self.commands: Dict[str, BaseCommand] = {}
        self.aliases: Dict[str, str] = {}
        self._register_commands()
    
    def _register_commands(self) -> None:
        """Register all available commands"""
        command_classes = [
            ScrapeCommand,
            ValidateCommand,
            MonitorCommand,
            HealthCommand,
            CleanupCommand,
            DataCommand,
            BatchCommand,
            QualityValidateCommand,
            LegacyCommand,
            MigrateCommand
        ]
        
        for command_class in command_classes:
            command = command_class()
            self.commands[command.name] = command
            
            # Register aliases
            for alias in command.aliases:
                self.aliases[alias] = command.name
    
    def get_command(self, name: str) -> BaseCommand:
        """Get command by name or alias"""
        # Check if it's an alias first
        if name in self.aliases:
            name = self.aliases[name]
        
        return self.commands.get(name)
    
    def get_available_commands(self) -> List[str]:
        """Get list of available command names"""
        return list(self.commands.keys())
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create main argument parser with all commands"""
        parser = argparse.ArgumentParser(
            prog='nfl-qb-scraper',
            description='NFL QB Data Scraping System CLI',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog=self._get_examples_text()
        )
        
        # Global options
        parser.add_argument(
            '--verbose', '-v',
            action='store_true',
            help='Enable verbose logging'
        )
        parser.add_argument(
            '--version',
            action='version',
            version='%(prog)s 1.0.0'
        )
        
        # Create subparsers for commands
        subparsers = parser.add_subparsers(
            dest='command',
            help='Available commands',
            metavar='COMMAND'
        )
        
        # Add each command as a subparser
        for command_name, command in self.commands.items():
            # Create subparser for this command
            command_parser = subparsers.add_parser(
                command_name,
                help=command.description,
                description=command.description,
                aliases=command.aliases
            )
            
            # Let the command add its arguments
            try:
                command.add_arguments(command_parser)
            except Exception as e:
                # Handle case where config is not available
                if config is None:
                    # Add basic arguments without config-dependent defaults
                    command_parser.add_argument('--help', action='help', help='Show this help message')
                else:
                    raise e
        
        return parser
    
    def _get_examples_text(self) -> str:
        """Get examples text for help"""
        return """
Examples:
  # Scrape 2024 season data
  nfl-qb-scraper scrape --season 2024
  
  # Scrape only splits for specific players
  nfl-qb-scraper scrape --splits-only --players "Patrick Mahomes" "Josh Allen"
  
  # Validate data integrity
  nfl-qb-scraper validate
  
  # Monitor system health
  nfl-qb-scraper health
  
  # Show recent activity
  nfl-qb-scraper monitor --recent --hours 24
  
  # Clean up old data
  nfl-qb-scraper cleanup --days 30
  
  # Use aliases for common commands
  nfl-qb-scraper s --season 2024  # same as 'scrape'
  nfl-qb-scraper v                # same as 'validate'
  nfl-qb-scraper h                # same as 'health'
        """
    
    def setup_logging(self, verbose: bool = False) -> None:
        """Setup global logging configuration"""
        level = logging.DEBUG if verbose else logging.INFO
        
        # Create logs directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Configure root logger
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/cli.log'),
                logging.StreamHandler()
            ]
        )
        
        # Set levels for specific loggers
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('requests').setLevel(logging.WARNING)
    
    def run(self, args: List[str] = None) -> int:
        """
        Main CLI entry point
        
        Args:
            args: Command line arguments (defaults to sys.argv[1:])
            
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            # Create parser and parse arguments
            parser = self.create_parser()
            parsed_args = parser.parse_args(args)
            
            # Setup logging
            self.setup_logging(parsed_args.verbose)
            
            # Show help if no command provided
            if not parsed_args.command:
                parser.print_help()
                return 0
            
            # Get the command
            command = self.get_command(parsed_args.command)
            if not command:
                print(f"Error: Unknown command '{parsed_args.command}'")
                print(f"Available commands: {', '.join(self.get_available_commands())}")
                return 1
            
            # Setup command logging
            command.setup_logging(parsed_args.verbose)
            
            # Validate arguments
            validation_errors = command.validate_args(parsed_args)
            if validation_errors:
                for error in validation_errors:
                    print(f"Error: {error}")
                return 1
            
            # Execute command
            logger.info(f"Executing command: {parsed_args.command}")
            exit_code = command.run(parsed_args)
            
            # Cleanup
            command.cleanup()
            
            return exit_code
            
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return 130  # Standard exit code for SIGINT
        except Exception as e:
            logger.error(f"CLI execution failed: {e}")
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug("Stack trace:", exc_info=True)
            return 1
    
    def show_command_help(self, command_name: str) -> None:
        """Show help for a specific command"""
        command = self.get_command(command_name)
        if command:
            parser = self.create_parser()
            # This will show the help for the specific command
            parser.parse_args([command_name, '--help'])
        else:
            print(f"Unknown command: {command_name}")
            print(f"Available commands: {', '.join(self.get_available_commands())}")


def main() -> int:
    """Main entry point for CLI"""
    cli = CLIManager()
    return cli.run()


if __name__ == "__main__":
    sys.exit(main()) 