#!/usr/bin/env python3
"""
Test to find the correct Joe Burrow URL on PFR
"""

import logging
import sys
import os
import re

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

def test_pfr_urls():
    """Test different PFR URLs to find the correct Joe Burrow page"""
    logger.info("Testing different PFR URLs for Joe Burrow...")
    
    # Different possible Joe Burrow URLs
    test_urls = [
        "https://www.pro-football-reference.com/players/B/BurrJo00.htm",  # Original
        "https://www.pro-football-reference.com/players/B/BurrJo01.htm",  # Alternative
        "https://www.pro-football-reference.com/players/B/BurrJo02.htm",  # Another alternative
        "https://www.pro-football-reference.com/players/B/BurrowJoe00.htm",  # Full name
        "https://www.pro-football-reference.com/players/B/BurrowJ00.htm",   # Shortened
    ]
    
    try:
        with WorkingSeleniumManager(
            headless=True,
            min_delay=7.0,
            max_delay=12.0
        ) as manager:
            
            for i, url in enumerate(test_urls, 1):
                logger.info(f"Test {i}/{len(test_urls)}: {url}")
                
                try:
                    response = manager.get(url)
                    
                    if response:
                        logger.info(f"   ✅ SUCCESS: Got {len(response)} characters")
                        
                        # Check the title
                        title_match = re.search(r'<title[^>]*>([^<]+)</title>', response, re.IGNORECASE)
                        if title_match:
                            title = title_match.group(1)
                            logger.info(f"   📄 Title: {title}")
                            
                            # Check if it's Joe Burrow
                            if "Joe Burrow" in title:
                                logger.info("   🎯 FOUND JOE BURROW!")
                                return url, response
                            elif "Burrow" in title:
                                logger.info("   🔍 Found Burrow (but not Joe)")
                            else:
                                logger.info("   ❌ Not Joe Burrow")
                        else:
                            logger.warning("   ⚠️  No title found")
                    else:
                        logger.error("   ❌ FAILED: No response")
                        
                except Exception as e:
                    logger.error(f"   ❌ ERROR: {e}")
                
                # Wait between tests
                if i < len(test_urls):
                    logger.info("   Waiting for variable delay before next test...")
            
            logger.warning("No Joe Burrow page found in the tested URLs")
            return None, None
            
    except Exception as e:
        logger.error(f"Failed to test URLs: {e}")
        return None, None

def test_pfr_search():
    """Test PFR search functionality to find Joe Burrow"""
    logger.info("\nTesting PFR search for Joe Burrow...")
    
    search_url = "https://www.pro-football-reference.com/search/search.fcgi?search=Joe+Burrow"
    
    try:
        with WorkingSeleniumManager(
            headless=True,
            min_delay=7.0,
            max_delay=12.0
        ) as manager:
            
            logger.info(f"Searching: {search_url}")
            
            response = manager.get(search_url)
            
            if response:
                logger.info(f"✅ SUCCESS: Got {len(response)} characters")
                
                # Look for Joe Burrow links
                burrow_links = re.findall(r'href="([^"]*Burrow[^"]*)"', response, re.IGNORECASE)
                
                if burrow_links:
                    logger.info(f"Found {len(burrow_links)} Burrow links:")
                    for link in burrow_links[:5]:  # Show first 5
                        logger.info(f"   - {link}")
                    
                    # Try the first link
                    if burrow_links:
                        first_link = burrow_links[0]
                        if not first_link.startswith('http'):
                            first_link = "https://www.pro-football-reference.com" + first_link
                        
                        logger.info(f"Trying first link: {first_link}")
                        
                        response2 = manager.get(first_link)
                        if response2:
                            title_match = re.search(r'<title[^>]*>([^<]+)</title>', response2, re.IGNORECASE)
                            if title_match:
                                title = title_match.group(1)
                                logger.info(f"   📄 Title: {title}")
                                
                                if "Joe Burrow" in title:
                                    logger.info("   🎯 SUCCESS: Found Joe Burrow via search!")
                                    return first_link, response2
                else:
                    logger.warning("No Burrow links found in search results")
            else:
                logger.error("❌ FAILED: No search response")
                
    except Exception as e:
        logger.error(f"Failed to search PFR: {e}")
    
    return None, None

if __name__ == "__main__":
    logger.info("PFR URL Testing for Joe Burrow")
    logger.info("=" * 40)
    
    # Test direct URLs
    url, content = test_pfr_urls()
    
    if not url:
        # Try search approach
        url, content = test_pfr_search()
    
    if url and content:
        logger.info(f"\n🎉 SUCCESS: Found Joe Burrow at {url}")
        
        # Save the correct content
        with open("joe_burrow_correct.html", "w", encoding="utf-8") as f:
            f.write(content)
        logger.info("📄 Saved correct Joe Burrow content to joe_burrow_correct.html")
        
    else:
        logger.error("\n❌ FAILED: Could not find Joe Burrow page") 