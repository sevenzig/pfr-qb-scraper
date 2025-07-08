#!/usr/bin/env python3
"""
Script to reset the database and apply the new schema
This will drop all existing tables and recreate them with the new PFR ID-based schema
"""

import sys
import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config.config import config

def setup_logging():
    """Setup logging configuration"""
    os.makedirs('logs', exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/reset_database.log'),
            logging.StreamHandler()
        ]
    )

def reset_database():
    """Reset the database and apply new schema"""
    logger = logging.getLogger(__name__)
    
    print("🔄 Resetting database and applying new schema...")
    print("=" * 60)
    
    # Get database connection string
    db_url = config.get_database_url()
    
    try:
        # Connect to database
        conn = psycopg2.connect(db_url)
        conn.autocommit = True  # Enable autocommit for DDL operations
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✓ Connected to database")
        
        # Step 1: Drop all existing tables and types
        print("\n🗑️  Dropping existing tables and types...")
        
        drop_queries = [
            "DROP TABLE IF EXISTS qb_splits CASCADE",
            "DROP TABLE IF EXISTS qb_advanced_stats CASCADE", 
            "DROP TABLE IF EXISTS qb_basic_stats CASCADE",
            "DROP TABLE IF EXISTS players CASCADE",
            "DROP TABLE IF EXISTS teams CASCADE",
            "DROP TABLE IF EXISTS scraping_logs CASCADE",
            "DROP TABLE IF EXISTS scraping_log CASCADE",
            "DROP TABLE IF EXISTS qb_stats CASCADE",
            "DROP TYPE IF EXISTS game_result CASCADE",
            "DROP TYPE IF EXISTS split_type CASCADE",
            "DROP TYPE IF EXISTS split_category CASCADE"
        ]
        
        for query in drop_queries:
            try:
                cur.execute(query)
                print(f"  ✓ {query}")
            except Exception as e:
                print(f"  ⚠️  {query}: {e}")
        
        print("✓ All existing tables and types dropped")
        
        # Step 2: Apply new schema
        print("\n📋 Applying new schema...")
        
        schema_file = "sql/schema.sql"
        try:
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            # Split the schema into individual statements
            statements = schema_sql.split(';')
            
            for statement in statements:
                statement = statement.strip()
                if statement and not statement.startswith('--'):
                    try:
                        cur.execute(statement)
                        print(f"  ✓ Executed: {statement[:50]}...")
                    except Exception as e:
                        print(f"  ⚠️  Error executing: {statement[:50]}... - {e}")
            
            print("✓ New schema applied successfully")
            
        except FileNotFoundError:
            print(f"❌ Schema file not found: {schema_file}")
            return False
        except Exception as e:
            print(f"❌ Error applying schema: {e}")
            return False
        
        # Step 3: Verify tables were created
        print("\n🔍 Verifying new tables...")
        
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('players', 'qb_basic_stats', 'qb_advanced_stats', 'qb_splits', 'scraping_logs')
            ORDER BY table_name
        """)
        
        tables = [row['table_name'] for row in cur.fetchall()]
        expected_tables = ['players', 'qb_basic_stats', 'qb_advanced_stats', 'qb_splits', 'scraping_logs']
        
        if set(tables) == set(expected_tables):
            print("✓ All expected tables created:")
            for table in tables:
                print(f"  - {table}")
        else:
            missing = set(expected_tables) - set(tables)
            extra = set(tables) - set(expected_tables)
            print(f"⚠️  Table mismatch:")
            if missing:
                print(f"  Missing: {missing}")
            if extra:
                print(f"  Extra: {extra}")
        
        # Step 4: Show table structures
        print("\n📊 Table structures:")
        for table in tables:
            cur.execute(f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table}' 
                ORDER BY ordinal_position
            """)
            
            columns = cur.fetchall()
            print(f"\n{table}:")
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"  {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        print(f"\n🎉 Database reset and new schema applied successfully!")
        print("You can now run the scraping scripts.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting database: {e}")
        logger.error(f"Database reset failed: {e}")
        return False
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

def main():
    """Main function"""
    setup_logging()
    
    print("⚠️  WARNING: This will delete ALL existing data in the database!")
    print("Make sure you have backups if needed.")
    
    response = input("\nDo you want to continue? (y/N): ")
    if response.lower() != 'y':
        print("Database reset cancelled.")
        return
    
    success = reset_database()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 