#!/usr/bin/env python3
"""
Database manager for NFL QB data with connection pooling and optimized operations
Handles all database operations for the new schema with PFR IDs and separated tables
"""

import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager

import psycopg2
from psycopg2.pool import SimpleConnectionPool
from psycopg2.extras import RealDictCursor, execute_batch
from psycopg2.extensions import connection

from models.qb_models import QBBasicStats, QBAdvancedStats, QBSplitStats, Player, Team, ScrapingLog
from config.config import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles all database operations for QB data with connection pooling"""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or config.get_database_url()
        self.pool: Optional[SimpleConnectionPool] = None
        self._initialize_pool()
        
    def _initialize_pool(self) -> None:
        """Initialize connection pool"""
        try:
            self.pool = SimpleConnectionPool(
                minconn=1,
                maxconn=config.database.max_connections,
                dsn=self.connection_string,
                cursor_factory=RealDictCursor
            )
            logger.info(f"Database connection pool initialized with {config.database.max_connections} connections")
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self) -> Any:
        """Context manager for database connections"""
        conn = None
        try:
            if self.pool is None:
                raise RuntimeError("Database pool not initialized")
            conn = self.pool.getconn()
            conn.autocommit = False  # Use transactions
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn and self.pool:
                self.pool.putconn(conn)
    
    @contextmanager
    def get_cursor(self, conn: connection) -> Any:
        """Context manager for database cursors"""
        cur = None
        try:
            cur = conn.cursor()
            yield cur
        except Exception as e:
            logger.error(f"Database cursor error: {e}")
            raise
        finally:
            if cur:
                cur.close()
    
    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    return result is not None
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    def query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """
        Execute a query and return results
        
        Args:
            sql: SQL query to execute
            params: Optional parameters for the query
            
        Returns:
            List of dictionaries with query results
        """
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    if params:
                        cur.execute(sql, params)
                    else:
                        cur.execute(sql)
                    results = cur.fetchall()
                    return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Query error: {e}")
            raise
    
    def create_tables(self) -> None:
        """Create all necessary tables with optimized schema"""
        logger.info("Creating database tables...")
        
        # Read and execute schema file
        schema_file = "sql/schema.sql"
        try:
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    # Split the schema into individual statements and execute them
                    statements = schema_sql.split(';')
                    
                    for statement in statements:
                        statement = statement.strip()
                        if statement and not statement.startswith('--'):
                            try:
                                cur.execute(statement)
                                logger.debug(f"Executed: {statement[:50]}...")
                            except Exception as e:
                                # If it's a "already exists" error, that's fine
                                if "already exists" in str(e).lower():
                                    logger.debug(f"Object already exists: {statement[:50]}...")
                                else:
                                    logger.warning(f"Error executing statement: {e}")
                                    # Continue with other statements
                    
                    conn.commit()
            
            logger.info("Database tables created successfully")
            
        except FileNotFoundError:
            logger.error(f"Schema file not found: {schema_file}")
            raise
        except Exception as e:
            logger.error(f"Error creating tables: {e}")
            raise
    
    def insert_player(self, player: Player) -> int:
        """
        Insert a single player with conflict resolution
        
        Args:
            player: Player object to insert
            
        Returns:
            Number of records inserted/updated
        """
        insert_query = """
        INSERT INTO players (
            pfr_id, player_name, pfr_url, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (pfr_id) 
        DO UPDATE SET
            player_name = EXCLUDED.player_name,
            pfr_url = EXCLUDED.pfr_url,
            updated_at = EXCLUDED.updated_at
        """
        
        try:
            values = [(
                player.pfr_id, player.player_name, player.pfr_url,
                player.created_at, player.updated_at
            )]
            
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    execute_batch(cur, insert_query, values, page_size=100)
                    conn.commit()
            
            logger.info(f"Inserted/updated player: {player.player_name}")
            return 1
            
        except Exception as e:
            logger.error(f"Error inserting player: {e}")
            raise
    
    def insert_qb_basic_stats(self, stats_list: List[QBBasicStats]) -> int:
        """
        Insert QB basic stats with conflict resolution
        
        Args:
            stats_list: List of QBBasicStats objects to insert
            
        Returns:
            Number of records inserted/updated
        """
        if not stats_list:
            return 0
        
        insert_query = """
        INSERT INTO qb_basic_stats (
            pfr_id, season, team, games_played, games_started,
            completions, attempts, completion_pct, pass_yards, pass_tds,
            interceptions, longest_pass, rating, sacks, sack_yards,
            net_yards_per_attempt, scraped_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (pfr_id, season) 
        DO UPDATE SET
            team = EXCLUDED.team,
            games_played = EXCLUDED.games_played,
            games_started = EXCLUDED.games_started,
            completions = EXCLUDED.completions,
            attempts = EXCLUDED.attempts,
            completion_pct = EXCLUDED.completion_pct,
            pass_yards = EXCLUDED.pass_yards,
            pass_tds = EXCLUDED.pass_tds,
            interceptions = EXCLUDED.interceptions,
            longest_pass = EXCLUDED.longest_pass,
            rating = EXCLUDED.rating,
            sacks = EXCLUDED.sacks,
            sack_yards = EXCLUDED.sack_yards,
            net_yards_per_attempt = EXCLUDED.net_yards_per_attempt,
            scraped_at = EXCLUDED.scraped_at,
            updated_at = EXCLUDED.updated_at
        """
        
        try:
            # Convert dataclass objects to tuples
            values = []
            for stat in stats_list:
                values.append((
                    stat.pfr_id, stat.season, stat.team, stat.games_played, stat.games_started,
                    stat.completions, stat.attempts, stat.completion_pct, stat.pass_yards,
                    stat.pass_tds, stat.interceptions, stat.longest_pass, stat.rating,
                    stat.sacks, stat.sack_yards, stat.net_yards_per_attempt,
                    stat.scraped_at, stat.updated_at
                ))
            
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    execute_batch(cur, insert_query, values, page_size=100)
                    conn.commit()
            
            logger.info(f"Inserted/updated {len(stats_list)} QB basic stats records")
            return len(stats_list)
            
        except Exception as e:
            logger.error(f"Error inserting QB basic stats: {e}")
            raise
    
    def insert_qb_advanced_stats(self, stats_list: List[QBAdvancedStats]) -> int:
        """
        Insert QB advanced stats with conflict resolution
        
        Args:
            stats_list: List of QBAdvancedStats objects to insert
            
        Returns:
            Number of records inserted/updated
        """
        if not stats_list:
            return 0
        
        insert_query = """
        INSERT INTO qb_advanced_stats (
            pfr_id, season, qbr, adjusted_net_yards_per_attempt,
            fourth_quarter_comebacks, game_winning_drives, scraped_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (pfr_id, season) 
        DO UPDATE SET
            qbr = EXCLUDED.qbr,
            adjusted_net_yards_per_attempt = EXCLUDED.adjusted_net_yards_per_attempt,
            fourth_quarter_comebacks = EXCLUDED.fourth_quarter_comebacks,
            game_winning_drives = EXCLUDED.game_winning_drives,
            scraped_at = EXCLUDED.scraped_at,
            updated_at = EXCLUDED.updated_at
        """
        
        try:
            # Convert dataclass objects to tuples
            values = []
            for stat in stats_list:
                values.append((
                    stat.pfr_id, stat.season, stat.qbr, stat.adjusted_net_yards_per_attempt,
                    stat.fourth_quarter_comebacks, stat.game_winning_drives,
                    stat.scraped_at, stat.updated_at
                ))
            
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    execute_batch(cur, insert_query, values, page_size=100)
                    conn.commit()
            
            logger.info(f"Inserted/updated {len(stats_list)} QB advanced stats records")
            return len(stats_list)
            
        except Exception as e:
            logger.error(f"Error inserting QB advanced stats: {e}")
            raise
    
    def insert_qb_splits(self, splits_list: List[QBSplitStats]) -> int:
        """
        Insert QB splits with conflict resolution
        
        Args:
            splits_list: List of QBSplitStats objects to insert
            
        Returns:
            Number of records inserted/updated
        """
        if not splits_list:
            return 0
        
        insert_query = """
        INSERT INTO qb_splits (
            pfr_id, season, split_type, split_category,
            games, completions, attempts, completion_pct, pass_yards, pass_tds,
            interceptions, rating, sacks, sack_yards, net_yards_per_attempt,
            rush_attempts, rush_yards, rush_tds, fumbles, fumbles_lost,
            fumbles_forced, fumbles_recovered, fumble_recovery_yards,
            fumble_recovery_tds, incompletions, wins, losses, ties,
            attempts_per_game, yards_per_game, rush_attempts_per_game,
            rush_yards_per_game, total_tds, points, scraped_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (pfr_id, season, split_type, split_category)
        DO UPDATE SET
            games = EXCLUDED.games,
            completions = EXCLUDED.completions,
            attempts = EXCLUDED.attempts,
            completion_pct = EXCLUDED.completion_pct,
            pass_yards = EXCLUDED.pass_yards,
            pass_tds = EXCLUDED.pass_tds,
            interceptions = EXCLUDED.interceptions,
            rating = EXCLUDED.rating,
            sacks = EXCLUDED.sacks,
            sack_yards = EXCLUDED.sack_yards,
            net_yards_per_attempt = EXCLUDED.net_yards_per_attempt,
            rush_attempts = EXCLUDED.rush_attempts,
            rush_yards = EXCLUDED.rush_yards,
            rush_tds = EXCLUDED.rush_tds,
            fumbles = EXCLUDED.fumbles,
            fumbles_lost = EXCLUDED.fumbles_lost,
            fumbles_forced = EXCLUDED.fumbles_forced,
            fumbles_recovered = EXCLUDED.fumbles_recovered,
            fumble_recovery_yards = EXCLUDED.fumble_recovery_yards,
            fumble_recovery_tds = EXCLUDED.fumble_recovery_tds,
            incompletions = EXCLUDED.incompletions,
            wins = EXCLUDED.wins,
            losses = EXCLUDED.losses,
            ties = EXCLUDED.ties,
            attempts_per_game = EXCLUDED.attempts_per_game,
            yards_per_game = EXCLUDED.yards_per_game,
            rush_attempts_per_game = EXCLUDED.rush_attempts_per_game,
            rush_yards_per_game = EXCLUDED.rush_yards_per_game,
            total_tds = EXCLUDED.total_tds,
            points = EXCLUDED.points,
            scraped_at = EXCLUDED.scraped_at,
            updated_at = EXCLUDED.updated_at
        """
        
        try:
            # Convert dataclass objects to tuples
            values = []
            for split in splits_list:
                values.append((
                    split.pfr_id, split.season, split.split_type, split.split_category,
                    split.games, split.completions, split.attempts, split.completion_pct,
                    split.pass_yards, split.pass_tds, split.interceptions, split.rating,
                    split.sacks, split.sack_yards, split.net_yards_per_attempt,
                    split.rush_attempts, split.rush_yards, split.rush_tds,
                    split.fumbles, split.fumbles_lost, split.fumbles_forced,
                    split.fumbles_recovered, split.fumble_recovery_yards,
                    split.fumble_recovery_tds, split.incompletions, split.wins,
                    split.losses, split.ties, split.attempts_per_game,
                    split.yards_per_game, split.rush_attempts_per_game,
                    split.rush_yards_per_game, split.total_tds, split.points,
                    split.scraped_at, split.updated_at
                ))
            
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    execute_batch(cur, insert_query, values, page_size=100)
                    conn.commit()
            
            logger.info(f"Inserted/updated {len(splits_list)} QB splits records")
            return len(splits_list)
            
        except Exception as e:
            logger.error(f"Error inserting QB splits: {e}")
            raise
    
    def insert_scraping_log(self, log: ScrapingLog) -> int:
        """
        Insert scraping log entry
        
        Args:
            log: ScrapingLog object to insert
            
        Returns:
            Number of records inserted
        """
        insert_query = """
        INSERT INTO scraping_logs (
            session_id, season, start_time, end_time, total_requests,
            successful_requests, failed_requests, total_qb_basic_stats,
            total_qb_advanced_stats, total_qb_splits, errors, warnings,
            rate_limit_violations, processing_time_seconds, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            values = [(
                log.session_id, log.season, log.start_time, log.end_time,
                log.total_requests, log.successful_requests, log.failed_requests,
                log.total_basic_stats, log.total_advanced_stats, log.total_qb_splits,
                log.errors, log.warnings, log.rate_limit_violations,
                log.processing_time_seconds, log.created_at
            )]
            
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    execute_batch(cur, insert_query, values, page_size=100)
                    conn.commit()
            
            logger.info(f"Inserted scraping log: {log.session_id}")
            return 1
            
        except Exception as e:
            logger.error(f"Error inserting scraping log: {e}")
            raise
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    stats = {}
                    
                    # Count players
                    cur.execute("SELECT COUNT(*) as count FROM players")
                    stats['total_players'] = cur.fetchone()['count']
                    
                    # Count basic stats
                    cur.execute("SELECT COUNT(*) as count FROM qb_basic_stats")
                    stats['total_basic_stats'] = cur.fetchone()['count']
                    
                    # Count advanced stats
                    cur.execute("SELECT COUNT(*) as count FROM qb_advanced_stats")
                    stats['total_advanced_stats'] = cur.fetchone()['count']
                    
                    # Count splits
                    cur.execute("SELECT COUNT(*) as count FROM qb_splits")
                    stats['total_splits'] = cur.fetchone()['count']
                    
                    # Count scraping logs
                    cur.execute("SELECT COUNT(*) as count FROM scraping_logs")
                    stats['total_scraping_logs'] = cur.fetchone()['count']
                    
                    return stats
                    
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def validate_data_integrity(self) -> Dict[str, List[str]]:
        """Validate data integrity across tables"""
        errors = {}
        
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    
                    # Check for orphaned basic stats
                    cur.execute("""
                        SELECT COUNT(*) as count 
                        FROM qb_basic_stats bs 
                        LEFT JOIN players p ON bs.pfr_id = p.pfr_id 
                        WHERE p.pfr_id IS NULL
                    """)
                    orphaned_basic = cur.fetchone()['count']
                    if orphaned_basic > 0:
                        errors['qb_basic_stats'] = [f"{orphaned_basic} records without matching player"]
                    
                    # Check for orphaned advanced stats
                    cur.execute("""
                        SELECT COUNT(*) as count 
                        FROM qb_advanced_stats ads 
                        LEFT JOIN players p ON ads.pfr_id = p.pfr_id 
                        WHERE p.pfr_id IS NULL
                    """)
                    orphaned_advanced = cur.fetchone()['count']
                    if orphaned_advanced > 0:
                        errors['qb_advanced_stats'] = [f"{orphaned_advanced} records without matching player"]
                    
                    # Check for orphaned splits
                    cur.execute("""
                        SELECT COUNT(*) as count 
                        FROM qb_splits s 
                        LEFT JOIN players p ON s.pfr_id = p.pfr_id 
                        WHERE p.pfr_id IS NULL
                    """)
                    orphaned_splits = cur.fetchone()['count']
                    if orphaned_splits > 0:
                        errors['qb_splits'] = [f"{orphaned_splits} records without matching player"]
                    
        except Exception as e:
            logger.error(f"Error validating data integrity: {e}")
            errors['validation_error'] = [str(e)]
        
        return errors
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on database"""
        health = {
            'connection_ok': False,
            'tables_exist': False,
            'data_accessible': False
        }
        
        try:
            # Test connection
            health['connection_ok'] = self.test_connection()
            
            if health['connection_ok']:
                with self.get_connection() as conn:
                    with self.get_cursor(conn) as cur:
                        # Check if tables exist
                        cur.execute("""
                            SELECT COUNT(*) as count 
                            FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name IN ('players', 'qb_basic_stats', 'qb_advanced_stats', 'qb_splits', 'scraping_logs')
                        """)
                        table_count = cur.fetchone()['count']
                        health['tables_exist'] = table_count == 5
                        
                        # Check if data is accessible
                        if health['tables_exist']:
                            cur.execute("SELECT COUNT(*) as count FROM players LIMIT 1")
                            health['data_accessible'] = True
                            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
        
        return health
    
    def close(self) -> None:
        """Close database connections"""
        if self.pool:
            self.pool.closeall()
            logger.info("Database connection pool closed")
    
    def __enter__(self) -> 'DatabaseManager':
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[Exception], exc_tb: Optional[Any]) -> None:
        """Context manager exit"""
        self.close() 