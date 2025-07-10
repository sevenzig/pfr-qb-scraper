# NFL QB Data Scraping System

A system for scraping NFL quarterback statistics and splits data from Pro Football
Reference and storing it in a PostgreSQL database via Supabase.

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- A PostgreSQL database (Supabase is recommended)
- Git

### Installation & Setup

1.  **Clone the repository**

    ```bash
    git clone <repository-url>
    cd pfr-qb-scraper
    ```

2.  **Create and activate a virtual environment**

    ```bash
    python -m venv venv

    # On Windows
    venv\\Scripts\\activate

    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure your environment**

    Create a `.env` file in the root of the project and add your database
    credentials. You can copy the example file to get started:

    ```bash
    cp .env.example .env
    ```

    Your `.env` file should look like this:
    ```
    DATABASE_URL="postgresql://user:password@host:port/database"
    SUPABASE_URL="https://your-project.supabase.co"
    SUPABASE_KEY="your-supabase-anon-key"
    ```

5.  **Initialize the database**

    Connect to your PostgreSQL database and run the schema definition found in
    `sql/schema.sql` to create the necessary tables.

## 📋 CLI Commands

The primary entry point for the application is `run_cli.py`.

### Data Scraping

The `scrape` command is used to fetch player data from Pro Football Reference.

```bash
# Scrape data for specific players for the 2024 season
python run_cli.py scrape --season 2024 --players "Joe Burrow" "Patrick Mahomes"

# Scrape data for all players found for a given season
python run_cli.py scrape --season 2023
```

**Available Flags:**

-   `--season <YEAR>`: (Required) The season year to scrape.
-   `--players <"Player Name" ...>`: A list of one or more player names to scrape. If not provided, the tool will attempt to scrape all QBs for the season.

### System Health

The `health` command is used to check the status of the database connection.

```bash
# Run a health check to verify the database connection
python run_cli.py health
```

## 🏗️ Project Architecture

```text
src/
├── cli/                    # Professional CLI interface
│   ├── base_command.py     # Abstract command base class
│   ├── cli_main.py         # Main CLI entry point
│   └── commands/           # Individual command implementations
│       ├── scrape_command.py
│       └── health_command.py
├── core/                   # Core business logic
│   └── scraper.py          # Unified CoreScraper
├── operations/             # Advanced operations (Work in Progress)
├── database/               # Database operations
├── models/                 # Data models
├── config/                 # Configuration management
└── utils/                  # Utility functions
```

For a list of planned features and future development, please see the
[Priority Upgrades Roadmap](./docs/PRIORITY_UPGRADES.md).
