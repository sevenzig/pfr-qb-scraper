#!/usr/bin/env python3
"""
Cleanup Command for NFL QB Data Scraping System CLI
Handles cleaning up data in the database.
"""

from argparse import ArgumentParser, Namespace

from ..base_command import BaseCommand

class CleanupCommand(BaseCommand):
    """Command to clean up database data"""

    @property
    def name(self) -> str:
        return "cleanup"

    @property
    def description(self) -> str:
        return "Clean up data in the database (e.g., duplicate teams)"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add cleanup-specific arguments"""
        subparsers = parser.add_subparsers(dest='cleanup_subcommand', help='Cleanup subcommands')
        
        # Cleanup teams subcommand
        teams_parser = subparsers.add_parser('teams', help='Clean up duplicate team codes')
        teams_parser.add_argument('--confirm', action='store_true', help='Confirm cleaning up team codes')

    def run(self, args: Namespace) -> int:
        """Execute the cleanup command"""
        if not args.cleanup_subcommand:
            self.print_error("No cleanup subcommand specified. Use 'teams'.")
            return 1

        if args.cleanup_subcommand == 'teams':
            return self._handle_cleanup_teams(args)
        
        self.print_error(f"Unknown cleanup subcommand: {args.cleanup_subcommand}")
        return 1

    def _handle_cleanup_teams(self, args: Namespace) -> int:
        """Handle cleaning up the teams table"""
        if not args.confirm:
            self.print_warning("This will clean up duplicate team codes, prioritizing 3-letter codes.")
            self.print_info("This operation will update related tables and delete the old team records.")
            self.print_info("Use the --confirm flag to proceed.")
            return 1
            
        self.print_info("Cleaning up team codes...")
        
        try:
            db_manager = self.get_database_manager()
            results = db_manager.cleanup_team_codes()
            self.print_success("Team code cleanup successful.")
            self.print_info(f"  Updated rows in qb_passing_stats: {results['updated_passing_stats_rows']}")
            self.print_info(f"  Deleted team records: {results['deleted_team_records']}")
            
            # Verify the teams count
            result = db_manager.query("SELECT COUNT(*) as count FROM teams")
            if result:
                count = result[0]['count']
                self.print_info(f"Teams table now contains {count} teams.")

            return 0
        except Exception as e:
            self.handle_error(e, "Failed to clean up team codes")
            return 1 