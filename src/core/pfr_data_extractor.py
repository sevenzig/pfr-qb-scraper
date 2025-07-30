#!/usr/bin/env python3
"""
PFR Data Extractor - Comprehensive data extraction from Pro Football Reference.

This module provides robust data extraction from PFR's HTML structure,
using the PFRStructureAnalyzer to ensure complete and accurate data extraction.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from bs4 import BeautifulSoup, Tag
import re

from .pfr_structure_analyzer import PFRStructureAnalyzer, DataStatMapping

logger = logging.getLogger(__name__)


@dataclass
class ExtractionResult:
    """Result of data extraction operation."""
    success: bool
    data: Dict[str, Any]
    table_type: str
    row_count: int
    extracted_fields: List[str]
    missing_fields: List[str]
    errors: List[str]
    warnings: List[str]


class PFRDataExtractor:
    """
    Comprehensive data extractor for Pro Football Reference.
    
    This class provides robust extraction of QB data from PFR's HTML structure,
    using proper attribute mapping and validation to ensure data completeness.
    """
    
    def __init__(self):
        """Initialize the PFR data extractor."""
        self.structure_analyzer = PFRStructureAnalyzer()
        self.safe_conversion_functions = {
            'int': self._safe_int,
            'float': self._safe_float,
            'str': self._safe_str
        }
    
    def extract_all_qb_data(self, soup: BeautifulSoup, player_name: str, 
                           season: int) -> Dict[str, ExtractionResult]:
        """
        Extract all QB data from a PFR page.
        
        Args:
            soup: BeautifulSoup object of the PFR page
            player_name: Name of the player being extracted
            season: Season year
            
        Returns:
            Dictionary mapping table types to extraction results
        """
        logger.info(f"Starting comprehensive data extraction for {player_name} ({season})")
        
        # Analyze page structure first
        structure_analysis = self.structure_analyzer.analyze_page_structure(soup)
        logger.info(f"Page analysis complete. Found {structure_analysis['total_tables']} tables")
        
        # Extract data from each table type
        results = {}
        
        # Extract basic stats
        basic_stats_result = self._extract_basic_stats(soup, structure_analysis)
        if basic_stats_result:
            results['basic_stats'] = basic_stats_result
        
        # Extract splits data
        splits_result = self._extract_splits_data(soup, structure_analysis)
        if splits_result:
            results['splits'] = splits_result
        
        # Extract advanced splits data
        advanced_splits_result = self._extract_advanced_splits_data(soup, structure_analysis)
        if advanced_splits_result:
            results['advanced_splits'] = advanced_splits_result
        
        # Add metadata
        for result in results.values():
            result.data['player_name'] = player_name
            result.data['season'] = season
        
        logger.info(f"Data extraction complete. Extracted {len(results)} table types")
        return results
    
    def _extract_basic_stats(self, soup: BeautifulSoup, 
                            structure_analysis: Dict[str, Any]) -> Optional[ExtractionResult]:
        """
        Extract QB basic stats from the page.
        
        Args:
            soup: BeautifulSoup object of the PFR page
            structure_analysis: Results from structure analysis
            
        Returns:
            ExtractionResult with basic stats data
        """
        logger.info("Extracting QB basic stats")
        
        # Find basic stats table
        basic_stats_tables = structure_analysis['table_categorization']['basic_stats']
        if not basic_stats_tables:
            logger.warning("No basic stats table found")
            return None
        
        # Use the first basic stats table found
        table_info = basic_stats_tables[0]
        table = self._find_table_by_info(soup, table_info)
        if not table:
            logger.error(f"Could not find basic stats table: {table_info.table_id}")
            return None
        
        # Extract data using proper mappings
        mappings = self.structure_analyzer.get_field_mappings('basic_stats')
        extraction_result = self._extract_table_data(table, mappings, 'basic_stats')
        
        logger.info(f"Basic stats extraction complete. Extracted {len(extraction_result.extracted_fields)} fields")
        return extraction_result
    
    def _extract_splits_data(self, soup: BeautifulSoup, 
                            structure_analysis: Dict[str, Any]) -> Optional[ExtractionResult]:
        """
        Extract QB splits data from the page.
        
        Args:
            soup: BeautifulSoup object of the PFR page
            structure_analysis: Results from structure analysis
            
        Returns:
            ExtractionResult with splits data
        """
        logger.info("Extracting QB splits data")
        
        # Find splits table
        splits_tables = structure_analysis['table_categorization']['splits']
        if not splits_tables:
            logger.warning("No splits table found")
            return None
        
        # Use the first splits table found
        table_info = splits_tables[0]
        table = self._find_table_by_info(soup, table_info)
        if not table:
            logger.error(f"Could not find splits table: {table_info.table_id}")
            return None
        
        # Extract data using proper mappings
        mappings = self.structure_analyzer.get_field_mappings('splits')
        extraction_result = self._extract_table_data(table, mappings, 'splits')
        
        logger.info(f"Splits extraction complete. Extracted {len(extraction_result.extracted_fields)} fields")
        return extraction_result
    
    def _extract_advanced_splits_data(self, soup: BeautifulSoup, 
                                     structure_analysis: Dict[str, Any]) -> Optional[ExtractionResult]:
        """
        Extract QB advanced splits data from the page.
        
        Args:
            soup: BeautifulSoup object of the PFR page
            structure_analysis: Results from structure analysis
            
        Returns:
            ExtractionResult with advanced splits data
        """
        logger.info("Extracting QB advanced splits data")
        
        # Find advanced splits table
        advanced_splits_tables = structure_analysis['table_categorization']['advanced_splits']
        if not advanced_splits_tables:
            logger.warning("No advanced splits table found")
            return None
        
        # Use the first advanced splits table found
        table_info = advanced_splits_tables[0]
        table = self._find_table_by_info(soup, table_info)
        if not table:
            logger.error(f"Could not find advanced splits table: {table_info.table_id}")
            return None
        
        # Extract data using proper mappings
        mappings = self.structure_analyzer.get_field_mappings('advanced_splits')
        extraction_result = self._extract_table_data(table, mappings, 'advanced_splits')
        
        logger.info(f"Advanced splits extraction complete. Extracted {len(extraction_result.extracted_fields)} fields")
        return extraction_result
    
    def _find_table_by_info(self, soup: BeautifulSoup, table_info: Any) -> Optional[Tag]:
        """
        Find a table in the soup based on table info.
        
        Args:
            soup: BeautifulSoup object
            table_info: TableInfo object with table details
            
        Returns:
            BeautifulSoup table tag if found, None otherwise
        """
        # Try to find by ID first
        if table_info.table_id and table_info.table_id != f'table_{table_info.table_index}':
            table = soup.find('table', id=table_info.table_id)
            if table:
                return table
        
        # Try to find by class
        if table_info.table_class:
            class_list = table_info.table_class.split()
            table = soup.find('table', class_=class_list)
            if table:
                return table
        
        # Fall back to index-based lookup
        tables = soup.find_all('table')
        if table_info.table_index < len(tables):
            return tables[table_info.table_index]
        
        return None
    
    def _extract_table_data(self, table: Tag, mappings: List[DataStatMapping], 
                           table_type: str) -> ExtractionResult:
        """
        Extract data from a table using provided mappings.
        
        Args:
            table: BeautifulSoup table tag
            mappings: List of DataStatMapping objects
            table_type: Type of table being extracted
            
        Returns:
            ExtractionResult with extracted data
        """
        logger.info(f"Extracting data from {table_type} table")
        
        # Find all data rows (skip header rows)
        rows = table.find_all('tr')
        data_rows = []
        
        for row in rows:
            # Skip header rows (rows with th elements)
            if not row.find('th') and row.find('td'):
                data_rows.append(row)
        
        if not data_rows:
            logger.warning(f"No data rows found in {table_type} table")
            return ExtractionResult(
                success=False,
                data={},
                table_type=table_type,
                row_count=0,
                extracted_fields=[],
                missing_fields=[m.database_field for m in mappings if m.is_required],
                errors=["No data rows found"],
                warnings=[]
            )
        
        # Extract data from each row
        extracted_data = {}
        extracted_fields = []
        missing_fields = []
        errors = []
        warnings = []
        
        # For basic stats, we typically want the first (and usually only) data row
        # For splits, we want all rows
        target_rows = data_rows if table_type in ['splits', 'advanced_splits'] else data_rows[:1]
        
        for row in target_rows:
            row_data = self._extract_row_data(row, mappings)
            extracted_data.update(row_data)
            
            # Track extracted and missing fields
            for mapping in mappings:
                if mapping.database_field in row_data:
                    if mapping.database_field not in extracted_fields:
                        extracted_fields.append(mapping.database_field)
                elif mapping.is_required and mapping.database_field not in missing_fields:
                    missing_fields.append(mapping.database_field)
        
        # Validate the extracted data
        validation_result = self.structure_analyzer.validate_extracted_data(extracted_data, table_type)
        
        success = validation_result['valid'] and len(errors) == 0
        
        return ExtractionResult(
            success=success,
            data=extracted_data,
            table_type=table_type,
            row_count=len(target_rows),
            extracted_fields=extracted_fields,
            missing_fields=missing_fields,
            errors=errors,
            warnings=warnings
        )
    
    def _extract_row_data(self, row: Tag, mappings: List[DataStatMapping]) -> Dict[str, Any]:
        """
        Extract data from a single table row.
        
        Args:
            row: BeautifulSoup tr tag
            mappings: List of DataStatMapping objects
            
        Returns:
            Dictionary of extracted field values
        """
        row_data = {}
        
        # Get all cells in the row
        cells = row.find_all(['td', 'th'])
        
        # Create mapping from data-stat attributes to cells
        cell_map = {}
        for cell in cells:
            data_stat = cell.get('data-stat')
            if data_stat:
                cell_map[data_stat] = cell
        
        # Extract data using mappings
        for mapping in mappings:
            cell = cell_map.get(mapping.pfr_attribute)
            if cell:
                # Extract text content
                text_content = cell.get_text(strip=True)
                
                # Convert to appropriate type
                converted_value = self._convert_value(text_content, mapping.data_type)
                
                if converted_value is not None:
                    row_data[mapping.database_field] = converted_value
                else:
                    logger.debug(f"Could not convert value '{text_content}' to {mapping.data_type} for {mapping.database_field}")
            else:
                logger.debug(f"No cell found for data-stat attribute '{mapping.pfr_attribute}'")
        
        return row_data
    
    def _convert_value(self, value: str, target_type: str) -> Any:
        """
        Safely convert a string value to the target type.
        
        Args:
            value: String value to convert
            target_type: Target data type ('int', 'float', 'str')
            
        Returns:
            Converted value or None if conversion fails
        """
        if not value or value.strip() == '':
            return None
        
        # Clean the value
        cleaned_value = value.strip()
        
        # Handle special cases
        if cleaned_value == '--' or cleaned_value == 'N/A':
            return None
        
        # Use safe conversion function
        conversion_func = self.safe_conversion_functions.get(target_type)
        if conversion_func:
            return conversion_func(cleaned_value)
        
        return None
    
    def _safe_int(self, value: str) -> Optional[int]:
        """Safely convert string to integer."""
        try:
            # Remove any non-numeric characters except minus sign
            cleaned = re.sub(r'[^\d\-]', '', value)
            if cleaned:
                return int(cleaned)
        except (ValueError, TypeError):
            pass
        return None
    
    def _safe_float(self, value: str) -> Optional[float]:
        """Safely convert string to float."""
        try:
            # Remove any non-numeric characters except minus sign and decimal point
            cleaned = re.sub(r'[^\d\-\.]', '', value)
            if cleaned:
                return float(cleaned)
        except (ValueError, TypeError):
            pass
        return None
    
    def _safe_str(self, value: str) -> Optional[str]:
        """Safely convert string (cleaning and validation)."""
        if value and value.strip():
            return value.strip()
        return None
    
    def get_extraction_summary(self, results: Dict[str, ExtractionResult]) -> Dict[str, Any]:
        """
        Generate a summary of extraction results.
        
        Args:
            results: Dictionary of extraction results
            
        Returns:
            Summary dictionary with key metrics
        """
        summary = {
            'total_tables_extracted': len(results),
            'successful_extractions': len([r for r in results.values() if r.success]),
            'total_fields_extracted': sum(len(r.extracted_fields) for r in results.values()),
            'total_missing_fields': sum(len(r.missing_fields) for r in results.values()),
            'total_errors': sum(len(r.errors) for r in results.values()),
            'total_warnings': sum(len(r.warnings) for r in results.values()),
            'table_details': {}
        }
        
        for table_type, result in results.items():
            summary['table_details'][table_type] = {
                'success': result.success,
                'row_count': result.row_count,
                'fields_extracted': len(result.extracted_fields),
                'fields_missing': len(result.missing_fields),
                'errors': len(result.errors),
                'warnings': len(result.warnings),
                'coverage_percentage': (len(result.extracted_fields) / 
                                      (len(result.extracted_fields) + len(result.missing_fields))) * 100
                if (len(result.extracted_fields) + len(result.missing_fields)) > 0 else 0
            }
        
        return summary 