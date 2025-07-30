#!/usr/bin/env python3
"""
Health command for NFL QB Data Scraping System CLI
Handles system health checks and diagnostics
"""

import sys
from argparse import ArgumentParser, Namespace
from typing import Dict, Any, List

from src.cli.base_command import BaseCommand


class HealthCommand(BaseCommand):
    """Command to perform system health checks"""
    
    @property
    def name(self) -> str:
        """Command name"""
        return "health"
    
    @property
    def description(self) -> str:
        """Command description"""
        return "Perform comprehensive system health checks"
    
    @property
    def aliases(self) -> List[str]:
        """Command aliases"""
        return ["h"]
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add health-specific arguments"""
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed health information'
        )
        parser.add_argument(
            '--fix',
            action='store_true',
            help='Attempt to fix issues found during health check'
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=30,
            help='Timeout for health checks in seconds (default: 30)'
        )
    
    def validate_args(self, args: Namespace) -> List[str]:
        """Validate health command arguments"""
        errors = []
        
        # Validate timeout
        if args.timeout < 1 or args.timeout > 300:
            errors.append(f"Invalid timeout: {args.timeout}. Must be between 1 and 300 seconds.")
        
        return errors
    
    def run(self, args: Namespace) -> int:
        """Execute the health command"""
        try:
            # Validate arguments
            validation_errors = self.validate_args(args)
            if validation_errors:
                for error in validation_errors:
                    self.print_error(error)
                return 1
            
            self.logger.info("Starting system health check")
            
            db_manager = self.get_database_manager()
            
            self.print_section_header("System Health Check")
            self.print_info("Performing health check...")
            
            # Run health checks
            health_results = db_manager.health_check()
            
            # Display results
            self._display_health_results(health_results, args.detailed)
            
            # Attempt fixes if requested
            if args.fix:
                self._attempt_fixes(db_manager, health_results)
            
            # Determine overall health status
            critical_checks = ['connection_ok', 'tables_exist', 'data_accessible']
            all_critical_healthy = all(
                health_results.get(check, False) for check in critical_checks
            )
            
            if all_critical_healthy:
                self.print_success("All critical health checks passed")
                return 0
            else:
                self.print_error("Some critical health checks failed")
                return 1
            
        except Exception as e:
            return self.handle_error(e, "Health check failed")
    
    def _display_health_results(self, health_results: Dict[str, Any], detailed: bool) -> None:
        """Display health check results"""
        self.print_section_header("Health Check Results")
        
        # Group checks by category
        critical_checks = {
            'connection_ok': 'Database Connection',
            'tables_exist': 'Database Tables',
            'data_accessible': 'Data Access'
        }
        
        optional_checks = {
            'indexes_optimal': 'Database Indexes',
            'disk_space_ok': 'Disk Space',
            'memory_ok': 'Memory Usage'
        }
        
        # Show critical checks
        self.print_info("Critical Systems:")
        for check, description in critical_checks.items():
            status = health_results.get(check, False)
            icon = "✓" if status else "✗"
            self.print_info(f"  {icon} {description}: {'OK' if status else 'FAILED'}")
        
        # Show optional checks if detailed or if they failed
        optional_results = {k: v for k, v in health_results.items() if k in optional_checks}
        if detailed or any(not v for v in optional_results.values()):
            self.print_info("\nOptional Systems:")
            for check, description in optional_checks.items():
                status = health_results.get(check, True)  # Default to True for optional
                icon = "✓" if status else "⚠"
                self.print_info(f"  {icon} {description}: {'OK' if status else 'WARNING'}")
        
        # Show additional details if requested
        if detailed:
            self._show_detailed_health_info(health_results)
    
    def _show_detailed_health_info(self, health_results: Dict[str, Any]) -> None:
        """Show detailed health information"""
        self.print_section_header("Detailed Health Information")
        
        try:
            # Database connection details
            if 'connection_details' in health_results:
                details = health_results['connection_details']
                self.print_info("Database Connection Details:")
                for key, value in details.items():
                    self.print_info(f"  {key}: {value}")
            
            # Performance metrics
            if 'performance_metrics' in health_results:
                metrics = health_results['performance_metrics']
                self.print_info("Performance Metrics:")
                for key, value in metrics.items():
                    self.print_info(f"  {key}: {value}")
            
            # System resources
            if 'system_resources' in health_results:
                resources = health_results['system_resources']
                self.print_info("System Resources:")
                for key, value in resources.items():
                    self.print_info(f"  {key}: {value}")
            
        except Exception as e:
            self.print_error(f"Failed to show detailed health info: {e}")
    
    def _attempt_fixes(self, db_manager, health_results: Dict[str, Any]) -> None:
        """Attempt to fix health issues"""
        self.print_section_header("Attempting to Fix Issues")
        
        fixes_attempted = 0
        fixes_successful = 0
        
        # Check for common fixable issues
        if not health_results.get('connection_ok', False):
            self.print_warning("Database connection issue detected")
            if self.confirm_action("Attempt to reconnect to database?"):
                try:
                    # Attempt to reconnect
                    db_manager = self.get_database_manager()
                    if db_manager.health_check().get('connection_ok', False):
                        self.print_success("Database connection restored")
                        fixes_successful += 1
                    else:
                        self.print_error("Failed to restore database connection")
                    fixes_attempted += 1
                except Exception as e:
                    self.print_error(f"Failed to reconnect: {e}")
                    fixes_attempted += 1
        
        if not health_results.get('tables_exist', False):
            self.print_warning("Database tables missing")
            if self.confirm_action("Attempt to create missing tables?"):
                try:
                    # This would require a method to create tables
                    self.print_info("Table creation not yet implemented")
                    # In future: db_manager.create_tables()
                    fixes_attempted += 1
                except Exception as e:
                    self.print_error(f"Failed to create tables: {e}")
                    fixes_attempted += 1
        
        if not health_results.get('indexes_optimal', True):
            self.print_warning("Database indexes not optimal")
            if self.confirm_action("Attempt to optimize indexes?"):
                try:
                    # This would require a method to optimize indexes
                    self.print_info("Index optimization not yet implemented")
                    # In future: db_manager.optimize_indexes()
                    fixes_attempted += 1
                except Exception as e:
                    self.print_error(f"Failed to optimize indexes: {e}")
                    fixes_attempted += 1
        
        # Summary
        if fixes_attempted == 0:
            self.print_info("No fixable issues found")
        else:
            self.print_info(f"Attempted {fixes_attempted} fixes, {fixes_successful} successful") 