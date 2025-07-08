#!/usr/bin/env python3
"""
Setup Supabase Environment Variables

This script helps you set up the environment variables needed to connect to Supabase.
It will create a .env file with the necessary configuration.

Usage:
    python scripts/setup_supabase_env.py
"""

import os
import sys
from pathlib import Path

def get_supabase_credentials():
    """Get Supabase credentials from user input"""
    print("🔧 Supabase Environment Setup")
    print("=" * 50)
    print()
    print("To get your Supabase credentials:")
    print("1. Go to https://supabase.com and sign in")
    print("2. Select your project (or create a new one)")
    print("3. Go to Settings > Database")
    print("4. Copy the connection string and API keys")
    print()
    
    # Get database URL
    print("📝 Database Connection String")
    print("Format: postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres")
    database_url = input("Enter your Supabase database URL: ").strip()
    
    if not database_url:
        print("❌ Database URL is required")
        return None
    
    # Get Supabase URL (optional)
    print()
    print("🌐 Supabase Project URL (optional)")
    print("Format: https://[YOUR-PROJECT-REF].supabase.co")
    supabase_url = input("Enter your Supabase project URL (optional): ").strip()
    
    # Get Supabase anon key (optional)
    print()
    print("🔑 Supabase Anonymous Key (optional)")
    print("Used for client-side access")
    supabase_anon_key = input("Enter your Supabase anonymous key (optional): ").strip()
    
    return {
        'DATABASE_URL': database_url,
        'SUPABASE_URL': supabase_url if supabase_url else '',
        'SUPABASE_ANON_KEY': supabase_anon_key if supabase_anon_key else ''
    }

def create_env_file(credentials: dict):
    """Create .env file with credentials"""
    if not credentials:
        return False
        
    env_content = f"""# Supabase Configuration
DATABASE_URL={credentials.get('DATABASE_URL', '')}

# Optional Supabase configuration
SUPABASE_URL={credentials.get('SUPABASE_URL', '')}
SUPABASE_ANON_KEY={credentials.get('SUPABASE_ANON_KEY', '')}

# Scraping Configuration
RATE_LIMIT_DELAY=3.0
MAX_RETRIES=3
MAX_WORKERS=2
JITTER_RANGE=0.5

# Application Configuration
TARGET_SEASON=2024
DATA_VALIDATION_ENABLED=true
AUTO_DISCOVERY_ENABLED=true

# Database Configuration
DB_MAX_CONNECTIONS=10
DB_CONNECTION_TIMEOUT=30
DB_STATEMENT_TIMEOUT=300

# Logging Configuration
LOG_LEVEL=INFO
LOG_TO_FILE=true
"""
    
    env_file = Path('.env')
    
    if env_file.exists():
        print(f"⚠️  .env file already exists at {env_file}")
        overwrite = input("Do you want to overwrite it? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("❌ Setup cancelled")
            return False
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ Created .env file at {env_file}")
        return True
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")
        return False

def test_connection(database_url):
    """Test the database connection"""
    print()
    print("🔍 Testing database connection...")
    
    try:
        import psycopg2
        conn = psycopg2.connect(database_url)
        
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()
            print(f"✅ Connected successfully!")
            print(f"   PostgreSQL version: {version[0]}")
            
            cur.execute("SELECT current_database();")
            db_name = cur.fetchone()
            print(f"   Database: {db_name[0]}")
            
            cur.execute("SELECT current_user;")
            user = cur.fetchone()
            print(f"   User: {user[0]}")
        
        conn.close()
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Install it with: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 Supabase Environment Setup")
    print("=" * 50)
    
    # Get credentials
    credentials = get_supabase_credentials()
    if not credentials:
        sys.exit(1)
    
    # Create .env file
    if not create_env_file(credentials):
        sys.exit(1)
    
    # Test connection
    if credentials is not None and not test_connection(credentials['DATABASE_URL']):
        print()
        print("⚠️  Connection test failed. Please check your credentials.")
        print("   You can still proceed with the setup and test later.")
    
    print()
    print("🎉 Setup completed!")
    print()
    print("Next steps:")
    print("1. Deploy the schema: python scripts/deploy_schema_to_supabase.py")
    print("2. Test scraping: python scripts/scrape_joe_burrow.py")
    print("3. Check the logs for any issues")
    print()
    print("For help, see the README.md file")

if __name__ == "__main__":
    main() 