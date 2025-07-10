# Supabase Schema Deployment Guide

This guide will help you deploy the NFL QB data schema to your Supabase
instance.

## Prerequisites

1. **Supabase Account**: You need a Supabase account and project
2. **Python Dependencies**: Make sure you have the required packages installed
3. **Database Credentials**: Your Supabase database connection string

## Step 1: Install Dependencies

First, make sure you have the required Python packages:

````bash
# Install psycopg2 for PostgreSQL connection
pip install psycopg2-binary

# Or if using uv
uv add psycopg2-binary
```text
## Step 2: Set Up Environment Variables

### Option A: Interactive Setup (Recommended)

Run the interactive setup script:

```bash
python scripts/setup_supabase_env.py
```text
This will:

- Guide you through entering your Supabase credentials
- Create a `.env` file with all necessary configuration
- Test the database connection

### Option B: Manual Setup

Create a `.env` file in your project root with the following content:

```env
# Supabase Configuration
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres

# Optional Supabase configuration
SUPABASE_URL=https://[YOUR-PROJECT-REF].supabase.co
SUPABASE_ANON_KEY=[YOUR-ANON-KEY]

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
```text
## Step 3: Get Your Supabase Credentials

1. **Go to Supabase**: Visit [https://supabase.com](https://supabase.com) and
   sign in
2. **Select Your Project**: Choose your project (or create a new one)
3. **Database Settings**: Go to Settings > Database
4. **Copy Connection String**: Copy the connection string from the "Connection
   string" section
5. **Copy API Keys**: Copy the URL and anon key from the "API" section

## Step 4: Deploy the Schema

### Option A: Using the Deployment Script (Recommended)

```bash
# Deploy the schema
python scripts/deploy_schema_to_supabase.py

# If you need to recreate existing tables
python scripts/deploy_schema_to_supabase.py --force

# Test connection only
python scripts/deploy_schema_to_supabase.py --test-only
```text
### Option B: Manual Deployment

If you prefer to deploy manually, you can use the Supabase SQL editor:

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Copy the contents of `sql/schema.sql`
4. Paste it into the SQL editor
5. Click "Run" to execute the schema

### Option C: Using psql Command Line

```bash
# Deploy using psql (replace with your connection string)
psql "postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres" -f sql/schema.sql
```text
## Step 5: Verify the Deployment

After deployment, verify that everything was created correctly:

```bash
# Test the deployment
python scripts/deploy_schema_to_supabase.py --test-only
```text
You should see output like:

```text
✅ Connected to PostgreSQL: PostgreSQL 15.1 on x86_64-pc-linux-gnu
✅ Connected to database: postgres
✅ Created tables: players, qb_advanced_stats, qb_basic_stats, qb_game_log, qb_splits, scraping_log, teams
✅ Created 25 indexes
✅ Created 5 views: database_stats, qb_home_away_splits, qb_quarter_performance, qb_red_zone_performance, qb_season_summary, qb_vs_winning_teams
✅ Created 2 functions: get_qb_splits_by_type, get_qb_stats_by_season
```text
## Step 6: Test with Sample Data

Once the schema is deployed, you can test it with sample data:

```bash
# Test scraping Joe Burrow's data
python scripts/scrape_joe_burrow.py
```text
## Troubleshooting

### Connection Issues

If you get connection errors:

1. **Check your DATABASE_URL**: Make sure it's correctly formatted
2. **Verify credentials**: Ensure your password is correct
3. **Check network**: Make sure you can reach Supabase from your network
4. **Test connection**: Use the test script to verify connectivity

### Schema Deployment Issues

If schema deployment fails:

1. **Check permissions**: Ensure your database user has CREATE privileges
2. **Check existing objects**: Use `--force` flag to recreate existing tables
3. **Review logs**: Check the `schema_deployment.log` file for detailed errors
4. **Manual deployment**: Try deploying manually through the Supabase SQL editor

### Common Error Messages

## "permission denied"

- Your database user doesn't have sufficient privileges
- Contact Supabase support or check your project settings

## "relation already exists"

- Tables already exist in your database
- Use `--force` flag to recreate them

## "connection timeout"

- Network connectivity issues
- Check your internet connection and firewall settings

## Schema Overview

The deployed schema includes:

### Core Tables

- `players`: Player master data and biographical information
- `teams`: NFL team information
- `qb_basic_stats`: Basic quarterback statistics by season
- `qb_advanced_stats`: Advanced quarterback metrics
- `qb_splits`: Situational performance splits
- `qb_game_log`: Individual game performance data
- `scraping_log`: Scraping session logs and monitoring

### Views

- `qb_season_summary`: Combined basic and advanced stats
- `qb_home_away_splits`: Home vs away performance
- `qb_quarter_performance`: Performance by game quarter
- `qb_red_zone_performance`: Red zone efficiency
- `qb_vs_winning_teams`: Performance against winning teams
- `database_stats`: Database statistics and metadata

### Functions

- `get_qb_stats_by_season(season)`: Get QB stats for a specific season
- `get_qb_splits_by_type(pfr_id, season, split_type)`: Get QB splits by type

### Features

- **Row Level Security (RLS)**: Enabled on all tables for Supabase
- **Constraints**: Data integrity constraints for statistical validity
- **Indexes**: Optimized indexes for common query patterns
- **Triggers**: Automatic timestamp updates
- **Custom Types**: ENUMs for game results, weather, and field surface

## Next Steps

After successful deployment:

1. **Test scraping**: Run `python scripts/scrape_joe_burrow.py`
2. **Explore data**: Use the Supabase dashboard to explore your data
3. **Build applications**: Use the Drizzle ORM schema in `src/lib/db/schema.ts`
4. **Monitor performance**: Check the `scraping_log` table for monitoring data

## Support

If you encounter issues:

1. Check the logs in `schema_deployment.log`
2. Review the troubleshooting section above
3. Check the Supabase documentation
4. Create an issue in the project repository

## Security Notes

- Never commit your `.env` file to version control
- Use environment variables for sensitive credentials
- The schema includes RLS policies for security
- Consider setting up proper authentication for production use
````
