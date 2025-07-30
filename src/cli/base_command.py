#!/usr/bin/env python3
"""
Base Command for NFL QB Data Scraping CLI
Base class for all CLI commands with common functionality
"""

import logging
import argparse
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from argparse import ArgumentParser, Namespace

from src.config.config import config  # avoid collision with external "config" package
from src.database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


class BaseCommand(ABC):
    """Abstract base class for CLI commands"""
    
    def __init__(self):
        """Initialize base command"""
        self.db_manager: Optional[Any] = None
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Handle case where config is not available (e.g., during testing)
        if self.config is None:
            # Create a minimal config for testing
            class MockConfig:
                app = type('obj', (object,), {'target_season': 2024})()
                scraping = type('obj', (object,), {'rate_limit_delay': 3.0})()
            self.config = MockConfig()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Command name (used in CLI)"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Command description for help text"""
        pass
    
    @property
    def aliases(self) -> List[str]:
        """Command aliases (optional)"""
        return []
    
    @abstractmethod
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments to parser"""
        pass
    
    @abstractmethod
    def run(self, args: Namespace) -> int:
        """
        Execute the command
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        pass
    
    def setup_logging(self, verbose: bool = False) -> None:
        """Setup logging configuration"""
        level = logging.DEBUG if verbose else logging.INFO
        
        # Create logs directory if it doesn't exist
        import os
        os.makedirs('logs', exist_ok=True)
        
        # Update logger level
        self.logger.setLevel(level)
        
        # Get or create handlers
        if not self.logger.handlers:
            # File handler
            file_handler = logging.FileHandler('logs/cli.log')
            file_handler.setLevel(level)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)
            
            # Formatter
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            # Add handlers
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
    
    def get_database_manager(self) -> Any:
        """Get database manager instance (lazy initialization)"""
        if self.db_manager is None:
            if DatabaseManager is not None:
                self.db_manager = DatabaseManager()
            else:
                # Return mock for testing
                mock_db_manager = type('MockDatabaseManager', (object,), {
                    'health_check': lambda: {'connection_ok': True, 'tables_exist': True, 'data_accessible': True},
                    'validate_data_integrity': lambda: {},
                    'get_database_stats': lambda: {'qb_stats_count': 0, 'qb_splits_count': 0},
                    'cleanup_old_data': lambda days: 0
                })()
                self.db_manager = mock_db_manager
        return self.db_manager
    
    def handle_error(self, error: Exception, message: Optional[str] = None) -> int:
        """
        Handle command errors with consistent logging and exit codes
        
        Args:
            error: The exception that occurred
            message: Optional custom error message
            
        Returns:
            Exit code (non-zero)
        """
        if message:
            self.logger.error(f"{message}: {error}")
        else:
            self.logger.error(f"Command failed: {error}")
        
        # Log stack trace in debug mode
        if self.logger.isEnabledFor(logging.DEBUG):
            self.logger.debug("Stack trace:", exc_info=True)
        
        return 1
    
    def validate_args(self, args: Namespace) -> List[str]:
        """
        Validate command arguments
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            List of validation error messages (empty if valid)
        """
        return []
    
    def print_success(self, message: str) -> None:
        """Print success message with consistent formatting"""
        print(f"✓ {message}")
    
    def print_error(self, message: str) -> None:
        """Print error message with consistent formatting"""
        print(f"✗ {message}")
    
    def print_warning(self, message: str) -> None:
        """Print warning message with consistent formatting"""
        print(f"⚠ {message}")
    
    def print_info(self, message: str) -> None:
        """Print info message with consistent formatting"""
        print(f"ℹ {message}")
    
    def print_section_header(self, title: str) -> None:
        """Print section header with consistent formatting"""
        print(f"\n=== {title.upper()} ===")
    
    def confirm_action(self, message: str, default: bool = False) -> bool:
        """
        Prompt user for confirmation
        
        Args:
            message: Confirmation message
            default: Default value if user just presses Enter
            
        Returns:
            True if user confirms, False otherwise
        """
        suffix = " [Y/n]" if default else " [y/N]"
        try:
            response = input(f"{message}{suffix}: ").strip().lower()
            if not response:
                return default
            return response in ('y', 'yes')
        except KeyboardInterrupt:
            print("\nCancelled by user")
            return False
    
    def cleanup(self) -> None:
        """Cleanup resources (called after command execution)"""
        if self.db_manager:
            # Database connections are handled by context managers
            # No explicit cleanup needed
            pass 