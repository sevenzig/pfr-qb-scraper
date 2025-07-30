#!/usr/bin/env python3
"""
Advanced Data Management System for NFL QB Data
Handles data validation, export/import, integrity checking, and quality monitoring
"""

import json
import csv
import logging
import sys
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import hashlib
import sqlite3
from contextlib import contextmanager

try:
    from src.database.db_manager import DatabaseManager
    from src.models.qb_models import QBBasicStats, QBAdvancedStats, QBSplitStats, Player
    from src.config.config import config
except ImportError:
    # Fallback for testing
    DatabaseManager = None
    QBBasicStats = None
    QBAdvancedStats = None
    QBSplitStats = None
    Player = None
    config = None

logger = logging.getLogger(__name__)


@dataclass
class DataQualityMetrics:
    """Metrics for data quality assessment"""
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    missing_fields: int = 0
    duplicate_records: int = 0
    data_integrity_score: float = 0.0
    last_updated: Optional[datetime] = None
    
    def calculate_integrity_score(self) -> float:
        """Calculate data integrity score (0-100)"""
        if self.total_records == 0:
            return 0.0
        
        valid_ratio = self.valid_records / self.total_records
        missing_penalty = min(self.missing_fields / self.total_records, 0.3)
        duplicate_penalty = min(self.duplicate_records / self.total_records, 0.2)
        
        score = (valid_ratio - missing_penalty - duplicate_penalty) * 100
        return max(0.0, min(100.0, score))


