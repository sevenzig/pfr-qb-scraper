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

from src.models.qb_models import QBBasicStats, QBAdvancedStats, QBSplitStats, QBSplitsType2, Player, Team, ScrapingLog
from src.config.config import config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles all database operations for QB data with connection pooling"""
    
    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string or config.get_database_url()
        self.pool: Optional[SimpleConnectionPool] = None
        self.logger = logging.getLogger(__name__)
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
    
    def execute(self, sql: str, params: Optional[tuple] = None) -> int:
        """
        Execute a statement (INSERT/UPDATE/DELETE) without returning results
        
        Args:
            sql: SQL statement to execute
            params: Optional parameters for the statement
            
        Returns:
            Number of rows affected
        """
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    if params:
                        cur.execute(sql, params)
                    else:
                        cur.execute(sql)
                    conn.commit()
                    return cur.rowcount
        except Exception as e:
            logger.error(f"Execute error: {e}")
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
        INSERT INTO qb_passing_stats (
            pfr_id, player_name, player_url, season, rk, age, team, pos, g, gs, qb_rec,
            cmp, att, cmp_pct, yds, td, td_pct, int, int_pct, first_downs, succ_pct,
            lng, y_a, ay_a, y_c, y_g, rate, qbr, sk, sk_yds, sk_pct, ny_a, any_a,
            four_qc, gwd, awards, player_additional, scraped_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (pfr_id, season) 
        DO UPDATE SET
            player_name = EXCLUDED.player_name,
            player_url = EXCLUDED.player_url,
            rk = EXCLUDED.rk,
            age = EXCLUDED.age,
            team = EXCLUDED.team,
            pos = EXCLUDED.pos,
            g = EXCLUDED.g,
            gs = EXCLUDED.gs,
            qb_rec = EXCLUDED.qb_rec,
            cmp = EXCLUDED.cmp,
            att = EXCLUDED.att,
            cmp_pct = EXCLUDED.cmp_pct,
            yds = EXCLUDED.yds,
            td = EXCLUDED.td,
            td_pct = EXCLUDED.td_pct,
            int = EXCLUDED.int,
            int_pct = EXCLUDED.int_pct,
            first_downs = EXCLUDED.first_downs,
            succ_pct = EXCLUDED.succ_pct,
            lng = EXCLUDED.lng,
            y_a = EXCLUDED.y_a,
            ay_a = EXCLUDED.ay_a,
            y_c = EXCLUDED.y_c,
            y_g = EXCLUDED.y_g,
            rate = EXCLUDED.rate,
            qbr = EXCLUDED.qbr,
            sk = EXCLUDED.sk,
            sk_yds = EXCLUDED.sk_yds,
            sk_pct = EXCLUDED.sk_pct,
            ny_a = EXCLUDED.ny_a,
            any_a = EXCLUDED.any_a,
            four_qc = EXCLUDED.four_qc,
            gwd = EXCLUDED.gwd,
            awards = EXCLUDED.awards,
            player_additional = EXCLUDED.player_additional,
            scraped_at = EXCLUDED.scraped_at,
            updated_at = EXCLUDED.updated_at
        """
        
        try:
            # Convert dataclass objects to tuples
            values = []
            for stat in stats_list:
                values.append((
                    stat.pfr_id, stat.player_name, stat.player_url, stat.season, stat.rk,
                    stat.age, stat.team, stat.pos, stat.g, stat.gs, stat.qb_rec, stat.cmp,
                    stat.att, stat.cmp_pct, stat.yds, stat.td, stat.td_pct, stat.int,
                    stat.int_pct, stat.first_downs, stat.succ_pct, stat.lng, stat.y_a,
                    stat.ay_a, stat.y_c, stat.y_g, stat.rate, stat.qbr, stat.sk, stat.sk_yds,
                    stat.sk_pct, stat.ny_a, stat.any_a, stat.four_qc, stat.gwd, stat.awards,
                    stat.player_additional, stat.scraped_at, stat.updated_at
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
        INSERT INTO qb_splits_advanced (
            pfr_id, player_name, season, split, value, cmp, att, inc, cmp_pct,
            yds, td, first_downs, int, rate, sk, sk_yds, y_a, ay_a,
            rush_att, rush_yds, rush_y_a, rush_td, rush_first_downs,
            scraped_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (pfr_id, season, split, value) 
        DO UPDATE SET
            cmp = EXCLUDED.cmp,
            att = EXCLUDED.att,
            inc = EXCLUDED.inc,
            cmp_pct = EXCLUDED.cmp_pct,
            yds = EXCLUDED.yds,
            td = EXCLUDED.td,
            first_downs = EXCLUDED.first_downs,
            int = EXCLUDED.int,
            rate = EXCLUDED.rate,
            sk = EXCLUDED.sk,
            sk_yds = EXCLUDED.sk_yds,
            y_a = EXCLUDED.y_a,
            ay_a = EXCLUDED.ay_a,
            rush_att = EXCLUDED.rush_att,
            rush_yds = EXCLUDED.rush_yds,
            rush_y_a = EXCLUDED.rush_y_a,
            rush_td = EXCLUDED.rush_td,
            rush_first_downs = EXCLUDED.rush_first_downs,
            scraped_at = EXCLUDED.scraped_at,
            updated_at = EXCLUDED.updated_at
        """
        
        try:
            # Convert dataclass objects to tuples
            values = []
            for stat in stats_list:
                values.append((
                    stat.pfr_id, stat.player_name, stat.season, stat.split, stat.value,
                    stat.cmp, stat.att, stat.inc, stat.cmp_pct, stat.yds, stat.td,
                    stat.first_downs, stat.int, stat.rate, stat.sk, stat.sk_yds,
                    stat.y_a, stat.ay_a, stat.rush_att, stat.rush_yds, stat.rush_y_a,
                    stat.rush_td, stat.rush_first_downs, stat.scraped_at, stat.updated_at
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
        Insert a list of QB splits (basic)
        """
        insert_query = """
        INSERT INTO qb_splits (
            pfr_id, player_name, season, split, value, g, w, l, t, cmp, att, inc, cmp_pct, yds, td, int, rate, sk, sk_yds, y_a, ay_a, a_g, y_g, rush_att, rush_yds, rush_y_a, rush_td, rush_a_g, rush_y_g, total_td, pts, fmb, fl, ff, fr, fr_yds, fr_td, scraped_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (pfr_id, season, split, value)
        DO UPDATE SET
            player_name = EXCLUDED.player_name,
            g = EXCLUDED.g,
            w = EXCLUDED.w,
            l = EXCLUDED.l,
            t = EXCLUDED.t,
            cmp = EXCLUDED.cmp,
            att = EXCLUDED.att,
            inc = EXCLUDED.inc,
            cmp_pct = EXCLUDED.cmp_pct,
            yds = EXCLUDED.yds,
            td = EXCLUDED.td,
            int = EXCLUDED.int,
            rate = EXCLUDED.rate,
            sk = EXCLUDED.sk,
            sk_yds = EXCLUDED.sk_yds,
            y_a = EXCLUDED.y_a,
            ay_a = EXCLUDED.ay_a,
            a_g = EXCLUDED.a_g,
            y_g = EXCLUDED.y_g,
            rush_att = EXCLUDED.rush_att,
            rush_yds = EXCLUDED.rush_yds,
            rush_y_a = EXCLUDED.rush_y_a,
            rush_td = EXCLUDED.rush_td,
            rush_a_g = EXCLUDED.rush_a_g,
            rush_y_g = EXCLUDED.rush_y_g,
            total_td = EXCLUDED.total_td,
            pts = EXCLUDED.pts,
            fmb = EXCLUDED.fmb,
            fl = EXCLUDED.fl,
            ff = EXCLUDED.ff,
            fr = EXCLUDED.fr,
            fr_yds = EXCLUDED.fr_yds,
            fr_td = EXCLUDED.fr_td,
            scraped_at = EXCLUDED.scraped_at,
            updated_at = EXCLUDED.updated_at
        """
        
        values = []
        for split in splits_list:
            values.append((
                split.pfr_id, split.player_name, split.season, split.split, split.value,
                split.g, split.w, split.l, split.t, split.cmp, split.att, split.inc,
                split.cmp_pct, split.yds, split.td, split.int, split.rate, split.sk,
                split.sk_yds, split.y_a, split.ay_a, split.a_g, split.y_g,
                split.rush_att, split.rush_yds, split.rush_y_a, split.rush_td,
                split.rush_a_g, split.rush_y_g, split.total_td, split.pts,
                split.fmb, split.fl, split.ff, split.fr, split.fr_yds, split.fr_td,
                split.scraped_at, split.updated_at
            ))
        
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    execute_batch(cur, insert_query, values, page_size=100)
                    conn.commit()
            
            logger.info(f"Inserted/updated {len(splits_list)} QB splits records")
            return len(splits_list)
            
        except Exception as e:
            logger.error(f"Error inserting QB splits: {e}")
            raise
    
    def insert_qb_splits_advanced(self, splits_list: List[QBSplitsType2]) -> int:
        """
        Insert a list of QB splits (advanced)
        """
        insert_query = """
        INSERT INTO qb_splits_advanced (
            pfr_id, player_name, season, split, value, cmp, att, inc, cmp_pct, yds, td, first_downs, int, rate, sk, sk_yds, y_a, ay_a, rush_att, rush_yds, rush_y_a, rush_td, rush_first_downs, scraped_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        ON CONFLICT (pfr_id, season, split, value)
        DO UPDATE SET
            cmp = EXCLUDED.cmp,
            att = EXCLUDED.att,
            inc = EXCLUDED.inc,
            cmp_pct = EXCLUDED.cmp_pct,
            yds = EXCLUDED.yds,
            td = EXCLUDED.td,
            first_downs = EXCLUDED.first_downs,
            int = EXCLUDED.int,
            rate = EXCLUDED.rate,
            sk = EXCLUDED.sk,
            sk_yds = EXCLUDED.sk_yds,
            y_a = EXCLUDED.y_a,
            ay_a = EXCLUDED.ay_a,
            rush_att = EXCLUDED.rush_att,
            rush_yds = EXCLUDED.rush_yds,
            rush_y_a = EXCLUDED.rush_y_a,
            rush_td = EXCLUDED.rush_td,
            rush_first_downs = EXCLUDED.rush_first_downs,
            scraped_at = EXCLUDED.scraped_at,
            updated_at = EXCLUDED.updated_at
        """
        
        values = []
        for split in splits_list:
            values.append((
                split.pfr_id, split.player_name, split.season, split.split, split.value,
                split.cmp, split.att, split.inc, split.cmp_pct, split.yds, split.td,
                split.first_downs, split.int, split.rate, split.sk, split.sk_yds,
                split.y_a, split.ay_a, split.rush_att, split.rush_yds, split.rush_y_a,
                split.rush_td, split.rush_first_downs, split.scraped_at, split.updated_at
            ))
        
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    execute_batch(cur, insert_query, values, page_size=100)
                    conn.commit()
            
            logger.info(f"Inserted/updated {len(splits_list)} QB splits advanced records")
            return len(splits_list)
            
        except Exception as e:
            logger.error(f"Error inserting QB splits advanced: {e}")
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
            successful_requests, failed_requests, total_players, total_passing_stats,
            total_splits, total_splits_advanced, errors, warnings,
            rate_limit_violations, processing_time_seconds, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        try:
            values = [(
                log.session_id, log.season, log.start_time, log.end_time,
                log.total_requests, log.successful_requests, log.failed_requests,
                log.total_players, log.total_passing_stats, log.total_splits,
                log.total_splits_advanced, log.errors, log.warnings, log.rate_limit_violations,
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
        """
        Get high-level database statistics for monitoring
        """
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    cur.execute("""
                        SELECT * FROM database_stats
                    """)
                    stats = cur.fetchall()
                    return {row['table_name']: row['record_count'] for row in stats}
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}
    
    def validate_data_integrity(self) -> Dict[str, List[str]]:
        """Validate data integrity across tables"""
        errors = {}
        
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    
                    # Check for orphaned passing stats
                    cur.execute("""
                        SELECT COUNT(*) as count 
                        FROM qb_passing_stats ps 
                        LEFT JOIN players p ON ps.pfr_id = p.pfr_id 
                        WHERE p.pfr_id IS NULL
                    """)
                    orphaned_passing = cur.fetchone()['count']
                    if orphaned_passing > 0:
                        errors['qb_passing_stats'] = [f"{orphaned_passing} records without matching player"]
                    
                    # Check for orphaned splits
                    cur.execute("""
                        SELECT COUNT(*) as count 
                        FROM qb_splits st1 
                        LEFT JOIN players p ON st1.pfr_id = p.pfr_id 
                        WHERE p.pfr_id IS NULL
                    """)
                    orphaned_splits = cur.fetchone()['count']
                    if orphaned_splits > 0:
                        errors['qb_splits'] = [f"{orphaned_splits} records without matching player"]
                    
                    # Check for orphaned splits advanced
                    cur.execute("""
                        SELECT COUNT(*) as count 
                        FROM qb_splits_advanced st2 
                        LEFT JOIN players p ON st2.pfr_id = p.pfr_id 
                        WHERE p.pfr_id IS NULL
                    """)
                    orphaned_splits_advanced = cur.fetchone()['count']
                    if orphaned_splits_advanced > 0:
                        errors['qb_splits_advanced'] = [f"{orphaned_splits_advanced} records without matching player"]
                    
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
                            AND table_name IN ('players', 'qb_passing_stats', 'qb_splits', 'qb_splits_advanced', 'scraping_logs')
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

    def populate_teams(self) -> int:
        """Populate the teams table with all 32 NFL teams."""
        teams_data = [
            # AFC East
            ('BUF', 'Buffalo Bills', 'Buffalo', 'East', 'AFC'),
            ('MIA', 'Miami Dolphins', 'Miami', 'East', 'AFC'),
            ('NWE', 'New England Patriots', 'Foxborough', 'East', 'AFC'),
            ('NYJ', 'New York Jets', 'East Rutherford', 'East', 'AFC'),
            
            # AFC North
            ('BAL', 'Baltimore Ravens', 'Baltimore', 'North', 'AFC'),
            ('CIN', 'Cincinnati Bengals', 'Cincinnati', 'North', 'AFC'),
            ('CLE', 'Cleveland Browns', 'Cleveland', 'North', 'AFC'),
            ('PIT', 'Pittsburgh Steelers', 'Pittsburgh', 'North', 'AFC'),
            
            # AFC South
            ('HOU', 'Houston Texans', 'Houston', 'South', 'AFC'),
            ('IND', 'Indianapolis Colts', 'Indianapolis', 'South', 'AFC'),
            ('JAX', 'Jacksonville Jaguars', 'Jacksonville', 'South', 'AFC'),
            ('TEN', 'Tennessee Titans', 'Nashville', 'South', 'AFC'),
            
            # AFC West
            ('DEN', 'Denver Broncos', 'Denver', 'West', 'AFC'),
            ('KAN', 'Kansas City Chiefs', 'Kansas City', 'West', 'AFC'),
            ('LVR', 'Las Vegas Raiders', 'Las Vegas', 'West', 'AFC'),
            ('LAC', 'Los Angeles Chargers', 'Inglewood', 'West', 'AFC'),
            
            # NFC East
            ('DAL', 'Dallas Cowboys', 'Arlington', 'East', 'NFC'),
            ('NYG', 'New York Giants', 'East Rutherford', 'East', 'NFC'),
            ('PHI', 'Philadelphia Eagles', 'Philadelphia', 'East', 'NFC'),
            ('WAS', 'Washington Commanders', 'Landover', 'East', 'NFC'),
            
            # NFC North
            ('CHI', 'Chicago Bears', 'Chicago', 'North', 'NFC'),
            ('DET', 'Detroit Lions', 'Detroit', 'North', 'NFC'),
            ('GNB', 'Green Bay Packers', 'Green Bay', 'North', 'NFC'),
            ('MIN', 'Minnesota Vikings', 'Minneapolis', 'North', 'NFC'),
            
            # NFC South
            ('ATL', 'Atlanta Falcons', 'Atlanta', 'South', 'NFC'),
            ('CAR', 'Carolina Panthers', 'Charlotte', 'South', 'NFC'),
            ('NOR', 'New Orleans Saints', 'New Orleans', 'South', 'NFC'),
            ('TAM', 'Tampa Bay Buccaneers', 'Tampa', 'South', 'NFC'),
            
            # NFC West
            ('ARI', 'Arizona Cardinals', 'Glendale', 'West', 'NFC'),
            ('LAR', 'Los Angeles Rams', 'Inglewood', 'West', 'NFC'),
            ('SFO', 'San Francisco 49ers', 'Santa Clara', 'West', 'NFC'),
            ('SEA', 'Seattle Seahawks', 'Seattle', 'West', 'NFC'),
        ]
        
        insert_query = """
        INSERT INTO teams (team_code, team_name, city, division, conference, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (team_code) 
        DO UPDATE SET
            team_name = EXCLUDED.team_name,
            city = EXCLUDED.city,
            division = EXCLUDED.division,
            conference = EXCLUDED.conference
        """
        
        now = datetime.now()
        values = [(team_code, team_name, city, division, conference, now) for team_code, team_name, city, division, conference in teams_data]
        
        try:
            with self.get_connection() as conn:
                with self.get_cursor(conn) as cur:
                    from psycopg2.extras import execute_batch
                    execute_batch(cur, insert_query, values, page_size=100)
                    conn.commit()
            return len(values)
        except Exception as e:
            self.logger.error(f"Error populating teams: {e}")
            raise

    def cleanup_team_codes(self) -> Dict[str, int]:
        """Clean up duplicate team codes, prioritizing 3-letter codes."""
        code_map = {
            'NE': 'NWE',
            'KC': 'KAN',
            'LV': 'LVR',
            'GB': 'GNB',
            'NO': 'NOR',
            'TB': 'TAM',
            'SF': 'SFO',
        }
        
        updated_rows = 0
        deleted_teams = 0
        
        with self.get_connection() as conn:
            with self.get_cursor(conn) as cur:
                for old_code, new_code in code_map.items():
                    try:
                        # Update referencing table
                        update_query = "UPDATE qb_passing_stats SET team = %s WHERE team = %s"
                        cur.execute(update_query, (new_code, old_code))
                        updated_rows += cur.rowcount
                        
                        # Delete old team record
                        delete_query = "DELETE FROM teams WHERE team_code = %s"
                        cur.execute(delete_query, (old_code,))
                        deleted_teams += cur.rowcount
                        
                        self.logger.info(f"Migrated team code {old_code} to {new_code}")

                    except Exception as e:
                        self.logger.error(f"Error migrating {old_code} to {new_code}: {e}")
                        conn.rollback()
                        raise
                
                conn.commit()
                
        return {"updated_passing_stats_rows": updated_rows, "deleted_team_records": deleted_teams}

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