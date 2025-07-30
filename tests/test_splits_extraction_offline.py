#!/usr/bin/env python3
"""
Offline test for splits extraction logic using mock HTML data.
Tests the field mapping fixes without requiring network access.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.scrapers.splits_extractor import SplitsExtractor
from src.core.selenium_manager import SeleniumManager, SeleniumConfig
from src.models.qb_models import QBSplitsType1, QBSplitsType2
from datetime import datetime
from bs4 import BeautifulSoup
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_mock_advanced_splits_html():
    """Create mock HTML for advanced splits table"""
    return """
    <table id="advanced_splits">
        <thead>
            <tr>
                <th data-stat="split">Split</th>
                <th data-stat="value">Value</th>
                <th data-stat="pass_cmp">Cmp</th>
                <th data-stat="pass_att">Att</th>
                <th data-stat="inc">Inc</th>
                <th data-stat="cmp_pct">Cmp%</th>
                <th data-stat="yds">Yds</th>
                <th data-stat="td">TD</th>
                <th data-stat="first_downs">1D</th>
                <th data-stat="int">Int</th>
                <th data-stat="rate">Rate</th>
                <th data-stat="sk">Sk</th>
                <th data-stat="sk_yds">Yds</th>
                <th data-stat="y_a">Y/A</th>
                <th data-stat="ay_a">AY/A</th>
                <th data-stat="rush_att">Rush Att</th>
                <th data-stat="rush_yds">Rush Yds</th>
                <th data-stat="rush_yds_per_att">Rush Y/A</th>
                <th data-stat="rush_td">Rush TD</th>
                <th data-stat="rush_first_down">Rush 1D</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td data-stat="split">1st Down</td>
                <td data-stat="value">1st</td>
                <td data-stat="pass_cmp">150</td>
                <td data-stat="pass_att">250</td>
                <td data-stat="inc">100</td>
                <td data-stat="cmp_pct">60.0</td>
                <td data-stat="yds">1800</td>
                <td data-stat="td">12</td>
                <td data-stat="first_downs">80</td>
                <td data-stat="int">5</td>
                <td data-stat="rate">92.0</td>
                <td data-stat="sk">15</td>
                <td data-stat="sk_yds">100</td>
                <td data-stat="y_a">7.2</td>
                <td data-stat="ay_a">7.8</td>
                <td data-stat="rush_att">25</td>
                <td data-stat="rush_yds">100</td>
                <td data-stat="rush_yds_per_att">4.0</td>
                <td data-stat="rush_td">1</td>
                <td data-stat="rush_first_down">8</td>
            </tr>
            <tr>
                <td data-stat="split">2nd Down</td>
                <td data-stat="value">2nd</td>
                <td data-stat="pass_cmp">120</td>
                <td data-stat="pass_att">200</td>
                <td data-stat="inc">80</td>
                <td data-stat="cmp_pct">60.0</td>
                <td data-stat="yds">1400</td>
                <td data-stat="td">8</td>
                <td data-stat="first_downs">60</td>
                <td data-stat="int">3</td>
                <td data-stat="rate">88.0</td>
                <td data-stat="sk">10</td>
                <td data-stat="sk_yds">70</td>
                <td data-stat="y_a">7.0</td>
                <td data-stat="ay_a">7.5</td>
                <td data-stat="rush_att">20</td>
                <td data-stat="rush_yds">80</td>
                <td data-stat="rush_yds_per_att">4.0</td>
                <td data-stat="rush_td">0</td>
                <td data-stat="rush_first_down">6</td>
            </tr>
        </tbody>
    </table>
    """

def create_mock_basic_splits_html():
    """Create mock HTML for basic splits table"""
    return """
    <table id="splits">
        <thead>
            <tr>
                <th data-stat="split">Split</th>
                <th data-stat="value">Value</th>
                <th data-stat="games">G</th>
                <th data-stat="wins">W</th>
                <th data-stat="losses">L</th>
                <th data-stat="ties">T</th>
                <th data-stat="cmp">Cmp</th>
                <th data-stat="att">Att</th>
                <th data-stat="inc">Inc</th>
                <th data-stat="cmp_pct">Cmp%</th>
                <th data-stat="yds">Yds</th>
                <th data-stat="td">TD</th>
                <th data-stat="int">Int</th>
                <th data-stat="rate">Rate</th>
                <th data-stat="sk">Sk</th>
                <th data-stat="sk_yds">Yds</th>
                <th data-stat="y_a">Y/A</th>
                <th data-stat="ay_a">AY/A</th>
                <th data-stat="a_g">A/G</th>
                <th data-stat="y_g">Y/G</th>
                <th data-stat="rush_att">Rush Att</th>
                <th data-stat="rush_yds">Rush Yds</th>
                <th data-stat="rush_yds_per_att">Rush Y/A</th>
                <th data-stat="rush_td">Rush TD</th>
                <th data-stat="rush_att_per_g">Rush A/G</th>
                <th data-stat="rush_yds_per_g">Rush Y/G</th>
                <th data-stat="total_td">Total TD</th>
                <th data-stat="pts">Pts</th>
                <th data-stat="fumble">Fmb</th>
                <th data-stat="fumble_lost">FL</th>
                <th data-stat="fumble_forced">FF</th>
                <th data-stat="fumble_recovered">FR</th>
                <th data-stat="fumble_yds">Fum Yds</th>
                <th data-stat="fumble_td">Fum TD</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td data-stat="split">Home</td>
                <td data-stat="value">Home</td>
                <td data-stat="games">8</td>
                <td data-stat="wins">5</td>
                <td data-stat="losses">3</td>
                <td data-stat="ties">0</td>
                <td data-stat="cmp">180</td>
                <td data-stat="att">300</td>
                <td data-stat="inc">120</td>
                <td data-stat="cmp_pct">60.0</td>
                <td data-stat="yds">2200</td>
                <td data-stat="td">15</td>
                <td data-stat="int">6</td>
                <td data-stat="rate">95.0</td>
                <td data-stat="sk">20</td>
                <td data-stat="sk_yds">140</td>
                <td data-stat="y_a">7.3</td>
                <td data-stat="ay_a">7.9</td>
                <td data-stat="a_g">37.5</td>
                <td data-stat="y_g">275.0</td>
                <td data-stat="rush_att">30</td>
                <td data-stat="rush_yds">120</td>
                <td data-stat="rush_yds_per_att">4.0</td>
                <td data-stat="rush_td">1</td>
                <td data-stat="rush_att_per_g">3.75</td>
                <td data-stat="rush_yds_per_g">15.0</td>
                <td data-stat="total_td">16</td>
                <td data-stat="pts">96</td>
                <td data-stat="fumble">2</td>
                <td data-stat="fumble_lost">1</td>
                <td data-stat="fumble_forced">0</td>
                <td data-stat="fumble_recovered">1</td>
                <td data-stat="fumble_yds">5</td>
                <td data-stat="fumble_td">0</td>
            </tr>
        </tbody>
    </table>
    """

def test_advanced_splits_extraction():
    """Test advanced splits extraction with mock data"""
    print("=== Testing Advanced Splits Extraction ===")
    
    # Create mock Selenium manager
    config = SeleniumConfig()
    selenium_manager = SeleniumManager(config)
    
    # Create splits extractor
    extractor = SplitsExtractor(selenium_manager)
    
    # Create mock HTML
    mock_html = create_mock_advanced_splits_html()
    soup = BeautifulSoup(mock_html, 'html.parser')
    
    # Find the table
    table = soup.find('table', id='advanced_splits')
    if not table:
        print("❌ Could not find advanced splits table in mock HTML")
        return False
    
    # Extract data
    scraped_at = datetime.now()
    results = extractor._extract_advanced_splits_table(
        table, 'burrjo01', 'Joe Burrow', 2024, scraped_at
    )
    
    print(f"✅ Extracted {len(results)} advanced splits records")
    
    # Validate results
    for i, result in enumerate(results):
        print(f"\n--- Record {i+1} ---")
        print(f"Split: {result.split}")
        print(f"Value: {result.value}")
        print(f"Cmp: {result.cmp}")
        print(f"Att: {result.att}")
        print(f"First Downs: {result.first_downs}")
        print(f"Rush Att: {result.rush_att}")
        print(f"Rush Yds: {result.rush_yds}")
        print(f"Rush TD: {result.rush_td}")
        print(f"Rush First Downs: {result.rush_first_downs}")
        
        # Check that all required fields are present
        if result.cmp is not None and result.att is not None:
            print("✅ Required fields present")
        else:
            print("❌ Missing required fields")
            return False
    
    return True

def test_basic_splits_extraction():
    """Test basic splits extraction with mock data"""
    print("\n=== Testing Basic Splits Extraction ===")
    
    # Create mock Selenium manager
    config = SeleniumConfig()
    selenium_manager = SeleniumManager(config)
    
    # Create splits extractor
    extractor = SplitsExtractor(selenium_manager)
    
    # Create mock HTML
    mock_html = create_mock_basic_splits_html()
    soup = BeautifulSoup(mock_html, 'html.parser')
    
    # Find the table
    table = soup.find('table', id='splits')
    if not table:
        print("❌ Could not find basic splits table in mock HTML")
        return False
    
    # Extract data
    scraped_at = datetime.now()
    results = extractor._extract_basic_splits_table(
        table, 'burrjo01', 'Joe Burrow', 2024, scraped_at
    )
    
    print(f"✅ Extracted {len(results)} basic splits records")
    
    # Validate results
    for i, result in enumerate(results):
        print(f"\n--- Record {i+1} ---")
        print(f"Split: {result.split}")
        print(f"Value: {result.value}")
        print(f"Games: {result.g}")
        print(f"Wins: {result.w}")
        print(f"Losses: {result.l}")
        print(f"Total TD: {result.total_td}")
        print(f"Rush Att: {result.rush_att}")
        print(f"Rush Yds: {result.rush_yds}")
        print(f"Fumble: {result.fmb}")
        print(f"Fumble Lost: {result.fl}")
        print(f"Fumble Recovered: {result.fr}")
        print(f"Fumble Yds: {result.fr_yds}")
        print(f"Fumble TD: {result.fr_td}")
        
        # Check that all required fields are present
        if result.g is not None and result.cmp is not None:
            print("✅ Required fields present")
        else:
            print("❌ Missing required fields")
            return False
    
    return True

def test_field_mapping():
    """Test that field mapping works correctly"""
    print("\n=== Testing Field Mapping ===")
    
    # Test that the field lists match the dataclass fields
    from src.scrapers.splits_extractor import SplitsExtractor
    
    # Get dataclass fields
    qb_splits_type1_fields = [field.name for field in QBSplitsType1.__dataclass_fields__.values()]
    qb_splits_type2_fields = [field.name for field in QBSplitsType2.__dataclass_fields__.values()]
    
    # Check for mismatches
    extraction_fields_1 = set(SplitsExtractor.QB_SPLITS_FIELDS)
    extraction_fields_2 = set(SplitsExtractor.QB_SPLITS_ADVANCED_FIELDS)
    
    dataclass_fields_1 = set(qb_splits_type1_fields)
    dataclass_fields_2 = set(qb_splits_type2_fields)
    
    # Remove metadata fields that are set separately
    metadata_fields = {'pfr_id', 'player_name', 'season', 'scraped_at', 'updated_at'}
    dataclass_fields_1 -= metadata_fields
    dataclass_fields_2 -= metadata_fields
    
    missing_1 = dataclass_fields_1 - extraction_fields_1
    extra_1 = extraction_fields_1 - dataclass_fields_1
    
    missing_2 = dataclass_fields_2 - extraction_fields_2
    extra_2 = extraction_fields_2 - dataclass_fields_2
    
    if missing_1:
        print(f"❌ QBSplitsType1 missing fields: {missing_1}")
        return False
    if extra_1:
        print(f"❌ QBSplitsType1 extra fields: {extra_1}")
        return False
    if missing_2:
        print(f"❌ QBSplitsType2 missing fields: {missing_2}")
        return False
    if extra_2:
        print(f"❌ QBSplitsType2 extra fields: {extra_2}")
        return False
    
    print("✅ Field mapping is correct")
    return True

if __name__ == "__main__":
    print("🧪 Running Offline Splits Extraction Tests")
    
    success = True
    
    # Test field mapping
    if not test_field_mapping():
        success = False
    
    # Test advanced splits extraction
    if not test_advanced_splits_extraction():
        success = False
    
    # Test basic splits extraction
    if not test_basic_splits_extraction():
        success = False
    
    if success:
        print("\n🎉 All tests passed! Field mapping fixes are working correctly.")
    else:
        print("\n❌ Some tests failed. Check the output above.")
    
    print("\n=== Offline Test Complete ===") 