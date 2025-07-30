#!/usr/bin/env python3
"""
Comprehensive test suite for bulk database operations
Tests all bulk insert methods with various scenarios and edge cases
"""

import pytest
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock

import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.db_manager import DatabaseManager
from src.models.qb_models import (
    QBPassingStats, QBSplitsType1, QBSplitsType2, 
    BulkInsertResult, BulkOperationConfig
)
from src.config.config import config


class TestBulkOperations:
    """Test suite for bulk database operations"""
    
    @pytest.fixture
    def db_manager(self):
        """Create a DatabaseManager instance for testing"""
        return DatabaseManager()
    
    @pytest.fixture
    def sample_qb_stats(self) -> List[QBPassingStats]:
        """Generate sample QB passing stats for testing"""
        stats = []
        for i in range(50):
            stat = QBPassingStats(
                pfr_id=f"testqb{i:02d}",
                player_name=f"Test QB {i}",
                player_url=f"https://www.pro-football-reference.com/players/t/testqb{i:02d}.htm",
                season=2024,
                rk=i + 1,
                age=25 + (i % 10),
                team="TST",
                pos="QB",
                g=16,
                gs=16,
                qb_rec="10-6-0",
                cmp=250 + i,
                att=400 + i,
                inc=150 + i,
                cmp_pct=62.5 + (i % 10),
                yds=3000 + (i * 50),
                td=20 + i,
                td_pct=5.0 + (i % 3),
                int=10 + (i % 5),
                int_pct=2.5 + (i % 2),
                first_downs=180 + i,
                succ_pct=45.0 + (i % 10),
                lng=65 + i,
                y_a=7.5 + (i % 3),
                ay_a=7.8 + (i % 3),
                y_c=12.0 + (i % 2),
                y_g=187.5 + (i * 3),
                rate=95.0 + (i % 20),
                qbr=65.0 + (i % 15),
                sk=30 + (i % 10),
                sk_yds=200 + (i * 5),
                sk_pct=7.0 + (i % 3),
                ny_a=6.8 + (i % 2),
                any_a=7.1 + (i % 2),
                four_qc=2 + (i % 3),
                gwd=3 + (i % 4),
                awards="Pro Bowl" if i % 5 == 0 else None,
                player_additional=None
            )
            stats.append(stat)
        return stats
    
    @pytest.fixture
    def sample_qb_splits(self) -> List[QBSplitsType1]:
        """Generate sample QB splits for testing with unique combinations"""
        splits = []
        split_types = ["Home", "Away", "1st Quarter", "2nd Quarter"]
        
        # Ensure unique combinations of pfr_id, season, split, value
        for i in range(40):
            player_idx = i // 10  # 4 players (0-3)
            split_type_idx = i % 4  # 4 different split types
            
            split = QBSplitsType1(
                pfr_id=f"testqb{player_idx:02d}",
                player_name=f"Test QB {player_idx}",
                season=2024,
                split="Place" if split_type_idx < 2 else "Quarter",
                value=split_types[split_type_idx],
                g=4 + (i % 8),
                w=2 + (i % 6),
                l=1 + (i % 3),
                t=0,
                cmp=60 + i,
                att=100 + i,
                inc=40 + i,
                cmp_pct=60.0 + (i % 10),
                yds=750 + (i * 10),
                td=5 + (i % 3),
                int=2 + (i % 2),
                rate=85.0 + (i % 15),
                sk=7 + (i % 5),
                sk_yds=50 + (i * 2),
                y_a=7.5 + (i % 2),
                ay_a=7.8 + (i % 2),
                a_g=25.0 + (i % 5),
                y_g=187.5 + (i % 10),
                rush_att=3 + (i % 4),
                rush_yds=15 + (i % 8),
                rush_y_a=5.0 + (i % 3),
                rush_td=0 + (i % 2),
                rush_a_g=0.75 + (i % 2),
                rush_y_g=3.75 + (i % 3),
                total_td=5 + (i % 3),
                pts=30 + (i % 10),
                fmb=1 + (i % 2),
                fl=0 + (i % 2),
                ff=0,
                fr=0,
                fr_yds=0,
                fr_td=0
            )
            splits.append(split)
        return splits
    
    @pytest.fixture
    def sample_qb_splits_advanced(self) -> List[QBSplitsType2]:
        """Generate sample QB advanced splits for testing with unique combinations"""
        splits = []
        advanced_split_types = ["1st Down", "2nd Down", "3rd Down", "4th Down"]
        
        # Ensure unique combinations of pfr_id, season, split, value
        for i in range(30):
            player_idx = i // 8  # 4 players (0-3) 
            split_type_idx = i % 4  # 4 different down types
            
            split = QBSplitsType2(
                pfr_id=f"testqb{player_idx:02d}",
                player_name=f"Test QB {player_idx}",
                season=2024,
                split="Down",
                value=advanced_split_types[split_type_idx],
                cmp=20 + i,
                att=35 + i,
                inc=15 + i,
                cmp_pct=57.1 + (i % 10),
                yds=250 + (i * 5),
                td=2 + (i % 2),
                first_downs=15 + (i % 5),
                int=1 + (i % 2),
                rate=80.0 + (i % 12),
                sk=2 + (i % 3),
                sk_yds=15 + (i % 5),
                y_a=7.1 + (i % 2),
                ay_a=7.4 + (i % 2),
                rush_att=1 + (i % 3),
                rush_yds=5 + (i % 6),
                rush_y_a=5.0 + (i % 2),
                rush_td=0 + (i % 3),
                rush_first_downs=0 + (i % 2)
            )
            splits.append(split)
        return splits
    
    def test_bulk_insert_result_creation(self):
        """Test BulkInsertResult initialization and methods"""
        result = BulkInsertResult(table_name="test_table")
        
        assert result.table_name == "test_table"
        assert result.success_count == 0
        assert result.failure_count == 0
        assert result.total_count == 0
        assert result.success_rate == 0.0
        assert result.records_per_second == 0.0
        
        # Test adding successes and errors
        result.add_success(10)
        result.add_error("Test error", {"test": "data"})
        result.add_warning("Test warning")
        
        assert result.success_count == 10
        assert result.failure_count == 1
        assert len(result.errors) == 1
        assert len(result.warnings) == 1
        assert len(result.failed_records) == 1
        
        # Test completion
        result.mark_complete()
        assert result.completed_at is not None
        assert result.total_count == 11
        # Use pytest.approx for floating point comparison
        assert result.success_rate == pytest.approx(90.909, rel=1e-2)
    
    def test_bulk_operation_config_validation(self):
        """Test BulkOperationConfig validation"""
        # Valid config
        config = BulkOperationConfig()
        errors = config.validate()
        assert len(errors) == 0
        
        # Invalid config
        invalid_config = BulkOperationConfig(
            batch_size=5,  # Below minimum
            timeout_seconds=-1,  # Invalid
            conflict_strategy="INVALID"  # Invalid strategy
        )
        errors = invalid_config.validate()
        assert len(errors) == 3
        assert any("below minimum" in error for error in errors)
        assert any("Timeout must be positive" in error for error in errors)
        assert any("Conflict strategy must be" in error for error in errors)
    
    def test_batch_size_optimization(self):
        """Test batch size optimization logic"""
        config = BulkOperationConfig(
            batch_size=100,
            memory_limit_mb=10  # Small memory limit
        )
        
        # Test with large record size - should reduce batch size
        optimized = config.optimize_batch_size(1000, 2048)  # 2KB per record
        assert optimized <= config.batch_size  # Should be reduced
        
        # Test with small dataset - should reduce batch size
        small_optimized = config.optimize_batch_size(20, 1024)
        assert small_optimized <= 20
        
        # Test with normal conditions
        normal_optimized = config.optimize_batch_size(500, 512)
        assert normal_optimized <= config.batch_size
    
    @patch('src.database.db_manager.psycopg2.extras.execute_values')
    @patch.object(DatabaseManager, 'get_connection')
    @patch.object(DatabaseManager, 'ensure_team_code')
    def test_bulk_insert_qb_basic_stats_success(self, mock_ensure_team, mock_get_conn, mock_execute_values, db_manager, sample_qb_stats):
        """Test successful bulk insert of QB basic stats"""
        # Mock database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_execute_values.return_value = None
        mock_cursor.rowcount = len(sample_qb_stats)
        
        # Execute bulk insert
        result = db_manager.bulk_insert_qb_basic_stats(
            sample_qb_stats,
            batch_size=10,
            conflict_strategy="UPDATE"
        )
        
        # Verify results
        assert result.table_name == "qb_passing_stats"
        assert result.success_count == len(sample_qb_stats)
        assert result.failure_count == 0
        assert result.batch_size == 10
        assert result.success_rate == 100.0
        assert len(result.errors) == 0
        
        # Verify database calls
        assert mock_execute_values.call_count > 0
        mock_conn.commit.assert_called()
        
        # Verify team code creation
        unique_teams = set(stat.team for stat in sample_qb_stats if stat.team)
        assert mock_ensure_team.call_count >= len(unique_teams)
    
    @patch('src.database.db_manager.psycopg2.extras.execute_values')
    @patch.object(DatabaseManager, 'get_connection')
    def test_bulk_insert_qb_splits_success(self, mock_get_conn, mock_execute_values, db_manager, sample_qb_splits):
        """Test successful bulk insert of QB splits"""
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_execute_values.return_value = None
        mock_cursor.rowcount = len(sample_qb_splits)
        
        # Execute bulk insert
        result = db_manager.bulk_insert_qb_splits(
            sample_qb_splits,
            batch_size=15,
            conflict_strategy="IGNORE"
        )
        
        # Verify results
        assert result.table_name == "qb_splits"
        assert result.success_count == len(sample_qb_splits)
        assert result.failure_count == 0
        assert result.batch_size == 15
        assert result.success_rate == 100.0
        
        # Verify database calls
        assert mock_execute_values.call_count > 0
        mock_conn.commit.assert_called()
    
    @patch('src.database.db_manager.psycopg2.extras.execute_values')
    @patch.object(DatabaseManager, 'get_connection')
    def test_bulk_insert_qb_splits_advanced_success(self, mock_get_conn, mock_execute_values, db_manager, sample_qb_splits_advanced):
        """Test successful bulk insert of QB advanced splits"""
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_execute_values.return_value = None
        mock_cursor.rowcount = len(sample_qb_splits_advanced)
        
        # Execute bulk insert
        result = db_manager.bulk_insert_qb_splits_advanced(
            sample_qb_splits_advanced,
            batch_size=8,
            conflict_strategy="UPDATE"
        )
        
        # Verify results
        assert result.table_name == "qb_splits_advanced"
        assert result.success_count == len(sample_qb_splits_advanced)
        assert result.failure_count == 0
        assert result.batch_size == 8
        assert result.success_rate == 100.0
        
        # Verify database calls
        assert mock_execute_values.call_count > 0
        mock_conn.commit.assert_called()
    
    @patch('src.database.db_manager.psycopg2.extras.execute_values')
    @patch.object(DatabaseManager, 'get_connection')
    def test_bulk_insert_with_validation_errors(self, mock_get_conn, mock_execute_values, db_manager):
        """Test bulk insert with validation errors"""
        # Create invalid stats (missing required fields)
        invalid_stats = [
            QBPassingStats(pfr_id="", player_name="", player_url="", season=1900),  # Invalid
            QBPassingStats(pfr_id="valid01", player_name="Valid Player", player_url="http://test.com", season=2024),  # Valid
            QBPassingStats(pfr_id="invalid02", player_name="Invalid Player", player_url="http://test.com", season=3000)  # Invalid season
        ]
        
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_execute_values.return_value = None
        mock_cursor.rowcount = 1  # Only one valid record
        
        # Execute bulk insert
        result = db_manager.bulk_insert_qb_basic_stats(invalid_stats)
        
        # Verify that invalid records were filtered out
        assert result.success_count == 1  # Only the valid record
        assert result.failure_count == 2  # Two invalid records
        assert len(result.errors) == 2
        # Use pytest.approx for floating point comparison (1/3 = 33.33%)
        assert result.success_rate == pytest.approx(33.333, rel=1e-2)
    
    @patch('src.database.db_manager.psycopg2.extras.execute_values')
    @patch.object(DatabaseManager, 'get_connection')
    def test_bulk_insert_with_database_errors(self, mock_get_conn, mock_execute_values, db_manager, sample_qb_stats):
        """Test bulk insert with database errors and retry logic"""
        # Mock database connection
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        
        # Mock execute_values to fail first, then succeed
        mock_execute_values.side_effect = [Exception("Database error"), None]
        mock_cursor.rowcount = len(sample_qb_stats)
        
        # Execute bulk insert (should retry and succeed)
        result = db_manager.bulk_insert_qb_basic_stats(sample_qb_stats[:5], batch_size=5)
        
        # Verify retry logic worked
        assert mock_execute_values.call_count == 2  # Failed once, then succeeded
        assert result.success_count > 0  # Should have some successes after retry
    
    @patch.object(DatabaseManager, 'bulk_insert_qb_basic_stats')
    @patch.object(DatabaseManager, 'bulk_insert_qb_splits')
    @patch.object(DatabaseManager, 'bulk_insert_qb_splits_advanced')
    def test_bulk_insert_combined(self, mock_advanced, mock_splits, mock_basic, db_manager, 
                                 sample_qb_stats, sample_qb_splits, sample_qb_splits_advanced):
        """Test coordinated bulk insert of all data types"""
        # Mock individual bulk insert methods
        mock_basic.return_value = BulkInsertResult(table_name="qb_passing_stats", success_count=50)
        mock_splits.return_value = BulkInsertResult(table_name="qb_splits", success_count=40)
        mock_advanced.return_value = BulkInsertResult(table_name="qb_splits_advanced", success_count=30)
        
        # Execute combined bulk insert
        results = db_manager.bulk_insert_combined(
            qb_stats=sample_qb_stats,
            qb_splits=sample_qb_splits,
            qb_splits_advanced=sample_qb_splits_advanced,
            batch_size=20,
            session_id="test_session_123"
        )
        
        # Verify all methods were called
        mock_basic.assert_called_once()
        mock_splits.assert_called_once()
        mock_advanced.assert_called_once()
        
        # Verify results structure
        assert len(results) == 3
        assert "qb_passing_stats" in results
        assert "qb_splits" in results
        assert "qb_splits_advanced" in results
        
        # Verify each result
        assert results["qb_passing_stats"].success_count == 50
        assert results["qb_splits"].success_count == 40
        assert results["qb_splits_advanced"].success_count == 30
    
    def test_empty_data_handling(self, db_manager):
        """Test bulk insert with empty data lists"""
        # Test empty QB stats
        result = db_manager.bulk_insert_qb_basic_stats([])
        assert result.success_count == 0
        assert result.failure_count == 0
        assert result.total_count == 0
        assert result.completed_at is not None
        
        # Test empty splits
        result = db_manager.bulk_insert_qb_splits([])
        assert result.success_count == 0
        assert result.total_count == 0
        
        # Test empty advanced splits
        result = db_manager.bulk_insert_qb_splits_advanced([])
        assert result.success_count == 0
        assert result.total_count == 0
    
    def test_conflict_strategy_sql_generation(self, db_manager):
        """Test SQL generation for different conflict strategies"""
        # Test UPDATE strategy
        update_clause = db_manager._handle_bulk_conflict_strategy("UPDATE")
        assert "ON CONFLICT" in update_clause
        
        # Test IGNORE strategy
        ignore_clause = db_manager._handle_bulk_conflict_strategy("IGNORE")
        assert "DO NOTHING" in ignore_clause
        
        # Test FAIL strategy
        fail_clause = db_manager._handle_bulk_conflict_strategy("FAIL")
        assert fail_clause == ""
    
    @patch('time.sleep')
    def test_exponential_backoff_retry(self, mock_sleep, db_manager):
        """Test exponential backoff retry logic"""
        call_count = 0
        
        def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception(f"Attempt {call_count} failed")
            return "Success"
        
        # Should succeed on third attempt
        result = db_manager._retry_with_exponential_backoff(failing_operation, max_retries=3, base_delay=0.1)
        assert result == "Success"
        assert call_count == 3
        assert mock_sleep.call_count == 2  # Two retries with delays
        
        # Verify exponential backoff delays
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_calls[0] == 0.1  # Base delay
        assert sleep_calls[1] == 0.2  # 2x base delay
    
    def test_batch_generator(self, db_manager):
        """Test batch generation utility"""
        data = list(range(25))  # 25 items
        batch_size = 10
        
        batches = list(db_manager._batch_generator(data, batch_size))
        
        assert len(batches) == 3  # 25 items in batches of 10 = 3 batches
        assert len(batches[0]) == 10  # First batch full
        assert len(batches[1]) == 10  # Second batch full
        assert len(batches[2]) == 5   # Third batch partial
        
        # Verify all data is preserved
        all_items = []
        for batch in batches:
            all_items.extend(batch)
        assert all_items == data


