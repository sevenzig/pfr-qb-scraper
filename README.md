# NFL QB Scraper

A professional CLI tool for scraping NFL quarterback statistics from Pro Football Reference and storing them in PostgreSQL/Supabase with comprehensive data validation and respectful rate limiting.

## 🎯 What It Does

- **Scrapes QB Statistics**: Basic stats, situational splits, and advanced metrics from Pro Football Reference
- **Stores Data Safely**: PostgreSQL database with proper schema and data validation
- **Respects Rate Limits**: Built-in delays and respectful scraping to avoid server overload
- **Handles Errors Gracefully**: Automatic retries, comprehensive logging, and resumable operations
- **Validates Data Quality**: Ensures all required fields are captured and validated before storage

## 📋 What You Get

### Database Tables
- **QB Basic Stats**: 33 columns of passing statistics (completions, yards, TDs, ratings, etc.)
- **QB Splits**: 34 columns of situational data (home/away, by quarter, vs different teams)
- **QB Advanced Splits**: 20 columns of advanced situational metrics
- **Player Information**: Basic player demographics and Pro Football Reference IDs
- **Scraping Logs**: Session tracking and quality metrics

## 🚀 Installation

### Prerequisites
- **Python 3.8+** (Python 3.9+ recommended)
- **PostgreSQL database** (Supabase recommended for cloud hosting)

### Step 1: Clone and Install
```bash
# Clone the repository
git clone <repository-url>
cd pfr-qb-scraper

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:  
source venv/bin/activate

# Install the package
pip install -e .
```

### Step 2: Database Setup

#### Option A: Supabase (Recommended)
1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Copy your project URL and anon key
4. Run the schema file in the Supabase SQL editor:
   ```sql
   -- Copy and paste contents of sql/schema.sql
   ```

#### Option B: Local PostgreSQL
```bash
# Install PostgreSQL locally, then:
createdb nfl_qb_data
psql -d nfl_qb_data -f sql/schema.sql
```

### Step 3: Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your database credentials:
DATABASE_URL="postgresql://user:password@host:port/database"
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-supabase-anon-key"
```

### Step 4: Test Installation
```bash
# Verify the CLI works
pfr-qb-scraper --help

# Test database connection
pfr-qb-scraper health
```

## 📋 Basic Usage

### Scrape Data

#### Get Started - Scrape One Season
```bash
# Scrape all QBs for 2024 season
pfr-qb-scraper scrape --season 2024

# This will:
# 1. Scrape basic passing stats for all QBs
# 2. Scrape detailed situational splits for each QB  
# 3. Store everything in your database
# 4. Take 10-15 minutes (respects rate limits)
```

#### Common Scraping Options
```bash
# Scrape specific players only
pfr-qb-scraper scrape --season 2024 --players "Josh Allen" "Patrick Mahomes"

# Scrape only the detailed splits data
pfr-qb-scraper scrape --season 2024 --splits-only

# Show progress as it runs
pfr-qb-scraper scrape --season 2024 --progress

# Use the short alias 
pfr-qb-scraper s --season 2024
```

### Check Your Data

#### Validate What You've Scraped
```bash
# Check if your data looks good (full validation)
pfr-qb-scraper validate

# Quick validation (skip comprehensive checks)  
pfr-qb-scraper validate --quick

# Attempt to fix issues found during validation
pfr-qb-scraper validate --fix

# Only show database statistics (skip validation)
pfr-qb-scraper validate --stats-only
```

#### View Data Summary
```bash
# See what's in your database
pfr-qb-scraper data summary

# See data summary for specific season
pfr-qb-scraper data summary --season 2024

# Export data to work with elsewhere
pfr-qb-scraper data export --season 2024 --format json
pfr-qb-scraper data export --season 2024 --format csv

# Export to specific file
pfr-qb-scraper data export --season 2024 --format json --output qb_data_2024.json
```

### Monitor System Health

#### Check If Everything's Working
```bash
# Test database connection and basic health
pfr-qb-scraper health

# Quick connection test
pfr-qb-scraper health --quick
```

#### View Recent Activity
```bash
# See what's happened recently
pfr-qb-scraper monitor --recent

# Check performance metrics
pfr-qb-scraper monitor --performance

# Check data quality metrics  
pfr-qb-scraper monitor --quality
```

### Maintenance

#### Clean Up Old Data
```bash
# Remove old log files (30+ days)
pfr-qb-scraper cleanup --days 30

# Interactive cleanup (will ask what to remove)
pfr-qb-scraper cleanup --interactive
```

## ⚙️ How It Works

### Built for Reliability
- **Rate Limited**: Minimum 7-second delays between requests to respect Pro Football Reference
- **Resumable**: If scraping fails, you can restart where you left off  
- **Validated**: All data is checked for completeness before storing
- **Logged**: Comprehensive logging so you know what happened

### What Gets Scraped
1. **Main Passing Stats Page**: Gets basic info for all QBs in a season
2. **Individual Player Pages**: Gets detailed situational splits for each QB
3. **Data Validation**: Ensures all required fields are captured
4. **Database Storage**: Stores everything in structured PostgreSQL tables

### Data Quality
- **Complete Coverage**: Scrapes all 33 basic stats, 34 splits, and 20 advanced splits columns
- **Type Validation**: Converts and validates data types (numbers, dates, etc.)
- **Missing Data Handling**: Logs and handles missing or malformed data gracefully
- **Quality Reports**: Shows you exactly what was scraped and any issues found

## 🔧 Troubleshooting

### Common Issues

#### "Database connection failed"
```bash
# Check your .env file has the right credentials
cat .env

# Test the connection
pfr-qb-scraper health --quick
```

#### "Scraping fails or gets blocked"
The scraper includes anti-detection features, but if you're getting blocked:
- The scraper already waits 7+ seconds between requests
- If still blocked, try running at different times of day
- Check logs for specific error messages

#### "Missing data in results"  
```bash
# Run validation to see what's missing
pfr-qb-scraper validate --season 2024 --detailed

# Check the logs for parsing errors
tail -f logs/nfl_qb_scraper.log
```

#### "CLI command not found"
```bash
# Reinstall the package
pip install -e .

# Or run via Python module
python -m src.cli.cli_main --help
```

### Getting Help

1. **Check the logs**: `logs/nfl_qb_scraper.log` has detailed information
2. **Run health check**: `pfr-qb-scraper health` shows system status
3. **Validate your data**: `pfr-qb-scraper validate` shows data quality issues
4. **Check the documentation**: See `docs/` folder for detailed guides

### Advanced Configuration

For advanced usage, custom rate limiting, performance monitoring, and batch operations, see the technical documentation in `src/README.md`.

---

**📧 Support**: For questions or issues, please check the documentation in the `docs/` folder or create an issue.

**⚠️ Important**: This tool is for personal use and research. Always respect Pro Football Reference's terms of service and rate limits.
