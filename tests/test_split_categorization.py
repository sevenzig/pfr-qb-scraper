#!/usr/bin/env python3
"""
Test script to verify the improved split categorization logic
"""

import sys
import os
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, 'src')

from scrapers.enhanced_scraper import EnhancedPFRScraper

def test_split_categorization():
    """Test the improved split categorization logic"""
    print("Testing improved split categorization logic...")
    
    # Initialize scraper
    scraper = EnhancedPFRScraper()
    
    # Test the _infer_split_type_from_values method
    test_cases = [
        (['Home', 'Away'], 'place'),
        (['Win', 'Loss', 'Tie'], 'result'),
        (['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter'], 'quarter'),
        (['Leading', 'Tied', 'Trailing'], 'score_differential'),
        (['1st Half', '2nd Half'], 'time'),
        (['1st Down', '2nd Down', '3rd Down'], 'down'),
        (['1-3 Yards', '4-6 Yards', '7-9 Yards'], 'yards_to_go'),
        (['Red Zone', 'Own 1-10', 'Opp 19-1'], 'field_position'),
        (['Huddle', 'No Huddle', 'Shotgun'], 'snap_type'),
        (['Play Action', 'Non-Play Action'], 'play_action'),
        (['RPO', 'Non-RPO'], 'run_pass_option'),
        (['2.5+ Seconds', 'Under 2.5 Seconds'], 'time_in_pocket'),
        (['Unknown Category 1', 'Unknown Category 2'], None),  # Should return None
    ]
    
    print("\nTesting _infer_split_type_from_values method:")
    for values, expected in test_cases:
        result = scraper._infer_split_type_from_values(values)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"  {status} - {values} -> {result} (expected: {expected})")
    
    # Test the split pattern matching
    print("\nTesting split pattern matching:")
    split_patterns = {
        'place': ['Home', 'Away'],
        'result': ['Win', 'Loss', 'Tie'],
        'quarter': ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter', 'Overtime'],
    }
    
    test_values = ['Home', 'Away', 'Win', 'Loss']
    
    for split_type, expected_values in split_patterns.items():
        matches = sum(1 for expected in expected_values 
                     for found in test_values 
                     if expected.lower() in found.lower() or found.lower() in expected.lower())
        match_score = matches / len(expected_values) if expected_values else 0
        print(f"  {split_type}: {matches}/{len(expected_values)} matches = {match_score:.2f}")
    
    print("\n✓ Split categorization logic test completed!")

def test_discover_splits_logic():
    """Test the discover_splits_from_page logic with mock data"""
    print("\nTesting discover_splits_from_page logic...")
    
    # Create a mock BeautifulSoup object to test the logic
    from bs4 import BeautifulSoup
    
    # Mock HTML structure that mimics PFR splits page
    mock_html = """
    <html>
        <body>
            <table>
                <tbody>
                    <tr class="thead"><th>Split</th><th>G</th><th>W</th><th>L</th></tr>
                    <tr><td>Home</td><td>8</td><td>6</td><td>2</td></tr>
                    <tr><td>Away</td><td>9</td><td>4</td><td>5</td></tr>
                </tbody>
            </table>
            <table>
                <tbody>
                    <tr class="thead"><th>Split</th><th>G</th><th>W</th><th>L</th></tr>
                    <tr><td>Win</td><td>10</td><td>10</td><td>0</td></tr>
                    <tr><td>Loss</td><td>7</td><td>0</td><td>7</td></tr>
                </tbody>
            </table>
            <table>
                <tbody>
                    <tr class="thead"><th>Split</th><th>G</th><th>W</th><th>L</th></tr>
                    <tr><td>1st Quarter</td><td>17</td><td>10</td><td>7</td></tr>
                    <tr><td>2nd Quarter</td><td>17</td><td>10</td><td>7</td></tr>
                    <tr><td>3rd Quarter</td><td>17</td><td>10</td><td>7</td></tr>
                    <tr><td>4th Quarter</td><td>17</td><td>10</td><td>7</td></tr>
                </tbody>
            </table>
        </body>
    </html>
    """
    
    soup = BeautifulSoup(mock_html, 'html.parser')
    scraper = EnhancedPFRScraper()
    
    # Test the discover_splits_from_page method
    discovered_splits = scraper.discover_splits_from_page(soup)
    
    print(f"Discovered splits: {discovered_splits}")
    
    # Check if we found the expected split types
    expected_types = ['place', 'result', 'quarter']
    found_types = list(discovered_splits.keys())
    
    print(f"Expected split types: {expected_types}")
    print(f"Found split types: {found_types}")
    
    for expected_type in expected_types:
        if expected_type in discovered_splits:
            categories = list(discovered_splits[expected_type].keys())
            print(f"  ✓ {expected_type}: {categories}")
        else:
            print(f"  ✗ {expected_type}: Not found")
    
    print("\n✓ Discover splits logic test completed!")

def main():
    """Run all tests"""
    print("Testing Improved Split Categorization")
    print("=" * 50)
    
    # Test the categorization logic
    test_split_categorization()
    
    # Test the discover splits logic
    test_discover_splits_logic()
    
    print("\n" + "=" * 50)
    print("✓ All tests completed!")
    print("\nThe improved split categorization should now properly identify:")
    print("- Place splits (Home/Away)")
    print("- Result splits (Win/Loss/Tie)")
    print("- Quarter splits (1st/2nd/3rd/4th Quarter)")
    print("- Score differential splits (Leading/Tied/Trailing)")
    print("- And many other split types")

if __name__ == "__main__":
    main() 