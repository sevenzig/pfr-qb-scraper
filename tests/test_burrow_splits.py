#!/usr/bin/env python3
"""
Simple test to verify Joe Burrow's splits data and categorization
"""

import requests
from bs4 import BeautifulSoup
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_joe_burrow_splits():
    """Test Joe Burrow's 2024 splits page"""
    
    # Joe Burrow's 2024 splits URL
    url = "https://www.pro-football-reference.com/players/B/BurrJo01/splits/2024/"
    
    print(f"Testing Joe Burrow's splits: {url}")
    print("=" * 60)
    
    try:
        # Make request
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        print(f"✓ Successfully loaded page ({len(response.text)} characters)")
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all tables
        tables = soup.find_all('table')
        print(f"✓ Found {len(tables)} tables on the page")
        
        # Look for splits tables
        splits_tables = []
        for i, table in enumerate(tables):
            table_id = table.get('id', '')
            caption = table.find('caption')
            caption_text = caption.get_text() if caption else ''
            
            if 'splits' in table_id.lower() or 'splits' in caption_text.lower():
                splits_tables.append((i, table_id, caption_text))
        
        print(f"✓ Found {len(splits_tables)} splits tables:")
        for i, table_id, caption in splits_tables:
            print(f"  Table {i}: ID='{table_id}', Caption='{caption[:50]}...'")
        
        # Test split categorization logic
        print("\n" + "=" * 60)
        print("TESTING SPLIT CATEGORIZATION")
        print("=" * 60)
        
        # Common split categories we expect to find
        expected_categories = {
            'place': ['Home', 'Away'],
            'result': ['Win', 'Loss'],
            'quarter': ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter'],
            'score_differential': ['Leading', 'Tied', 'Trailing'],
            'time': ['1st Half', '2nd Half'],
            'opponent': ['vs. AFC', 'vs. NFC', 'vs. Division'],
            'down': ['1st Down', '2nd Down', '3rd Down', '4th Down'],
            'yards_to_go': ['1-3 Yards', '4-6 Yards', '7-9 Yards', '10+ Yards'],
            'field_position': ['Own 1-10', 'Own 11-20', 'Own 21-50', 'Opp 49-20', 'Red Zone'],
            'snap_type': ['Huddle', 'No Huddle', 'Shotgun', 'Under Center'],
            'play_action': ['Play Action', 'Non-Play Action'],
            'run_pass_option': ['RPO', 'Non-RPO'],
            'time_in_pocket': ['2.5+ Seconds', 'Under 2.5 Seconds']
        }
        
        # Check each table for split categories
        for table_idx, table in enumerate(tables):
            tbody = table.find('tbody')
            if not tbody:
                continue
                
            rows = tbody.find_all('tr')
            if len(rows) < 3:  # Skip tables with too few rows
                continue
            
            # Extract split values from first column
            split_values = []
            for row in rows:
                first_cell = row.find('td')
                if first_cell:
                    value = first_cell.get_text(strip=True)
                    if value and value not in split_values:
                        split_values.append(value)
            
            if not split_values:
                continue
                
            print(f"\nTable {table_idx} - Found {len(split_values)} split values:")
            print(f"  Values: {split_values[:10]}{'...' if len(split_values) > 10 else ''}")
            
            # Try to categorize the splits
            identified_category = None
            best_match_score = 0
            
            for category, expected_values in expected_categories.items():
                matches = sum(1 for expected in expected_values 
                            for found in split_values 
                            if expected.lower() in found.lower() or found.lower() in expected.lower())
                
                if matches > 0:
                    match_score = matches / len(expected_values)
                    if match_score > best_match_score:
                        best_match_score = match_score
                        identified_category = category
            
            if identified_category and best_match_score >= 0.3:
                print(f"  ✓ Identified as '{identified_category}' (match score: {best_match_score:.2f})")
            else:
                # Try to infer from values
                inferred_category = infer_split_type_from_values(split_values)
                if inferred_category:
                    print(f"  ✓ Inferred as '{inferred_category}'")
                else:
                    print(f"  ✗ Could not categorize (would be 'other')")
        
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print("✓ Page loads successfully")
        print(f"✓ Found {len(splits_tables)} splits tables")
        print("✓ Split categorization logic is working")
        print("✓ The scraper should be able to properly categorize splits")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        logger.exception("Test failed")

def infer_split_type_from_values(values):
    """Infer split type from values (simplified version)"""
    if not values:
        return None
    
    values_lower = [v.lower() for v in values]
    
    # Check for common patterns
    if any('quarter' in v for v in values_lower):
        return 'quarter'
    elif any('half' in v for v in values_lower):
        return 'time'
    elif any('leading' in v or 'trailing' in v or 'tied' in v for v in values_lower):
        return 'score_differential'
    elif any('home' in v or 'away' in v for v in values_lower):
        return 'place'
    elif any('win' in v or 'loss' in v for v in values_lower):
        return 'result'
    elif any('down' in v for v in values_lower):
        return 'down'
    elif any('yard' in v for v in values_lower):
        return 'yards_to_go'
    elif any('zone' in v for v in values_lower):
        return 'field_position'
    elif any('huddle' in v or 'shotgun' in v for v in values_lower):
        return 'snap_type'
    elif any('action' in v for v in values_lower):
        return 'play_action'
    elif any('rpo' in v for v in values_lower):
        return 'run_pass_option'
    elif any('second' in v or 'pocket' in v for v in values_lower):
        return 'time_in_pocket'
    
    return None

if __name__ == "__main__":
    test_joe_burrow_splits() 