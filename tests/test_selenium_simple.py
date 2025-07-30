#!/usr/bin/env python3
"""
Simple Selenium test for PFR access
"""

import sys
import os
import time
import logging

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_selenium_simple():
    """Simple Selenium test with minimal setup"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        logger.info("Setting up Chrome options...")
        
        # Chrome options
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        logger.info("Initializing Chrome driver...")
        driver = webdriver.Chrome(options=options)
        
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        logger.info("Testing with httpbin.org first...")
        
        # Test with httpbin first
        driver.get("https://httpbin.org/user-agent")
        time.sleep(2)
        
        user_agent_text = driver.find_element(By.TAG_NAME, "pre").text
        logger.info(f"User agent test result: {user_agent_text}")
        
        logger.info("Testing with PFR...")
        
        # Test with PFR
        driver.get("https://www.pro-football-reference.com/")
        time.sleep(5)  # Wait for page to load
        
        # Check if we got PFR content
        page_source = driver.page_source
        logger.info(f"Page source length: {len(page_source)}")
        
        if "Pro Football Reference" in page_source:
            logger.info("✅ SUCCESS: Found PFR content!")
            
            # Try to get the title
            title = driver.title
            logger.info(f"Page title: {title}")
            
            # Check for specific elements
            try:
                # Look for navigation elements
                nav_elements = driver.find_elements(By.CSS_SELECTOR, "nav, .nav, #nav")
                logger.info(f"Found {len(nav_elements)} navigation elements")
                
                # Look for stats table
                table_elements = driver.find_elements(By.CSS_SELECTOR, "table")
                logger.info(f"Found {len(table_elements)} table elements")
                
            except Exception as e:
                logger.warning(f"Error finding elements: {e}")
            
            return True
        else:
            logger.warning("⚠️ No PFR content found in page source")
            logger.info(f"Page source preview: {page_source[:500]}...")
            return False
            
    except Exception as e:
        logger.error(f"❌ Selenium test failed: {e}")
        return False
    finally:
        try:
            driver.quit()
            logger.info("Browser closed")
        except:
            pass

def test_selenium_headless():
    """Test Selenium in headless mode"""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        logger.info("Testing headless mode...")
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        driver.get("https://www.pro-football-reference.com/")
        time.sleep(3)
        
        page_source = driver.page_source
        logger.info(f"Headless page source length: {len(page_source)}")
        
        if "Pro Football Reference" in page_source:
            logger.info("✅ SUCCESS: Headless mode works!")
            return True
        else:
            logger.warning("⚠️ Headless mode failed to get PFR content")
            return False
            
    except Exception as e:
        logger.error(f"❌ Headless test failed: {e}")
        return False
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    logger.info("Starting Selenium tests...")
    
    # Test regular mode
    success1 = test_selenium_simple()
    
    # Test headless mode
    success2 = test_selenium_headless()
    
    logger.info("\n=== RESULTS ===")
    logger.info(f"Regular mode: {'✅ SUCCESS' if success1 else '❌ FAILED'}")
    logger.info(f"Headless mode: {'✅ SUCCESS' if success2 else '❌ FAILED'}")
    
    if success1 or success2:
        logger.info("🎉 Selenium approach works! You can use this to access PFR.")
    else:
        logger.info("❌ Selenium approach failed. Consider proxy rotation or alternative sources.") 