#!/usr/bin/env python3
"""
Simple test to debug table structure
"""

import logging
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from core.working_selenium_manager import WorkingSeleniumManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're in the project root directory")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_table_structure():
    """Test to see the actual table structure"""
    logger.info("Testing table structure on PFR passing stats page...")
    
    try:
        with WorkingSeleniumManager(headless=True, min_delay=7.0, max_delay=12.0) as manager:
            
            url = "https://www.pro-football-reference.com/years/2024/passing.htm"
            logger.info(f"Loading: {url}")
            
            response = manager.get(url)
            if not response:
                logger.error("Failed to load page")
                return False
            
            logger.info(f"Got {len(response)} characters")
            
            # Save a sample for inspection
            with open("pfr_passing_sample.html", "w", encoding="utf-8") as f:
                f.write(response[:10000])  # First 10K chars
            logger.info("Saved sample to pfr_passing_sample.html")
            
            # Look for table structure
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response, 'html.parser')
            
            # Find all tables
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables")
            
            for i, table in enumerate(tables):
                table_id = table.get('id', 'NO_ID')
                logger.info(f"Table {i}: ID = '{table_id}'")
                
                # Check if this looks like the passing stats table
                if table_id == 'passing':
                    logger.info("Found passing table!")
                    
                    # Look for rows
                    tbody = table.find('tbody')
                    if tbody:
                        rows = tbody.find_all('tr')
                        logger.info(f"Found {len(rows)} rows in tbody")
                        
                        # Check first few rows
                        for j, row in enumerate(rows[:5]):
                            player_cell = row.find('td', {'data-stat': 'player'})
                            pos_cell = row.find('td', {'data-stat': 'pos'})
                            
                            if player_cell:
                                player_name = player_cell.get_text(strip=True)
                                pos = pos_cell.get_text(strip=True) if pos_cell else "N/A"
                                logger.info(f"  Row {j}: {player_name} - {pos}")
                            else:
                                logger.info(f"  Row {j}: No player cell found")
                    else:
                        logger.warning("No tbody found in passing table")
            
            return True
            
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    logger.info("Simple Selenium Table Structure Test")
    logger.info("=" * 40)
    
    success = test_table_structure()
    
    if success:
        logger.info("Test completed successfully!")
    else:
        logger.error("Test failed!") 