# Project Priority Upgrades

This document outlines a roadmap for implementing high-value features that were
envisioned for the NFL QB Scraper but are not yet fully implemented in the
current CLI. This list is derived from the legacy `README.md` and serves as a
guide for future development work.

## 1. Data Management Subcommand (`data`)

The `data` command should be the central hub for all data import, export, and
quality operations.

- [ ] **`data validate`**: Implement a robust data validation command.
  - [ ] Define validation rules in a configurable way.
  - [ ] Check for data completeness, correctness, and adherence to business logic.
  - [ ] Generate detailed validation reports in JSON or other formats.

- [ ] **`data export`**: Create a flexible data export tool.
  - [ ] Support multiple formats (JSON, CSV, SQLite).
  - [ ] Allow filtering by season, players, or other criteria.
  - [ ] Ensure consistent data structure in exports.

- [ ] **`data import`**: Build a safe and reliable data import tool.
  - [ ] Support multiple formats (JSON, CSV).
  - [ ] Include a `--validate` flag to check data quality before insertion.
  - [ ] Handle conflicts and updates gracefully.

- [ ] **`data quality`**: Develop a command to generate data quality reports.
  - [ ] Provide summary and detailed views of data quality metrics.
  - [ ] Track quality over time.

- [ ] **`data backup`**: Implement database backup and restore functionality.
  - [ ] Create timestamped, named backups.
  - [ ] Provide a simple restore command.
  - [ ] Include integrity checks for backup files.

- [ ] **`data summary`**: Create a command to provide quick summaries of the data.
  - [ ] Show record counts by season.
  - [ ] Provide high-level statistics.

## 2. Batch Operations Subcommand (`batch`)

The `batch` command is crucial for running large-scale, potentially long-running
scraping jobs.

- [ ] **`batch scrape-season`**: Implement scraping for an entire season as a managed batch job.
  - [ ] Use a worker model for parallel processing.
  - [ ] Ensure robust session management to track progress.

- [ ] **`batch scrape-players`**: Allow scraping a list of players as a batch job.

- [ ] **Session Management**: Build out the session management capabilities.
  - [ ] `batch status`: Check the real-time status of a running session.
  - [ ] `batch list`: List all active and completed sessions.
  - [ ] `batch stop`: Gracefully stop a running session.
  - [ ] `batch resume`: Resume an interrupted session.

- [ ] **`batch cleanup`**: Implement cleanup for old or failed sessions.
  - [ ] Allow cleanup by age (e.g., `--older-than 7`).
  - [ ] Provide an `--all` flag to clear all session data.

## 3. System Management & Monitoring

These commands are for ensuring the health and maintenance of the application.

- [ ] **`monitor`**: Flesh out the system monitoring command.
  - [ ] Track recent scraping activity (success/failure rates).
  - [ ] Monitor database health and performance.

- [ ] **`cleanup`**: Implement a general data cleanup command.
  - [ ] Remove old records from the database (e.g., `--days 30`).

- [ ] **`validate` (System-wide)**: Create a top-level command to run a full system validation, checking database connections, configurations, and data integrity.

## 4. `scrape` Command Enhancements

- [ ] **`--splits-only` flag**: Add functionality to only scrape and update the splits data for existing players without re-scraping the main profile.
- [ ] **`--enhanced` flag**: Define and implement what "enhanced" scraping means. This could involve scraping additional tables like advanced stats, game logs, etc., and integrating them into the database. 