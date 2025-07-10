#!/usr/bin/env python3
"""
Legacy Deprecation CLI Commands
Manage legacy script deprecation and migration
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from cli.base_command import BaseCommand
from operations.legacy_deprecation import LegacyDeprecationManager

logger = logging.getLogger(__name__)


class LegacyCommand(BaseCommand):
    """Manage legacy script deprecation and migration"""
    
    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "legacy"

    @property
    def description(self) -> str:
        return "Manage legacy script deprecation and migration"

    def run(self, args) -> int:
        return self.execute(args)
    
    def add_arguments(self, parser):
        """Add command-specific arguments"""
        parser.add_argument(
            '--action', '-a',
            choices=['status', 'warn', 'migrate', 'redirect', 'plan', 'report', 'help'],
            default='status',
            help='Legacy management action to perform'
        )
        parser.add_argument(
            '--script', '-s',
            type=str,
            help='Specific script to operate on'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes'
        )
        parser.add_argument(
            '--output', '-o',
            type=str,
            help='Output file for reports'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force operation even if warnings are present'
        )
    
    def execute(self, args) -> int:
        """Execute the legacy management command"""
        try:
            deprecation_manager = LegacyDeprecationManager()
            
            if args.action == 'status':
                return self._show_status(deprecation_manager, args)
            elif args.action == 'warn':
                return self._add_warnings(deprecation_manager, args)
            elif args.action == 'migrate':
                return self._migrate_script(deprecation_manager, args)
            elif args.action == 'redirect':
                return self._create_redirects(deprecation_manager, args)
            elif args.action == 'plan':
                return self._show_removal_plan(deprecation_manager, args)
            elif args.action == 'report':
                return self._generate_report(deprecation_manager, args)
            elif args.action == 'help':
                return self._show_migration_help(deprecation_manager, args)
            else:
                logger.error(f"Unknown legacy action: {args.action}")
                return 1
        
        except Exception as e:
            logger.error(f"Legacy management failed: {e}")
            return 1
    
    def _show_status(self, manager: LegacyDeprecationManager, args) -> int:
        """Show status of legacy scripts"""
        print("\n" + "="*60)
        print("LEGACY SCRIPT STATUS")
        print("="*60)
        
        current_date = datetime.now()
        total_scripts = len(manager.legacy_scripts)
        
        if total_scripts == 0:
            print("No legacy scripts found.")
            return 0
        
        print(f"Total Legacy Scripts: {total_scripts}")
        print(f"Current Date: {current_date.strftime('%Y-%m-%d')}")
        print()
        
        # Categorize scripts by status
        active_scripts = []
        deprecated_scripts = []
        removal_soon_scripts = []
        past_due_scripts = []
        
        for script_name, script_info in manager.legacy_scripts.items():
            days_until_removal = (script_info.removal_date - current_date).days
            
            if days_until_removal < 0:
                past_due_scripts.append((script_name, script_info, days_until_removal))
            elif days_until_removal < 30:
                removal_soon_scripts.append((script_name, script_info, days_until_removal))
            elif days_until_removal < 90:
                deprecated_scripts.append((script_name, script_info, days_until_removal))
            else:
                active_scripts.append((script_name, script_info, days_until_removal))
        
        # Display scripts by category
        if past_due_scripts:
            print("🚨 PAST DUE FOR REMOVAL:")
            print("-" * 30)
            for script_name, script_info, days in past_due_scripts:
                print(f"  {script_name} (overdue by {abs(days)} days)")
                print(f"    CLI: pfr-scraper {script_info.cli_equivalent}")
            print()
        
        if removal_soon_scripts:
            print("⚠️  REMOVAL SOON (Next 30 Days):")
            print("-" * 30)
            for script_name, script_info, days in removal_soon_scripts:
                print(f"  {script_name} ({days} days until removal)")
                print(f"    CLI: pfr-scraper {script_info.cli_equivalent}")
            print()
        
        if deprecated_scripts:
            print("📝 DEPRECATED (Next 90 Days):")
            print("-" * 30)
            for script_name, script_info, days in deprecated_scripts:
                print(f"  {script_name} ({days} days until removal)")
                print(f"    CLI: pfr-scraper {script_info.cli_equivalent}")
            print()
        
        if active_scripts:
            print("✅ ACTIVE:")
            print("-" * 30)
            for script_name, script_info, days in active_scripts:
                print(f"  {script_name} ({days} days until removal)")
                print(f"    CLI: pfr-scraper {script_info.cli_equivalent}")
            print()
        
        # Summary
        print("Summary:")
        print(f"  Past Due: {len(past_due_scripts)}")
        print(f"  Removal Soon: {len(removal_soon_scripts)}")
        print(f"  Deprecated: {len(deprecated_scripts)}")
        print(f"  Active: {len(active_scripts)}")
        
        if past_due_scripts:
            print("\n⚠️  Action Required: Some scripts are past due for removal!")
            return 1
        
        return 0
    
    def _add_warnings(self, manager: LegacyDeprecationManager, args) -> int:
        """Add deprecation warnings to legacy scripts"""
        if args.script:
            if args.script not in manager.legacy_scripts:
                logger.error(f"Script {args.script} not found in legacy registry")
                return 1
            
            script_info = manager.legacy_scripts[args.script]
            if args.dry_run:
                print(f"DRY RUN: Would add deprecation warning to {args.script}")
                print(f"  CLI Alternative: pfr-scraper {script_info.cli_equivalent}")
                return 0
            
            manager._add_script_deprecation_warning(script_info)
            print(f"✓ Added deprecation warning to {args.script}")
        else:
            if args.dry_run:
                print("DRY RUN: Would add deprecation warnings to all legacy scripts")
                for script_name in manager.legacy_scripts:
                    print(f"  - {script_name}")
                return 0
            
            manager.add_deprecation_warnings()
            print(f"✓ Added deprecation warnings to {len(manager.legacy_scripts)} scripts")
        
        return 0
    
    def _migrate_script(self, manager: LegacyDeprecationManager, args) -> int:
        """Migrate a specific script to CLI"""
        if not args.script:
            logger.error("Script name required for migration")
            return 1
        
        if args.script not in manager.legacy_scripts:
            logger.error(f"Script {args.script} not found in legacy registry")
            return 1
        
        script_info = manager.legacy_scripts[args.script]
        
        print(f"Migrating {args.script} to CLI equivalent...")
        print(f"  CLI Command: pfr-scraper {script_info.cli_equivalent}")
        print(f"  Migration Notes: {script_info.migration_notes}")
        
        if args.dry_run:
            print("DRY RUN: Would perform migration")
            return 0
        
        success = manager.execute_migration(args.script, dry_run=False)
        if success:
            print(f"✓ Successfully migrated {args.script}")
            return 0
        else:
            print(f"✗ Failed to migrate {args.script}")
            return 1
    
    def _create_redirects(self, manager: LegacyDeprecationManager, args) -> int:
        """Create redirect scripts"""
        if args.dry_run:
            print("DRY RUN: Would create redirect scripts for all legacy scripts")
            for script_name, script_info in manager.legacy_scripts.items():
                print(f"  - {script_name} → pfr-scraper {script_info.cli_equivalent}")
            return 0
        
        manager.create_redirect_scripts()
        print(f"✓ Created redirect scripts for {len(manager.legacy_scripts)} scripts")
        return 0
    
    def _show_removal_plan(self, manager: LegacyDeprecationManager, args) -> int:
        """Show removal plan for legacy scripts"""
        removal_plan = manager.create_removal_plan()
        
        print("\n" + "="*60)
        print("LEGACY SCRIPT REMOVAL PLAN")
        print("="*60)
        
        if removal_plan['immediate_removal']:
            print("\n🚨 IMMEDIATE REMOVAL (Past Due):")
            print("-" * 30)
            for script in removal_plan['immediate_removal']:
                print(f"  {script.name}")
                print(f"    CLI: pfr-scraper {script.cli_equivalent}")
                print(f"    Migration: {script.migration_notes}")
            print()
        
        if removal_plan['scheduled_removal']:
            print("\n⚠️  SCHEDULED REMOVAL (Next 30 Days):")
            print("-" * 30)
            for script in removal_plan['scheduled_removal']:
                days = (script.removal_date - datetime.now()).days
                print(f"  {script.name} ({days} days)")
                print(f"    CLI: pfr-scraper {script.cli_equivalent}")
                print(f"    Migration: {script.migration_notes}")
            print()
        
        if removal_plan['migration_required']:
            print("\n📋 MIGRATION REQUIRED:")
            print("-" * 30)
            for script in removal_plan['migration_required']:
                print(f"  {script.name} (used {script.usage_count} times)")
                print(f"    CLI: pfr-scraper {script.cli_equivalent}")
                print(f"    Migration: {script.migration_notes}")
            print()
        
        if removal_plan['keep_for_compatibility']:
            print("\n✅ KEEP FOR COMPATIBILITY:")
            print("-" * 30)
            for script in removal_plan['keep_for_compatibility']:
                print(f"  {script.name}")
                print(f"    CLI: pfr-scraper {script.cli_equivalent}")
            print()
        
        # Summary
        print("Removal Plan Summary:")
        print(f"  Immediate Removal: {len(removal_plan['immediate_removal'])}")
        print(f"  Scheduled Removal: {len(removal_plan['scheduled_removal'])}")
        print(f"  Migration Required: {len(removal_plan['migration_required'])}")
        print(f"  Keep for Compatibility: {len(removal_plan['keep_for_compatibility'])}")
        
        return 0
    
    def _generate_report(self, manager: LegacyDeprecationManager, args) -> int:
        """Generate comprehensive legacy usage report"""
        report = manager.generate_usage_report()
        
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                f.write(report)
            print(f"Report saved to: {output_path}")
        else:
            print(report)
        
        return 0
    
    def _show_migration_help(self, manager: LegacyDeprecationManager, args) -> int:
        """Show migration help and guide"""
        guide = manager.generate_migration_guide()
        
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                f.write(guide)
            print(f"Migration guide saved to: {output_path}")
        else:
            print(guide)
        
        return 0


class MigrateCommand(BaseCommand):
    """Migrate from legacy scripts to CLI"""
    
    def __init__(self):
        super().__init__()

    @property
    def name(self) -> str:
        return "migrate"

    @property
    def description(self) -> str:
        return "Interactive migration assistant for transitioning from old scripts to new CLI"

    def run(self, args) -> int:
        return self.execute(args)
    
    def add_arguments(self, parser):
        """Add command-specific arguments"""
        parser.add_argument(
            '--script', '-s',
            type=str,
            help='Specific script to migrate'
        )
        parser.add_argument(
            '--auto',
            action='store_true',
            help='Automatically migrate all scripts without prompting'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be migrated without making changes'
        )
        parser.add_argument(
            '--backup',
            action='store_true',
            help='Create backups before migration'
        )
    
    def execute(self, args) -> int:
        """Execute the migration command"""
        try:
            deprecation_manager = LegacyDeprecationManager()
            
            if args.script:
                return self._migrate_single_script(deprecation_manager, args)
            elif args.auto:
                return self._migrate_all_scripts(deprecation_manager, args)
            else:
                return self._interactive_migration(deprecation_manager, args)
        
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return 1
    
    def _migrate_single_script(self, manager: LegacyDeprecationManager, args) -> int:
        """Migrate a single script"""
        if args.script not in manager.legacy_scripts:
            logger.error(f"Script {args.script} not found in legacy registry")
            return 1
        
        script_info = manager.legacy_scripts[args.script]
        
        print(f"\nMigrating {args.script}...")
        print(f"  CLI Equivalent: pfr-scraper {script_info.cli_equivalent}")
        print(f"  Migration Notes: {script_info.migration_notes}")
        
        if args.dry_run:
            print("DRY RUN: Would perform migration")
            return 0
        
        success = manager.execute_migration(args.script, dry_run=False)
        if success:
            print(f"✓ Successfully migrated {args.script}")
            return 0
        else:
            print(f"✗ Failed to migrate {args.script}")
            return 1
    
    def _migrate_all_scripts(self, manager: LegacyDeprecationManager, args) -> int:
        """Migrate all scripts automatically"""
        if args.dry_run:
            print("DRY RUN: Would migrate all legacy scripts")
            for script_name, script_info in manager.legacy_scripts.items():
                print(f"  - {script_name} → pfr-scraper {script_info.cli_equivalent}")
            return 0
        
        print(f"Migrating {len(manager.legacy_scripts)} legacy scripts...")
        
        success_count = 0
        for script_name in manager.legacy_scripts:
            try:
                success = manager.execute_migration(script_name, dry_run=False)
                if success:
                    success_count += 1
                    print(f"✓ {script_name}")
                else:
                    print(f"✗ {script_name}")
            except Exception as e:
                print(f"✗ {script_name}: {e}")
        
        print(f"\nMigration complete: {success_count}/{len(manager.legacy_scripts)} successful")
        return 0 if success_count == len(manager.legacy_scripts) else 1
    
    def _interactive_migration(self, manager: LegacyDeprecationManager, args) -> int:
        """Interactive migration assistant"""
        print("\n" + "="*60)
        print("LEGACY SCRIPT MIGRATION ASSISTANT")
        print("="*60)
        
        if not manager.legacy_scripts:
            print("No legacy scripts found to migrate.")
            return 0
        
        print(f"Found {len(manager.legacy_scripts)} legacy scripts to migrate:")
        print()
        
        for i, (script_name, script_info) in enumerate(manager.legacy_scripts.items(), 1):
            print(f"{i}. {script_name}")
            print(f"   CLI: pfr-scraper {script_info.cli_equivalent}")
            print(f"   Notes: {script_info.migration_notes}")
            print()
        
        print("Migration Options:")
        print("  1. Migrate all scripts")
        print("  2. Migrate specific script")
        print("  3. Show migration guide")
        print("  4. Exit")
        print()
        
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == '1':
                return self._migrate_all_scripts(manager, args)
            elif choice == '2':
                script_name = input("Enter script name: ").strip()
                if script_name in manager.legacy_scripts:
                    args.script = script_name
                    return self._migrate_single_script(manager, args)
                else:
                    print(f"Script '{script_name}' not found.")
                    return 1
            elif choice == '3':
                guide = manager.generate_migration_guide()
                print(guide)
                return 0
            elif choice == '4':
                print("Migration cancelled.")
                return 0
            else:
                print("Invalid choice.")
                return 1
        
        except KeyboardInterrupt:
            print("\nMigration cancelled.")
            return 0 