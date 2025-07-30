#!/usr/bin/env python3
"""
Test for full PFR passing stats content
"""

import logging
import sys
import os
import time
from bs4 import BeautifulSoup

try:
    from src.core.working_selenium_manager import WorkingSeleniumManager
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're in the project root directory")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_full_passing_stats():
    """Test full passing stats content"""
    logger.info("Testing full PFR passing stats content...")
    
    try:
        with WorkingSeleniumManager(
            headless=True, 
            min_delay=7.0, 
            max_delay=12.0
        ) as manager:
            
            # Test passing stats page
            logger.info("Testing PFR passing stats page...")
            start_time = time.time()
            
            passing_response = manager.get("https://www.pro-football-reference.com/years/2024/passing.htm")
            
            if passing_response:
                logger.info(f"✅ PFR passing stats response length: {len(passing_response)}")
                logger.info(f"⏱️  Time taken: {time.time() - start_time:.2f} seconds")
                
                # Save full content
                with open("passing_stats_full.html", "w", encoding="utf-8") as f:
                    f.write(passing_response)
                logger.info("📄 Saved full passing stats to passing_stats_full.html")
                
                # Parse with BeautifulSoup to find table
                soup = BeautifulSoup(passing_response, 'html.parser')
                
                # Look for the passing table
                passing_table = soup.find('table', {'id': 'passing'})
                if passing_table:
                    logger.info("✅ Found passing table with ID 'passing'")
                    
                    # Look for table rows
                    rows = passing_table.find_all('tr')
                    logger.info(f"Found {len(rows)} table rows")
                    
                    # Look for player names in the table
                    player_links = passing_table.find_all('a')
                    player_names = [link.text for link in player_links if link.text.strip()]
                    
                    logger.info(f"Found {len(player_names)} player links")
                    if player_names:
                        logger.info(f"Sample players: {player_names[:5]}")
                    
                    # Check for specific players
                    if "Joe Burrow" in player_names:
                        logger.info("✅ Found Joe Burrow in table")
                    else:
                        logger.warning("⚠️  Joe Burrow not found in table")
                    
                    if "Patrick Mahomes" in player_names:
                        logger.info("✅ Found Patrick Mahomes in table")
                    else:
                        logger.warning("⚠️  Patrick Mahomes not found in table")
                    
                else:
                    logger.warning("⚠️  Passing table with ID 'passing' not found")
                    
                    # Look for any table
                    tables = soup.find_all('table')
                    logger.info(f"Found {len(tables)} tables on the page")
                    
                    for i, table in enumerate(tables):
                        table_id = table.get('id', 'no-id')
                        logger.info(f"Table {i+1}: id='{table_id}'")
                
                return True
            else:
                logger.error("❌ Failed to get PFR passing stats response")
                return False
                
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_full_passing_stats()
    if success:
        logger.info("🎉 Full passing stats test completed successfully!")
    else:
        logger.error("💥 Full passing stats test failed")
        sys.exit(1) 