@dataclass
class ValidationRule:
    """Data validation rule definition"""
    name: str
    description: str
    severity: str  # 'error', 'warning', 'info'
    field: str
    rule_type: str  # 'required', 'range', 'format', 'relationship'
    parameters: Dict[str, Any]
    
    def validate(self, value: Any, context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Validate a value against this rule"""
        if self.rule_type == 'required':
            return self._validate_required(value)
        elif self.rule_type == 'range':
            return self._validate_range(value)
        elif self.rule_type == 'format':
            return self._validate_format(value)
        elif self.rule_type == 'relationship':
            return self._validate_relationship(value, context or {})
        else:
            return True, "Unknown rule type"
    
    def _validate_required(self, value: Any) -> Tuple[bool, str]:
        """Validate required field"""
        if value is None or (isinstance(value, str) and not value.strip()):
            return False, f"Field {self.field} is required"
        return True, "Valid"
    
    def _validate_range(self, value: Any) -> Tuple[bool, str]:
        """Validate value is within range"""
        if value is None:
            return True, "Skipped (null value)"
        
        try:
            num_value = float(value)
            min_val = self.parameters.get('min')
            max_val = self.parameters.get('max')
            
            if min_val is not None and num_value < min_val:
                return False, f"Value {num_value} below minimum {min_val}"
            if max_val is not None and num_value > max_val:
                return False, f"Value {num_value} above maximum {max_val}"
            
            return True, "Valid"
        except (ValueError, TypeError):
            return False, f"Value {value} is not numeric"
    
    def _validate_format(self, value: Any) -> Tuple[bool, str]:
        """Validate format"""
        if value is None:
            return True, "Skipped (null value)"
        
        pattern = self.parameters.get('pattern')
        if pattern and isinstance(value, str):
            import re
            if not re.match(pattern, value):
                return False, f"Value {value} does not match pattern {pattern}"
        
        return True, "Valid"
    
    def _validate_relationship(self, value: Any, context: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate relationships between fields"""
        if value is None:
            return True, "Skipped (null value)"
        
        # Example: completion percentage should be between 0-100
        if self.field == 'cmp_pct' and isinstance(value, (int, float)):
            if not (0 <= value <= 100):
                return False, f"Completion percentage {value} should be between 0-100"
        
        # Example: attempts should be >= completions
        if self.field == 'att' and 'cmp' in context:
            if value < context['cmp']:
                return False, f"Attempts {value} should be >= completions {context['cmp']}"
        
        return True, "Valid"


class DataValidationEngine:
    """Engine for validating QB data quality and integrity"""
    
    def __init__(self):
        """Initialize validation engine with default rules"""
        self.rules = self._create_default_rules()
    
    def _create_default_rules(self) -> List[ValidationRule]:
        """Create default validation rules for QB data"""
        rules = [
            # Required fields
            ValidationRule(
                name="player_name_required",
                description="Player name is required",
                severity="error",
                field="player_name",
                rule_type="required",
                parameters={}
            ),
            ValidationRule(
                name="season_required",
                description="Season is required",
                severity="error",
                field="season",
                rule_type="required",
                parameters={}
            ),
            
            # Range validations
            ValidationRule(
                name="completion_pct_range",
                description="Completion percentage should be 0-100",
                severity="warning",
                field="cmp_pct",
                rule_type="range",
                parameters={"min": 0, "max": 100}
            ),
            ValidationRule(
                name="rating_range",
                description="Passer rating should be 0-158.3",
                severity="warning",
                field="rate",
                rule_type="range",
                parameters={"min": 0, "max": 158.3}
            ),
            ValidationRule(
                name="age_range",
                description="Player age should be 18-50",
                severity="warning",
                field="age",
                rule_type="range",
                parameters={"min": 18, "max": 50}
            ),
            
            # Format validations
            ValidationRule(
                name="team_code_format",
                description="Team code should be 2-3 characters",
                severity="warning",
                field="team",
                rule_type="format",
                parameters={"pattern": r"^[A-Z]{2,3}$"}
            ),
            
            # Relationship validations
            ValidationRule(
                name="attempts_vs_completions",
                description="Attempts should be >= completions",
                severity="error",
                field="att",
                rule_type="relationship",
                parameters={}
            ),
            ValidationRule(
                name="yards_per_attempt_consistency",
                description="Yards per attempt should be consistent",
                severity="warning",
                field="y_a",
                rule_type="relationship",
                parameters={}
            )
        ]
        return rules
    
    def validate_record(self, record: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate a single record against all rules"""
        issues = []
        
        for rule in self.rules:
            value = record.get(rule.field)
            context = {k: v for k, v in record.items() if k != rule.field}
            
            is_valid, message = rule.validate(value, context)
            
            if not is_valid:
                issues.append({
                    'rule_name': rule.name,
                    'field': rule.field,
                    'severity': rule.severity,
                    'message': message,
                    'value': value
                })
        
        return issues
    
    def validate_dataset(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate entire dataset and return quality report"""
        total_records = len(records)
        valid_records = 0
        invalid_records = 0
        total_issues = 0
        issues_by_severity = {'error': 0, 'warning': 0, 'info': 0}
        field_issues = {}
        
        for record in records:
            record_issues = self.validate_record(record)
            
            if not record_issues:
                valid_records += 1
            else:
                invalid_records += 1
                total_issues += len(record_issues)
                
                for issue in record_issues:
                    # Count by severity
                    issues_by_severity[issue['severity']] += 1
                    
                    # Count by field
                    field = issue['field']
                    if field not in field_issues:
                        field_issues[field] = 0
                    field_issues[field] += 1
        
        # Calculate quality metrics
        quality_metrics = DataQualityMetrics(
            total_records=total_records,
            valid_records=valid_records,
            invalid_records=invalid_records,
            data_integrity_score=valid_records / total_records * 100 if total_records > 0 else 0,
            last_updated=datetime.now()
        )
        
        return {
            'quality_metrics': quality_metrics,
            'total_issues': total_issues,
            'issues_by_severity': issues_by_severity,
            'field_issues': field_issues,
            'validation_timestamp': datetime.now()
        }


class DataManager:
    """Advanced data management system for QB data"""
    
    def __init__(self, db_manager=None):
        """Initialize data manager"""
        self.db_manager = db_manager or self._create_mock_db_manager()
        self.validation_engine = DataValidationEngine()
        self.backup_dir = Path("backups")
        self.backup_dir.mkdir(exist_ok=True)
    
    def _create_mock_db_manager(self):
        """Create mock database manager for testing"""
        class MockDBManager:
            def get_all_qb_stats(self, season=None):
                return []
            def get_all_splits(self, season=None):
                return []
            def get_all_advanced_stats(self, season=None):
                return []
        return MockDBManager()
    
    def validate_data(self, season: Optional[int] = None) -> Dict[str, Any]:
        """Validate data quality for a season or all data"""
        logger.info(f"Validating data for season: {season}")
        
        # Get data from database
        qb_stats = self.db_manager.get_all_qb_stats(season)
        splits_data = self.db_manager.get_all_splits(season)
        advanced_stats = self.db_manager.get_all_advanced_stats(season)
        
        # Convert to dictionaries for validation
        qb_records = [self._record_to_dict(stat) for stat in qb_stats]
        splits_records = [self._record_to_dict(stat) for stat in splits_data]
        advanced_records = [self._record_to_dict(stat) for stat in advanced_stats]
        
        # Validate each dataset
        qb_validation = self.validation_engine.validate_dataset(qb_records)
        splits_validation = self.validation_engine.validate_dataset(splits_records)
        advanced_validation = self.validation_engine.validate_dataset(advanced_records)
        
        return {
            'qb_stats': qb_validation,
            'splits_data': splits_validation,
            'advanced_stats': advanced_validation,
            'overall_quality': self._calculate_overall_quality([
                qb_validation, splits_validation, advanced_validation
            ])
        }
    
    def _record_to_dict(self, record) -> Dict[str, Any]:
        """Convert a record object to dictionary"""
        if hasattr(record, '__dict__'):
            return record.__dict__
        elif hasattr(record, '_asdict'):
            return record._asdict()
        else:
            return dict(record)
    
    def _calculate_overall_quality(self, validations: List[Dict[str, Any]]) -> float:
        """Calculate overall data quality score"""
        total_score = 0
        total_weight = 0
        
        for validation in validations:
            metrics = validation.get('quality_metrics', DataQualityMetrics())
            # Weight QB stats more heavily
            weight = 0.5 if 'qb_stats' in str(validation) else 0.25
            total_score += metrics.data_integrity_score * weight
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0
    
    def export_data(self, format: str = 'json', season: Optional[int] = None, 
                   output_file: Optional[str] = None) -> str:
        """Export data in specified format"""
        logger.info(f"Exporting data in {format} format for season: {season}")
        
        # Get data
        qb_stats = self.db_manager.get_all_qb_stats(season)
        splits_data = self.db_manager.get_all_splits(season)
        advanced_stats = self.db_manager.get_all_advanced_stats(season)
        
        # Convert to dictionaries
        data = {
            'qb_stats': [self._record_to_dict(stat) for stat in qb_stats],
            'splits_data': [self._record_to_dict(stat) for stat in splits_data],
            'advanced_stats': [self._record_to_dict(stat) for stat in advanced_stats],
            'export_metadata': {
                'export_timestamp': datetime.now().isoformat(),
                'season': season,
                'format': format,
                'total_records': len(qb_stats) + len(splits_data) + len(advanced_stats)
            }
        }
        
        # Generate output filename
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            season_suffix = f"_season_{season}" if season else "_all"
            output_file = f"qb_data_export_{timestamp}{season_suffix}.{format}"
        
        # Export based on format
        if format.lower() == 'json':
            self._export_json(data, output_file)
        elif format.lower() == 'csv':
            self._export_csv(data, output_file)
        elif format.lower() == 'sqlite':
            self._export_sqlite(data, output_file)
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
        logger.info(f"Data exported to: {output_file}")
        return output_file
    
    def _export_json(self, data: Dict[str, Any], output_file: str):
        """Export data as JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def _export_csv(self, data: Dict[str, Any], output_file: str):
        """Export data as CSV files"""
        base_name = output_file.replace('.csv', '')
        
        for table_name, records in data.items():
            if table_name == 'export_metadata':
                continue
            
            if not records:
                continue
            
            csv_file = f"{base_name}_{table_name}.csv"
            with open(csv_file, 'w', newline='', encoding='utf-8') as f:
                if records:
                    writer = csv.DictWriter(f, fieldnames=records[0].keys())
                    writer.writeheader()
                    writer.writerows(records)
    
    def _export_sqlite(self, data: Dict[str, Any], output_file: str):
        """Export data as SQLite database"""
        with sqlite3.connect(output_file) as conn:
            for table_name, records in data.items():
                if table_name == 'export_metadata':
                    continue
                
                if not records:
                    continue
                
                # Create table
                if records:
                    columns = list(records[0].keys())
                    create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ("
                    create_sql += ", ".join([f"{col} TEXT" for col in columns])
                    create_sql += ")"
                    conn.execute(create_sql)
                    
                    # Insert data
                    placeholders = ", ".join(["?" for _ in columns])
                    insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                    
                    for record in records:
                        values = [str(record.get(col, '')) for col in columns]
                        conn.execute(insert_sql, values)
            
            conn.commit()
    
    def import_data(self, input_file: str, format: str = None) -> Dict[str, Any]:
        """Import data from file"""
        logger.info(f"Importing data from: {input_file}")
        
        # Detect format if not specified
        if not format:
            format = self._detect_format(input_file)
        
        # Import based on format
        if format.lower() == 'json':
            data = self._import_json(input_file)
        elif format.lower() == 'csv':
            data = self._import_csv(input_file)
        elif format.lower() == 'sqlite':
            data = self._import_sqlite(input_file)
        else:
            raise ValueError(f"Unsupported import format: {format}")
        
        # Validate imported data
        validation_result = self.validate_imported_data(data)
        
        return {
            'imported_data': data,
            'validation_result': validation_result,
            'import_timestamp': datetime.now()
        }
    
    def _detect_format(self, filename: str) -> str:
        """Detect file format from extension"""
        ext = Path(filename).suffix.lower()
        if ext == '.json':
            return 'json'
        elif ext == '.csv':
            return 'csv'
        elif ext == '.db' or ext == '.sqlite':
            return 'sqlite'
        else:
            raise ValueError(f"Cannot detect format for file: {filename}")
    
    def _import_json(self, input_file: str) -> Dict[str, Any]:
        """Import data from JSON file"""
        with open(input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _import_csv(self, input_file: str) -> Dict[str, Any]:
        """Import data from CSV file"""
        data = {}
        with open(input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            records = list(reader)
            # Assume table name from filename
            table_name = Path(input_file).stem
            data[table_name] = records
        return data
    
    def _import_sqlite(self, input_file: str) -> Dict[str, Any]:
        """Import data from SQLite database"""
        data = {}
        with sqlite3.connect(input_file) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            for (table_name,) in tables:
                cursor.execute(f"SELECT * FROM {table_name}")
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                records = []
                for row in rows:
                    record = dict(zip(columns, row))
                    records.append(record)
                
                data[table_name] = records
        
        return data
    
    def validate_imported_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate imported data structure and quality"""
        validation_results = {}
        
        for table_name, records in data.items():
            if table_name == 'export_metadata':
                continue
            
            if isinstance(records, list):
                validation_results[table_name] = self.validation_engine.validate_dataset(records)
            else:
                validation_results[table_name] = {
                    'error': f"Invalid data structure for table {table_name}"
                }
        
        return validation_results
    
    def create_backup(self, backup_name: str = None) -> str:
        """Create backup of current data"""
        if not backup_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_{timestamp}"
        
        backup_file = self.backup_dir / f"{backup_name}.json"
        
        # Export all data as backup
        self.export_data('json', output_file=str(backup_file))
        
        logger.info(f"Backup created: {backup_file}")
        return str(backup_file)
    
    def restore_backup(self, backup_file: str) -> bool:
        """Restore data from backup"""
        logger.info(f"Restoring from backup: {backup_file}")
        
        try:
            # Import backup data
            import_result = self.import_data(backup_file, 'json')
            
            # Validate backup data
            validation = import_result['validation_result']
            
            # Check if backup is valid
            has_errors = any(
                'error' in result for result in validation.values()
            )
            
            if has_errors:
                logger.error("Backup validation failed")
                return False
            
            logger.info("Backup restored successfully")
            return True
            
        except Exception as e:
            logger.error(f"Backup restoration failed: {e}")
            return False
    
    def get_data_summary(self, season: Optional[int] = None) -> Dict[str, Any]:
        """Get summary statistics for data"""
        qb_stats = self.db_manager.get_all_qb_stats(season)
        splits_data = self.db_manager.get_all_splits(season)
        advanced_stats = self.db_manager.get_all_advanced_stats(season)
        
        return {
            'summary': {
                'total_qb_stats': len(qb_stats),
                'total_splits': len(splits_data),
                'total_advanced_stats': len(advanced_stats),
                'season': season,
                'generated_at': datetime.now().isoformat()
            },
            'qb_stats_summary': self._calculate_stats_summary(qb_stats),
            'splits_summary': self._calculate_stats_summary(splits_data),
            'advanced_summary': self._calculate_stats_summary(advanced_stats)
        }
    
    def _calculate_stats_summary(self, records: List[Any]) -> Dict[str, Any]:
        """Calculate summary statistics for a dataset"""
        if not records:
            return {'count': 0}
        
        # Convert to dictionaries
        dict_records = [self._record_to_dict(record) for record in records]
        
        # Calculate basic stats
        summary = {
            'count': len(dict_records),
            'fields': list(dict_records[0].keys()) if dict_records else []
        }
        
        # Calculate numeric field statistics
        numeric_fields = {}
        for field in summary['fields']:
            values = []
            for record in dict_records:
                value = record.get(field)
                if isinstance(value, (int, float)) and value is not None:
                    values.append(value)
            
            if values:
                numeric_fields[field] = {
                    'min': min(values),
                    'max': max(values),
                    'avg': sum(values) / len(values),
                    'count': len(values)
                }
        
        summary['numeric_fields'] = numeric_fields
        return summary 