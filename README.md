# NFL QB Data Scraping System

Purpose of the Application

The primary purpose of this project is to create a robust and automated data pipeline for scraping, processing, and storing NFL quarterback statistics from the sports reference website Pro Football Reference.

Here is a breakdown of its key objectives and features, as identified from the code:

    Comprehensive Data Scraping: The application is designed to systematically collect a wide range of quarterback data. This isn't limited to basic season totals; it also captures:
        Advanced Statistics: Deeper metrics beyond standard passing and rushing numbers.
        Game Splits: Highly detailed situational statistics, such as a quarterback's performance under specific conditions (e.g., home vs. away, on grass vs. turf, in different quarters, or against winning vs. losing teams).

    Robust and Respectful Scraping: The scripts are built to be reliable and considerate of the website they are scraping. Features like rate limiting, automatic retries with exponential backoff, and concurrent processing show an emphasis on collecting data efficiently without overwhelming the source server.

    Structured Data Storage: After the data is scraped and processed, it is stored in a structured PostgreSQL database. The project is specifically configured to integrate with Supabase, a backend-as-a-service platform that provides a PostgreSQL database along with other features. The sql/schema.sql file defines a well-organized database structure to ensure data integrity and efficient querying.

    Data Management and Maintenance: The project includes a command-line interface (CLI) for managing the entire data pipeline. This CLI allows a user to:
        Initiate scraping for specific seasons or players.
        Validate the integrity of the data in the database.
        Monitor the health of the system and review performance metrics.
        Clean up old logs and data.

    Enable Downstream Applications: The inclusion of a Drizzle ORM schema and TypeScript type definitions strongly indicates that the collected data is intended to be consumed by other applications, most likely a web-based front-end. This project serves as the foundational data layer, providing clean, reliable, and type-safe data for building analytical tools, dashboards, or other user-facing applications that display NFL QB statistics.

In essence, this project is a complete data engineering solution for creating and maintaining a specialized dataset of NFL quarterback performance, with a clear path toward powering a modern data-driven application.

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
