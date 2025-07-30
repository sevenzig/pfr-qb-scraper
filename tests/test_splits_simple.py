#!/usr/bin/env python3
"""
Simple test for splits extraction
"""

import sys
import os
import logging
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_splits_url_construction():
    """Test splits URL construction"""
    logger.info("Testing splits URL construction")
    
    try:
        # Test the URL construction logic
        base_url = "https://www.pro-football-reference.com"
        pfr_id = "burrjo01"
        season = 2024
        
        # Extract first letter for URL construction
        first_letter = pfr_id[0].upper() if pfr_id else None
        if not first_letter:
            logger.error("Could not extract first letter from PFR ID")
            return False
        
        # Primary URL format
        splits_url = f"{base_url}/players/{first_letter}/{pfr_id}/splits/{season}/"
        
        logger.info(f"Built splits URL: {splits_url}")
        
        # Expected URL
        expected_url = "https://www.pro-football-reference.com/players/B/burrjo01/splits/2024/"
        
        if splits_url == expected_url:
            logger.info("✓ URL construction successful")
            return True
        else:
            logger.error(f"✗ URL construction failed. Expected: {expected_url}, Got: {splits_url}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing URL construction: {e}")
        return False


def test_splits_extraction_logic():
    """Test the splits extraction logic without Selenium"""
    logger.info("Testing splits extraction logic")
    
    try:
        # Test the table categorization logic
        from bs4 import BeautifulSoup
        
        # Create a simple test HTML
        test_html = """
        <html>
        <body>
            <table id="splits">
                <thead>
                    <tr>
                        <th>Split</th>
                        <th>Value</th>
                        <th>G</th>
                        <th>W</th>
                        <th>L</th>
                        <th>T</th>
                        <th>Cmp</th>
                        <th>Att</th>
                        <th>Yds</th>
                        <th>TD</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Home</td>
                        <td>Home</td>
                        <td>8</td>
                        <td>5</td>
                        <td>3</td>
                        <td>0</td>
                        <td>180</td>
                        <td>280</td>
                        <td>2100</td>
                        <td>15</td>
                    </tr>
                    <tr>
                        <td>Away</td>
                        <td>Away</td>
                        <td>8</td>
                        <td>4</td>
                        <td>4</td>
                        <td>0</td>
                        <td>175</td>
                        <td>275</td>
                        <td>2000</td>
                        <td>12</td>
                    </tr>
                </tbody>
            </table>
            
            <table id="advanced_splits">
                <thead>
                    <tr>
                        <th>Split</th>
                        <th>Value</th>
                        <th>Cmp</th>
                        <th>Att</th>
                        <th>1D</th>
                        <th>Yds</th>
                        <th>TD</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Down</td>
                        <td>1st Down</td>
                        <td>120</td>
                        <td>180</td>
                        <td>80</td>
                        <td>1400</td>
                        <td>8</td>
                    </tr>
                    <tr>
                        <td>Down</td>
                        <td>2nd Down</td>
                        <td>100</td>
                        <td>160</td>
                        <td>60</td>
                        <td>1200</td>
                        <td>6</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        
        soup = BeautifulSoup(test_html, 'html.parser')
        
        # Test table discovery
        tables = soup.find_all('table')
        logger.info(f"Found {len(tables)} tables in test HTML")
        
        # Test table categorization
        basic_tables = []
        advanced_tables = []
        
        for table in tables:
            table_id = table.get('id', '').lower()
            if 'advanced' in table_id:
                advanced_tables.append(table)
                logger.info(f"Found advanced splits table: {table_id}")
            elif 'splits' in table_id:
                basic_tables.append(table)
                logger.info(f"Found basic splits table: {table_id}")
        
        logger.info(f"Found {len(basic_tables)} basic splits tables")
        logger.info(f"Found {len(advanced_tables)} advanced splits tables")
        
        # Test data extraction
        if basic_tables:
            table = basic_tables[0]
            rows = table.find('tbody').find_all('tr')
            logger.info(f"Found {len(rows)} rows in basic splits table")
            
            for i, row in enumerate(rows[:2]):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    split_type = cells[0].get_text(strip=True)
                    split_value = cells[1].get_text(strip=True)
                    logger.info(f"Row {i+1}: {split_type} = {split_value}")
        
        if advanced_tables:
            table = advanced_tables[0]
            rows = table.find('tbody').find_all('tr')
            logger.info(f"Found {len(rows)} rows in advanced splits table")
            
            for i, row in enumerate(rows[:2]):
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    split_type = cells[0].get_text(strip=True)
                    split_value = cells[1].get_text(strip=True)
                    logger.info(f"Row {i+1}: {split_type} = {split_value}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing splits extraction logic: {e}")
        return False


if __name__ == "__main__":
    logger.info("Starting simple splits tests")
    
    # Test URL construction
    url_success = test_splits_url_construction()
    
    # Test extraction logic
    logic_success = test_splits_extraction_logic()
    
    if url_success and logic_success:
        logger.info("All tests completed successfully")
    else:
        logger.error("Some tests failed")
        sys.exit(1) 