#!/usr/bin/env python3
"""
CLI command to fix split categories in the database
"""

import sys
import os
import logging
import argparse
from typing import Dict, Any, List
from argparse import ArgumentParser, Namespace
from datetime import datetime
from src.cli.base_command import BaseCommand
from src.database.db_manager import DatabaseManager
from src.utils.data_utils import logger

class FixSplitsCommand(BaseCommand):
    """Fix split categories for existing 'other' splits"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
    
    @property
    def name(self) -> str:
        return "fix-splits"
    
    @property
    def description(self) -> str:
        return "Fix categorization of existing 'other' splits"
    
    def add_arguments(self, parser):
        """Add command-specific arguments"""
        parser.add_argument(
            '--preview',
            action='store_true',
            help='Preview changes without applying them'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Skip confirmation prompt'
        )
    
    def create_split_mapping(self):
        """Create comprehensive mapping from values to proper split types"""
        
        # Define the comprehensive mapping
        split_mapping = {
            # Place splits
            'Home': 'place',
            'Road': 'place',
            
            # Result splits  
            'Win': 'result',
            'Loss': 'result',
            
            # Time splits
            'Early': 'time',
            'Late': 'time',
            'Afternoon': 'time',
            'Morning': 'time',
            
            # Day splits
            'Sunday': 'day',
            'Monday': 'day',
            'Thursday': 'day',
            'Saturday': 'day',
            'Wednesday': 'day',
            'Friday': 'day',
            
            # Month splits
            'September': 'month',
            'October': 'month', 
            'November': 'month',
            'December': 'month',
            'January': 'month',
            
            # Conference splits
            'AFC': 'conference',
            'NFC': 'conference',
            
            # Division splits
            'AFC North': 'division',
            'AFC South': 'division',
            'AFC East': 'division',
            'AFC West': 'division',
            'NFC North': 'division',
            'NFC South': 'division',
            'NFC East': 'division',
            'NFC West': 'division',
            
            # Score differential splits
            '0-7 points': 'score_differential',
            '5-8': 'score_differential',
            '8-14 points': 'score_differential',
            '9-12': 'score_differential',
            '13+': 'score_differential',
            '15+ points': 'score_differential',
            'Leading': 'score_differential',
            'Tied': 'score_differential',
            'Trailing': 'score_differential',
            'Leading, < 2 min to go': 'score_differential',
            'Leading, < 4 min to go': 'score_differential',
            'Tied, < 2 min to go': 'score_differential',
            'Tied, < 4 min to go': 'score_differential',
            'Trailing, < 2 min to go': 'score_differential',
            'Trailing, < 4 min to go': 'score_differential',
            
            # Field position splits
            '1-4': 'field_position',
            'Own 1-10': 'field_position',
            'Own 1-20': 'field_position',
            'Own 21-50': 'field_position',
            'Opp 1-10': 'field_position',
            'Opp 49-20': 'field_position',
            'Red Zone': 'field_position',
            
            # Stadium type splits
            'outdoors': 'stadium_type',
            'retroof': 'stadium_type',
            'dome': 'stadium_type',
            
            # Game situation splits
            'Starter': 'game_situation',
            'Total': 'game_situation',
            
            # League splits
            'NFL': 'league',
            
            # Team/opponent splits
            'Denver Broncos': 'opponent',
            'Dallas Cowboys': 'opponent',
            'New England Patriots': 'opponent',
            'Washington Commanders': 'opponent',
            'Houston Texans': 'opponent',
            'Cleveland Browns': 'opponent',
            'Baltimore Ravens': 'opponent',
            'San Francisco 49ers': 'opponent',
            'New York Jets': 'opponent',
            'New York Giants': 'opponent',
            'Carolina Panthers': 'opponent',
            'Chicago Bears': 'opponent',
            'Los Angeles Chargers': 'opponent',
            'Jacksonville Jaguars': 'opponent',
            'Philadelphia Eagles': 'opponent',
            'Kansas City Chiefs': 'opponent',
            'Cincinnati Bengals': 'opponent',
            'New Orleans Saints': 'opponent',
            'Buffalo Bills': 'opponent',
            'Indianapolis Colts': 'opponent',
            'Atlanta Falcons': 'opponent',
            'Tampa Bay Buccaneers': 'opponent',
            'Seattle Seahawks': 'opponent',
            'Los Angeles Rams': 'opponent',
            'Miami Dolphins': 'opponent',
            'Pittsburgh Steelers': 'opponent',
            'Tennessee Titans': 'opponent',
            'Detroit Lions': 'opponent',
            'Minnesota Vikings': 'opponent',
            'Arizona Cardinals': 'opponent',
            'Green Bay Packers': 'opponent',
            'Las Vegas Raiders': 'opponent',
            
            # Playoff type splits
            'Wild Card': 'playoff_type',
            'Divisional': 'playoff_type',
            'Conference Championship': 'playoff_type',
            'Super Bowl': 'playoff_type',
            
            # Snap type splits
            'Huddle': 'snap_type',
            'No Huddle': 'snap_type',
            'Shotgun': 'snap_type',
            'Under Center': 'snap_type',
            
            # Down splits
            '1st': 'down',
            '2nd': 'down',
            '3rd': 'down',
            '4th': 'down',
            '1st & 10': 'down',
            '1st & >10': 'down',
            '1st & <10': 'down',
            '2nd & 1-3': 'down',
            '2nd & 4-6': 'down',
            '2nd & 7-9': 'down',
            '2nd & 10+': 'down',
            '3rd & 1-3': 'down',
            '3rd & 4-6': 'down',
            '3rd & 7-9': 'down',
            '3rd & 10+': 'down',
            '4th & 1-3': 'down',
            '4th & 4-6': 'down',
            '4th & 10+': 'down',
            
            # Yards to go splits
            '1-3': 'yards_to_go',
            '4-6': 'yards_to_go',
            '7-9': 'yards_to_go',
            '10+': 'yards_to_go',
            
            # Quarter splits
            '1st Qtr': 'quarter',
            '2nd Qtr': 'quarter',
            '3rd Qtr': 'quarter',
            '4th Qtr': 'quarter',
            'OT': 'quarter',
            
            # Half splits
            '1st Half': 'half',
            '2nd Half': 'half',
            
            # Play action splits
            'play action': 'play_action',
            'non-play action': 'play_action',
            
            # RPO splits
            'rpo': 'run_pass_option',
            'non-rpo': 'run_pass_option',
            
            # Time in pocket splits
            '2.5+ seconds': 'time_in_pocket',
            '< 2.5 seconds': 'time_in_pocket',
        }
        
        return split_mapping
    
    def preview_changes(self, args):
        """Preview what changes would be made"""
        
        split_mapping = self.create_split_mapping()
        
        print("=== Preview of Split Category Changes ===")
        print("(This is a preview - no changes will be made)")
        
        total_to_update = 0
        for value, new_split_type in split_mapping.items():
            # Count records that would be updated
            result = self.db_manager.query("""
                SELECT COUNT(*) 
                FROM qb_splits 
                WHERE split = 'other' AND value = %s
            """, (value,))
            
            count = result[0]['count'] if result else 0
            if count > 0:
                print(f"  '{value}' -> '{new_split_type}': {count} records")
                total_to_update += count
        
        print(f"\nTotal records that would be updated: {total_to_update}")
        
        # Show current distribution
        print(f"\n=== Current Split Distribution ===")
        result = self.db_manager.query("""
            SELECT split, COUNT(*) as count 
            FROM qb_splits 
            GROUP BY split 
            ORDER BY count DESC
        """)
        
        for row in result:
            print(f"  - {row['split']}: {row['count']} records")
    
    def fix_splits(self, args):
        """Fix the split categories"""
        
        split_mapping = self.create_split_mapping()
        
        print("=== Fixing Split Categories ===")
        print(f"Mapping {len(split_mapping)} value types to proper split categories")
        
        # Get current stats
        result = self.db_manager.query("SELECT COUNT(*) as count FROM qb_splits WHERE split = 'other'")
        total_other = result[0]['count'] if result else 0
        print(f"Total 'other' splits to process: {total_other}")
        
        if total_other == 0:
            print("✅ No 'other' splits found - all splits are already properly categorized!")
            return
        
        # Process each mapping
        updated_count = 0
        for value, new_split_type in split_mapping.items():
            # Update records for this value
            result = self.db_manager.execute("""
                UPDATE qb_splits 
                SET split = %s, updated_at = %s
                WHERE split = 'other' AND value = %s
            """, (new_split_type, datetime.now(), value))
            
            if result > 0:
                print(f"  ✓ Updated {result} records: '{value}' -> '{new_split_type}'")
                updated_count += result
        
        print(f"\n=== Update Summary ===")
        print(f"Total records updated: {updated_count}")
        print(f"Records remaining as 'other': {total_other - updated_count}")
        
        # Show new split distribution
        print(f"\n=== New Split Distribution ===")
        result = self.db_manager.query("""
            SELECT split, COUNT(*) as count 
            FROM qb_splits 
            GROUP BY split 
            ORDER BY count DESC
        """)
        
        for row in result:
            print(f"  - {row['split']}: {row['count']} records")
        
        # Show any remaining "other" values
        if total_other - updated_count > 0:
            print(f"\n=== Remaining 'other' values ===")
            result = self.db_manager.query("""
                SELECT value, COUNT(*) as count 
                FROM qb_splits 
                WHERE split = 'other' 
                GROUP BY value 
                ORDER BY count DESC
            """)
            
            for row in result:
                print(f"  - {row['value']}: {row['count']} records")
    
    def run(self, args):
        """Execute the command"""
        
        try:
            if args.preview:
                self.preview_changes(args)
            else:
                if not args.force:
                    print("This command will update the split categories for existing 'other' splits.")
                    print("This will change the 'split' field from 'other' to proper categories.")
                    response = input("Do you want to proceed? (y/N): ")
                    
                    if response.lower() not in ['y', 'yes']:
                        print("Operation cancelled. Use --preview to see what would be changed.")
                        return 0
                
                self.fix_splits(args)
                print("\n✅ Split categorization fix completed successfully!")
            
            return 0
                
        except Exception as e:
            logger.error(f"Error fixing split categories: {e}")
            return 1 