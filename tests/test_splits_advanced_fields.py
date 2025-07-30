#!/usr/bin/env python3
"""
Test script to verify that cmp_pct and first_downs are being extracted correctly
from the advanced splits scraper.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

import logging
from datetime import datetime
from src.scrapers.enhanced_scraper import EnhancedPFRScraper
from src.models.qb_models import QBSplitsType2

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_advanced_splits_extraction():
    """Test that advanced splits extraction includes cmp_pct and first_downs"""
    
    # Create scraper instance
    scraper = EnhancedPFRScraper(rate_limit_delay=3.0)
    
    # Test with a known player URL (Joe Burrow 2024)
    test_url = "https://www.pro-football-reference.com/players/B/BurrJo01/splits/2024/"
    
    try:
        logger.info(f"Testing advanced splits extraction from: {test_url}")
        
        # Make request to get the page
        response = scraper.make_request_with_retry(test_url)
        if not response:
            logger.error("Failed to get response from test URL")
            return False
            
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract advanced splits
        advanced_splits = scraper._extract_advanced_splits(
            soup=soup,
            pfr_id="BurrJo01",
            player_name="Joe Burrow",
            season=2024,
            scraped_at=datetime.now()
        )
        
        logger.info(f"Extracted {len(advanced_splits)} advanced split records")
        
        # Check if we have any records
        if not advanced_splits:
            logger.warning("No advanced splits found - this might indicate the table structure has changed")
            return False
        
        # Check each record for the required fields
        missing_cmp_pct = 0
        missing_first_downs = 0
        total_records = 0
        
        for split in advanced_splits:
            total_records += 1
            
            if split.cmp_pct is None:
                missing_cmp_pct += 1
                logger.debug(f"Missing cmp_pct in split: {split.split} = {split.value}")
            
            if split.first_downs is None:
                missing_first_downs += 1
                logger.debug(f"Missing first_downs in split: {split.split} = {split.value}")
        
        logger.info(f"Total records: {total_records}")
        logger.info(f"Records missing cmp_pct: {missing_cmp_pct}")
        logger.info(f"Records missing first_downs: {missing_first_downs}")
        
        # Show sample data
        if advanced_splits:
            sample = advanced_splits[0]
            logger.info(f"Sample record:")
            logger.info(f"  Split: {sample.split} = {sample.value}")
            logger.info(f"  cmp_pct: {sample.cmp_pct}")
            logger.info(f"  first_downs: {sample.first_downs}")
            logger.info(f"  cmp: {sample.cmp}, att: {sample.att}")
        
        # Check if the issue is widespread
        if missing_cmp_pct > total_records * 0.5:
            logger.error(f"More than 50% of records are missing cmp_pct ({missing_cmp_pct}/{total_records})")
            return False
            
        if missing_first_downs > total_records * 0.5:
            logger.error(f"More than 50% of records are missing first_downs ({missing_first_downs}/{total_records})")
            return False
        
        logger.info("Advanced splits extraction test completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        return False

def test_html_structure():
    """Test to see what the actual HTML structure looks like for advanced splits"""
    
    scraper = EnhancedPFRScraper(rate_limit_delay=3.0)
    test_url = "https://www.pro-football-reference.com/players/B/BurrJo01/splits/2024/"
    
    try:
        response = scraper.make_request_with_retry(test_url)
        if not response:
            logger.error("Failed to get response")
            return False
            
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for the advanced splits table
        table = soup.find('table', {'id': 'advanced_splits'})
        if not table:
            logger.error("Advanced splits table not found")
            return False
        
        logger.info("Found advanced splits table")
        
        # Look for the specific data attributes we're trying to extract
        tbody = table.find('tbody')
        if tbody:
            rows = tbody.find_all('tr')
            logger.info(f"Found {len(rows)} rows in advanced splits table")
            
            # Check first few rows for data attributes
            for i, row in enumerate(rows[:3]):
                logger.info(f"Row {i}:")
                
                # Look for cmp_pct
                cmp_pct_cell = row.find('td', {'data-stat': 'pass_cmp_pct'})
                if cmp_pct_cell:
                    logger.info(f"  Found pass_cmp_pct: {cmp_pct_cell.get_text(strip=True)}")
                else:
                    logger.warning(f"  No pass_cmp_pct found")
                
                # Look for first_downs
                first_downs_cell = row.find('td', {'data-stat': 'pass_first_down'})
                if first_downs_cell:
                    logger.info(f"  Found pass_first_down: {first_downs_cell.get_text(strip=True)}")
                else:
                    logger.warning(f"  No pass_first_down found")
                
                # Show all data-stat attributes in this row
                all_data_stats = row.find_all('td', attrs={'data-stat': True})
                logger.info(f"  All data-stat attributes: {[td.get('data-stat') for td in all_data_stats]}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during HTML structure test: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting advanced splits field extraction tests")
    
    # Test 1: Check HTML structure
    logger.info("\n=== Testing HTML Structure ===")
    test_html_structure()
    
    # Test 2: Check extraction
    logger.info("\n=== Testing Field Extraction ===")
    test_advanced_splits_extraction()
    
    logger.info("Tests completed") 