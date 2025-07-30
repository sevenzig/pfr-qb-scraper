#!/usr/bin/env python3
"""
Unified Scraping Pipeline
Coordinates all scraping components to ensure proper data extraction from PFR.
"""

import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import traceback

from ..core.selenium_manager import SeleniumManager, SeleniumConfig
from ..core.pfr_structure_analyzer import PFRStructureAnalyzer
from ..core.pfr_data_extractor import PFRDataExtractor, ExtractionResult
from ..models.qb_models import QBSplitsType1, QBSplitsType2
from ..utils.data_utils import build_splits_url

logger = logging.getLogger(__name__)


@dataclass
class PipelineResult:
    """Result of unified scraping pipeline"""
    success: bool
    player_name: str
    pfr_id: str
    season: int
    basic_splits: List[QBSplitsType1]
    advanced_splits: List[QBSplitsType2]
    structure_analysis: Optional[Dict[str, Any]]
    extraction_result: Optional[ExtractionResult]
    processing_time: float
    errors: List[str]
    warnings: List[str]


class UnifiedScrapingPipeline:
    """
    Unified scraping pipeline that coordinates all components:
    - Selenium manager for page loading
    - Structure analyzer for understanding PFR layout
    - Data extractor for parsing and extracting data
    - Validation and error handling
    """
    
    def __init__(self, rate_limit_delay: float = 7.0):
        # Create Selenium manager with respectful rate limiting
        selenium_config = SeleniumConfig(
            headless=True,
            human_behavior_delay=(rate_limit_delay, rate_limit_delay + 3.0)
        )
        self.selenium_manager = SeleniumManager(selenium_config)
        
        # Initialize components
        self.structure_analyzer = PFRStructureAnalyzer(self.selenium_manager)
        self.data_extractor = PFRDataExtractor()
        
        # Pipeline configuration
        self.enable_structure_analysis = True
        self.enable_data_extraction = True
        self.enable_validation = True
        self.max_retries = 3
    
    def scrape_player_splits(self, pfr_id: str, player_name: str, season: int) -> PipelineResult:
        """
        Scrape splits data for a specific player using the unified pipeline
        
        Args:
            pfr_id: Player's PFR ID
            player_name: Player's name
            season: Season year
            
        Returns:
            PipelineResult with complete scraping results
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        try:
            logger.info(f"Starting unified scraping pipeline for {player_name} ({pfr_id})")
            
            # Step 1: Load page content
            html_content = self._load_page_content(pfr_id, player_name, season)
            if not html_content:
                error_msg = f"Failed to load page content for {player_name}"
                errors.append(error_msg)
                return PipelineResult(
                    success=False,
                    player_name=player_name,
                    pfr_id=pfr_id,
                    season=season,
                    basic_splits=[],
                    advanced_splits=[],
                    structure_analysis=None,
                    extraction_result=None,
                    processing_time=time.time() - start_time,
                    errors=errors,
                    warnings=warnings
                )
            
            # Step 2: Analyze structure (optional)
            structure_analysis = None
            if self.enable_structure_analysis:
                logger.info(f"Analyzing PFR structure for {player_name}")
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')
                structure_analysis = self.structure_analyzer.analyze_page_structure(soup)
                
                # Log structure analysis results
                logger.info(f"Structure analysis for {player_name}:")
                logger.info(f"  - Tables found: {structure_analysis.get('total_tables', 0)}")
                table_categorization = structure_analysis.get('table_categorization', {})
                logger.info(f"  - Basic splits tables: {len(table_categorization.get('splits', []))}")
                logger.info(f"  - Advanced splits tables: {len(table_categorization.get('advanced_splits', []))}")
            
            # Step 3: Extract data
            extraction_result = None
            if self.enable_data_extraction:
                logger.info(f"Extracting data for {player_name}")
                scraped_at = datetime.now()
                extraction_result = self.data_extractor.extract_splits_data(
                    html_content, pfr_id, player_name, season, scraped_at
                )
                
                if extraction_result.errors:
                    errors.extend([f"Data extraction error: {error}" for error in extraction_result.errors])
                
                if extraction_result.warnings:
                    warnings.extend([f"Data extraction warning: {warning}" for warning in extraction_result.warnings])
                
                # Log extraction results
                logger.info(f"Data extraction for {player_name}:")
                logger.info(f"  - Basic splits: {len(extraction_result.basic_splits)}")
                logger.info(f"  - Advanced splits: {len(extraction_result.advanced_splits)}")
                logger.info(f"  - Rows processed: {extraction_result.rows_processed}")
                logger.info(f"  - Rows extracted: {extraction_result.rows_extracted}")
            
            # Step 4: Validate results
            if self.enable_validation and extraction_result:
                validation_errors = self._validate_results(extraction_result, structure_analysis)
                if validation_errors:
                    errors.extend([f"Validation error: {error}" for error in validation_errors])
            
            # Determine success
            success = len(errors) == 0 and extraction_result and (
                len(extraction_result.basic_splits) > 0 or len(extraction_result.advanced_splits) > 0
            )
            
            processing_time = time.time() - start_time
            
            # Log final results
            logger.info(f"Unified pipeline completed for {player_name}:")
            logger.info(f"  - Success: {success}")
            logger.info(f"  - Processing time: {processing_time:.2f}s")
            logger.info(f"  - Errors: {len(errors)}")
            logger.info(f"  - Warnings: {len(warnings)}")
            
            return PipelineResult(
                success=success,
                player_name=player_name,
                pfr_id=pfr_id,
                season=season,
                basic_splits=extraction_result.basic_splits if extraction_result else [],
                advanced_splits=extraction_result.advanced_splits if extraction_result else [],
                structure_analysis=structure_analysis,
                extraction_result=extraction_result,
                processing_time=processing_time,
                errors=errors,
                warnings=warnings
            )
            
        except Exception as e:
            error_msg = f"Unexpected error in unified pipeline for {player_name}: {e}"
            errors.append(error_msg)
            logger.error(error_msg, exc_info=True)
            
            return PipelineResult(
                success=False,
                player_name=player_name,
                pfr_id=pfr_id,
                season=season,
                basic_splits=[],
                advanced_splits=[],
                structure_analysis=None,
                extraction_result=None,
                processing_time=time.time() - start_time,
                errors=errors,
                warnings=warnings
            )
    
    def _load_page_content(self, pfr_id: str, player_name: str, season: int) -> Optional[str]:
        """Load page content with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Build splits URL
                splits_url = build_splits_url(pfr_id, season)
                logger.debug(f"Loading page content for {player_name} (attempt {attempt + 1})")
                
                # Get page content
                result = self.selenium_manager.get_page(splits_url, enable_js=False)
                if result['success']:
                    logger.debug(f"Successfully loaded page content for {player_name}")
                    return result['content']
                else:
                    logger.warning(f"Failed to load page content for {player_name} (attempt {attempt + 1}): {result['error']}")
                    
            except Exception as e:
                logger.warning(f"Error loading page content for {player_name} (attempt {attempt + 1}): {e}")
                
            # Wait before retry
            if attempt < self.max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
        
        logger.error(f"Failed to load page content for {player_name} after {self.max_retries} attempts")
        return None
    
    def _validate_results(self, extraction_result: ExtractionResult, 
                         structure_analysis: Optional[Dict[str, Any]]) -> List[str]:
        """Validate extraction results"""
        errors = []
        
        # Validate extraction result
        extraction_errors = self.data_extractor.validate_extraction_result(extraction_result)
        errors.extend(extraction_errors)
        
        # Validate against structure analysis if available
        if structure_analysis:
            # Check if we found the expected number of tables
            total_tables = structure_analysis.get('total_tables', 0)
            if total_tables == 0:
                errors.append("No tables found in structure analysis")
            
            # Check if we extracted data from all identified splits tables
            table_categorization = structure_analysis.get('table_categorization', {})
            expected_basic_tables = len(table_categorization.get('splits', []))
            expected_advanced_tables = len(table_categorization.get('advanced_splits', []))
            
            if expected_basic_tables > 0 and len(extraction_result.basic_splits) == 0:
                errors.append(f"Found {expected_basic_tables} basic splits tables but extracted 0 basic splits")
            
            if expected_advanced_tables > 0 and len(extraction_result.advanced_splits) == 0:
                errors.append(f"Found {expected_advanced_tables} advanced splits tables but extracted 0 advanced splits")
        
        # Check for reasonable data volumes
        if extraction_result.rows_processed > 0:
            success_rate = extraction_result.rows_extracted / extraction_result.rows_processed
            if success_rate < 0.5:  # Less than 50% success rate
                errors.append(f"Low extraction success rate: {success_rate:.1%}")
        
        return errors
    
    def generate_pipeline_report(self, result: PipelineResult) -> str:
        """Generate a detailed pipeline report"""
        report = []
        report.append("=" * 80)
        report.append("UNIFIED SCRAPING PIPELINE REPORT")
        report.append("=" * 80)
        report.append(f"Player: {result.player_name}")
        report.append(f"PFR ID: {result.pfr_id}")
        report.append(f"Season: {result.season}")
        report.append(f"Success: {result.success}")
        report.append(f"Processing Time: {result.processing_time:.2f}s")
        report.append("")
        
        # Data extraction results
        report.append("DATA EXTRACTION RESULTS:")
        report.append("-" * 40)
        report.append(f"Basic Splits: {len(result.basic_splits)}")
        report.append(f"Advanced Splits: {len(result.advanced_splits)}")
        
        if result.extraction_result:
            report.append(f"Rows Processed: {result.extraction_result.rows_processed}")
            report.append(f"Rows Extracted: {result.extraction_result.rows_extracted}")
            if result.extraction_result.rows_processed > 0:
                success_rate = result.extraction_result.rows_extracted / result.extraction_result.rows_processed
                report.append(f"Success Rate: {success_rate:.1%}")
        
        # Structure analysis results
        if result.structure_analysis:
            report.append("")
            report.append("STRUCTURE ANALYSIS RESULTS:")
            report.append("-" * 40)
            report.append(f"Tables Found: {result.structure_analysis.get('total_tables', 0)}")
            table_categorization = result.structure_analysis.get('table_categorization', {})
            report.append(f"Basic Splits Tables: {len(table_categorization.get('splits', []))}")
            report.append(f"Advanced Splits Tables: {len(table_categorization.get('advanced_splits', []))}")
            report.append(f"Other Tables: {len(table_categorization.get('other', []))}")
        
        # Sample data
        if result.basic_splits:
            report.append("")
            report.append("SAMPLE BASIC SPLITS:")
            report.append("-" * 40)
            for i, split in enumerate(result.basic_splits[:3]):  # First 3
                report.append(f"Split {i+1}: {split.split} = {split.value}")
                report.append(f"  Completions: {split.cmp}, Attempts: {split.att}")
                report.append(f"  Yards: {split.yds}, TDs: {split.td}")
        
        if result.advanced_splits:
            report.append("")
            report.append("SAMPLE ADVANCED SPLITS:")
            report.append("-" * 40)
            for i, split in enumerate(result.advanced_splits[:3]):  # First 3
                report.append(f"Split {i+1}: {split.split} = {split.value}")
                report.append(f"  Completions: {split.cmp}, Attempts: {split.att}")
                report.append(f"  Yards: {split.yds}, TDs: {split.td}")
        
        # Errors and warnings
        if result.errors:
            report.append("")
            report.append("ERRORS:")
            report.append("-" * 40)
            for error in result.errors:
                report.append(f"  - {error}")
        
        if result.warnings:
            report.append("")
            report.append("WARNINGS:")
            report.append("-" * 40)
            for warning in result.warnings:
                report.append(f"  - {warning}")
        
        report.append("=" * 80)
        return "\n".join(report)
    
    def close(self):
        """Clean up resources"""
        if self.selenium_manager:
            self.selenium_manager.end_session()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close() 