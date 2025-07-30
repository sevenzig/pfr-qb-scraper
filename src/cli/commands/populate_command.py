#!/usr/bin/env python3
"""
Populate Command for NFL QB Data Scraping
CLI command for populating database with sample data
"""

import logging
import argparse
from typing import Dict, Any, List
from argparse import ArgumentParser, Namespace

from src.cli.base_command import BaseCommand
from src.database.db_manager import DatabaseManager

class PopulateCommand(BaseCommand):
    """Command to populate database tables"""

    @property
    def name(self) -> str:
        return "populate"

    @property
    def description(self) -> str:
        return "Populate the database with initial data (e.g., teams)"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add populate-specific arguments"""
        subparsers = parser.add_subparsers(dest='populate_subcommand', help='Populate subcommands')
        
        # Populate teams subcommand
        teams_parser = subparsers.add_parser('teams', help='Populate the teams table')
        teams_parser.add_argument('--confirm', action='store_true', help='Confirm populating teams data')

    def run(self, args: Namespace) -> int:
        """Execute the populate command"""
        if not args.populate_subcommand:
            self.print_error("No populate subcommand specified. Use 'teams'.")
            return 1

        if args.populate_subcommand == 'teams':
            return self._handle_populate_teams(args)
        
        self.print_error(f"Unknown populate subcommand: {args.populate_subcommand}")
        return 1

    def _handle_populate_teams(self, args: Namespace) -> int:
        """Handle populating the teams table"""
        if not args.confirm:
            self.print_warning("This will populate the 'teams' table with all 32 NFL teams.")
            self.print_info("This operation is idempotent and can be run multiple times safely.")
            self.print_info("Use the --confirm flag to proceed.")
            return 1
            
        self.print_info("Populating teams table...")
        
        try:
            db_manager = self.get_database_manager()
            teams_populated = db_manager.populate_teams()
            self.print_success(f"Successfully inserted/updated {teams_populated} teams.")
            
            # Verify the teams were inserted
            result = db_manager.query("SELECT COUNT(*) as count FROM teams")
            if result:
                count = result[0]['count']
                self.print_info(f"Teams table now contains {count} teams.")

            return 0
        except Exception as e:
            self.handle_error(e, "Failed to populate teams table")
            return 1 