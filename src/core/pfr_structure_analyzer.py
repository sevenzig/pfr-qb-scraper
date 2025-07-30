#!/usr/bin/env python3
"""
PFR Structure Analyzer - Comprehensive analysis of Pro Football Reference HTML structure.

This module provides tools to analyze PFR's HTML structure, map data attributes,
and validate data extraction against the database schema.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag
import re

logger = logging.getLogger(__name__)


@dataclass
class TableInfo:
    """Information about a table found in PFR HTML."""
    table_id: str
    table_class: str
    table_index: int
    row_count: int
    column_count: int
    headers: List[str]
    data_stat_attributes: Set[str]
    table_type: str  # 'basic_stats', 'splits', 'advanced_splits', 'unknown'


@dataclass
class DataStatMapping:
    """Mapping between PFR data-stat attributes and database fields."""
    pfr_attribute: str
    database_field: str
    data_type: str
    is_required: bool
    description: str
    example_value: Optional[str] = None


class PFRStructureAnalyzer:
    """
    Comprehensive analyzer for Pro Football Reference HTML structure.
    
    This class provides tools to:
    - Analyze table structure and identify data patterns
    - Map PFR data-stat attributes to database fields
    - Validate data extraction completeness
    - Generate detailed reports for debugging
    """
    
    def __init__(self):
        """Initialize the PFR structure analyzer."""
        self.qb_basic_stats_mappings = self._create_qb_basic_stats_mappings()
        self.qb_splits_mappings = self._create_qb_splits_mappings()
        self.qb_splits_advanced_mappings = self._create_qb_splits_advanced_mappings()
        
    def _create_qb_basic_stats_mappings(self) -> List[DataStatMapping]:
        """Create mappings for QB Basic Stats table (33 columns)."""
        return [
            DataStatMapping("ranker", "rk", "int", True, "Rank"),
            DataStatMapping("player", "player_name", "str", True, "Player name"),
            DataStatMapping("age", "age", "int", True, "Player age"),
            DataStatMapping("team", "team", "str", True, "Team"),
            DataStatMapping("pos", "pos", "str", True, "Position"),
            DataStatMapping("g", "g", "int", True, "Games played"),
            DataStatMapping("gs", "gs", "int", True, "Games started"),
            DataStatMapping("qb_rec", "qbrec", "str", True, "QB record (W-L-T)"),
            DataStatMapping("pass_cmp", "cmp", "int", True, "Passing completions"),
            DataStatMapping("pass_att", "att", "int", True, "Passing attempts"),
            DataStatMapping("pass_cmp_perc", "cmp_perc", "float", True, "Completion percentage"),
            DataStatMapping("pass_yds", "yds", "int", True, "Passing yards"),
            DataStatMapping("pass_td", "td", "int", True, "Passing touchdowns"),
            DataStatMapping("pass_td_perc", "td_perc", "float", True, "Touchdown percentage"),
            DataStatMapping("pass_int", "int", "int", True, "Interceptions"),
            DataStatMapping("pass_int_perc", "int_perc", "float", True, "Interception percentage"),
            DataStatMapping("pass_first_down", "first_down", "int", True, "First downs"),
            DataStatMapping("pass_success_rate", "success_perc", "float", True, "Success percentage"),
            DataStatMapping("pass_long", "lng", "int", True, "Longest pass"),
            DataStatMapping("pass_yds_per_att", "yds_per_att", "float", True, "Yards per attempt"),
            DataStatMapping("pass_adj_yds_per_att", "adj_yds_per_att", "float", True, "Adjusted yards per attempt"),
            DataStatMapping("pass_yds_per_cmp", "yds_per_cmp", "float", True, "Yards per completion"),
            DataStatMapping("pass_yds_per_g", "yds_per_g", "float", True, "Yards per game"),
            DataStatMapping("pass_rating", "rating", "float", True, "Passer rating"),
            DataStatMapping("qbr", "qbr", "float", False, "Total QBR"),
            DataStatMapping("pass_sacked", "sacked", "int", True, "Times sacked"),
            DataStatMapping("pass_sacked_yds", "sacked_yds", "int", True, "Sack yards lost"),
            DataStatMapping("pass_sacked_perc", "sacked_perc", "float", True, "Sack percentage"),
            DataStatMapping("pass_net_yds_per_att", "net_yds_per_att", "float", True, "Net yards per attempt"),
            DataStatMapping("pass_adj_net_yds_per_att", "adj_net_yds_per_att", "float", True, "Adjusted net yards per attempt"),
            DataStatMapping("pass_4qc", "fourth_qtr_comebacks", "int", True, "Fourth quarter comebacks"),
            DataStatMapping("pass_gwd", "game_winning_drives", "int", True, "Game winning drives"),
            DataStatMapping("awards", "awards", "str", False, "Awards"),
            DataStatMapping("player_additional", "player_additional", "str", False, "Additional player info"),
        ]
    
    def _create_qb_splits_mappings(self) -> List[DataStatMapping]:
        """Create mappings for QB Splits table (34 columns)."""
        return [
            DataStatMapping("split", "split", "str", True, "Split category"),
            DataStatMapping("value", "value", "str", True, "Split value"),
            DataStatMapping("g", "g", "int", True, "Games"),
            DataStatMapping("w", "w", "int", True, "Wins"),
            DataStatMapping("l", "l", "int", True, "Losses"),
            DataStatMapping("t", "t", "int", True, "Ties"),
            DataStatMapping("pass_cmp", "cmp", "int", True, "Completions"),
            DataStatMapping("pass_att", "att", "int", True, "Attempts"),
            DataStatMapping("pass_inc", "inc", "int", True, "Incompletions"),
            DataStatMapping("pass_cmp_perc", "cmp_perc", "float", True, "Completion percentage"),
            DataStatMapping("pass_yds", "yds", "int", True, "Passing yards"),
            DataStatMapping("pass_td", "td", "int", True, "Touchdowns"),
            DataStatMapping("pass_int", "int", "int", True, "Interceptions"),
            DataStatMapping("pass_rating", "rating", "float", True, "Passer rating"),
            DataStatMapping("pass_sacked", "sacked", "int", True, "Times sacked"),
            DataStatMapping("pass_sacked_yds", "sacked_yds", "int", True, "Sack yards lost"),
            DataStatMapping("pass_yds_per_att", "yds_per_att", "float", True, "Yards per attempt"),
            DataStatMapping("pass_adj_yds_per_att", "adj_yds_per_att", "float", True, "Adjusted yards per attempt"),
            DataStatMapping("pass_att_per_g", "att_per_g", "float", True, "Attempts per game"),
            DataStatMapping("pass_yds_per_g", "yds_per_g", "float", True, "Yards per game"),
            DataStatMapping("rush_att", "rush_att", "int", True, "Rush attempts"),
            DataStatMapping("rush_yds", "rush_yds", "int", True, "Rush yards"),
            DataStatMapping("rush_yds_per_att", "rush_yds_per_att", "float", True, "Rush yards per attempt"),
            DataStatMapping("rush_td", "rush_td", "int", True, "Rush touchdowns"),
            DataStatMapping("rush_att_per_g", "rush_att_per_g", "float", True, "Rush attempts per game"),
            DataStatMapping("rush_yds_per_g", "rush_yds_per_g", "float", True, "Rush yards per game"),
            DataStatMapping("rush_td_per_g", "rush_td_per_g", "float", True, "Rush touchdowns per game"),
            DataStatMapping("points", "points", "int", True, "Points scored"),
            DataStatMapping("fumbles", "fumbles", "int", True, "Fumbles"),
            DataStatMapping("fumbles_lost", "fumbles_lost", "int", True, "Fumbles lost"),
            DataStatMapping("fumbles_forced", "fumbles_forced", "int", True, "Fumbles forced"),
            DataStatMapping("fumbles_recovered", "fumbles_recovered", "int", True, "Fumbles recovered"),
            DataStatMapping("fumble_yds", "fumble_yds", "int", True, "Fumble yards"),
            DataStatMapping("fumble_td", "fumble_td", "int", True, "Fumble touchdowns"),
        ]
    
    def _create_qb_splits_advanced_mappings(self) -> List[DataStatMapping]:
        """Create mappings for QB Splits Advanced table (20 columns)."""
        return [
            DataStatMapping("split", "split", "str", True, "Split category"),
            DataStatMapping("value", "value", "str", True, "Split value"),
            DataStatMapping("pass_cmp", "cmp", "int", True, "Completions"),
            DataStatMapping("pass_att", "att", "int", True, "Attempts"),
            DataStatMapping("pass_inc", "inc", "int", True, "Incompletions"),
            DataStatMapping("pass_cmp_perc", "cmp_perc", "float", True, "Completion percentage"),
            DataStatMapping("pass_yds", "yds", "int", True, "Passing yards"),
            DataStatMapping("pass_td", "td", "int", True, "Touchdowns"),
            DataStatMapping("pass_first_down", "first_down", "int", True, "First downs"),
            DataStatMapping("pass_int", "int", "int", True, "Interceptions"),
            DataStatMapping("pass_rating", "rating", "float", True, "Passer rating"),
            DataStatMapping("pass_sacked", "sacked", "int", True, "Times sacked"),
            DataStatMapping("pass_sacked_yds", "sacked_yds", "int", True, "Sack yards lost"),
            DataStatMapping("pass_yds_per_att", "yds_per_att", "float", True, "Yards per attempt"),
            DataStatMapping("pass_adj_yds_per_att", "adj_yds_per_att", "float", True, "Adjusted yards per attempt"),
            DataStatMapping("rush_att", "rush_att", "int", True, "Rush attempts"),
            DataStatMapping("rush_yds", "rush_yds", "int", True, "Rush yards"),
            DataStatMapping("rush_yds_per_att", "rush_yds_per_att", "float", True, "Rush yards per attempt"),
            DataStatMapping("rush_td", "rush_td", "int", True, "Rush touchdowns"),
            DataStatMapping("rush_first_down", "rush_first_down", "int", True, "Rush first downs"),
        ]
    
    def analyze_page_structure(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Analyze the complete structure of a PFR page.
        
        Args:
            soup: BeautifulSoup object of the PFR page
            
        Returns:
            Dictionary containing comprehensive analysis results
        """
        logger.info("Starting comprehensive PFR page structure analysis")
        
        # Find all tables
        tables = soup.find_all('table')
        logger.info(f"Found {len(tables)} tables on the page")
        
        table_analyses = []
        for i, table in enumerate(tables):
            table_info = self._analyze_table(table, i)
            table_analyses.append(table_info)
            
        # Analyze overall structure
        analysis = {
            'total_tables': len(tables),
            'table_analyses': table_analyses,
            'data_stat_coverage': self._analyze_data_stat_coverage(table_analyses),
            'table_categorization': self._categorize_tables(table_analyses),
            'missing_fields': self._identify_missing_fields(table_analyses),
            'recommendations': self._generate_recommendations(table_analyses)
        }
        
        logger.info(f"Analysis complete. Found {len(table_analyses)} analyzable tables")
        return analysis
    
    def _analyze_table(self, table: Tag, index: int) -> TableInfo:
        """
        Analyze a single table's structure and content.
        
        Args:
            table: BeautifulSoup table tag
            index: Table index on the page
            
        Returns:
            TableInfo object with comprehensive table analysis
        """
        # Get table attributes
        table_id = table.get('id', f'table_{index}')
        table_class = ' '.join(table.get('class', []))
        
        # Find all rows
        rows = table.find_all('tr')
        row_count = len(rows)
        
        # Analyze headers and data-stat attributes
        headers = []
        data_stat_attrs = set()
        
        # Look for header row
        header_row = None
        for row in rows:
            if row.find('th'):
                header_row = row
                break
        
        if header_row:
            headers = [th.get_text(strip=True) for th in header_row.find_all('th')]
            # Also get data-stat attributes from header cells
            for th in header_row.find_all('th'):
                data_stat = th.get('data-stat')
                if data_stat:
                    data_stat_attrs.add(data_stat)
        
        # Analyze data rows for additional data-stat attributes
        for row in rows[1:]:  # Skip header row
            for cell in row.find_all(['td', 'th']):
                data_stat = cell.get('data-stat')
                if data_stat:
                    data_stat_attrs.add(data_stat)
        
        # Count columns (use header row if available, otherwise first data row)
        column_count = len(headers) if headers else 0
        if not column_count and rows:
            first_data_row = rows[1] if len(rows) > 1 else rows[0]
            column_count = len(first_data_row.find_all(['td', 'th']))
        
        # Categorize table type
        table_type = self._categorize_table_type(table_id, table_class, headers, data_stat_attrs)
        
        return TableInfo(
            table_id=table_id,
            table_class=table_class,
            table_index=index,
            row_count=row_count,
            column_count=column_count,
            headers=headers,
            data_stat_attributes=data_stat_attrs,
            table_type=table_type
        )
    
    def _categorize_table_type(self, table_id: str, table_class: str, 
                              headers: List[str], data_stat_attrs: Set[str]) -> str:
        """
        Categorize a table based on its structure and attributes.
        
        Args:
            table_id: Table ID attribute
            table_class: Table class attribute
            headers: List of header texts
            data_stat_attrs: Set of data-stat attributes found
            
        Returns:
            Table type categorization
        """
        # Check for specific table IDs
        if 'stats' in table_id.lower():
            return 'basic_stats'
        elif 'advanced_splits' in table_id.lower():
            return 'advanced_splits'
        elif 'splits' in table_id.lower():
            return 'splits'
        
        # Check for specific data-stat attributes that indicate table type
        basic_stats_attrs = {'pass_cmp', 'pass_att', 'pass_yds', 'pass_td', 'pass_int'}
        splits_attrs = {'split', 'value', 'g', 'w', 'l'}
        advanced_attrs = {'pass_first_down', 'pass_success_rate'}
        
        if basic_stats_attrs.intersection(data_stat_attrs):
            return 'basic_stats'
        elif splits_attrs.intersection(data_stat_attrs):
            if advanced_attrs.intersection(data_stat_attrs):
                return 'advanced_splits'
            else:
                return 'splits'
        
        # Check headers for clues
        header_text = ' '.join(headers).lower()
        if 'split' in header_text:
            if 'advanced' in header_text or 'success' in header_text:
                return 'advanced_splits'
            else:
                return 'splits'
        
        return 'unknown'
    
    def _analyze_data_stat_coverage(self, table_analyses: List[TableInfo]) -> Dict[str, Any]:
        """
        Analyze coverage of data-stat attributes across all tables.
        
        Args:
            table_analyses: List of table analysis results
            
        Returns:
            Dictionary with coverage analysis
        """
        all_data_stats = set()
        for analysis in table_analyses:
            all_data_stats.update(analysis.data_stat_attributes)
        
        # Check coverage against expected mappings
        expected_basic = {m.pfr_attribute for m in self.qb_basic_stats_mappings}
        expected_splits = {m.pfr_attribute for m in self.qb_splits_mappings}
        expected_advanced = {m.pfr_attribute for m in self.qb_splits_advanced_mappings}
        
        coverage = {
            'total_data_stats_found': len(all_data_stats),
            'basic_stats_coverage': len(all_data_stats.intersection(expected_basic)),
            'splits_coverage': len(all_data_stats.intersection(expected_splits)),
            'advanced_splits_coverage': len(all_data_stats.intersection(expected_advanced)),
            'missing_basic_stats': expected_basic - all_data_stats,
            'missing_splits': expected_splits - all_data_stats,
            'missing_advanced_splits': expected_advanced - all_data_stats,
            'unexpected_attributes': all_data_stats - (expected_basic | expected_splits | expected_advanced)
        }
        
        return coverage
    
    def _categorize_tables(self, table_analyses: List[TableInfo]) -> Dict[str, List[TableInfo]]:
        """
        Categorize tables by type.
        
        Args:
            table_analyses: List of table analysis results
            
        Returns:
            Dictionary mapping table types to lists of tables
        """
        categorized = {
            'basic_stats': [],
            'splits': [],
            'advanced_splits': [],
            'unknown': []
        }
        
        for analysis in table_analyses:
            categorized[analysis.table_type].append(analysis)
        
        return categorized
    
    def _identify_missing_fields(self, table_analyses: List[TableInfo]) -> Dict[str, List[str]]:
        """
        Identify missing fields based on expected mappings.
        
        Args:
            table_analyses: List of table analysis results
            
        Returns:
            Dictionary mapping table types to lists of missing fields
        """
        all_data_stats = set()
        for analysis in table_analyses:
            all_data_stats.update(analysis.data_stat_attributes)
        
        missing = {
            'basic_stats': [m.pfr_attribute for m in self.qb_basic_stats_mappings 
                           if m.pfr_attribute not in all_data_stats],
            'splits': [m.pfr_attribute for m in self.qb_splits_mappings 
                      if m.pfr_attribute not in all_data_stats],
            'advanced_splits': [m.pfr_attribute for m in self.qb_splits_advanced_mappings 
                               if m.pfr_attribute not in all_data_stats]
        }
        
        return missing
    
    def _generate_recommendations(self, table_analyses: List[TableInfo]) -> List[str]:
        """
        Generate recommendations based on analysis results.
        
        Args:
            table_analyses: List of table analysis results
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check for missing tables
        categorized = self._categorize_tables(table_analyses)
        if not categorized['basic_stats']:
            recommendations.append("No basic stats table found - check if page structure has changed")
        if not categorized['splits']:
            recommendations.append("No splits table found - check if splits URL is correct")
        if not categorized['advanced_splits']:
            recommendations.append("No advanced splits table found - may be optional")
        
        # Check for missing fields
        missing = self._identify_missing_fields(table_analyses)
        if missing['basic_stats']:
            recommendations.append(f"Missing basic stats fields: {missing['basic_stats']}")
        if missing['splits']:
            recommendations.append(f"Missing splits fields: {missing['splits']}")
        if missing['advanced_splits']:
            recommendations.append(f"Missing advanced splits fields: {missing['advanced_splits']}")
        
        # Check for unexpected attributes
        coverage = self._analyze_data_stat_coverage(table_analyses)
        if coverage['unexpected_attributes']:
            recommendations.append(f"Found unexpected data-stat attributes: {coverage['unexpected_attributes']}")
        
        return recommendations
    
    def get_field_mappings(self, table_type: str) -> List[DataStatMapping]:
        """
        Get field mappings for a specific table type.
        
        Args:
            table_type: Type of table ('basic_stats', 'splits', 'advanced_splits')
            
        Returns:
            List of DataStatMapping objects
        """
        if table_type == 'basic_stats':
            return self.qb_basic_stats_mappings
        elif table_type == 'splits':
            return self.qb_splits_mappings
        elif table_type == 'advanced_splits':
            return self.qb_splits_advanced_mappings
        else:
            raise ValueError(f"Unknown table type: {table_type}")
    
    def validate_extracted_data(self, extracted_data: Dict[str, Any], 
                               table_type: str) -> Dict[str, Any]:
        """
        Validate extracted data against expected schema.
        
        Args:
            extracted_data: Dictionary of extracted data
            table_type: Type of table the data came from
            
        Returns:
            Dictionary with validation results
        """
        mappings = self.get_field_mappings(table_type)
        validation_results = {
            'valid': True,
            'missing_required_fields': [],
            'type_mismatches': [],
            'unexpected_fields': [],
            'coverage_percentage': 0.0
        }
        
        # Check for missing required fields
        for mapping in mappings:
            if mapping.is_required and mapping.database_field not in extracted_data:
                validation_results['missing_required_fields'].append(mapping.database_field)
                validation_results['valid'] = False
        
        # Check for unexpected fields
        expected_fields = {m.database_field for m in mappings}
        for field in extracted_data.keys():
            if field not in expected_fields:
                validation_results['unexpected_fields'].append(field)
        
        # Calculate coverage percentage
        if mappings:
            required_fields = [m.database_field for m in mappings if m.is_required]
            found_required = len([f for f in required_fields if f in extracted_data])
            validation_results['coverage_percentage'] = (found_required / len(required_fields)) * 100
        
        return validation_results 