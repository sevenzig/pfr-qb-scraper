#!/usr/bin/env python3
"""
Data Command for NFL QB Data Scraping System CLI
Handles data validation, import/export, quality checks, and backups
"""

from argparse import ArgumentParser, Namespace
from typing import List

from ..base_command import BaseCommand
from .populate_command import PopulateCommand
from .cleanup_command import CleanupCommand

# Use try/except for optional imports
try:
    from ...operations.data_manager import DataManager
except ImportError:
    try:
        from operations.data_manager import DataManager
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

    def add_arguments(self, parser: ArgumentParser):
        """Add command-specific arguments"""
        subparsers = parser.add_subparsers(dest='data_subcommand', help='Data operation subcommands')
        
        # Validate subcommand
        validate_parser = subparsers.add_parser('validate', help='Validate data integrity')
        validate_parser.add_argument('--season', type=int, help='Specific season to validate')
        validate_parser.add_argument('--detailed', action='store_true', help='Show detailed validation results')
        
        # Export subcommand
        export_parser = subparsers.add_parser('export', help='Export data to a file')
        export_parser.add_argument('--format', choices=['json', 'csv', 'sqlite'], 
                                   default='json', help='Export format (default: json)')
        export_parser.add_argument('--season', type=int, help='Specific season to export')
        export_parser.add_argument('--output-file', type=str, help='Output file path')
        
        # Import subcommand
        import_parser = subparsers.add_parser('import', help='Import data from a file')
        import_parser.add_argument('--file', type=str, required=True, help='File to import')
        import_parser.add_argument('--format', choices=['json', 'csv', 'sqlite'], 
                                   help='Import format (auto-detected if not specified)')
        import_parser.add_argument('--validate', action='store_true', help='Validate imported data')
        
        # Populate subcommand
        populate_parser = subparsers.add_parser('populate', help='Populate database with initial data')
        populate_command = PopulateCommand()
        populate_command.add_arguments(populate_parser)

        # Cleanup subcommand
        cleanup_parser = subparsers.add_parser('cleanup', help='Clean up data in the database')
        cleanup_command = CleanupCommand()
        cleanup_command.add_arguments(cleanup_parser)

        # Quality subcommand
        quality_parser = subparsers.add_parser('quality', help='Run data quality checks')
        quality_parser.add_argument('--season', type=int, help='Specific season for quality checks')
        quality_parser.add_argument('--report-file', type=str, help='Save quality report to a file')
        
        # Backup subcommand
        backup_parser = subparsers.add_parser('backup', help='Create or restore a database backup')
        backup_parser.add_argument('action', choices=['create', 'restore'], help='Backup action')
        backup_parser.add_argument('--file', type=str, help='Backup file path')
        
        # Summary subcommand
        summary_parser = subparsers.add_parser('summary', help='Show data summary')
        summary_parser.add_argument('--season', type=int, help='Specific season for summary')

    def run(self, args: Namespace) -> int:
        """Execute the data command"""
        if not args.data_subcommand:
            self.logger.error("No data subcommand specified. Use --help for available options.")
            return 1
        
        try:
            if args.data_subcommand == 'validate':
                return self._handle_validate(args)
            elif args.data_subcommand == 'export':
                return self._handle_export(args)
            elif args.data_subcommand == 'import':
                return self._handle_import(args)
            elif args.data_subcommand == 'populate':
                return self._handle_populate(args)
            elif args.data_subcommand == 'cleanup':
                return self._handle_cleanup(args)
            elif args.data_subcommand == 'quality':
                return self._handle_quality(args)
            elif args.data_subcommand == 'backup':
                return self._handle_backup(args)
            elif args.data_subcommand == 'summary':
                return self._handle_summary(args)
            else:
                self.logger.error(f"Unknown data subcommand: {args.data_subcommand}")
                return 1
                
        except Exception as e:
            self.logger.error(f"Data command failed: {e}")
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
                output_file=args.output_file
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