#!/usr/bin/env python3
"""
Performance Benchmarking Script for Bulk Database Operations
Demonstrates 80-90% performance improvement over individual inserts
"""

import sys
import os
import time
import statistics
import psutil
import gc
from datetime import datetime
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import random
import uuid

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.db_manager import DatabaseManager
from src.models.qb_models import QBPassingStats, QBSplitsType1, QBSplitsType2, BulkInsertResult, Player
from src.config.config import config


@dataclass
class BenchmarkResult:
    """Result of a benchmark test"""
    test_name: str
    record_count: int
    execution_time: float
    records_per_second: float
    memory_peak_mb: float
    database_calls: int
    success_rate: float
    errors: List[str]
    
    def __str__(self) -> str:
        return (
            f"{self.test_name}: {self.record_count} records in {self.execution_time:.2f}s "
            f"({self.records_per_second:.1f} rec/s, {self.memory_peak_mb:.1f}MB peak, "
            f"{self.database_calls} DB calls, {self.success_rate:.1f}% success)"
        )


class PerformanceBenchmark:
    """Comprehensive performance benchmarking for bulk operations"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.results: List[BenchmarkResult] = []
        self.process = psutil.Process()
    
    def generate_qb_stats(self, count: int) -> List[QBPassingStats]:
        """Generate realistic QB stats for benchmarking"""
        stats = []
        teams = ["BUF", "MIA", "NWE", "NYJ", "BAL", "CIN", "CLE", "PIT", "HOU", "IND"]
        
        # First, create and insert the required players
        players = []
        for i in range(count):
            player = Player(
                pfr_id=f"bench{i:06d}",
                player_name=f"Benchmark QB {i}",
                pfr_url=f"https://www.pro-football-reference.com/players/b/bench{i:06d}.htm",
                position="QB",
                age=random.randint(22, 40)
            )
            players.append(player)
        
        # Insert players first to satisfy foreign key constraints
        try:
            player_result = self.db_manager.insert_players(players)
            print(f"✅ Created {player_result} player records for benchmarking")
        except Exception as e:
            print(f"⚠️  Warning: Could not create player records: {e}")
            print("Continuing with benchmark anyway...")
        
        for i in range(count):
            stat = QBPassingStats(
                pfr_id=f"bench{i:06d}",
                player_name=f"Benchmark QB {i}",
                player_url=f"https://www.pro-football-reference.com/players/b/bench{i:06d}.htm",
                season=2024,
                rk=i + 1,
                age=random.randint(22, 40),
                team=random.choice(teams),
                pos="QB",
                g=random.randint(1, 17),
                gs=random.randint(0, 17),
                qb_rec=f"{random.randint(0, 17)}-{random.randint(0, 17)}-0",
                cmp=random.randint(100, 500),
                att=random.randint(150, 750),
                inc=random.randint(50, 250),
                cmp_pct=random.uniform(50.0, 80.0),
                yds=random.randint(1000, 6000),
                td=random.randint(5, 60),
                td_pct=random.uniform(2.0, 8.0),
                int=random.randint(0, 25),
                int_pct=random.uniform(0.5, 4.0),
                first_downs=random.randint(50, 300),
                succ_pct=random.uniform(30.0, 60.0),
                lng=random.randint(20, 99),
                y_a=random.uniform(4.0, 12.0),
                ay_a=random.uniform(4.0, 12.0),
                y_c=random.uniform(8.0, 20.0),
                y_g=random.uniform(100.0, 400.0),
                rate=random.uniform(50.0, 130.0),
                qbr=random.uniform(20.0, 90.0),
                sk=random.randint(10, 70),
                sk_yds=random.randint(50, 500),
                sk_pct=random.uniform(3.0, 12.0),
                ny_a=random.uniform(3.0, 10.0),
                any_a=random.uniform(3.0, 10.0),
                four_qc=random.randint(0, 8),
                gwd=random.randint(0, 10),
                awards="Pro Bowl" if random.random() < 0.1 else None,
                player_additional=None
            )
            stats.append(stat)
        
        return stats
    
    def generate_qb_splits(self, count: int) -> List[QBSplitsType1]:
        """Generate realistic QB splits for benchmarking with unique constraint combinations"""
        splits = []
        split_types = [
            ("Place", ["Home", "Away"]),
            ("Quarter", ["1st Quarter", "2nd Quarter", "3rd Quarter", "4th Quarter"]),
            ("Down", ["1st Down", "2nd Down", "3rd Down", "4th Down"]),
            ("Field Position", ["Own 1-20", "Own 21-40", "Opp 21-40", "Red Zone"])
        ]
        
        # Calculate how many players we need based on count
        # Each player can have multiple splits, but ensure uniqueness
        num_players = min(count // 4, 100)  # At least 4 splits per player, max 100 players
        if num_players == 0:
            num_players = 1
        
        # First, create and insert the required players
        players = []
        for i in range(num_players):
            player = Player(
                pfr_id=f"bench{i:06d}",
                player_name=f"Benchmark QB {i}",
                pfr_url=f"https://www.pro-football-reference.com/players/b/bench{i:06d}.htm",
                position="QB",
                age=random.randint(22, 40)
            )
            players.append(player)
        
        # Insert players first to satisfy foreign key constraints
        try:
            player_result = self.db_manager.insert_players(players)
            print(f"✅ Created {player_result} player records for splits benchmarking")
        except Exception as e:
            print(f"⚠️  Warning: Could not create player records for splits: {e}")
            print("Continuing with benchmark anyway...")
        
        # Track used combinations to ensure uniqueness
        used_combinations = set()
        generated_count = 0
        
        # Generate splits ensuring unique (pfr_id, season, split, value) combinations
        for player_idx in range(num_players):
            if generated_count >= count:
                break
                
            pfr_id = f"bench{player_idx:06d}"
            player_name = f"Benchmark QB {player_idx}"
            
            # For each player, generate splits from different categories
            for split_type, values in split_types:
                if generated_count >= count:
                    break
                    
                for split_value in values:
                    if generated_count >= count:
                        break
                    
                    # Create unique combination key
                    combination_key = (pfr_id, 2024, split_type, split_value)
                    
                    # Skip if combination already exists
                    if combination_key in used_combinations:
                        continue
                    
                    used_combinations.add(combination_key)
                    
                    split = QBSplitsType1(
                        pfr_id=pfr_id,
                        player_name=player_name,
                        season=2024,
                        split=split_type,
                        value=split_value,
                        g=random.randint(1, 8),
                        w=random.randint(0, 8),
                        l=random.randint(0, 8),
                        t=0,
                        cmp=random.randint(20, 150),
                        att=random.randint(30, 200),
                        inc=random.randint(10, 80),
                        cmp_pct=random.uniform(50.0, 80.0),
                        yds=random.randint(200, 2000),
                        td=random.randint(1, 20),
                        int=random.randint(0, 8),
                        rate=random.uniform(50.0, 130.0),
                        sk=random.randint(1, 20),
                        sk_yds=random.randint(5, 150),
                        y_a=random.uniform(4.0, 12.0),
                        ay_a=random.uniform(4.0, 12.0),
                        a_g=random.uniform(10.0, 50.0),
                        y_g=random.uniform(50.0, 300.0),
                        rush_att=random.randint(0, 15),
                        rush_yds=random.randint(0, 100),
                        rush_y_a=random.uniform(2.0, 8.0),
                        rush_td=random.randint(0, 5),
                        rush_a_g=random.uniform(0.0, 5.0),
                        rush_y_g=random.uniform(0.0, 25.0),
                        total_td=random.randint(1, 25),
                        pts=random.randint(6, 150),
                        fmb=random.randint(0, 5),
                        fl=random.randint(0, 3),
                        ff=random.randint(0, 2),
                        fr=random.randint(0, 2),
                        fr_yds=random.randint(0, 50),
                        fr_td=random.randint(0, 1)
                    )
                    splits.append(split)
                    generated_count += 1
        
        print(f"Generated {len(splits)} unique QB splits records")
        return splits
    
    def monitor_memory(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def benchmark_individual_inserts(self, stats: List[QBPassingStats]) -> BenchmarkResult:
        """Benchmark individual insert performance (for comparison)"""
        print(f"Benchmarking individual inserts for {len(stats)} records...")
        
        # Clear any caches
        gc.collect()
        
        start_memory = self.monitor_memory()
        peak_memory = start_memory
        database_calls = 0
        errors = []
        success_count = 0
        
        start_time = time.time()
        
        try:
            for stat in stats:
                try:
                    # Simulate individual insert call
                    result = self.db_manager.insert_qb_basic_stats([stat])
                    database_calls += 1
                    success_count += result
                    
                    # Monitor memory
                    current_memory = self.monitor_memory()
                    peak_memory = max(peak_memory, current_memory)
                    
                except Exception as e:
                    errors.append(str(e))
        
        except Exception as e:
            errors.append(f"Major error during individual inserts: {e}")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return BenchmarkResult(
            test_name="Individual Inserts",
            record_count=len(stats),
            execution_time=execution_time,
            records_per_second=len(stats) / execution_time if execution_time > 0 else 0,
            memory_peak_mb=peak_memory,
            database_calls=database_calls,
            success_rate=(success_count / len(stats)) * 100 if stats else 0,
            errors=errors
        )
    
    def benchmark_bulk_insert(self, stats: List[QBPassingStats], batch_size: int = 100) -> BenchmarkResult:
        """Benchmark bulk insert performance"""
        print(f"Benchmarking bulk insert for {len(stats)} records with batch size {batch_size}...")
        
        # Clear any caches
        gc.collect()
        
        start_memory = self.monitor_memory()
        peak_memory = start_memory
        
        start_time = time.time()
        
        try:
            # Monitor memory during operation
            def memory_monitor():
                nonlocal peak_memory
                current_memory = self.monitor_memory()
                peak_memory = max(peak_memory, current_memory)
            
            # Execute bulk insert
            result = self.db_manager.bulk_insert_qb_basic_stats(
                stats,
                batch_size=batch_size,
                conflict_strategy="UPDATE",
                enable_progress_tracking=True
            )
            
            memory_monitor()
            
        except Exception as e:
            result = BulkInsertResult(table_name="qb_passing_stats")
            result.add_error(str(e))
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Estimate database calls (batches + overhead)
        estimated_db_calls = (len(stats) // batch_size) + (1 if len(stats) % batch_size else 0)
        
        return BenchmarkResult(
            test_name=f"Bulk Insert (batch={batch_size})",
            record_count=len(stats),
            execution_time=execution_time,
            records_per_second=result.records_per_second,
            memory_peak_mb=peak_memory,
            database_calls=estimated_db_calls,
            success_rate=result.success_rate,
            errors=result.errors
        )
    
    def benchmark_bulk_splits_insert(self, splits: List[QBSplitsType1], batch_size: int = 100) -> BenchmarkResult:
        """Benchmark bulk splits insert performance"""
        print(f"Benchmarking bulk splits insert for {len(splits)} records...")
        
        gc.collect()
        start_memory = self.monitor_memory()
        peak_memory = start_memory
        
        start_time = time.time()
        
        try:
            result = self.db_manager.bulk_insert_qb_splits(
                splits,
                batch_size=batch_size,
                conflict_strategy="UPDATE"
            )
            
            current_memory = self.monitor_memory()
            peak_memory = max(peak_memory, current_memory)
            
        except Exception as e:
            result = BulkInsertResult(table_name="qb_splits")
            result.add_error(str(e))
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        estimated_db_calls = (len(splits) // batch_size) + (1 if len(splits) % batch_size else 0)
        
        return BenchmarkResult(
            test_name=f"Bulk Splits Insert (batch={batch_size})",
            record_count=len(splits),
            execution_time=execution_time,
            records_per_second=result.records_per_second,
            memory_peak_mb=peak_memory,
            database_calls=estimated_db_calls,
            success_rate=result.success_rate,
            errors=result.errors
        )
    
    def benchmark_combined_operations(self, stats: List[QBPassingStats], splits: List[QBSplitsType1]) -> BenchmarkResult:
        """Benchmark combined bulk operations"""
        print(f"Benchmarking combined operations: {len(stats)} stats + {len(splits)} splits...")
        
        gc.collect()
        start_memory = self.monitor_memory()
        peak_memory = start_memory
        
        start_time = time.time()
        
        try:
            results = self.db_manager.bulk_insert_combined(
                qb_stats=stats,
                qb_splits=splits,
                batch_size=100,
                session_id=f"benchmark_{uuid.uuid4().hex[:8]}"
            )
            
            current_memory = self.monitor_memory()
            peak_memory = max(peak_memory, current_memory)
            
            # Aggregate results
            total_success = sum(r.success_count for r in results.values())
            total_records = len(stats) + len(splits)
            success_rate = (total_success / total_records) * 100 if total_records > 0 else 0
            
            all_errors = []
            estimated_calls = 0
            for result in results.values():
                all_errors.extend(result.errors)
                estimated_calls += result.batches_processed
            
        except Exception as e:
            total_success = 0
            total_records = len(stats) + len(splits)
            success_rate = 0
            all_errors = [str(e)]
            estimated_calls = 0
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        return BenchmarkResult(
            test_name="Combined Bulk Operations",
            record_count=total_records,
            execution_time=execution_time,
            records_per_second=total_records / execution_time if execution_time > 0 else 0,
            memory_peak_mb=peak_memory,
            database_calls=estimated_calls,
            success_rate=success_rate,
            errors=all_errors
        )
    
    def run_comprehensive_benchmark(self, test_sizes: List[int] = None) -> Dict[str, Any]:
        """Run comprehensive performance benchmarks"""
        if test_sizes is None:
            test_sizes = [100, 500, 1000, 2000]
        
        print("="*80)
        print("COMPREHENSIVE BULK OPERATIONS PERFORMANCE BENCHMARK")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database: {config.database.connection_string[:50]}...")
        print(f"System: {psutil.cpu_count()} CPU cores, {psutil.virtual_memory().total // (1024**3)}GB RAM")
        print()
        
        all_results = {}
        
        for size in test_sizes:
            print(f"\n📊 TESTING WITH {size} RECORDS")
            print("-" * 50)
            
            # Generate test data
            print("Generating test data...")
            stats = self.generate_qb_stats(size)
            splits = self.generate_qb_splits(size)
            
            size_results = {}
            
            # Benchmark individual inserts (only for smaller datasets)
            if size <= 500:  # Skip individual inserts for large datasets to save time
                individual_result = self.benchmark_individual_inserts(stats[:min(100, size)])
                size_results["individual"] = individual_result
                self.results.append(individual_result)
                print(f"✓ {individual_result}")
            
            # Benchmark bulk inserts with different batch sizes
            for batch_size in [50, 100, 200]:
                if batch_size <= size:  # Only test relevant batch sizes
                    bulk_result = self.benchmark_bulk_insert(stats, batch_size)
                    size_results[f"bulk_{batch_size}"] = bulk_result
                    self.results.append(bulk_result)
                    print(f"✓ {bulk_result}")
            
            # Benchmark splits
            splits_result = self.benchmark_bulk_splits_insert(splits[:min(size, len(splits))])
            size_results["splits"] = splits_result
            self.results.append(splits_result)
            print(f"✓ {splits_result}")
            
            # Benchmark combined operations
            combined_result = self.benchmark_combined_operations(
                stats[:min(size//2, len(stats))], 
                splits[:min(size//2, len(splits))]
            )
            size_results["combined"] = combined_result
            self.results.append(combined_result)
            print(f"✓ {combined_result}")
            
            all_results[size] = size_results
            
            # Calculate and display performance improvements
            if "individual" in size_results and "bulk_100" in size_results:
                self._display_improvement_analysis(size_results["individual"], size_results["bulk_100"])
        
        return all_results
    
    def _display_improvement_analysis(self, individual: BenchmarkResult, bulk: BenchmarkResult):
        """Display performance improvement analysis"""
        print("\n📈 PERFORMANCE IMPROVEMENT ANALYSIS")
        print("-" * 40)
        
        # Calculate improvements
        speed_improvement = (bulk.records_per_second / individual.records_per_second - 1) * 100
        time_reduction = (1 - bulk.execution_time / individual.execution_time) * 100
        db_calls_reduction = (1 - bulk.database_calls / individual.database_calls) * 100
        
        print(f"Speed Improvement: {speed_improvement:.1f}% faster")
        print(f"Time Reduction: {time_reduction:.1f}% less time")
        print(f"Database Calls Reduction: {db_calls_reduction:.1f}% fewer calls")
        print(f"Memory Efficiency: {bulk.memory_peak_mb:.1f}MB vs {individual.memory_peak_mb:.1f}MB")
        
        # Determine if we met the 80-90% improvement target
        if time_reduction >= 80:
            print("🎯 TARGET ACHIEVED: 80-90% performance improvement!")
        elif time_reduction >= 70:
            print("🎯 STRONG IMPROVEMENT: 70%+ performance improvement")
        else:
            print("⚠️  Improvement below target, consider optimization")
    
    def generate_report(self) -> str:
        """Generate a comprehensive benchmark report"""
        report = []
        report.append("="*80)
        report.append("BULK OPERATIONS PERFORMANCE BENCHMARK REPORT")
        report.append("="*80)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Summary statistics
        if self.results:
            avg_speed = statistics.mean(r.records_per_second for r in self.results if r.records_per_second > 0)
            max_speed = max(r.records_per_second for r in self.results if r.records_per_second > 0)
            avg_memory = statistics.mean(r.memory_peak_mb for r in self.results)
            
            report.append("SUMMARY STATISTICS")
            report.append("-" * 30)
            report.append(f"Total Tests: {len(self.results)}")
            report.append(f"Average Speed: {avg_speed:.1f} records/second")
            report.append(f"Peak Speed: {max_speed:.1f} records/second")
            report.append(f"Average Memory Usage: {avg_memory:.1f} MB")
            report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS")
        report.append("-" * 30)
        for result in self.results:
            report.append(str(result))
            if result.errors:
                report.append(f"  Errors: {len(result.errors)}")
                for error in result.errors[:3]:  # Show first 3 errors
                    report.append(f"    - {error}")
        
        report.append("")
        report.append("RECOMMENDATIONS")
        report.append("-" * 30)
        
        # Find optimal batch size
        bulk_results = [r for r in self.results if "Bulk Insert" in r.test_name]
        if bulk_results:
            best_bulk = max(bulk_results, key=lambda x: x.records_per_second)
            report.append(f"Optimal Configuration: {best_bulk.test_name}")
            report.append(f"Best Performance: {best_bulk.records_per_second:.1f} records/second")
        
        # Memory recommendations
        high_memory_tests = [r for r in self.results if r.memory_peak_mb > 500]
        if high_memory_tests:
            report.append("Memory Optimization: Consider smaller batch sizes for large datasets")
        
        return "\n".join(report)


def main():
    """Main benchmark execution"""
    print("Initializing Performance Benchmark...")
    
    # Initialize database manager
    try:
        db_manager = DatabaseManager()
        
        # Test database connection
        if not db_manager.test_connection():
            print("❌ Database connection failed! Please check your configuration.")
            return
        
        print("✅ Database connection successful")
        
    except Exception as e:
        print(f"❌ Failed to initialize database manager: {e}")
        return
    
    # Create benchmark instance
    benchmark = PerformanceBenchmark(db_manager)
    
    try:
        # Run comprehensive benchmarks
        results = benchmark.run_comprehensive_benchmark([100, 500, 1000])
        
        # Generate and display report
        print("\n" + "="*80)
        print("FINAL BENCHMARK REPORT")
        print("="*80)
        report = benchmark.generate_report()
        print(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"logs/bulk_operations_benchmark_{timestamp}.txt"
        os.makedirs("logs", exist_ok=True)
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"\n📄 Full report saved to: {report_file}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Benchmark interrupted by user")
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            db_manager.close()
        except:
            pass


if __name__ == "__main__":
    main() 