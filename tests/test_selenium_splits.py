#!/usr/bin/env python3
"""
Test Selenium-based splits scraping with enhanced anti-detection
"""

import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_enhanced_chrome_driver():
    """Create Chrome driver with enhanced anti-detection settings"""
    options = Options()
    
    # Enhanced anti-detection options
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Realistic window size and user agent
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
    
    # Additional stealth options
    options.add_argument("--disable-web-security")
    options.add_argument("--allow-running-insecure-content")
    options.add_argument("--disable-features=VizDisplayCompositor")
    
    # Language and locale
    options.add_argument("--lang=en-US")
    options.add_experimental_option("prefs", {
        "intl.accept_languages": "en-US,en;q=0.9"
    })
    
    try:
        driver = webdriver.Chrome(options=options)
        
        # Execute script to remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        logger.error(f"Failed to create Chrome driver: {e}")
        return None

def test_selenium_splits_access():
    """Test accessing splits page with Selenium"""
    
    url = "https://www.pro-football-reference.com/players/H/HurtJa00/splits/2024/"
    logger.info(f"Testing Selenium access to: {url}")
    
    driver = create_enhanced_chrome_driver()
    if not driver:
        return False
    
    try:
        # Set timeouts
        driver.set_page_load_timeout(60)
        driver.implicitly_wait(10)
        
        # Navigate to page
        logger.info("Loading page...")
        driver.get(url)
        
        # Wait a bit for any challenges to load
        time.sleep(random.uniform(5.0, 8.0))
        
        # Check if we're on a Cloudflare challenge page
        page_source = driver.page_source
        if "just a moment" in page_source.lower() or "checking your browser" in page_source.lower():
            logger.info("Detected Cloudflare challenge, waiting...")
            
            # Wait for challenge to complete (up to 30 seconds)
            wait = WebDriverWait(driver, 30)
            try:
                # Wait for the challenge to complete by checking for normal content
                wait.until(lambda d: "splits" in d.page_source.lower() and len(d.page_source) > 10000)
                logger.info("Challenge completed successfully!")
            except:
                logger.warning("Challenge may not have completed, proceeding anyway...")
        
        # Get final page source
        final_source = driver.page_source
        logger.info(f"Final page length: {len(final_source)}")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(final_source, 'html.parser')
        
        # Look for page title
        title = soup.find('title')
        logger.info(f"Page title: {title.get_text() if title else 'No title'}")
        
        # Find tables
        tables = soup.find_all('table')
        logger.info(f"Found {len(tables)} tables")
        
        if len(tables) == 0:
            logger.warning("No tables found - may still be blocked or challenge not completed")
            # Check for signs of blocking
            if "cloudflare" in final_source.lower():
                logger.error("Still seeing Cloudflare content")
            return False
        
        # Debug table discovery
        splits_tables_found = 0
        for i, table in enumerate(tables):
            table_id = table.get('id', 'no-id')
            table_class = table.get('class', [])
            caption = table.find('caption')
            caption_text = caption.get_text(strip=True) if caption else 'no-caption'
            row_count = len(table.find_all('tr'))
            
            logger.info(f"Table {i}: ID='{table_id}', Class={table_class}, Caption='{caption_text[:50]}', Rows={row_count}")
            
            # Check if this looks like a splits table
            is_splits_table = False
            if 'split' in table_id.lower():
                is_splits_table = True
            elif 'split' in caption_text.lower():
                is_splits_table = True
            elif row_count > 10:  # Likely a data table
                # Check first column for split indicators
                tbody = table.find('tbody')
                if tbody:
                    first_few_rows = tbody.find_all('tr')[:5]
                    split_indicators = []
                    for row in first_few_rows:
                        first_cell = row.find(['td', 'th'])
                        if first_cell:
                            text = first_cell.get_text(strip=True).lower()
                            split_indicators.append(text)
                    
                    # Look for common split indicators
                    common_splits = ['home', 'away', 'win', 'loss', '1st', '2nd', '3rd', '4th', 'quarter']
                    if any(indicator in ' '.join(split_indicators) for indicator in common_splits):
                        is_splits_table = True
            
            if is_splits_table:
                splits_tables_found += 1
                logger.info(f"  → SPLITS TABLE FOUND! #{splits_tables_found}")
                
                # Show headers
                headers = []
                header_row = table.find('tr')
                if header_row:
                    header_cells = header_row.find_all(['th', 'td'])
                    headers = [cell.get_text(strip=True) for cell in header_cells]
                    data_stats = [cell.get('data-stat', '') for cell in header_cells]
                    
                logger.info(f"    Headers: {headers[:10]}{'...' if len(headers) > 10 else ''}")
                logger.info(f"    Data-stats: {data_stats[:10]}{'...' if len(data_stats) > 10 else ''}")
                
                # Show first data row
                tbody = table.find('tbody')
                if tbody:
                    first_data_row = tbody.find('tr')
                    if first_data_row:
                        cells = first_data_row.find_all(['td', 'th'])
                        cell_texts = [cell.get_text(strip=True) for cell in cells]
                        cell_data_stats = [cell.get('data-stat', '') for cell in cells]
                        logger.info(f"    First row: {cell_texts[:10]}{'...' if len(cell_texts) > 10 else ''}")
                        logger.info(f"    Row data-stats: {cell_data_stats[:10]}{'...' if len(cell_data_stats) > 10 else ''}")
        
        logger.info(f"Total splits tables found: {splits_tables_found}")
        
        return splits_tables_found > 0
        
    except Exception as e:
        logger.error(f"Error during Selenium test: {e}")
        return False
        
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_selenium_splits_access()
    if success:
        logger.info("✓ Successfully accessed and parsed splits tables!")
    else:
        logger.error("✗ Failed to access splits tables")