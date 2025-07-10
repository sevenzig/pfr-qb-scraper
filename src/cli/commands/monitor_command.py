#!/usr/bin/env python3
"""
Monitor command for NFL QB Data Scraping System CLI
Handles system monitoring and metrics display
"""

import sys
from argparse import ArgumentParser, Namespace
from typing import Dict, Any, List

from ..base_command import BaseCommand


class MonitorCommand(BaseCommand):
    """Command to monitor system and data metrics"""
    
    @property
    def name(self) -> str:
        """Command name"""
        return "monitor"
    
    @property
    def description(self) -> str:
        """Command description"""
        return "Monitor system performance and data quality metrics"
    
    @property
    def aliases(self) -> List[str]:
        """Command aliases"""
        return ["m"]
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add monitor-specific arguments"""
        parser.add_argument(
            '--recent',
            action='store_true',
            help='Show recent scraping sessions'
        )
        parser.add_argument(
            '--performance',
            action='store_true',
            help='Show performance metrics'
        )
        parser.add_argument(
            '--quality',
            action='store_true',
            help='Show data quality metrics'
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours to look back for recent sessions (default: 24)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=20,
            help='Limit number of sessions to display (default: 20)'
        )
    
    def validate_args(self, args: Namespace) -> List[str]:
        """Validate monitor command arguments"""
        errors = []
        
        # Validate hours
        if args.hours < 1 or args.hours > 720:  # Max 30 days
            errors.append(f"Invalid hours: {args.hours}. Must be between 1 and 720.")
        
        # Validate limit
        if args.limit < 1 or args.limit > 100:
            errors.append(f"Invalid limit: {args.limit}. Must be between 1 and 100.")
        
        return errors
    
    def run(self, args: Namespace) -> int:
        """Execute the monitor command"""
        try:
            # Validate arguments
            validation_errors = self.validate_args(args)
            if validation_errors:
                for error in validation_errors:
                    self.print_error(error)
                return 1
            
            self.logger.info("Starting system monitoring")
            
            db_manager = self.get_database_manager()
            
            # Show recent sessions if requested
            if args.recent:
                self._show_recent_sessions(db_manager, args.hours, args.limit)
            
            # Show performance metrics if requested
            if args.performance:
                self._show_performance_metrics(db_manager)
            
            # Show data quality metrics if requested
            if args.quality:
                self._show_data_quality_metrics(db_manager)
            
            # Show all if no specific option selected
            if not any([args.recent, args.performance, args.quality]):
                self._show_recent_sessions(db_manager, args.hours, args.limit)
                print()
                self._show_performance_metrics(db_manager)
                print()
                self._show_data_quality_metrics(db_manager)
            
            return 0
            
        except Exception as e:
            return self.handle_error(e, "Monitoring failed")
    
    def _show_recent_sessions(self, db_manager, hours: int, limit: int) -> None:
        """Show recent scraping sessions"""
        self.print_section_header(f"Recent Scraping Sessions (Last {hours} hours)")
        
        try:
            # This would require a method to get recent sessions from the database
            # For now, show a placeholder since the method isn't implemented
            self.print_warning("Recent sessions feature not yet implemented")
            self.print_info("This feature will show:")
            self.print_info(f"  - Last {limit} scraping sessions")
            self.print_info(f"  - Sessions from the last {hours} hours")
            self.print_info("  - Session status, duration, and results")
            
        except Exception as e:
            self.print_error(f"Failed to retrieve recent sessions: {e}")
    
    def _show_performance_metrics(self, db_manager) -> None:
        """Show performance metrics"""
        self.print_section_header("Performance Metrics")
        
        try:
            stats = db_manager.get_database_stats()
            
            # Database size metrics
            qb_stats_count = stats.get('qb_stats_count', 0)
            qb_splits_count = stats.get('qb_splits_count', 0)
            unique_players = stats.get('unique_players', 0)
            unique_teams = stats.get('unique_teams', 0)
            unique_seasons = stats.get('unique_seasons', 0)
            
            self.print_info(f"Total QB Stats Records: {qb_stats_count:,}")
            self.print_info(f"Total QB Splits Records: {qb_splits_count:,}")
            self.print_info(f"Unique Players: {unique_players:,}")
            self.print_info(f"Unique Teams: {unique_teams:,}")
            self.print_info(f"Seasons Covered: {unique_seasons:,}")
            
            # Calculate some derived metrics
            if unique_players > 0:
                avg_stats_per_player = qb_stats_count / unique_players
                avg_splits_per_player = qb_splits_count / unique_players
                self.print_info(f"Avg Stats per Player: {avg_stats_per_player:.1f}")
                self.print_info(f"Avg Splits per Player: {avg_splits_per_player:.1f}")
            
        except Exception as e:
            self.print_error(f"Failed to retrieve performance metrics: {e}")
    
    def _show_data_quality_metrics(self, db_manager) -> None:
        """Show data quality metrics"""
        self.print_section_header("Data Quality Metrics")
        
        try:
            validation_errors = db_manager.validate_data_integrity()
            total_errors = sum(len(errors) for errors in validation_errors.values())
            
            if total_errors == 0:
                self.print_success("No data integrity issues found")
            else:
                self.print_error(f"Found {total_errors} data integrity issues")
                
                # Show breakdown by table
                for table, errors in validation_errors.items():
                    if errors:
                        self.print_warning(f"{table}: {len(errors)} issues")
            
            # Show additional quality metrics
            self._show_data_completeness(db_manager)
            
        except Exception as e:
            self.print_error(f"Failed to retrieve data quality metrics: {e}")
    
    def _show_data_completeness(self, db_manager) -> None:
        """Show data completeness metrics"""
        try:
            stats = db_manager.get_database_stats()
            
            # Calculate completeness ratios
            qb_stats_count = stats.get('qb_stats_count', 0)
            qb_splits_count = stats.get('qb_splits_count', 0)
            
            if qb_stats_count > 0:
                splits_ratio = qb_splits_count / qb_stats_count
                self.print_info(f"Splits to Stats Ratio: {splits_ratio:.2f}")
                
                # Expected ratio depends on number of split types
                # This is a rough estimate
                expected_ratio = 15  # Approximate expected splits per stat record
                completeness = min(100, (splits_ratio / expected_ratio) * 100)
                
                if completeness >= 80:
                    self.print_success(f"Data Completeness: {completeness:.1f}%")
                elif completeness >= 60:
                    self.print_warning(f"Data Completeness: {completeness:.1f}%")
                else:
                    self.print_error(f"Data Completeness: {completeness:.1f}%")
            
        except Exception as e:
            self.print_error(f"Failed to calculate data completeness: {e}") 