class TestBulkOperationPerformance:
    """Performance tests for bulk operations"""
    
    def generate_large_dataset(self, size: int) -> List[QBPassingStats]:
        """Generate a large dataset for performance testing"""
        return [
            QBPassingStats(
                pfr_id=f"perftest{i:06d}",
                player_name=f"Performance Test QB {i}",
                player_url=f"https://test.com/player{i}",
                season=2024,
                rk=i,
                team="TST"
            )
            for i in range(size)
        ]
    
    @pytest.mark.performance
    @patch('src.database.db_manager.psycopg2.extras.execute_values')
    @patch.object(DatabaseManager, 'get_connection')
    @patch.object(DatabaseManager, 'ensure_team_code')
    def test_bulk_insert_performance_vs_individual(self, mock_ensure_team, mock_get_conn, mock_execute_values):
        """Test performance improvement of bulk vs individual inserts"""
        db_manager = DatabaseManager()
        
        # Mock database operations
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_get_conn.return_value.__enter__.return_value = mock_conn
        mock_execute_values.return_value = None
        mock_cursor.rowcount = 1
        
        # Generate test data
        test_data = self.generate_large_dataset(1000)
        
        # Time bulk insert
        start_time = time.time()
        bulk_result = db_manager.bulk_insert_qb_basic_stats(test_data, batch_size=100)
        bulk_time = time.time() - start_time
        
        # Simulate individual inserts (mock them for speed)
        start_time = time.time()
        for _ in test_data:
            mock_execute_values.return_value = None  # Simulate individual insert
        individual_time = time.time() - start_time
        
        # Calculate improvement (bulk should be much faster due to fewer DB calls)
        bulk_db_calls = mock_execute_values.call_count
        expected_individual_calls = len(test_data)
        
        # Bulk should make significantly fewer database calls
        improvement_ratio = expected_individual_calls / bulk_db_calls
        assert improvement_ratio >= 5  # At least 5x fewer database calls
        
        # Verify bulk result
        assert bulk_result.success_count == len(test_data)
        assert bulk_result.records_per_second > 0
    
    @pytest.mark.performance
    def test_memory_usage_optimization(self):
        """Test memory usage with large datasets"""
        config = BulkOperationConfig(
            batch_size=1000,
            memory_limit_mb=50  # 50MB limit
        )
        
        # Test with large record size
        large_record_size = 10 * 1024  # 10KB per record
        optimized_batch = config.optimize_batch_size(10000, large_record_size)
        
        # Should reduce batch size to fit memory constraint
        max_records_in_memory = (50 * 1024 * 1024) // large_record_size
        assert optimized_batch <= max_records_in_memory
        assert optimized_batch >= config.min_batch_size


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"]) 