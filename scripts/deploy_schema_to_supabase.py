#!/usr/bin/env python3
"""
Deploy Database Schema to Supabase

This script deploys the complete NFL QB data schema to your Supabase instance.
It includes connection testing, schema validation, and proper error handling.

Usage:
    python scripts/deploy_schema_to_supabase.py

Environment Variables Required:
    DATABASE_URL: Your Supabase PostgreSQL connection string
    SUPABASE_URL: Your Supabase project URL (optional, for validation)
    SUPABASE_ANON_KEY: Your Supabase anonymous key (optional, for validation)
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('schema_deployment.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SupabaseSchemaDeployer:
    """Handles deployment of database schema to Supabase"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')
        self.schema_file = Path('sql/schema.sql')
        
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable is required")
    
    def test_connection(self) -> bool:
        """Test connection to Supabase database"""
        try:
            logger.info("Testing database connection...")
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()
                logger.info(f"✅ Connected to PostgreSQL: {version[0]}")
                
                # Test if we can create tables
                cur.execute("SELECT current_database();")
                db_name = cur.fetchone()
                logger.info(f"✅ Connected to database: {db_name[0]}")
                
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False
    
    def validate_schema_file(self) -> bool:
        """Validate that the schema file exists and is readable"""
        if not self.schema_file.exists():
            logger.error(f"❌ Schema file not found: {self.schema_file}")
            return False
        
        try:
            with open(self.schema_file, 'r') as f:
                content = f.read()
                if len(content.strip()) == 0:
                    logger.error("❌ Schema file is empty")
                    return False
                
                # Basic validation - check for key table definitions
                required_tables = [
                    'CREATE TABLE.*players',
                    'CREATE TABLE.*teams', 
                    'CREATE TABLE.*qb_basic_stats',
                    'CREATE TABLE.*qb_advanced_stats',
                    'CREATE TABLE.*qb_splits'
                ]
                
                for table_pattern in required_tables:
                    if not re.search(table_pattern, content, re.IGNORECASE):
                        logger.warning(f"⚠️  Schema may be missing table: {table_pattern}")
                
                logger.info(f"✅ Schema file validated: {self.schema_file}")
                logger.info(f"✅ Schema size: {len(content)} characters")
                return True
                
        except Exception as e:
            logger.error(f"❌ Error reading schema file: {e}")
            return False
    
    def check_existing_tables(self) -> Dict[str, bool]:
        """Check which tables already exist in the database"""
        existing_tables = {}
        
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN (
                        'players', 'teams', 'qb_basic_stats', 'qb_advanced_stats', 
                        'qb_splits', 'qb_game_log', 'scraping_log'
                    )
                """)
                
                existing = [row[0] for row in cur.fetchall()]
                
                for table in ['players', 'teams', 'qb_basic_stats', 'qb_advanced_stats', 
                             'qb_splits', 'qb_game_log', 'scraping_log']:
                    existing_tables[table] = table in existing
                    
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Error checking existing tables: {e}")
            return {}
        
        return existing_tables
    
    def deploy_schema(self, force_recreate: bool = False) -> bool:
        """Deploy the schema to Supabase"""
        try:
            logger.info("🚀 Starting schema deployment...")
            
            # Read schema file
            with open(self.schema_file, 'r') as f:
                schema_sql = f.read()
            
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cur:
                # Check if we need to drop existing tables
                if force_recreate:
                    logger.info("🗑️  Dropping existing tables...")
                    drop_sql = """
                    DROP TABLE IF EXISTS scraping_log CASCADE;
                    DROP TABLE IF EXISTS qb_game_log CASCADE;
                    DROP TABLE IF EXISTS qb_splits CASCADE;
                    DROP TABLE IF EXISTS qb_advanced_stats CASCADE;
                    DROP TABLE IF EXISTS qb_basic_stats CASCADE;
                    DROP TABLE IF EXISTS players CASCADE;
                    DROP TABLE IF EXISTS teams CASCADE;
                    DROP TYPE IF EXISTS game_result CASCADE;
                    DROP TYPE IF EXISTS weather_condition CASCADE;
                    DROP TYPE IF EXISTS field_surface CASCADE;
                    """
                    cur.execute(drop_sql)
                    logger.info("✅ Existing tables dropped")
                
                # Execute schema
                logger.info("📝 Executing schema...")
                cur.execute(schema_sql)
                logger.info("✅ Schema executed successfully")
                
                # Verify tables were created
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN (
                        'players', 'teams', 'qb_basic_stats', 'qb_advanced_stats', 
                        'qb_splits', 'qb_game_log', 'scraping_log'
                    )
                    ORDER BY table_name
                """)
                
                created_tables = [row[0] for row in cur.fetchall()]
                logger.info(f"✅ Created tables: {', '.join(created_tables)}")
                
                # Check indexes
                cur.execute("""
                    SELECT indexname 
                    FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND tablename IN (
                        'players', 'teams', 'qb_basic_stats', 'qb_advanced_stats', 
                        'qb_splits', 'qb_game_log', 'scraping_log'
                    )
                    ORDER BY tablename, indexname
                """)
                
                indexes = [row[0] for row in cur.fetchall()]
                logger.info(f"✅ Created {len(indexes)} indexes")
                
                # Check views
                cur.execute("""
                    SELECT viewname 
                    FROM pg_views 
                    WHERE schemaname = 'public'
                    ORDER BY viewname
                """)
                
                views = [row[0] for row in cur.fetchall()]
                logger.info(f"✅ Created {len(views)} views: {', '.join(views)}")
                
                # Check functions
                cur.execute("""
                    SELECT proname 
                    FROM pg_proc p
                    JOIN pg_namespace n ON p.pronamespace = n.oid
                    WHERE n.nspname = 'public'
                    ORDER BY proname
                """)
                
                functions = [row[0] for row in cur.fetchall()]
                logger.info(f"✅ Created {len(functions)} functions: {', '.join(functions)}")
                
            conn.close()
            logger.info("🎉 Schema deployment completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Schema deployment failed: {e}")
            return False
    
    def verify_deployment(self) -> Dict[str, Any]:
        """Verify that the deployment was successful"""
        verification = {
            'tables_created': False,
            'indexes_created': False,
            'views_created': False,
            'functions_created': False,
            'rls_enabled': False
        }
        
        try:
            conn = psycopg2.connect(self.database_url)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            
            with conn.cursor() as cur:
                # Check tables
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN (
                        'players', 'teams', 'qb_basic_stats', 'qb_advanced_stats', 
                        'qb_splits', 'qb_game_log', 'scraping_log'
                    )
                """)
                table_count = cur.fetchone()[0]
                verification['tables_created'] = table_count == 7
                
                # Check indexes
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM pg_indexes 
                    WHERE schemaname = 'public' 
                    AND tablename IN (
                        'players', 'teams', 'qb_basic_stats', 'qb_advanced_stats', 
                        'qb_splits', 'qb_game_log', 'scraping_log'
                    )
                """)
                index_count = cur.fetchone()[0]
                verification['indexes_created'] = index_count > 0
                
                # Check views
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM pg_views 
                    WHERE schemaname = 'public'
                """)
                view_count = cur.fetchone()[0]
                verification['views_created'] = view_count > 0
                
                # Check functions
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM pg_proc p
                    JOIN pg_namespace n ON p.pronamespace = n.oid
                    WHERE n.nspname = 'public'
                """)
                function_count = cur.fetchone()[0]
                verification['functions_created'] = function_count > 0
                
                # Check RLS
                cur.execute("""
                    SELECT COUNT(*) 
                    FROM pg_tables 
                    WHERE schemaname = 'public' 
                    AND rowsecurity = true
                    AND tablename IN (
                        'players', 'teams', 'qb_basic_stats', 'qb_advanced_stats', 
                        'qb_splits', 'qb_game_log', 'scraping_log'
                    )
                """)
                rls_count = cur.fetchone()[0]
                verification['rls_enabled'] = rls_count == 7
                
            conn.close()
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
        
        return verification
    
    def run(self, force_recreate: bool = False) -> bool:
        """Run the complete deployment process"""
        logger.info("=" * 60)
        logger.info("🏗️  Supabase Schema Deployment")
        logger.info("=" * 60)
        
        # Step 1: Validate environment
        if not self.database_url:
            logger.error("❌ DATABASE_URL environment variable is required")
            return False
        
        # Step 2: Test connection
        if not self.test_connection():
            return False
        
        # Step 3: Validate schema file
        if not self.validate_schema_file():
            return False
        
        # Step 4: Check existing tables
        existing_tables = self.check_existing_tables()
        if existing_tables:
            logger.info("📋 Existing tables found:")
            for table, exists in existing_tables.items():
                status = "✅" if exists else "❌"
                logger.info(f"  {status} {table}")
            
            if any(existing_tables.values()) and not force_recreate:
                logger.warning("⚠️  Some tables already exist. Use --force to recreate them.")
                return False
        
        # Step 5: Deploy schema
        if not self.deploy_schema(force_recreate):
            return False
        
        # Step 6: Verify deployment
        logger.info("🔍 Verifying deployment...")
        verification = self.verify_deployment()
        
        logger.info("📊 Deployment Verification Results:")
        for check, result in verification.items():
            status = "✅" if result else "❌"
            logger.info(f"  {status} {check.replace('_', ' ').title()}")
        
        all_passed = all(verification.values())
        if all_passed:
            logger.info("🎉 All verification checks passed!")
        else:
            logger.warning("⚠️  Some verification checks failed")
        
        return all_passed

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Deploy schema to Supabase')
    parser.add_argument('--force', action='store_true', 
                       help='Force recreation of existing tables')
    parser.add_argument('--test-only', action='store_true',
                       help='Only test connection, don\'t deploy')
    
    args = parser.parse_args()
    
    try:
        deployer = SupabaseSchemaDeployer()
        
        if args.test_only:
            success = deployer.test_connection()
        else:
            success = deployer.run(force_recreate=args.force)
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        logger.error(f"❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 