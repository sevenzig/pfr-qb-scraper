#!/usr/bin/env python3
"""
Data Command for NFL QB Data Scraping System CLI
Handles data validation, import/export, quality checks, and backups
"""

from argparse import ArgumentParser, Namespace
from typing import List

from src.cli.base_command import BaseCommand
from src.cli.commands.populate_command import PopulateCommand
from src.cli.commands.cleanup_command import CleanupCommand

# Use try/except for optional imports
try:
    from ...operations.data_manager import DataManager
except ImportError:
    try:
        from src.operations.data_manager import DataManager
    except ImportError:
        DataManager = None

class DataCommand(BaseCommand):
    """Command for data management operations"""

    def __init__(self):
        super().__init__()
        if DataManager:
            self.data_manager = DataManager()
        else:
            self.data_manager = None

    @property
    def name(self) -> str:
        return "data"

    @property
    def aliases(self) -> List[str]:
        return ["d"]

    @property
    def description(self) -> str:
        return "Data management: validate, import/export, quality checks"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add data-specific arguments"""
        subparsers = parser.add_subparsers(dest='data_subcommand', help='Data subcommands')
        
        # Export subcommand
        export_parser = subparsers.add_parser('export', help='Export data from database')
        export_parser.add_argument('--season', type=int, help='Season to export')
        export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Export format')
        export_parser.add_argument('--output', help='Output file path')
        
        # Import subcommand
        import_parser = subparsers.add_parser('import', help='Import data to database')
        import_parser.add_argument('--file', required=True, help='File to import')
        import_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Import format')
        
        # Quality subcommand
        quality_parser = subparsers.add_parser('quality', help='Analyze data quality')
        quality_parser.add_argument('--season', type=int, help='Season to analyze')
        quality_parser.add_argument('--detailed', action='store_true', help='Show detailed analysis')
        
        # Summary subcommand
        summary_parser = subparsers.add_parser('summary', help='Show data summary')
        summary_parser.add_argument('--season', type=int, help='Season to summarize')
        
        # Clear subcommand
        clear_parser = subparsers.add_parser('clear', help='Clear all data from database')
        clear_parser.add_argument('--confirm', action='store_true', help='Confirm clearing all data')
        clear_parser.add_argument('--season', type=int, help='Clear data for specific season only')
        clear_parser.add_argument('--tables', nargs='+', help='Specific tables to clear')

    def run(self, args: Namespace) -> int:
        """Execute the data command"""
        if not args.data_subcommand:
            self.print_error("No data subcommand specified. Use 'export', 'import', 'quality', 'summary', or 'clear'.")
            return 1

        if args.data_subcommand == 'export':
            return self._handle_export(args)
        elif args.data_subcommand == 'import':
            return self._handle_import(args)
        elif args.data_subcommand == 'quality':
            return self._handle_quality(args)
        elif args.data_subcommand == 'summary':
            return self._handle_summary(args)
        elif args.data_subcommand == 'clear':
            return self._handle_clear(args)
        
        self.print_error(f"Unknown data subcommand: {args.data_subcommand}")
        return 1
    
    def _handle_populate(self, args: Namespace) -> int:
        """Handle the populate subcommand"""
        populate_command = PopulateCommand()
        return populate_command.run(args)

    def _handle_cleanup(self, args: Namespace) -> int:
        """Handle the cleanup subcommand"""
        cleanup_command = CleanupCommand()
        return cleanup_command.run(args)

    def _handle_validate(self, args: Namespace) -> int:
        """Handle data validation"""
        if not self.data_manager:
            self.print_error("DataManager not available")
            return 1
            
        self.print_info("Running data validation...")
        validation_results = self.data_manager.validate_data(season=args.season)
        
        # Display validation results
        self.print_section_header("Data Validation Results")
        
        overall_quality = self.data_manager._calculate_overall_quality(list(validation_results.values()))
        self.print_info(f"Overall Data Quality Score: {overall_quality:.2f}%")
        
        if args.detailed:
            for data_type, report in validation_results.items():
                self.print_info(f"\n{data_type.title()} Validation:")
                if report['errors']:
                    for error in report['errors']:
                        self.print_error(f"  - {error}")
                else:
                    self.print_success("  No validation errors found")
        
        if overall_quality < 95.0:
            self.print_warning("Data quality is below threshold (95%)")
            return 1
        else:
            self.print_success("Data quality is excellent")
            return 0
    
    def _handle_export(self, args: Namespace) -> int:
        """Handle data export"""
        if not self.data_manager:
            self.print_error("DataManager not available")
            return 1
            
        self.print_info(f"Exporting data to {args.format} format...")
        
        try:
            output_file = self.data_manager.export_data(
                format=args.format,
                season=args.season,
                output_file=args.output
            )
            self.print_success(f"Data exported successfully to: {output_file}")
            return 0
        except Exception as e:
            self.handle_error(e, f"Failed to export data")
            return 1
    
    def _handle_import(self, args: Namespace) -> int:
        """Handle data import"""
        if not self.data_manager:
            self.print_error("DataManager not available")
            return 1
            
        self.print_info(f"Importing data from {args.file}...")
        
        try:
            import_results = self.data_manager.import_data(
                input_file=args.file,
                format=args.format
            )
            
            self.print_success("Data imported successfully")
            
            if args.validate:
                self.print_info("Validating imported data...")
                validation_results = self.data_manager.validate_imported_data(import_results)
                # Display validation results
                # (similar to _handle_validate)
            
            return 0
        except Exception as e:
            self.handle_error(e, f"Failed to import data")
            return 1
    
    def _handle_quality(self, args: Namespace) -> int:
        """Handle data quality checks"""
        if not self.data_manager:
            self.print_error("DataManager not available")
            return 1
            
        self.print_info("Running data quality checks...")
        
        # This would call a more comprehensive quality check from DataManager
        # For now, we'll just run validation
        return self._handle_validate(args)
    
    def _handle_backup(self, args: Namespace) -> int:
        """Handle database backup"""
        if not self.data_manager:
            self.print_error("DataManager not available")
            return 1
            
        if args.action == 'create':
            self.print_info("Creating database backup...")
            try:
                backup_file = self.data_manager.create_backup(backup_name=args.file)
                self.print_success(f"Backup created successfully: {backup_file}")
                return 0
            except Exception as e:
                self.handle_error(e, "Failed to create backup")
                return 1
        
        elif args.action == 'restore':
            if not args.file:
                self.print_error("Backup file must be specified for restore")
                return 1
            
            self.print_warning(f"This will restore the database from {args.file}")
            if not self.confirm_action("Are you sure you want to proceed?"):
                self.print_info("Restore operation cancelled")
                return 0
            
            self.print_info(f"Restoring database from {args.file}...")
            try:
                success = self.data_manager.restore_backup(backup_file=args.file)
                if success:
                    self.print_success("Database restored successfully")
                    return 0
                else:
                    self.print_error("Failed to restore database")
                    return 1
            except Exception as e:
                self.handle_error(e, "Failed to restore backup")
                return 1
        
        return 1
    
    def _handle_summary(self, args: Namespace) -> int:
        """Handle data summary"""
        if not self.data_manager:
            self.print_error("DataManager not available")
            return 1
            
        self.print_info("Generating data summary...")
        summary = self.data_manager.get_data_summary(season=args.season)
        
        self.print_section_header("Data Summary")
        for key, value in summary.items():
            if isinstance(value, dict):
                self.print_info(f"\n{key.replace('_', ' ').title()}:")
                for sub_key, sub_value in value.items():
                    self.print_info(f"  {sub_key.replace('_', ' ').title()}: {sub_value}")
            else:
                self.print_info(f"{key.replace('_', ' ').title()}: {value}")
        
        return 0 

    def _handle_clear(self, args: Namespace) -> int:
        """Handle clearing data from database"""
        try:
            db_manager = self.get_database_manager()
            
            if not args.confirm:
                self.print_warning("⚠️  WARNING: This will delete data from the database!")
                self.print_info("Tables will be preserved, but records will be removed.")
                self.print_info("This operation cannot be undone.")
                self.print_info("Use --confirm to proceed.")
                return 1
            
            if args.season:
                # Clear data for specific season
                self.print_info(f"Clearing data for season {args.season}...")
                return self._clear_season_data(db_manager, args.season)
            elif args.tables:
                # Clear specific tables
                self.print_info(f"Clearing tables: {', '.join(args.tables)}...")
                return self._clear_specific_tables(db_manager, args.tables)
            else:
                # Clear all data
                self.print_info("Clearing all data from database...")
                return self._clear_all_data(db_manager)
                
        except Exception as e:
            self.handle_error(e, "Failed to clear data")
            return 1
    
    def _clear_all_data(self, db_manager) -> int:
        """Clear all data from database"""
        # Tables to clear (in order to respect foreign key constraints)
        tables_to_clear = [
            'scraping_logs',
            'qb_splits_advanced', 
            'qb_splits',
            'qb_passing_stats',
            'players'
        ]
        
        total_deleted = 0
        
        for table in tables_to_clear:
            try:
                # Get count before deletion
                count_result = db_manager.query(f"SELECT COUNT(*) as count FROM {table}")
                count_before = count_result[0]['count'] if count_result else 0
                
                # Delete all records
                deleted_count = db_manager.execute(f"DELETE FROM {table}")
                
                self.print_info(f"✅ Deleted {deleted_count} records from {table} (was {count_before})")
                total_deleted += deleted_count
                
            except Exception as e:
                self.print_error(f"❌ Error clearing table {table}: {e}")
                continue
        
        self.print_success(f"✅ Database clearing completed! Total records deleted: {total_deleted}")
        return 0
    
    def _clear_season_data(self, db_manager, season: int) -> int:
        """Clear data for specific season"""
        tables_to_clear = [
            'qb_splits_advanced', 
            'qb_splits',
            'qb_passing_stats'
        ]
        
        total_deleted = 0
        
        for table in tables_to_clear:
            try:
                # Get count before deletion
                count_result = db_manager.query(f"SELECT COUNT(*) as count FROM {table} WHERE season = %s", (season,))
                count_before = count_result[0]['count'] if count_result else 0
                
                # Delete records for specific season
                deleted_count = db_manager.execute(f"DELETE FROM {table} WHERE season = %s", (season,))
                
                self.print_info(f"✅ Deleted {deleted_count} records from {table} for season {season} (was {count_before})")
                total_deleted += deleted_count
                
            except Exception as e:
                self.print_error(f"❌ Error clearing table {table}: {e}")
                continue
        
        self.print_success(f"✅ Season {season} data clearing completed! Total records deleted: {total_deleted}")
        return 0
    
    def _clear_specific_tables(self, db_manager, tables: list) -> int:
        """Clear specific tables"""
        total_deleted = 0
        
        for table in tables:
            try:
                # Get count before deletion
                count_result = db_manager.query(f"SELECT COUNT(*) as count FROM {table}")
                count_before = count_result[0]['count'] if count_result else 0
                
                # Delete all records
                deleted_count = db_manager.execute(f"DELETE FROM {table}")
                
                self.print_info(f"✅ Deleted {deleted_count} records from {table} (was {count_before})")
                total_deleted += deleted_count
                
            except Exception as e:
                self.print_error(f"❌ Error clearing table {table}: {e}")
                continue
        
        self.print_success(f"✅ Table clearing completed! Total records deleted: {total_deleted}")
        return 0 