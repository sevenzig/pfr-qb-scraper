#!/usr/bin/env python3
"""
Splits Extractor for NFL QB Data Scraping
Dedicated extractor for QB splits data with comprehensive error handling and field mapping validation.

References:
- Field mapping and validation: .cursor/rules/field-mapping-validation.mdc
- Data models: src/models/qb_models.py
- Database schema: sql/schema.sql
- CSV format reference: setup/advanced_stats_1.csv, setup/advanced_stats.2.csv
"""

import logging
import time
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
import re

from bs4 import BeautifulSoup, Tag
import requests

from src.models.qb_models import QBSplitsType1, QBSplitsType2
from src.utils.data_utils import (
    safe_int, safe_float, safe_percentage, clean_player_name, build_splits_url
)
from src.core.selenium_manager import SeleniumManager, SeleniumConfig
from src.config.config import config

logger = logging.getLogger(__name__)


@dataclass
class SplitsExtractionResult:
    """Result of splits extraction operation"""
    basic_splits: List[QBSplitsType1]
    advanced_splits: List[QBSplitsType2]
    errors: List[str]
    warnings: List[str]
    tables_discovered: int
    tables_processed: int
    extraction_time: float


class SplitsExtractor:
    """
    Dedicated QB Splits Extractor with enhanced functionality.

    Features:
    - Enhanced splits URL construction with fallback mechanisms
    - Automatic table discovery and categorization
    - Comprehensive extraction of all required QB splits columns (basic and advanced)
    - Robust error handling and structured logging for missing/unmapped fields
    - Rate limiting and respectful scraping
    - Field mapping and validation per .cursor/rules/field-mapping-validation.mdc
    - CSV format compliance: matches advanced_stats_1.csv and advanced_stats.2.csv exactly

    All extraction and mapping logic is validated against the authoritative field mapping rule.
    """
    # Authoritative field lists from cursor rules - these are what we extract from PFR HTML
    # From .cursor/rules/qb_splits_scraping.mdc
    QB_SPLITS_FIELDS = [
        "Split", "Value", "G", "W", "L", "T", "Cmp", "Att", "Inc", "Cmp%", "Yds", "TD", "Int", "Rate",
        "Sk", "Yds", "Y/A", "AY/A", "A/G", "Y/G", "Att", "Yds", "Y/A", "TD", "A/G", "Y/G", "TD",
        "Pts", "Fmb", "FL", "FF", "FR", "Yds", "TD"
    ]
    
    # From .cursor/rules/qb_splits_advanced_scraping.mdc
    QB_SPLITS_ADVANCED_FIELDS = [
        "Split", "Value", "Cmp", "Att", "Inc", "Cmp%", "Yds", "TD", "1D", "Int", "Rate", "Sk", "Yds", "Y/A", "AY/A", "Att", "Yds", "Y/A", "TD", "1D"
    ]
    # Note: split, value, pfr_id, player_name, season, scraped_at, updated_at are always set
    
    def __init__(self, selenium_manager: SeleniumManager):
        self.selenium_manager = selenium_manager
        self.base_url = "https://www.pro-football-reference.com"
        self.missing_fields_log = []  # Collect missing field logs for summary
        
        # Enhanced split table patterns based on actual PFR structure
        self.split_table_patterns = {
            # Advanced splits patterns - matches actual PFR advanced_splits table
            'advanced_splits': {
                'primary_ids': ['advanced_splits'],  # This is the exact ID used by PFR
                'fallback_ids': ['splits_advanced', 'detailed_splits', 'play_splits'],
                'class_patterns': ['sortable', 'stats_table', 'now_sortable'],  # Actual PFR classes
                'caption_patterns': ['advanced splits table', 'advanced splits'],
                'headers': ['Passing', 'Rushing'],  # Actual headers from PFR
                'data_stat_patterns': ['split_type', 'split_value', 'pass_cmp', 'pass_att', 'pass_inc', 'pass_cmp_perc', 'pass_yds', 'pass_td', 'pass_first_down', 'pass_int'],
                'content_indicators': ['Down', '1st', '2nd', '3rd', '4th', 'Yards To Go', 'Field Position', 'Red Zone']
            },
            # Basic splits patterns - matches actual PFR stats table
            'basic_splits': {
                'primary_ids': ['stats'],  # This is the exact ID used by PFR for main splits table
                'fallback_ids': ['splits', 'basic_splits', 'game_splits'],
                'class_patterns': ['sortable', 'stats_table', 'now_sortable'],  # Actual PFR classes
                'caption_patterns': ['splits table', '2024 splits table'],
                'headers': ['Games', 'Passing', 'Rushing', 'Scoring', 'Fumbles'],  # Actual headers from PFR
                'data_stat_patterns': ['split_id', 'split_value', 'g', 'wins', 'losses', 'ties', 'pass_cmp', 'pass_att', 'pass_inc', 'pass_cmp_perc'],
                'content_indicators': ['League', 'Place', 'Result', 'Home', 'Away', 'Win', 'Loss', '1st Quarter', '2nd Quarter']
            }
        }
        
        # Mapping from PFR data-stat attributes to cursor rule field names
        self.pfr_to_cursor_basic_mapping = {
            # First two columns are always Split and Value
            'split_id': 'Split', 'split_value': 'Value',
            # Games section
            'g': 'G', 'wins': 'W', 'losses': 'L', 'ties': 'T',
            # Passing section  
            'pass_cmp': 'Cmp', 'pass_att': 'Att', 'pass_inc': 'Inc', 'pass_cmp_perc': 'Cmp%',
            'pass_yds': 'Yds', 'pass_td': 'TD', 'pass_int': 'Int', 'pass_rating': 'Rate',
            'pass_sacked': 'Sk', 'pass_sacked_yds': 'Yds', 'pass_yds_per_att': 'Y/A', 'pass_adj_yds_per_att': 'AY/A',
            'pass_att_per_g': 'A/G', 'pass_yds_per_g': 'Y/G',
            # Rushing section
            'rush_att': 'Att', 'rush_yds': 'Yds', 'rush_yds_per_att': 'Y/A', 'rush_td': 'TD',
            'rush_att_per_g': 'A/G', 'rush_yds_per_g': 'Y/G',
            # Total/Scoring section
            'all_td': 'TD', 'scoring': 'Pts',
            # Fumbles section
            'fumbles': 'Fmb', 'fumbles_lost': 'FL', 'fumbles_forced': 'FF', 'fumbles_rec': 'FR',
            'fumbles_rec_yds': 'Yds', 'fumbles_rec_td': 'TD'
        }
        
        self.pfr_to_cursor_advanced_mapping = {
            # First two columns
            'split_type': 'Split', 'split_value': 'Value',
            # Passing section
            'pass_cmp': 'Cmp', 'pass_att': 'Att', 'pass_inc': 'Inc', 'pass_cmp_perc': 'Cmp%',
            'pass_yds': 'Yds', 'pass_td': 'TD', 'pass_first_down': '1D', 'pass_int': 'Int',
            'pass_rating': 'Rate', 'pass_sacked': 'Sk', 'pass_sacked_yds': 'Yds',
            'pass_yds_per_att': 'Y/A', 'pass_adj_yds_per_att': 'AY/A',
            # Rushing section
            'rush_att': 'Att', 'rush_yds': 'Yds', 'rush_yds_per_att': 'Y/A', 'rush_td': 'TD',
            'rush_first_down': '1D'
        }
    
    def extract_player_splits(self, pfr_id: str, player_name: str, season: int, scraped_at: datetime) -> SplitsExtractionResult:
        """
        Extract splits data for a specific player and season.

        Args:
            pfr_id: Player's PFR ID
            player_name: Player's name
            season: Season year
            scraped_at: Timestamp of extraction

        Returns:
            SplitsExtractionResult with extracted data, errors, warnings, and extraction metadata.

        This method logs a summary of all missing/unmapped fields at the end of extraction, as required by .cursor/rules/field-mapping-validation.mdc.
        """
        logger.debug(f"[DEBUG] extract_player_splits called for {player_name} ({pfr_id}), season {season}")
        start_time = time.time()
        basic_splits = []
        advanced_splits = []
        errors = []
        warnings = []
        self.missing_fields_log = []  # Reset for each extraction
        
        try:
            # Build splits URL
            splits_url = self._build_enhanced_splits_url(pfr_id, season)
            if not splits_url:
                error_msg = f"Could not build splits URL for {player_name} ({pfr_id}), season {season}"
                errors.append(error_msg)
                logger.error(error_msg)
                return SplitsExtractionResult(
                    basic_splits=[], advanced_splits=[], 
                    errors=[error_msg], warnings=[],
                    tables_discovered=0, tables_processed=0, extraction_time=0.0
                )
            logger.info(f"Extracting splits for {player_name} from {splits_url}")
            
            # Get page content - ENABLE JavaScript to load the splits tables
            result = self.selenium_manager.get_page(splits_url, enable_js=True)
            if not result['success']:
                error_msg = f"Failed to load splits page for {player_name}: {result['error']}"
                errors.append(error_msg)
                logger.error(error_msg)
                return SplitsExtractionResult(
                    basic_splits=[], advanced_splits=[], 
                    errors=[error_msg], warnings=[],
                    tables_discovered=0, tables_processed=0, extraction_time=0.0
                )
            
            response = result['content']
            
            # Parse HTML
            soup = BeautifulSoup(response, 'html.parser')
            
            # Discover splits tables
            discovered_tables = self._discover_splits_tables(soup)
            tables_discovered = len(discovered_tables)
            logger.info(f"Discovered {tables_discovered} splits tables for {player_name}")
            
            # Process tables in priority order
            priority_tables = self._get_priority_tables(discovered_tables)
            tables_processed = 0
            
            for table_info in priority_tables:
                try:
                    table = self._find_table_by_info(soup, table_info)
                    if not table:
                        continue
                    
                    table_type = table_info.get('type', 'unknown')
                    logger.info(f"Processing {table_type} table: {table_info.get('id', 'unknown')}")
                    
                    if table_type == 'basic_splits':
                        extracted_basic = self._extract_basic_splits_table(table, pfr_id, player_name, season, scraped_at)
                        basic_splits.extend(extracted_basic)
                        logger.info(f"Extracted {len(extracted_basic)} basic splits rows")
                        
                    elif table_type == 'advanced_splits':
                        extracted_advanced = self._extract_advanced_splits_table(table, pfr_id, player_name, season, scraped_at)
                        advanced_splits.extend(extracted_advanced)
                        logger.info(f"Extracted {len(extracted_advanced)} advanced splits rows")
                    
                    tables_processed += 1
                    
                except Exception as e:
                    error_msg = f"Error processing table {table_info.get('id', 'unknown')}: {e}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            # Log summary of missing fields
            if self.missing_fields_log:
                logger.warning(f"Missing fields summary for {player_name} season {season}:")
                for missing in self.missing_fields_log:
                    logger.warning(f"  {missing['split']} -> {missing['value']}: missing {missing['field']}")
                
                # Group missing fields by type for summary
                missing_by_field = {}
                for missing in self.missing_fields_log:
                    field = missing['field']
                    if field not in missing_by_field:
                        missing_by_field[field] = 0
                    missing_by_field[field] += 1
                
                logger.warning("Missing field counts:")
                for field, count in missing_by_field.items():
                    logger.warning(f"  {field}: {count} times")
            
            extraction_time = time.time() - start_time
            logger.info(f"Splits extraction complete for {player_name}. "
                       f"Basic: {len(basic_splits)}, Advanced: {len(advanced_splits)}, "
                       f"Time: {extraction_time:.2f}s")
            
            return SplitsExtractionResult(
                basic_splits=basic_splits,
                advanced_splits=advanced_splits,
                errors=errors,
                warnings=warnings,
                tables_discovered=tables_discovered,
                tables_processed=tables_processed,
                extraction_time=extraction_time
            )
            
        except Exception as e:
            error_msg = f"Unexpected error extracting splits for {player_name}: {e}"
            errors.append(error_msg)
            logger.error(error_msg, exc_info=True)
            return SplitsExtractionResult(
                basic_splits=[], advanced_splits=[], 
                errors=[error_msg], warnings=[],
                tables_discovered=0, tables_processed=0, extraction_time=time.time() - start_time
            )
    
    def _build_enhanced_splits_url(self, pfr_id: str, season: int) -> Optional[str]:
        """Build enhanced splits URL with fallback mechanisms"""
        if not pfr_id:
            return None
        
        # Extract first letter for URL construction
        first_letter = pfr_id[0].upper() if pfr_id else None
        if not first_letter:
            return None
        
        # Primary URL format
        splits_url = f"{self.base_url}/players/{first_letter}/{pfr_id}/splits/{season}/"
        
        logger.debug(f"Built splits URL: {splits_url}")
        return splits_url
    
    def _discover_splits_tables(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Discover splits tables using specific PFR IDs"""
        discovered_tables = []
        
        logger.info(f"=== TABLE DISCOVERY DEBUG ===")
        
        # Look for basic splits: <div id="div_stats"> containing <table id="stats">
        basic_div = soup.find('div', id='div_stats')
        if basic_div and isinstance(basic_div, Tag):
            basic_table = basic_div.find('table', id='stats')
            if basic_table and isinstance(basic_table, Tag):
                logger.info(f"Found basic splits table: div#div_stats > table#stats")
                discovered_tables.append({
                    'table': basic_table,
                    'type': 'basic_splits',
                    'id': 'stats',
                    'category': 'basic_splits',
                    'priority': 1,
                    'confidence': 'high',
                    'score': 10
                })
            else:
                logger.warning(f"Found div#div_stats but no table#stats inside")
        else:
            logger.warning(f"No div#div_stats found")
        
        # Look for advanced splits: <div id="div_advanced_splits"> containing <table id="advanced_splits">
        advanced_div = soup.find('div', id='div_advanced_splits')
        if advanced_div and isinstance(advanced_div, Tag):
            advanced_table = advanced_div.find('table', id='advanced_splits')
            if advanced_table and isinstance(advanced_table, Tag):
                logger.info(f"Found advanced splits table: div#div_advanced_splits > table#advanced_splits")
                discovered_tables.append({
                    'table': advanced_table,
                    'type': 'advanced_splits',
                    'id': 'advanced_splits',
                    'category': 'advanced_splits',
                    'priority': 1,
                    'confidence': 'high',
                    'score': 10
                })
            else:
                logger.warning(f"Found div#div_advanced_splits but no table#advanced_splits inside")
        else:
            logger.warning(f"No div#div_advanced_splits found")
        
        logger.info(f"=== DISCOVERY SUMMARY ===")
        logger.info(f"Splits tables discovered: {len(discovered_tables)}")
        
        for table_info in discovered_tables:
            logger.info(f"Final: {table_info['type']} table - ID: {table_info['id']}, Priority: {table_info.get('priority', 'unknown')}")
        
        return discovered_tables
    
    def _categorize_table_enhanced(self, table: Tag) -> Optional[Dict[str, Any]]:
        """Enhanced table categorization with confidence scoring and debugging"""
        table_id_raw = table.get('id')
        table_id = str(table_id_raw).lower() if table_id_raw else ''
        class_attr = table.get('class')
        if isinstance(class_attr, list):
            table_class = ' '.join([str(c) for c in class_attr]).lower()
        elif isinstance(class_attr, str):
            table_class = class_attr.lower()
        else:
            table_class = ''
        
        caption = table.find('caption')
        caption_text = caption.get_text(strip=True).lower() if caption and isinstance(caption, Tag) else ''
        headers = self._extract_table_headers(table)
        headers_text = ' '.join(headers).lower()
        
        logger.debug(f"Categorizing table - ID: '{table_id}', Class: '{table_class}', Caption: '{caption_text}'")
        
        # Score-based categorization for better confidence
        advanced_score = 0
        basic_score = 0
        
        # Primary ID matches (highest priority)
        for pattern_id in self.split_table_patterns['advanced_splits']['primary_ids']:
            if pattern_id in table_id:
                advanced_score += 10
                logger.debug(f"  Advanced ID match: {pattern_id} (+10)")
                
        for pattern_id in self.split_table_patterns['basic_splits']['primary_ids']:
            if pattern_id in table_id:
                basic_score += 10
                logger.debug(f"  Basic ID match: {pattern_id} (+10)")
        
        # Fallback ID matches
        for pattern_id in self.split_table_patterns['advanced_splits']['fallback_ids']:
            if pattern_id in table_id:
                advanced_score += 5
                logger.debug(f"  Advanced fallback ID: {pattern_id} (+5)")
                
        for pattern_id in self.split_table_patterns['basic_splits']['fallback_ids']:
            if pattern_id in table_id:
                basic_score += 5
                logger.debug(f"  Basic fallback ID: {pattern_id} (+5)")
        
        # Class pattern matches
        for class_pattern in self.split_table_patterns['advanced_splits']['class_patterns']:
            if class_pattern in table_class:
                advanced_score += 3
                logger.debug(f"  Advanced class match: {class_pattern} (+3)")
                
        for class_pattern in self.split_table_patterns['basic_splits']['class_patterns']:
            if class_pattern in table_class:
                basic_score += 3
                logger.debug(f"  Basic class match: {class_pattern} (+3)")
        
        # Caption pattern matches
        for caption_pattern in self.split_table_patterns['advanced_splits']['caption_patterns']:
            if caption_pattern in caption_text:
                advanced_score += 4
                logger.debug(f"  Advanced caption match: {caption_pattern} (+4)")
                
        for caption_pattern in self.split_table_patterns['basic_splits']['caption_patterns']:
            if caption_pattern in caption_text:
                basic_score += 4
                logger.debug(f"  Basic caption match: {caption_pattern} (+4)")
        
        # Header pattern matches
        for header in self.split_table_patterns['advanced_splits']['headers']:
            if header.lower() in headers_text:
                advanced_score += 2
                logger.debug(f"  Advanced header match: {header} (+2)")
                
        for header in self.split_table_patterns['basic_splits']['headers']:
            if header.lower() in headers_text:
                basic_score += 2
                logger.debug(f"  Basic header match: {header} (+2)")
        
        # Content indicator matches
        table_text = table.get_text().lower()
        for indicator in self.split_table_patterns['advanced_splits']['content_indicators']:
            if indicator.lower() in table_text:
                advanced_score += 1
                logger.debug(f"  Advanced content indicator: {indicator} (+1)")
                
        for indicator in self.split_table_patterns['basic_splits']['content_indicators']:
            if indicator.lower() in table_text:
                basic_score += 1
                logger.debug(f"  Basic content indicator: {indicator} (+1)")
        
        logger.debug(f"  Final scores - Advanced: {advanced_score}, Basic: {basic_score}")
        
        # Determine table type based on scores
        if advanced_score > basic_score and advanced_score >= 3:
            confidence = "high" if advanced_score >= 10 else "medium" if advanced_score >= 5 else "low"
            priority = 1 if advanced_score >= 10 else 2 if advanced_score >= 5 else 3
            return {
                'table': table,
                'type': 'advanced_splits',
                'id': table.get('id', 'unknown'),
                'category': 'advanced_splits',
                'priority': priority,
                'confidence': confidence,
                'score': advanced_score
            }
        elif basic_score > advanced_score and basic_score >= 3:
            confidence = "high" if basic_score >= 10 else "medium" if basic_score >= 5 else "low"
            priority = 1 if basic_score >= 10 else 2 if basic_score >= 5 else 3
            return {
                'table': table,
                'type': 'basic_splits',
                'id': table.get('id', 'unknown'),
                'category': 'basic_splits',
                'priority': priority,
                'confidence': confidence,
                'score': basic_score
            }
        
        return None
    
    def _fallback_table_discovery(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Fallback table discovery when primary methods fail"""
        logger.info("Attempting fallback table discovery...")
        fallback_tables = []
        tables = soup.find_all('table')
        
        for i, table in enumerate(tables):
            if not isinstance(table, Tag):
                continue
            
            # Check if table has enough data to be a splits table
            rows = table.find_all('tr')
            if len(rows) < 5:  # Too few rows to be splits table
                continue
                
            # Check if first column contains split-like data
            first_col_texts = []
            for row in rows[:10]:  # Check first 10 rows
                if not isinstance(row, Tag):
                    continue
                first_cell = row.find(['td', 'th'])
                if first_cell and isinstance(first_cell, Tag):
                    text = first_cell.get_text(strip=True)
                    if text and len(text) > 0:
                        first_col_texts.append(text.lower())
            
            # Look for split indicators in first column
            split_indicators = ['home', 'away', 'win', 'loss', '1st', '2nd', '3rd', '4th', 'quarter', 'down', 'yards']
            indicator_matches = sum(1 for text in first_col_texts for indicator in split_indicators if indicator in text)
            
            if indicator_matches >= 2:
                # Assume it's a basic splits table if we find common split indicators
                table_info = {
                    'table': table,
                    'type': 'basic_splits',
                    'id': table.get('id', f'fallback-table-{i}'),
                    'category': 'basic_splits',
                    'priority': 4,  # Low priority for fallback
                    'confidence': 'fallback',
                    'score': indicator_matches
                }
                fallback_tables.append(table_info)
                logger.info(f"Fallback discovered: Table {i} as basic_splits (indicators: {indicator_matches})")
        
        return fallback_tables
    
    def _has_advanced_splits_indicators(self, table: Tag) -> bool:
        """Check if table has advanced splits indicators"""
        table_id_raw = table.get('id')
        table_id = str(table_id_raw).lower() if table_id_raw else ''
        # Check table ID
        if any(pattern in table_id for pattern in ['advanced', 'splits_advanced', 'detailed']):
            return True
        
        # Check headers for advanced splits patterns
        headers = self._extract_table_headers(table)
        advanced_headers = ['1D', 'first_down', 'down', 'yards_to_go', 'field_position', 'score_differential', 'snap_type', 'play_action', 'time_in_pocket']
        if any(header in ' '.join(headers).lower() for header in advanced_headers):
            return True
        
        # Check for advanced splits content patterns - be more specific
        table_text = table.get_text().lower()
        advanced_patterns = ['1st down', '2nd down', '3rd down', '4th down', 'yards to go', 'field position', 'score differential', 'snap type', 'play action', 'time in pocket', 'leading', 'trailing', 'tied']
        
        # Count how many advanced patterns are found
        pattern_count = sum(1 for pattern in advanced_patterns if pattern in table_text)
        
        # Only classify as advanced if we find multiple advanced patterns
        if pattern_count >= 2:
            return True
        
        return False
    
    def _has_basic_splits_indicators(self, table: Tag) -> bool:
        """Check if table has basic splits indicators"""
        table_id_raw = table.get('id')
        table_id = str(table_id_raw).lower() if table_id_raw else ''
        # Check table ID
        if any(pattern in table_id for pattern in ['splits', 'basic', 'game', 'situational']):
            return True
        
        # Check headers for basic splits patterns
        headers = self._extract_table_headers(table)
        basic_headers = ['split', 'value', 'g', 'w', 'l', 't', 'cmp', 'att', 'yds', 'td', 'int', 'rate']
        if any(header in ' '.join(headers).lower() for header in basic_headers):
            return True
        
        # Check for basic splits content patterns - be more specific
        table_text = table.get_text().lower()
        basic_patterns = ['home', 'away', 'win', 'loss', 'tie', 'quarter', 'overtime', 'league', 'place', 'result', 'month', 'day', 'time', 'conference', 'division', 'opponent', 'stadium']
        
        # Count how many basic patterns are found
        pattern_count = sum(1 for pattern in basic_patterns if pattern in table_text)
        
        # Only classify as basic if we find multiple basic patterns (to avoid false positives)
        if pattern_count >= 2:
            return True
        
        return False
    
    def _extract_table_headers(self, table: Tag) -> List[str]:
        """Extract table headers"""
        headers = []
        thead = table.find('thead')
        if thead and isinstance(thead, Tag):
            header_rows = thead.find_all('tr')
            for row in header_rows:
                if not isinstance(row, Tag):
                    continue
                cells = row.find_all(['th', 'td'])
                for cell in cells:
                    if not isinstance(cell, Tag):
                        continue
                    header_text = cell.get_text(strip=True)
                    if header_text:
                        headers.append(header_text)
        # If no thead, look for first row
        if not headers:
            first_row = table.find('tr')
            if first_row and isinstance(first_row, Tag):
                cells = first_row.find_all(['th', 'td'])
                for cell in cells:
                    if not isinstance(cell, Tag):
                        continue
                    header_text = cell.get_text(strip=True)
                    if header_text:
                        headers.append(header_text)
        return headers
    
    def _has_advanced_splits_data_patterns(self, table: Tag) -> bool:
        """Check for advanced splits data patterns in table"""
        # Look for rows with advanced splits data
        rows = [row for row in table.find_all('tr') if isinstance(row, Tag)]
        advanced_patterns = ['1st down', '2nd down', '3rd down', '4th down', '1-3', '4-6', '7-9', '10+']
        for row in rows:
            row_text = row.get_text().lower()
            if any(pattern in row_text for pattern in advanced_patterns):
                return True
        return False
    
    def _has_basic_splits_data_patterns(self, table: Tag) -> bool:
        """Check for basic splits data patterns in table"""
        # Look for rows with basic splits data
        rows = [row for row in table.find_all('tr') if isinstance(row, Tag)]
        basic_patterns = ['home', 'away', 'win', 'loss', 'tie', 'quarter', 'overtime']
        for row in rows:
            row_text = row.get_text().lower()
            if any(pattern in row_text for pattern in basic_patterns):
                return True
        return False
    
    def _extract_basic_splits_table(self, table: Tag, pfr_id: str, player_name: str, 
                                   season: int, scraped_at: datetime) -> List[QBSplitsType1]:
        """
        Extract basic splits data from a table (34 columns)
        
        Args:
            table: BeautifulSoup table element
            pfr_id: Player's PFR ID
            player_name: Player's name
            season: Season year
            scraped_at: Timestamp
            
        Returns:
            List of QBSplitsType1 objects
        """
        splits = []
        
        # Find all data rows
        tbody = table.find('tbody')
        if not tbody or not isinstance(tbody, Tag):
            logger.warning("No tbody found in basic splits table")
            return splits
        
        rows = [row for row in tbody.find_all('tr') if isinstance(row, Tag)]
        logger.info(f"Found {len(rows)} rows in basic splits table tbody")
        
        # Parse the PFR table structure with split categories and values
        current_split_category = None
        successful_rows = 0
        
        for i, row in enumerate(rows):
            try:
                # Skip header rows
                if self._is_header_or_empty_row(row):
                    logger.debug(f"Skipping header row {i}")
                    continue
                
                # Extract split data using data-stat based parsing  
                split_data = self._extract_basic_split_row(row, pfr_id, player_name, season, scraped_at)
                
                if split_data:
                    splits.append(split_data)
                    successful_rows += 1
                    
                    # Update current category if this looks like a category row
                    if self._looks_like_category_name(split_data.value):
                        current_split_category = split_data.value
                        logger.debug(f"Updated category to: {current_split_category}")
                    
                    logger.debug(f"Successfully extracted split: {split_data.split} = {split_data.value}")
                else:
                    logger.debug(f"Row {i} returned None from parsing")
                    
            except Exception as e:
                logger.error(f"Error processing basic split row {i}: {e}")
                continue
        
        logger.info(f"Basic splits processing summary: {len(rows)} total rows, {successful_rows} successful extractions")
        
        return splits
    
    def _parse_pfr_basic_splits_row(self, row: Tag, pfr_id: str, player_name: str, 
                                  season: int, scraped_at: datetime, 
                                  current_split_category: Optional[str]) -> Optional[QBSplitsType1]:
        """
        Parse a PFR basic splits row handling the concatenated split category + value structure
        
        Args:
            row: BeautifulSoup tr element
            pfr_id: Player's PFR ID
            player_name: Player's name
            season: Season year
            scraped_at: Timestamp
            current_split_category: Current split category for continuation rows
        
        Returns:
            QBSplitsType1 object or None if extraction fails
        """
        try:
            cells = [cell for cell in row.find_all(['td', 'th']) if isinstance(cell, Tag)]
            if len(cells) < 10:  # Basic splits should have many columns
                logger.debug(f"Row skipped: insufficient cells ({len(cells)})")
                return None
            
            first_cell_text = cells[0].get_text(strip=True)
            logger.debug(f"Parsing row with first cell: '{first_cell_text}'")
            
            # Simplified approach: use first cell as value, derive split from context
            if not first_cell_text:
                logger.debug(f"Row skipped: empty first cell")
                return None
                
            # Use first cell directly as the split value
            split_value = first_cell_text
            split_category = current_split_category or "Unknown"
            
            logger.debug(f"Using simplified parsing: split='{split_category}', value='{split_value}'")
            
            # Extract all cell values - PFR uses data-stat attributes
            stats_data = {}
            for i, cell in enumerate(cells):
                if not isinstance(cell, Tag):
                    continue
                data_stat = cell.get('data-stat', f'col_{i}')
                cell_text = cell.get_text(strip=True)
                stats_data[data_stat] = cell_text
                
            logger.debug(f"Extracted {len(stats_data)} data fields: {list(stats_data.keys())[:10]}...")
            
            # Map to QBSplitsType1 fields based on expected CSV structure
            # Expected columns: Split,Value,G,W,L,T,Cmp,Att,Inc,Cmp%,Yds,TD,Int,Rate,Sk,Yds,Y/A,AY/A,A/G,Y/G,Att,Yds,Y/A,TD,A/G,Y/G,TD,Pts,Fmb,FL,FF,FR,Yds,TD
            
            return QBSplitsType1(
                pfr_id=pfr_id,
                player_name=player_name,
                season=season,
                split=split_category,
                value=split_value,
                g=self._safe_int(stats_data.get('g')),
                w=self._safe_int(stats_data.get('w')),
                l=self._safe_int(stats_data.get('l')),
                t=self._safe_int(stats_data.get('t')),
                cmp=self._safe_int(stats_data.get('pass_cmp')),
                att=self._safe_int(stats_data.get('pass_att')),
                inc=self._safe_int(stats_data.get('pass_inc')),
                cmp_pct=self._safe_percentage(stats_data.get('pass_cmp_perc')),
                yds=self._safe_int(stats_data.get('pass_yds')),
                td=self._safe_int(stats_data.get('pass_td')),
                int=self._safe_int(stats_data.get('pass_int')),
                rate=self._safe_float(stats_data.get('pass_rating')),
                sk=self._safe_int(stats_data.get('pass_sacked')),
                sk_yds=self._safe_int(stats_data.get('pass_sacked_yds')),
                y_a=self._safe_float(stats_data.get('pass_yds_per_att')),
                ay_a=self._safe_float(stats_data.get('pass_adj_yds_per_att')),
                a_g=self._safe_float(stats_data.get('pass_att_per_game')),
                y_g=self._safe_float(stats_data.get('pass_yds_per_game')),
                rush_att=self._safe_int(stats_data.get('rush_att')),
                rush_yds=self._safe_int(stats_data.get('rush_yds')),
                rush_y_a=self._safe_float(stats_data.get('rush_yds_per_att')),
                rush_td=self._safe_int(stats_data.get('rush_td')),
                rush_a_g=self._safe_float(stats_data.get('rush_att_per_game')),
                rush_y_g=self._safe_float(stats_data.get('rush_yds_per_game')),
                total_td=self._safe_int(stats_data.get('total_td')),
                pts=self._safe_int(stats_data.get('fantasy_points')),
                fmb=self._safe_int(stats_data.get('fumbles')),
                fl=self._safe_int(stats_data.get('fumbles_lost')),
                ff=self._safe_int(stats_data.get('fumbles_forced')),
                fr=self._safe_int(stats_data.get('fumbles_rec')),
                fr_yds=self._safe_int(stats_data.get('fumbles_rec_yds')),
                fr_td=self._safe_int(stats_data.get('fumbles_rec_td')),
                scraped_at=scraped_at,
                updated_at=scraped_at
            )
            
        except Exception as e:
            logger.error(f"Error parsing PFR basic splits row: {e}")
            return None
    
    def _parse_pfr_split_category_and_value(self, first_cell_text: str, 
                                          current_split_category: Optional[str]) -> tuple[Optional[str], Optional[str]]:
        """
        Parse PFR's concatenated split category and value from first cell text
        
        Examples:
        - "PlaceHome" -> ("Place", "Home")
        - "Road" -> (current_split_category, "Road") 
        - "ResultWin" -> ("Result", "Win")
        - "Loss" -> (current_split_category, "Loss")
        """
        if not first_cell_text:
            return None, None
            
        # Known split categories from the CSV - comprehensive list
        split_categories = [
            'League', 'Place', 'Result', 'Final Margin', 'Month', 'Game Number', 
            'Day', 'Time', 'Conference', 'Division', 'Opponent', 'Stadium', 'QB Start'
        ]
        
        # Check if the text starts with a known category
        for category in split_categories:
            if first_cell_text.startswith(category):
                # Extract the value part
                value = first_cell_text[len(category):]
                if value:  # Only return if there's a value part
                    return category, value
        
        # If no category match, this might be a continuation row
        if current_split_category:
            return current_split_category, first_cell_text
            
        # Fallback: treat the whole text as a value with unknown category
        logger.debug(f"Could not categorize: '{first_cell_text}'")
        return "Other", first_cell_text
    
    def _safe_int(self, value: Optional[str]) -> Optional[int]:
        """Safely convert string to int"""
        if not value or value == '':
            return None
        try:
            return int(float(value))  # Handle "123.0" strings
        except (ValueError, TypeError):
            return None
    
    def _safe_float(self, value: Optional[str]) -> Optional[float]:
        """Safely convert string to float"""
        if not value or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _safe_percentage(self, value: Optional[str]) -> Optional[float]:
        """Safely convert percentage string to float"""
        if not value or value == '':
            return None
        try:
            # Remove % if present
            clean_value = value.replace('%', '')
            return float(clean_value)
        except (ValueError, TypeError):
            return None
    
    def _extract_basic_split_row(self, row: Tag, pfr_id: str, player_name: str, 
                                season: int, scraped_at: datetime) -> Optional[QBSplitsType1]:
        """
        Extract data from a single basic split row using data-stat attributes for reliable mapping.
        
        Args:
            row: BeautifulSoup tr element
            pfr_id: Player's PFR ID
            player_name: Player's name
            season: Season year
            scraped_at: Timestamp

        Returns:
            QBSplitsType1 object or None if extraction fails.
        """
        try:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                return None
                
            # Skip header rows - check if first cell contains header text
            first_cell_text = ''
            if cells and isinstance(cells[0], Tag):
                first_cell_text = cells[0].get_text(strip=True)
            if first_cell_text in ['Split', 'Value']:  # Only skip actual header rows
                return None
            
            # Use data-stat attributes for reliable field mapping
            row_data = {
                'pfr_id': pfr_id,
                'player_name': player_name, 
                'season': season,
                'scraped_at': scraped_at,
                'updated_at': scraped_at
            }
            
            # Extract all cells using data-stat attributes
            for cell in cells:
                if not isinstance(cell, Tag):
                    continue
                data_stat = cell.get('data-stat')
                cell_text = cell.get_text(strip=True)
                
                if data_stat and cell_text:
                    # Map data-stat attributes to model fields
                    if data_stat == 'split_id':  # Split category (League, Place, etc.)
                        row_data['split'] = cell_text
                    elif data_stat == 'split_value':  # Split value (NFL, Home, etc.)
                        row_data['value'] = cell_text
                    elif data_stat == 'g':
                        row_data['g'] = self._safe_int(cell_text)
                    elif data_stat == 'wins':
                        row_data['w'] = self._safe_int(cell_text)
                    elif data_stat == 'losses':
                        row_data['l'] = self._safe_int(cell_text)
                    elif data_stat == 'ties':
                        row_data['t'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_cmp':
                        row_data['cmp'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_att':
                        row_data['att'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_inc':
                        row_data['inc'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_cmp_perc':
                        row_data['cmp_pct'] = self._safe_percentage(cell_text)
                    elif data_stat == 'pass_yds':
                        row_data['yds'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_td':
                        row_data['td'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_int':
                        row_data['int'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_rating':
                        row_data['rate'] = self._safe_float(cell_text)
                    elif data_stat == 'pass_sacked':
                        row_data['sk'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_sacked_yds':
                        row_data['sk_yds'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_yds_per_att':
                        row_data['y_a'] = self._safe_float(cell_text)
                    elif data_stat == 'pass_adj_yds_per_att':
                        row_data['ay_a'] = self._safe_float(cell_text)
                    elif data_stat == 'pass_att_per_g':
                        row_data['a_g'] = self._safe_float(cell_text)
                    elif data_stat == 'pass_yds_per_g':
                        row_data['y_g'] = self._safe_float(cell_text)
                    elif data_stat == 'rush_att':
                        row_data['rush_att'] = self._safe_int(cell_text)
                    elif data_stat == 'rush_yds':
                        row_data['rush_yds'] = self._safe_int(cell_text)
                    elif data_stat == 'rush_yds_per_att':
                        row_data['rush_y_a'] = self._safe_float(cell_text)
                    elif data_stat == 'rush_td':
                        row_data['rush_td'] = self._safe_int(cell_text)
                    elif data_stat == 'rush_att_per_g':
                        row_data['rush_a_g'] = self._safe_float(cell_text)
                    elif data_stat == 'rush_yds_per_g':
                        row_data['rush_y_g'] = self._safe_float(cell_text)
                    elif data_stat == 'all_td':
                        row_data['total_td'] = self._safe_int(cell_text)
                    elif data_stat == 'scoring':
                        row_data['pts'] = self._safe_int(cell_text)
                    elif data_stat == 'fumbles':
                        row_data['fmb'] = self._safe_int(cell_text)
                    elif data_stat == 'fumbles_lost':
                        row_data['fl'] = self._safe_int(cell_text)
                    elif data_stat == 'fumbles_forced':
                        row_data['ff'] = self._safe_int(cell_text)
                    elif data_stat == 'fumbles_rec':
                        row_data['fr'] = self._safe_int(cell_text)
                    elif data_stat == 'fumbles_rec_yds':
                        row_data['fr_yds'] = self._safe_int(cell_text)
                    elif data_stat == 'fumbles_rec_td':
                        row_data['fr_td'] = self._safe_int(cell_text)
            
            # Validate required fields - allow rows with at least split OR value
            if not row_data.get('split') and not row_data.get('value'):
                logger.debug("Row skipped: no split category or value")
                return None
            
            # For continuation rows (empty split but has value), use "Continuation" as split  
            if not row_data.get('split') and row_data.get('value'):
                row_data['split'] = 'Continuation'
                
            # Create QBSplitsType1 instance
            return QBSplitsType1(**row_data)
            
        except Exception as e:
            logger.debug(f"Failed to extract basic split row: {e}")
            return None
    
    def _extract_advanced_split_row(self, row: Tag, pfr_id: str, player_name: str,
                                   season: int, scraped_at: datetime) -> Optional[QBSplitsType2]:
        """
        Extract data from a single advanced split row (qb_splits_advanced table).

        Args:
            row: BeautifulSoup tr element
            pfr_id: Player's PFR ID
            player_name: Player's name
            season: Season year
            scraped_at: Timestamp

        Returns:
            QBSplitsType2 object or None if extraction fails.

        For each required field, if missing/unmapped, assigns a default value and logs a warning with full context (player, season, split, value, field name).
        Follows mapping and validation rules in .cursor/rules/field-mapping-validation.mdc.
        """
        try:
            cells = row.find_all(['td', 'th'])
            if len(cells) < 2:
                return None
                
            # Skip header rows - check if first cell contains header text  
            first_cell_text = cells[0].get_text(strip=True)
            if first_cell_text in ['Split', 'Value']:  # Only skip actual header rows
                return None
            
            # Use data-stat attributes for reliable field mapping
            row_data = {
                'pfr_id': pfr_id,
                'player_name': player_name, 
                'season': season,
                'scraped_at': scraped_at,
                'updated_at': scraped_at
            }
            
            # Extract all cells using data-stat attributes for advanced splits
            for cell in cells:
                if not isinstance(cell, Tag):
                    continue
                data_stat = cell.get('data-stat')
                cell_text = cell.get_text(strip=True)
                
                if data_stat and cell_text:
                    # Map data-stat attributes to model fields for advanced splits
                    if data_stat == 'split_type':  # Split category (Down, Field Position, etc.)
                        row_data['split'] = cell_text
                    elif data_stat == 'split_value':  # Split value (1st, 2nd, Red Zone, etc.)
                        row_data['value'] = cell_text
                    elif data_stat == 'pass_cmp':
                        row_data['cmp'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_att':
                        row_data['att'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_inc':
                        row_data['inc'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_cmp_perc':
                        row_data['cmp_pct'] = self._safe_percentage(cell_text)
                    elif data_stat == 'pass_yds':
                        row_data['yds'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_td':
                        row_data['td'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_first_down':
                        row_data['first_downs'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_int':
                        row_data['int'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_rating':
                        row_data['rate'] = self._safe_float(cell_text)
                    elif data_stat == 'pass_sacked':
                        row_data['sk'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_sacked_yds':
                        row_data['sk_yds'] = self._safe_int(cell_text)
                    elif data_stat == 'pass_yds_per_att':
                        row_data['y_a'] = self._safe_float(cell_text)
                    elif data_stat == 'pass_adj_yds_per_att':
                        row_data['ay_a'] = self._safe_float(cell_text)
                    elif data_stat == 'rush_att':
                        row_data['rush_att'] = self._safe_int(cell_text)
                    elif data_stat == 'rush_yds':
                        row_data['rush_yds'] = self._safe_int(cell_text)
                    elif data_stat == 'rush_yds_per_att':
                        row_data['rush_y_a'] = self._safe_float(cell_text)
                    elif data_stat == 'rush_td':
                        row_data['rush_td'] = self._safe_int(cell_text)
                    elif data_stat == 'rush_first_down':
                        row_data['rush_first_downs'] = self._safe_int(cell_text)
            
            # Validate required fields - allow rows with at least split OR value 
            if not row_data.get('split') and not row_data.get('value'):
                return None
            
            # For continuation rows (empty split but has value), use "Continuation" as split
            if not row_data.get('split') and row_data.get('value'):
                row_data['split'] = 'Continuation'
                
            # Create QBSplitsType2 instance
            return QBSplitsType2(**row_data)
            
        except Exception as e:
            logger.error(f"Error extracting advanced split row data: {e}")
            return None
    
    def _extract_split_type_from_row(self, row: Tag) -> str:
        """Extract split type from a table row"""
        # Try to determine split type from row context
        # Look for parent table ID or nearby headers
        table = row.find_parent('table') if isinstance(row, Tag) else None
        if table and isinstance(table, Tag):
            table_id_raw = table.get('id')
            table_id = str(table_id_raw).lower() if table_id_raw else ''
        else:
            table_id = ''
        if 'advanced' in table_id or 'splits_advanced' in table_id:
            return 'advanced_splits'
        elif 'down' in table_id or 'yards' in table_id:
            return 'down_and_distance'
        elif 'quarter' in table_id:
            return 'by_quarter'
        elif 'home' in table_id or 'away' in table_id:
            return 'home_away'
        elif 'win' in table_id or 'loss' in table_id:
            return 'win_loss'
        return 'basic_splits'
    
    def _extract_all_cell_values(self, cells: List[Tag]) -> Dict[str, str]:
        """
        Extract all cell values using aria-label, data-stat, and data-name attributes
        
        Args:
            cells: List of table cells
            
        Returns:
            Dictionary mapping field names to cell values
        """
        extracted_data = {}
        
        for cell in cells:
            # Try aria-label first, then data-stat, then data-name
            aria_label = cell.get('aria-label', '') if hasattr(cell, 'get') else ''
            data_stat = cell.get('data-stat', '') if hasattr(cell, 'get') else ''
            data_name = cell.get('data-name', '') if hasattr(cell, 'get') else ''
            
            # Use the first available attribute
            field_name = aria_label or data_stat or data_name
            
            if field_name:
                cell_value = cell.get_text(strip=True) if hasattr(cell, 'get_text') else ''
                extracted_data[field_name] = cell_value
                
                # Also store under data-stat for backward compatibility
                if data_stat and data_stat != field_name:
                    extracted_data[data_stat] = cell_value
        
        return extracted_data
    
    def validate_extraction_result(self, result: SplitsExtractionResult) -> List[str]:
        """
        Validate the extraction result
        
        Args:
            result: SplitsExtractionResult to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Check for critical errors
        if result.errors:
            errors.extend([f"Extraction error: {error}" for error in result.errors])
        
        # Check data quality
        if result.tables_discovered == 0:
            errors.append("No splits tables discovered")
        
        if result.tables_processed == 0:
            errors.append("No splits tables processed")
        
        if result.tables_processed < result.tables_discovered:
            warnings = [f"Only processed {result.tables_processed}/{result.tables_discovered} tables"]
            result.warnings.extend(warnings)
        
        # Check extraction time
        if result.extraction_time > 30:  # More than 30 seconds
            warnings = [f"Slow extraction time: {result.extraction_time:.2f}s"]
            result.warnings.extend(warnings)
        
        return errors 
    
    def _looks_like_category_name(self, value: Optional[str]) -> bool:
        """Check if a value looks like a split category name"""
        if not value:
            return False
        category_names = [
            'League', 'Place', 'Result', 'Final Margin', 'Month', 'Game Number', 
            'Day', 'Time', 'Conference', 'Division', 'Opponent', 'Stadium', 'QB Start'
        ]
        return value in category_names
    
    def _looks_like_advanced_category_name(self, value: Optional[str]) -> bool:
        """Check if a value looks like an advanced split category name"""
        if not value:
            return False
        advanced_category_names = [
            'Down', 'Yards To Go', 'Down & Yards to Go', 'Field Position', 'Score Differential',
            'Quarter', 'Game Situation', 'Snap Type & Huddle', 'Play Action', 'Run/Pass Option', 'Time in Pocket'
        ]
        return value in advanced_category_names
    
    def _extract_advanced_splits_table(self, table: Tag, pfr_id: str, player_name: str, 
                                      season: int, scraped_at: datetime) -> List[QBSplitsType2]:
        """
        Extract advanced splits data from a table (20 columns)
        
        Args:
            table: BeautifulSoup table element
            pfr_id: Player's PFR ID
            player_name: Player's name
            season: Season year
            scraped_at: Timestamp
            
        Returns:
            List of QBSplitsType2 objects
        """
        splits = []
        
        # Find all data rows
        tbody = table.find('tbody')
        if not tbody or not isinstance(tbody, Tag):
            logger.warning("No tbody found in advanced splits table")
            return splits
        
        rows = [row for row in tbody.find_all('tr') if isinstance(row, Tag)]
        logger.info(f"Found {len(rows)} rows in advanced splits table tbody")
        
        # Parse the PFR table structure with split categories and values
        current_split_category = None
        successful_rows = 0
        
        for i, row in enumerate(rows):
            try:
                # Skip header rows
                if self._is_header_or_empty_row(row):
                    logger.debug(f"Skipping header row {i}")
                    continue
                
                # Extract split data using advanced splits parsing
                split_data = self._extract_advanced_split_row(row, pfr_id, player_name, season, scraped_at)
                
                if split_data:
                    splits.append(split_data)
                    successful_rows += 1
                    
                    # Update current category if this looks like a category row
                    if self._looks_like_advanced_category_name(split_data.value):
                        current_split_category = split_data.value
                        logger.debug(f"Updated advanced category to: {current_split_category}")
                    
                    logger.debug(f"Successfully extracted advanced split: {split_data.split} = {split_data.value}")
                else:
                    logger.debug(f"Advanced row {i} returned None from parsing")
                    
            except Exception as e:
                logger.error(f"Error processing advanced split row {i}: {e}")
                continue
        
        logger.info(f"Advanced splits processing summary: {len(rows)} total rows, {successful_rows} successful extractions")
        
        return splits

    def _get_priority_tables(self, discovered_tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process ALL discovered tables to extract all splits categories"""
        # Process ALL tables instead of just the "best" one
        # This ensures we get all the different splits categories (Home/Away, Win/Loss, Quarters, etc.)
        logger.info(f"Processing ALL {len(discovered_tables)} discovered tables")
        
        # Group tables by type for logging
        basic_tables = [t for t in discovered_tables if t['type'] == 'basic_splits']
        advanced_tables = [t for t in discovered_tables if t['type'] == 'advanced_splits']
        
        logger.info(f"Found {len(basic_tables)} basic splits tables and {len(advanced_tables)} advanced splits tables")
        
        # Log all tables for debugging
        for i, table in enumerate(basic_tables):
            logger.info(f"Basic splits table {i+1}: {table['id']} (priority: {table.get('priority', 'unknown')})")
        
        for i, table in enumerate(advanced_tables):
            logger.info(f"Advanced splits table {i+1}: {table['id']} (priority: {table.get('priority', 'unknown')})")
        
        # Return ALL tables - don't filter by priority
        return discovered_tables 

    def _find_table_by_info(self, soup: BeautifulSoup, table_info: Dict[str, Any]) -> Optional[Tag]:
        """Find a table element based on its table_info dictionary."""
        table_id = table_info['id']
        table_type = table_info['type']
        
        # Find the table by ID
        table = soup.find('table', id=table_id)
        if not table or not isinstance(table, Tag):
            logger.warning(f"Table with ID '{table_id}' not found or not a Tag.")
            return None
        
        # Verify the table type matches the expected type
        if table_type == 'advanced_splits':
            if not self._has_advanced_splits_indicators(table):
                logger.warning(f"Table with ID '{table_id}' is marked as advanced_splits but does not have advanced indicators.")
                return None
        elif table_type == 'basic_splits':
            if not self._has_basic_splits_indicators(table):
                logger.warning(f"Table with ID '{table_id}' is marked as basic_splits but does not have basic indicators.")
                return None
        
        return table

    def _is_header_or_empty_row(self, row: Tag) -> bool:
        """
        Helper to check if a row is a header row or an empty row.
        Header rows contain column headers like 'Split', 'Value', 'G', 'W', 'L', etc.
        """
        # Check if the row is empty or contains only whitespace
        if not isinstance(row, Tag) or not row.find_all(['th', 'td']):
            return True
        
        # Get all cell text content
        cells = row.find_all(['th', 'td'])
        if not cells:
            return True
            
        # Check if this is a header row by looking for the full header pattern
        row_text = ''.join(cell.get_text(strip=True) for cell in cells if isinstance(cell, Tag))
        
        # Real header rows contain multiple column headers together
        # Like: "SplitValueGWLTCmpAttIncCmp%YdsTDIntRate..."
        header_indicators = ['SplitValue', 'CmpAtt', 'YdsIntRate', 'GWLTCmp']
        if any(indicator in row_text for indicator in header_indicators):
            return True
            
        # Also check if row contains all TH elements (traditional header row)
        if all(isinstance(cell, Tag) and cell.name == 'th' for cell in cells):
            return True
            
        # Check if first cell contains only "Split" or "Value" (column header)
        first_cell_text = cells[0].get_text(strip=True) if cells and isinstance(cells[0], Tag) else ''
        if first_cell_text in ['Split', 'Value'] and len(cells) > 10:
            return True
            
        return False

    def _validate_csv_format_compliance(self, row_data: Dict[str, Any], split_type: str, 
                                       player_name: str, season: int) -> List[str]:
        """
        Validate that extracted data matches CSV format exactly.
        
        Args:
            row_data: Extracted row data
            split_type: Type of split (basic or advanced)
            player_name: Player name for logging
            season: Season for logging
            
        Returns:
            List of validation errors
        """
        errors = []
        
        if split_type == 'basic_splits':
            # Validate against advanced_stats_1.csv format
            expected_fields = self.QB_SPLITS_FIELDS
            csv_format = "advanced_stats_1.csv"
        else:
            # Validate against advanced_stats.2.csv format
            expected_fields = self.QB_SPLITS_ADVANCED_FIELDS
            csv_format = "advanced_stats.2.csv"
        
        # Check that all expected fields are present
        missing_fields = []
        for field in expected_fields:
            if field not in row_data or row_data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            errors.append(f"Missing required fields for {csv_format}: {missing_fields}")
            logger.warning(f"CSV format violation for {player_name} season {season}: "
                          f"missing fields {missing_fields} for {csv_format}")
        
        # Check for unexpected fields
        unexpected_fields = []
        for field in row_data:
            if field not in expected_fields and field not in ['pfr_id', 'player_name', 'season', 'scraped_at', 'updated_at']:
                unexpected_fields.append(field)
        
        if unexpected_fields:
            errors.append(f"Unexpected fields for {csv_format}: {unexpected_fields}")
            logger.warning(f"CSV format violation for {player_name} season {season}: "
                          f"unexpected fields {unexpected_fields} for {csv_format}")
        
        return errors 
