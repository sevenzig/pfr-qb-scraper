#!/usr/bin/env python3
"""
Simple Database Analysis Script
Directly connects to database to discover which fields exist and which are missing
"""

import sys
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connection():
    """Get a direct database connection"""
    try:
        # Get connection string from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not found")
            return None
        
        # Connect to database
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return None

def analyze_schema(conn):
    """Analyze the database schema"""
    
    print("🔍 Analyzing Database Schema...")
    print("=" * 60)
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            
            # Check if tables exist
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('qb_passing_stats', 'qb_splits', 'qb_splits_advanced')
                ORDER BY table_name;
            """)
            
            tables = cur.fetchall()
            print(f"Found {len(tables)} tables: {[t['table_name'] for t in tables]}")
            
            # Analyze qb_passing_stats table
            print("\n📊 QB Passing Stats Table Analysis:")
            print("-" * 40)
            
            cur.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'qb_passing_stats' 
                ORDER BY ordinal_position;
            """)
            
            columns = cur.fetchall()
            
            if columns:
                print(f"Found {len(columns)} columns in qb_passing_stats table:")
                for col in columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                    print(f"  • {col['column_name']}: {col['data_type']} {nullable}{default}")
                
                # Check for specific missing fields
                print("\n🔍 Checking for specific missing fields:")
                print("-" * 40)
                
                expected_fields = ['inc', 'cmp_pct', 'rush_first_downs']
                existing_columns = [col['column_name'] for col in columns]
                
                for field in expected_fields:
                    if field in existing_columns:
                        print(f"✅ {field}: EXISTS")
                    else:
                        print(f"❌ {field}: MISSING")
            else:
                print("❌ No columns found in qb_passing_stats table")
            
            # Analyze qb_splits table
            print("\n📊 QB Splits Table Analysis:")
            print("-" * 40)
            
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'qb_splits' 
                ORDER BY ordinal_position;
            """)
            
            splits_columns = cur.fetchall()
            
            if splits_columns:
                print(f"Found {len(splits_columns)} columns in qb_splits table:")
                for col in splits_columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    print(f"  • {col['column_name']}: {col['data_type']} {nullable}")
            else:
                print("❌ No columns found in qb_splits table")
            
            # Analyze qb_splits_advanced table
            print("\n📊 QB Splits Advanced Table Analysis:")
            print("-" * 40)
            
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'qb_splits_advanced' 
                ORDER BY ordinal_position;
            """)
            
            advanced_columns = cur.fetchall()
            
            if advanced_columns:
                print(f"Found {len(advanced_columns)} columns in qb_splits_advanced table:")
                for col in advanced_columns:
                    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                    print(f"  • {col['column_name']}: {col['data_type']} {nullable}")
            else:
                print("❌ No columns found in qb_splits_advanced table")
        
        return True
        
    except Exception as e:
        print(f"❌ Error analyzing schema: {e}")
        return False

def analyze_sample_data(conn):
    """Analyze sample data"""
    
    print("\n📈 Sample Data Analysis:")
    print("=" * 60)
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            
            # Get sample data from qb_passing_stats
            cur.execute("SELECT * FROM qb_passing_stats LIMIT 3;")
            sample_results = cur.fetchall()
            
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
            cur.execute("""
                SELECT * FROM qb_splits_advanced 
                WHERE rush_first_downs IS NOT NULL
                LIMIT 3;
            """)
            
            splits_sample_results = cur.fetchall()
            
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
        return False

def check_data_quality(conn):
    """Check data quality"""
    
    print("\n🔍 Data Quality Analysis:")
    print("=" * 60)
    
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            
            # Check for NULL values in key fields
            cur.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(cmp) as cmp_not_null,
                    COUNT(att) as att_not_null,
                    COUNT(inc) as inc_not_null,
                    COUNT(cmp_pct) as cmp_pct_not_null
                FROM qb_passing_stats;
            """)
            
            null_results = cur.fetchone()
            
            if null_results:
                print("NULL Value Analysis for qb_passing_stats:")
                print(f"  Total Records: {null_results['total_records']}")
                print(f"  Completions (cmp): {null_results['cmp_not_null']} populated, {null_results['total_records'] - null_results['cmp_not_null']} NULL")
                print(f"  Attempts (att): {null_results['att_not_null']} populated, {null_results['total_records'] - null_results['att_not_null']} NULL")
                print(f"  Incompletions (inc): {null_results['inc_not_null']} populated, {null_results['total_records'] - null_results['inc_not_null']} NULL")
                print(f"  Completion % (cmp_pct): {null_results['cmp_pct_not_null']} populated, {null_results['total_records'] - null_results['cmp_pct_not_null']} NULL")
            
            # Check for data consistency
            cur.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    COUNT(CASE WHEN inc = att - cmp THEN 1 END) as inc_correct,
                    COUNT(CASE WHEN inc != att - cmp THEN 1 END) as inc_incorrect
                FROM qb_passing_stats 
                WHERE att IS NOT NULL AND cmp IS NOT NULL AND inc IS NOT NULL;
            """)
            
            consistency_results = cur.fetchone()
            
            if consistency_results and consistency_results['total_records'] > 0:
                print(f"\nIncompletions Consistency Check:")
                print(f"  Total records with all fields: {consistency_results['total_records']}")
                print(f"  Correct calculations (inc = att - cmp): {consistency_results['inc_correct']}")
                print(f"  Incorrect calculations: {consistency_results['inc_incorrect']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking data quality: {e}")
        return False

def main():
    """Main analysis function"""
    
    print("🏈 NFL QB Database Field Analysis (Simple Version)")
    print("=" * 60)
    
    # Get database connection
    conn = get_database_connection()
    if not conn:
        print("❌ Could not establish database connection")
        sys.exit(1)
    
    try:
        success = True
        
        # Analyze schema
        if not analyze_schema(conn):
            success = False
        
        # Analyze sample data
        if not analyze_sample_data(conn):
            success = False
        
        # Check data quality
        if not check_data_quality(conn):
            success = False
        
        if success:
            print("\n✅ Database analysis completed successfully!")
        else:
            print("\n❌ Some analysis steps failed.")
            sys.exit(1)
            
    finally:
        conn.close()

if __name__ == "__main__":
    main() 