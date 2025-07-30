#!/usr/bin/env python3
"""
Debug script to test splits page access and table discovery
"""

import requests
import time
import random
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_splits_access():
    """Test accessing splits page with enhanced anti-detection"""
    
    # Try Jalen Hurts 2024 splits
    url = "https://www.pro-football-reference.com/players/H/HurtJa00/splits/2024/"
    
    logger.info(f"Testing splits page access: {url}")
    
    # Enhanced headers to mimic real browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }
    
    session = requests.Session()
    
    try:
        # Add delay to be respectful
        time.sleep(random.uniform(2.0, 4.0))
        
        response = session.get(url, headers=headers, timeout=30)
        
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response headers: {dict(response.headers)}")
        logger.info(f"Content length: {len(response.content)}")
        
        if response.status_code == 200:
            logger.info("✓ Successfully accessed page!")
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find tables
            tables = soup.find_all('table')
            logger.info(f"Found {len(tables)} tables")
            
            # Debug table discovery
            for i, table in enumerate(tables):
                table_id = table.get('id', 'no-id')
                table_class = table.get('class', [])
                caption = table.find('caption')
                caption_text = caption.get_text(strip=True) if caption else 'no-caption'
                row_count = len(table.find_all('tr'))
                
                logger.info(f"Table {i}: ID='{table_id}', Class={table_class}, Caption='{caption_text}', Rows={row_count}")
                
                # Check if this looks like a splits table
                if 'split' in table_id.lower() or 'split' in caption_text.lower() or row_count > 5:
                    logger.info(f"  → Potential splits table!")
                    
                    # Show first few rows
                    rows = table.find_all('tr')[:5]
                    for j, row in enumerate(rows):
                        cells = row.find_all(['td', 'th'])
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        logger.info(f"    Row {j}: {cell_texts[:5]}{'...' if len(cell_texts) > 5 else ''}")
                        
                        # Check for data-stat attributes
                        if j == 0:  # Header row
                            data_stats = [cell.get('data-stat', 'no-data-stat') for cell in cells]
                            logger.info(f"    Data-stats: {data_stats[:5]}{'...' if len(data_stats) > 5 else ''}")
            
            return True
            
        elif response.status_code == 403:
            logger.error("✗ 403 Forbidden - Site is blocking our requests")
            logger.info("Response content preview:")
            logger.info(response.text[:500])
            return False
            
        else:
            logger.error(f"✗ HTTP {response.status_code}")
            logger.info("Response content preview:")
            logger.info(response.text[:500])
            return False
    
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    test_splits_access()