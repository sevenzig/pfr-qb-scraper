#!/usr/bin/env python3
"""
Legacy Deprecation System for NFL QB Data Scraping System
Handles transition from old scripts to new CLI architecture
"""

import sys
import os
import logging
import warnings
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from pathlib import Path
import json
import subprocess
import importlib.util

logger = logging.getLogger(__name__)


@dataclass
class LegacyScript:
    """Information about a legacy script"""
    name: str
    path: Path
    cli_equivalent: str
    deprecated_since: datetime
    removal_date: datetime
    migration_notes: str
    usage_count: int = 0
    last_used: Optional[datetime] = None


@dataclass
class DeprecationWarning:
    """Deprecation warning information"""
    script_name: str
    warning_type: str  # 'deprecated', 'removal_soon', 'removed'
    message: str
    timestamp: datetime
    cli_alternative: str
    migration_guide: str


class LegacyDeprecationManager:
    """Manages legacy script deprecation and migration"""
    
    def __init__(self):
        """Initialize deprecation manager"""
        self.project_root = Path(__file__).parent.parent.parent
        self.scripts_dir = self.project_root / "scripts"
        self.legacy_dir = self.project_root / "legacy"
        
        # Deprecation timeline
        self.deprecation_timeline = {
            'phase_1': datetime(2024, 1, 1),  # Initial deprecation warnings
            'phase_2': datetime(2024, 4, 1),  # Enhanced warnings
            'phase_3': datetime(2024, 7, 1),  # Removal warnings
            'phase_4': datetime(2024, 10, 1)  # Complete removal
        }
        
        # Create legacy directory if it doesn't exist
        self.legacy_dir.mkdir(exist_ok=True)
        
        # Legacy script registry
        self.legacy_scripts = self._build_legacy_registry()
    
    def _build_legacy_registry(self) -> Dict[str, LegacyScript]:
        """Build registry of legacy scripts"""
        registry = {}
        
        # Define legacy scripts and their CLI equivalents
        legacy_definitions = [
            {
                'name': 'enhanced_qb_scraper.py',
                'cli_equivalent': 'scrape --enhanced',
                'migration_notes': 'Use "pfr-scraper scrape --enhanced --season <year>" instead'
            },
            {
                'name': 'robust_qb_scraper.py',
                'cli_equivalent': 'scrape --robust',
                'migration_notes': 'Use "pfr-scraper scrape --robust --season <year>" instead'
            },
            {
                'name': 'simple_scrape.py',
                'cli_equivalent': 'scrape --simple',
                'migration_notes': 'Use "pfr-scraper scrape --simple --season <year>" instead'
            },
            {
                'name': 'scrape_qb_data_2024.py',
                'cli_equivalent': 'scrape --season 2024',
                'migration_notes': 'Use "pfr-scraper scrape --season 2024" instead'
            },
            {
                'name': 'clear_qb_data.py',
                'cli_equivalent': 'data --clear',
                'migration_notes': 'Use "pfr-scraper data --clear" instead'
            },
            {
                'name': 'populate_teams.py',
                'cli_equivalent': 'setup --populate-teams',
                'migration_notes': 'Use "pfr-scraper setup --populate-teams" instead'
            },
            {
                'name': 'update_qb_stats_team_codes.py',
                'cli_equivalent': 'data --update-team-codes',
                'migration_notes': 'Use "pfr-scraper data --update-team-codes" instead'
            },
            {
                'name': 'update_teams_to_pfr_codes.py',
                'cli_equivalent': 'setup --update-team-codes',
                'migration_notes': 'Use "pfr-scraper setup --update-team-codes" instead'
            }
        ]
        
        for definition in legacy_definitions:
            script_path = self.scripts_dir / definition['name']
            if script_path.exists():
                registry[definition['name']] = LegacyScript(
                    name=definition['name'],
                    path=script_path,
                    cli_equivalent=definition['cli_equivalent'],
                    deprecated_since=self.deprecation_timeline['phase_1'],
                    removal_date=self.deprecation_timeline['phase_4'],
                    migration_notes=definition['migration_notes']
                )
        
        return registry
    
    def add_deprecation_warnings(self):
        """Add deprecation warnings to all legacy scripts"""
        logger.info("Adding deprecation warnings to legacy scripts")
        
        for script_name, script_info in self.legacy_scripts.items():
            self._add_script_deprecation_warning(script_info)
    
    def _add_script_deprecation_warning(self, script_info: LegacyScript):
        """Add deprecation warning to a specific script"""
        try:
            with open(script_info.path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if deprecation warning already exists
            if 'DEPRECATED' in content or 'deprecated' in content:
                logger.info(f"Deprecation warning already exists in {script_info.name}")
                return
            
            # Create deprecation warning
            warning = self._generate_deprecation_warning(script_info)
            
            # Add warning at the top of the file
            new_content = warning + "\n\n" + content
            
            # Create backup
            backup_path = self.legacy_dir / f"{script_info.name}.backup"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Write updated content
            with open(script_info.path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Added deprecation warning to {script_info.name}")
            
        except Exception as e:
            logger.error(f"Failed to add deprecation warning to {script_info.name}: {e}")
    
    def _generate_deprecation_warning(self, script_info: LegacyScript) -> str:
        """Generate deprecation warning text"""
        days_until_removal = (script_info.removal_date - datetime.now()).days
        
        warning = f'''#!/usr/bin/env python3
"""
DEPRECATED: This script is deprecated and will be removed on {script_info.removal_date.strftime('%Y-%m-%d')}

MIGRATION: {script_info.migration_notes}

CLI EQUIVALENT: pfr-scraper {script_info.cli_equivalent}

This script will be removed in {days_until_removal} days.
Please migrate to the new CLI interface as soon as possible.

For migration help, run: pfr-scraper help migrate
"""

import warnings
import sys

# Show deprecation warning
warnings.warn(
    f"This script is deprecated. Use 'pfr-scraper {script_info.cli_equivalent}' instead. "
    f"Removal date: {script_info.removal_date.strftime('%Y-%m-%d')}",
    DeprecationWarning,
    stacklevel=2
)

# Print deprecation notice
print("="*80)
print("DEPRECATION NOTICE")
print("="*80)
print(f"This script ({script_info.name}) is deprecated and will be removed on {script_info.removal_date.strftime('%Y-%m-%d')}")
print(f"CLI Alternative: pfr-scraper {script_info.cli_equivalent}")
print(f"Migration: {script_info.migration_notes}")
print("="*80)
print()

# Continue with original script execution
'''
        return warning
    
    def create_redirect_scripts(self):
        """Create redirect scripts that point to CLI commands"""
        logger.info("Creating redirect scripts for legacy compatibility")
        
        for script_name, script_info in self.legacy_scripts.items():
            self._create_redirect_script(script_info)
    
    def _create_redirect_script(self, script_info: LegacyScript):
        """Create a redirect script for a legacy script"""
        try:
            # Parse CLI command and arguments
            cli_parts = script_info.cli_equivalent.split()
            command = cli_parts[0]
            args = cli_parts[1:] if len(cli_parts) > 1 else []
            
            # Create redirect script content
            redirect_content = f'''#!/usr/bin/env python3
"""
Redirect script for {script_info.name}
Automatically redirects to CLI equivalent
"""

import sys
import subprocess
import os

def main():
    """Redirect to CLI equivalent"""
    # Get the CLI command
    cli_command = ["python", "-m", "src.cli.cli_main"] + {args}
    
    # Add any additional arguments passed to this script
    if len(sys.argv) > 1:
        cli_command.extend(sys.argv[1:])
    
    # Execute the CLI command
    try:
        result = subprocess.run(cli_command, check=True)
        sys.exit(result.returncode)
    except subprocess.CalledProcessError as e:
        print(f"Error executing CLI command: {{e}}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("Error: CLI module not found. Please ensure the project is properly installed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
            
            # Write redirect script
            redirect_path = self.legacy_dir / f"redirect_{script_info.name}"
            with open(redirect_path, 'w', encoding='utf-8') as f:
                f.write(redirect_content)
            
            # Make it executable
            redirect_path.chmod(0o755)
            
            logger.info(f"Created redirect script: {redirect_path}")
            
        except Exception as e:
            logger.error(f"Failed to create redirect script for {script_info.name}: {e}")
    
    def generate_migration_guide(self) -> str:
        """Generate comprehensive migration guide"""
        guide = f"""
# Legacy Script Migration Guide

## Overview
This guide helps you migrate from the old script-based system to the new CLI architecture.

## Migration Timeline
- **Phase 1 (Jan 2024)**: Initial deprecation warnings
- **Phase 2 (Apr 2024)**: Enhanced warnings
- **Phase 3 (Jul 2024)**: Removal warnings
- **Phase 4 (Oct 2024)**: Complete removal

## Script Migration Table

| Legacy Script | CLI Equivalent | Migration Notes |
|---------------|----------------|-----------------|
"""
        
        for script_name, script_info in self.legacy_scripts.items():
            guide += f"| `{script_name}` | `pfr-scraper {script_info.cli_equivalent}` | {script_info.migration_notes} |\n"
        
        guide += """
## Migration Steps

### 1. Install the New CLI
```bash
# Ensure you have the latest version
pip install -e .
```

### 2. Test CLI Commands
```bash
# Test the CLI help
pfr-scraper --help

# Test specific commands
pfr-scraper scrape --help
pfr-scraper data --help
pfr-scraper setup --help
```

### 3. Update Your Workflows
Replace script calls with CLI commands:

**Before:**
```bash
python scripts/enhanced_qb_scraper.py --season 2024
```

**After:**
```bash
pfr-scraper scrape --enhanced --season 2024
```

### 4. Update Automation Scripts
Update any automation or CI/CD scripts to use the new CLI commands.

## Benefits of Migration

1. **Better Error Handling**: Comprehensive error messages and recovery
2. **Progress Tracking**: Real-time progress updates for long operations
3. **Validation**: Built-in data validation and quality checks
4. **Batch Operations**: Efficient batch processing capabilities
5. **Monitoring**: Performance monitoring and health checks
6. **Configuration**: Centralized configuration management

## Getting Help

- Run `pfr-scraper --help` for general help
- Run `pfr-scraper <command> --help` for command-specific help
- Check the main README.md for detailed documentation
- Review the migration documentation in `docs/migration/`

## Support

If you encounter issues during migration:
1. Check the error messages for guidance
2. Review the CLI help documentation
3. Test with a small dataset first
4. Contact the development team if needed

## Legacy Script Status

"""
        
        current_date = datetime.now()
        for script_name, script_info in self.legacy_scripts.items():
            days_until_removal = (script_info.removal_date - current_date).days
            status = "REMOVED" if days_until_removal < 0 else f"DEPRECATED ({days_until_removal} days until removal)"
            
            guide += f"- **{script_name}**: {status}\n"
        
        return guide
    
    def check_usage_patterns(self) -> Dict[str, Any]:
        """Check for usage patterns of legacy scripts"""
        logger.info("Checking legacy script usage patterns")
        
        usage_data = {
            'total_scripts': len(self.legacy_scripts),
            'scripts_with_usage': 0,
            'total_usage_count': 0,
            'most_used_scripts': [],
            'recent_usage': []
        }
        
        # This would typically check logs, git history, or other usage tracking
        # For now, we'll provide a template for usage analysis
        
        for script_name, script_info in self.legacy_scripts.items():
            # Simulate usage data (in real implementation, this would come from actual tracking)
            script_info.usage_count = 0  # Would be populated from actual data
            script_info.last_used = None  # Would be populated from actual data
            
            if script_info.usage_count > 0:
                usage_data['scripts_with_usage'] += 1
                usage_data['total_usage_count'] += script_info.usage_count
        
        # Sort by usage count
        usage_data['most_used_scripts'] = sorted(
            self.legacy_scripts.values(),
            key=lambda x: x.usage_count,
            reverse=True
        )[:5]
        
        return usage_data
    
    def create_removal_plan(self) -> Dict[str, Any]:
        """Create a plan for removing legacy scripts"""
        logger.info("Creating legacy script removal plan")
        
        current_date = datetime.now()
        removal_plan = {
            'immediate_removal': [],
            'scheduled_removal': [],
            'keep_for_compatibility': [],
            'migration_required': []
        }
        
        for script_name, script_info in self.legacy_scripts.items():
            days_until_removal = (script_info.removal_date - current_date).days
            
            if days_until_removal < 0:
                removal_plan['immediate_removal'].append(script_info)
            elif days_until_removal < 30:
                removal_plan['scheduled_removal'].append(script_info)
            elif script_info.usage_count > 0:
                removal_plan['migration_required'].append(script_info)
            else:
                removal_plan['keep_for_compatibility'].append(script_info)
        
        return removal_plan
    
    def execute_migration(self, script_name: str, dry_run: bool = True) -> bool:
        """Execute migration for a specific script"""
        if script_name not in self.legacy_scripts:
            logger.error(f"Script {script_name} not found in legacy registry")
            return False
        
        script_info = self.legacy_scripts[script_name]
        
        if dry_run:
            logger.info(f"DRY RUN: Would migrate {script_name} to CLI equivalent")
            logger.info(f"  CLI Command: pfr-scraper {script_info.cli_equivalent}")
            logger.info(f"  Migration Notes: {script_info.migration_notes}")
            return True
        
        try:
            # Create backup
            backup_path = self.legacy_dir / f"{script_name}.migrated_backup"
            with open(script_info.path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Create redirect script
            self._create_redirect_script(script_info)
            
            # Move original to legacy directory
            legacy_path = self.legacy_dir / script_name
            script_info.path.rename(legacy_path)
            
            logger.info(f"Successfully migrated {script_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to migrate {script_name}: {e}")
            return False
    
    def generate_usage_report(self) -> str:
        """Generate a usage report for legacy scripts"""
        usage_data = self.check_usage_patterns()
        removal_plan = self.create_removal_plan()
        
        report = f"""
# Legacy Script Usage Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Total Legacy Scripts: {usage_data['total_scripts']}
- Scripts with Usage: {usage_data['scripts_with_usage']}
- Total Usage Count: {usage_data['total_usage_count']}

## Most Used Scripts
"""
        
        for script in usage_data['most_used_scripts']:
            report += f"- {script.name}: {script.usage_count} uses\n"
        
        report += """
## Removal Plan
"""
        
        if removal_plan['immediate_removal']:
            report += "\n### Immediate Removal (Past Due)\n"
            for script in removal_plan['immediate_removal']:
                report += f"- {script.name}\n"
        
        if removal_plan['scheduled_removal']:
            report += "\n### Scheduled Removal (Next 30 Days)\n"
            for script in removal_plan['scheduled_removal']:
                days = (script.removal_date - datetime.now()).days
                report += f"- {script.name} ({days} days)\n"
        
        if removal_plan['migration_required']:
            report += "\n### Migration Required\n"
            for script in removal_plan['migration_required']:
                report += f"- {script.name} (used {script.usage_count} times)\n"
        
        return report 