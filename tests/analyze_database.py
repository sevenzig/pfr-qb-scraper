#!/usr/bin/env python3
"""
Database Analysis Script
Discovers which fields exist and which are missing in the NFL QB database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.database.db_manager import DatabaseManager
from src.config.config import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_database_schema():
    """Analyze the database schema to discover existing fields"""
    
    print("🔍 Analyzing Database Schema...")
    print("=" * 60)
    
    try:
        # Create database manager
        db_manager = DatabaseManager()
        
        # Test connection
        if not db_manager.test_connection():
            print("❌ Failed to connect to database")
            return False
        
        print("✅ Database connection successful")
        
        # Analyze qb_passing_stats table
        print("\n📊 QB Passing Stats Table Analysis:")
        print("-" * 40)
        
        # Get table schema
        schema_query = """
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns 
        WHERE table_name = 'qb_passing_stats' 
        ORDER BY ordinal_position;
        """
        
        schema_results = db_manager.query(schema_query)
        
        if not schema_results:
            print("❌ No schema information found for qb_passing_stats table")
            return False
        
        print(f"Found {len(schema_results)} columns in qb_passing_stats table:")
        for col in schema_results:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            print(f"  • {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        # Check for specific missing fields
        print("\n🔍 Checking for specific missing fields:")
        print("-" * 40)
        
        expected_fields = [
            'inc', 'cmp_pct', 'rush_first_downs'
        ]
        
        existing_columns = [col['column_name'] for col in schema_results]
        
        for field in expected_fields:
            if field in existing_columns:
                print(f"✅ {field}: EXISTS")
            else:
                print(f"❌ {field}: MISSING")
        
        # Analyze qb_splits table
        print("\n📊 QB Splits Table Analysis:")
        print("-" * 40)
        
        splits_schema_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'qb_splits' 
        ORDER BY ordinal_position;
        """
        
        splits_schema_results = db_manager.query(splits_schema_query)
        
        if splits_schema_results:
            print(f"Found {len(splits_schema_results)} columns in qb_splits table:")
            for col in splits_schema_results:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"  • {col['column_name']}: {col['data_type']} {nullable}")
        else:
            print("❌ No schema information found for qb_splits table")
        
        # Analyze qb_splits_advanced table
        print("\n📊 QB Splits Advanced Table Analysis:")
        print("-" * 40)
        
        advanced_schema_query = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns 
        WHERE table_name = 'qb_splits_advanced' 
        ORDER BY ordinal_position;
        """
        
        advanced_schema_results = db_manager.query(advanced_schema_query)
        
        if advanced_schema_results:
            print(f"Found {len(advanced_schema_results)} columns in qb_splits_advanced table:")
            for col in advanced_schema_results:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                print(f"  • {col['column_name']}: {col['data_type']} {nullable}")
        else:
            print("❌ No schema information found for qb_splits_advanced table")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing database schema: {e}")
        logger.exception("Database analysis failed")
        return False

def analyze_sample_data():
    """Analyze sample data to see which fields are populated"""
    
    print("\n📈 Sample Data Analysis:")
    print("=" * 60)
    
    try:
        db_manager = DatabaseManager()
        
        # Get sample data from qb_passing_stats
        sample_query = """
        SELECT * FROM qb_passing_stats 
        LIMIT 3;
        """
        
        sample_results = db_manager.query(sample_query)
        
        if sample_results:
            print(f"Found {len(sample_results)} sample records in qb_passing_stats:")
            
            for i, record in enumerate(sample_results, 1):
                print(f"\nRecord {i}:")
                print(f"  Player: {record.get('player_name', 'N/A')}")
                print(f"  Season: {record.get('season', 'N/A')}")
                print(f"  Completions: {record.get('cmp', 'N/A')}")
                print(f"  Attempts: {record.get('att', 'N/A')}")
                print(f"  Incompletions: {record.get('inc', 'N/A')}")
                print(f"  Completion %: {record.get('cmp_pct', 'N/A')}")
                print(f"  Rush First Downs: {record.get('rush_first_downs', 'N/A')}")
        else:
            print("❌ No sample data found in qb_passing_stats table")
        
        # Get sample data from qb_splits_advanced
        splits_sample_query = """
        SELECT * FROM qb_splits_advanced 
        WHERE rush_first_downs IS NOT NULL
        LIMIT 3;
        """
        
        splits_sample_results = db_manager.query(splits_sample_query)
        
        if splits_sample_results:
            print(f"\nFound {len(splits_sample_results)} sample records with rush_first_downs in qb_splits_advanced:")
            
            for i, record in enumerate(splits_sample_results, 1):
                print(f"\nSplits Record {i}:")
                print(f"  Player: {record.get('player_name', 'N/A')}")
                print(f"  Split: {record.get('split', 'N/A')}")
                print(f"  Value: {record.get('value', 'N/A')}")
                print(f"  Rush First Downs: {record.get('rush_first_downs', 'N/A')}")
        else:
            print("\n❌ No sample data with rush_first_downs found in qb_splits_advanced table")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing sample data: {e}")
        logger.exception("Sample data analysis failed")
        return False

def check_data_quality():
    """Check data quality and identify issues"""
    
    print("\n🔍 Data Quality Analysis:")
    print("=" * 60)
    
    try:
        db_manager = DatabaseManager()
        
        # Check for NULL values in key fields
        null_check_query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(cmp) as cmp_not_null,
            COUNT(att) as att_not_null,
            COUNT(inc) as inc_not_null,
            COUNT(cmp_pct) as cmp_pct_not_null,
            COUNT(rush_first_downs) as rush_first_downs_not_null
        FROM qb_passing_stats;
        """
        
        null_results = db_manager.query(null_check_query)
        
        if null_results:
            result = null_results[0]
            print("NULL Value Analysis for qb_passing_stats:")
            print(f"  Total Records: {result['total_records']}")
            print(f"  Completions (cmp): {result['cmp_not_null']} populated, {result['total_records'] - result['cmp_not_null']} NULL")
            print(f"  Attempts (att): {result['att_not_null']} populated, {result['total_records'] - result['att_not_null']} NULL")
            print(f"  Incompletions (inc): {result['inc_not_null']} populated, {result['total_records'] - result['inc_not_null']} NULL")
            print(f"  Completion % (cmp_pct): {result['cmp_pct_not_null']} populated, {result['total_records'] - result['cmp_pct_not_null']} NULL")
            print(f"  Rush First Downs: {result['rush_first_downs_not_null']} populated, {result['total_records'] - result['rush_first_downs_not_null']} NULL")
        
        # Check for data consistency
        consistency_query = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(CASE WHEN inc = att - cmp THEN 1 END) as inc_correct,
            COUNT(CASE WHEN inc != att - cmp THEN 1 END) as inc_incorrect
        FROM qb_passing_stats 
        WHERE att IS NOT NULL AND cmp IS NOT NULL AND inc IS NOT NULL;
        """
        
        consistency_results = db_manager.query(consistency_query)
        
        if consistency_results:
            result = consistency_results[0]
            if result['total_records'] > 0:
                print(f"\nIncompletions Consistency Check:")
                print(f"  Total records with all fields: {result['total_records']}")
                print(f"  Correct calculations (inc = att - cmp): {result['inc_correct']}")
                print(f"  Incorrect calculations: {result['inc_incorrect']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking data quality: {e}")
        logger.exception("Data quality check failed")
        return False

def main():
    """Main analysis function"""
    
    print("🏈 NFL QB Database Field Analysis")
    print("=" * 60)
    
    success = True
    
    # Analyze schema
    if not analyze_database_schema():
        success = False
    
    # Analyze sample data
    if not analyze_sample_data():
        success = False
    
    # Check data quality
    if not check_data_quality():
        success = False
    
    if success:
        print("\n✅ Database analysis completed successfully!")
    else:
        print("\n❌ Some analysis steps failed.")
        sys.exit(1)

if __name__ == "__main__":
    main() 