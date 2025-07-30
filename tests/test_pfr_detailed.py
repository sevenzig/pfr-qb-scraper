#!/usr/bin/env python3
"""
Detailed PFR scraping test with variable delays (7-12 seconds)
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

def analyze_pfr_content(html_content: str, url: str):
    """Analyze PFR content for key indicators"""
    logger.info(f"Analyzing content from: {url}")
    logger.info(f"Content length: {len(html_content)} characters")
    
    # Check for PFR indicators
    pfr_indicators = [
        "Pro Football Reference",
        "pro-football-reference.com",
        "data-version=\"klecko\"",
        "pfr/build"
    ]
    
    for indicator in pfr_indicators:
        if indicator in html_content:
            logger.info(f"   ✅ Found PFR indicator: {indicator}")
        else:
            logger.warning(f"   ⚠️  Missing PFR indicator: {indicator}")
    
    # Look for player-specific content
    if "BurrJo00" in url:
        player_indicators = [
            "Joe Burrow",
            "Burrow",
            "Cincinnati",
            "Bengals",
            "QB",
            "passing",
            "rushing",
            "stats"
        ]
        
        for indicator in player_indicators:
            if indicator in html_content:
                logger.info(f"   ✅ Found player indicator: {indicator}")
            else:
                logger.warning(f"   ⚠️  Missing player indicator: {indicator}")
    
    # Look for common PFR elements
    pfr_elements = [
        "table",
        "thead",
        "tbody",
        "tr",
        "td",
        "th",
        "class=",
        "id="
    ]
    
    element_counts = {}
    for element in pfr_elements:
        count = html_content.count(element)
        element_counts[element] = count
        if count > 0:
            logger.info(f"   📊 Found {count} '{element}' elements")
    
    # Check for data tables
    if "table" in element_counts and element_counts["table"] > 0:
        logger.info("   ✅ HTML structure looks like it contains data tables")
    else:
        logger.warning("   ⚠️  No table elements found - may not be player stats page")
    
    return html_content

def test_pfr_detailed():
    """Test PFR scraping with detailed analysis"""
    logger.info("Testing PFR scraping with detailed analysis...")
    
    player_url = "https://www.pro-football-reference.com/players/B/BurrJo00.htm"
    
    try:
        with WorkingSeleniumManager(
            headless=True,
            min_delay=7.0,
            max_delay=12.0
        ) as manager:
            
            logger.info(f"Scraping Joe Burrow's page: {player_url}")
            
            response = manager.get(player_url)
            
            if response:
                logger.info(f"✅ SUCCESS: Got {len(response)} characters")
                
                # Analyze the content
                analyze_pfr_content(response, player_url)
                
                # Save full content for inspection
                with open("pfr_full_content.html", "w", encoding="utf-8") as f:
                    f.write(response)
                logger.info("   📄 Saved full content to pfr_full_content.html")
                
                # Save a more readable sample (first 10K chars)
                with open("pfr_readable_sample.html", "w", encoding="utf-8") as f:
                    f.write(response[:10000])
                logger.info("   📄 Saved readable sample to pfr_readable_sample.html")
                
                # Look for specific data patterns
                patterns = [
                    r'<h1[^>]*>([^<]+)</h1>',  # Main heading
                    r'<title[^>]*>([^<]+)</title>',  # Page title
                    r'class="[^"]*player[^"]*"',  # Player-related classes
                    r'id="[^"]*stats[^"]*"',  # Stats-related IDs
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, response, re.IGNORECASE)
                    if matches:
                        logger.info(f"   🔍 Pattern '{pattern}': Found {len(matches)} matches")
                        for match in matches[:3]:  # Show first 3 matches
                            logger.info(f"      - {match[:100]}...")
                    else:
                        logger.warning(f"   ⚠️  Pattern '{pattern}': No matches found")
                
            else:
                logger.error("❌ FAILED: No response received")
                
    except Exception as e:
        logger.error(f"Failed to scrape player page: {e}")
        return False
    
    return True

if __name__ == "__main__":
    logger.info("Detailed PFR Scraping Test")
    logger.info("=" * 40)
    
    success = test_pfr_detailed()
    
    if success:
        logger.info("\n🎉 Test completed successfully!")
        logger.info("Check the saved HTML files for detailed content analysis.")
    else:
        logger.error("\n❌ Test failed. Check the logs above.") 