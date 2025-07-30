#!/usr/bin/env python3
"""
Simple test to verify the improved split categorization logic
"""

def infer_split_type_from_values(values):
    """
    Copy of the improved _infer_split_type_from_values method from EnhancedPFRScraper
    """
    if not values:
        return None
    
    # Convert to lowercase for comparison
    values_lower = [v.lower() for v in values]
    
    # Check for common patterns - order matters for priority
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
    elif any(('own ' in v or 'opp ') and ('1-' in v or '2-' in v or '3-' in v or '4-' in v or '5-' in v or '6-' in v or '7-' in v or '8-' in v or '9-' in v) for v in values_lower):
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

def test_split_categorization():
    """Test the improved split categorization logic"""
    print("Testing improved split categorization logic...")
    
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
    passed = 0
    total = len(test_cases)
    
    for values, expected in test_cases:
        result = infer_split_type_from_values(values)
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"  {status} - {values} -> {result} (expected: {expected})")
        if result == expected:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    # Test the split pattern matching logic
    print("\nTesting split pattern matching logic:")
    split_patterns = {
        'place': ['Home', 'Away'],
        'result': ['Win', 'Loss', 'Tie'],
        'quarter': ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter'],
    }
    
    test_values = ['Home', 'Away', 'Win', 'Loss']
    
    for split_type, expected_values in split_patterns.items():
        matches = sum(1 for expected in expected_values 
                     for found in test_values 
                     if expected.lower() in found.lower() or found.lower() in expected.lower())
        match_score = matches / len(expected_values) if expected_values else 0
        print(f"  {split_type}: {matches}/{len(expected_values)} matches = {match_score:.2f}")
    
    print("\n✓ Split categorization logic test completed!")
    return passed == total

def test_discover_splits_logic():
    """Test the discover_splits_from_page logic with mock data"""
    print("\nTesting discover_splits_from_page logic...")
    
    # Mock the logic from discover_splits_from_page
    split_patterns = {
        'place': ['Home', 'Away'],
        'result': ['Win', 'Loss', 'Tie'],
        'quarter': ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter', 'Overtime'],
    }
    
    # Mock table data
    mock_tables = [
        ['Home', 'Away'],  # Table 1: Place splits
        ['Win', 'Loss'],   # Table 2: Result splits
        ['1st Quarter', '2nd Quarter', '3rd Quarter', '4th Quarter'],  # Table 3: Quarter splits
    ]
    
    discovered_splits = {}
    
    for table_idx, split_values in enumerate(mock_tables):
        # Try to identify the split type based on the values found
        identified_split_type = None
        best_match_score = 0
        
        for split_type, expected_values in split_patterns.items():
            # Calculate how many expected values match what we found
            matches = sum(1 for expected in expected_values 
                        for found in split_values 
                        if expected.lower() in found.lower() or found.lower() in expected.lower())
            
            if matches > 0:
                match_score = matches / len(expected_values)
                if match_score > best_match_score:
                    best_match_score = match_score
                    identified_split_type = split_type
        
        # If we found a good match, add it to discovered splits
        if identified_split_type and best_match_score >= 0.3:  # At least 30% match
            if identified_split_type not in discovered_splits:
                discovered_splits[identified_split_type] = {}
            
            # Add all found values as categories
            for value in split_values:
                if value:  # Skip empty values
                    discovered_splits[identified_split_type][value] = identified_split_type
            
            print(f"Table {table_idx}: Identified as '{identified_split_type}' with {len(split_values)} categories (match score: {best_match_score:.2f})")
    
    print(f"Discovered splits: {discovered_splits}")
    
    # Check if we found the expected split types
    expected_types = ['place', 'result', 'quarter']
    found_types = list(discovered_splits.keys())
    
    print(f"Expected split types: {expected_types}")
    print(f"Found split types: {found_types}")
    
    success = True
    for expected_type in expected_types:
        if expected_type in discovered_splits:
            categories = list(discovered_splits[expected_type].keys())
            print(f"  ✓ {expected_type}: {categories}")
        else:
            print(f"  ✗ {expected_type}: Not found")
            success = False
    
    print("\n✓ Discover splits logic test completed!")
    return success

def main():
    """Run all tests"""
    print("Testing Improved Split Categorization")
    print("=" * 50)
    
    # Test the categorization logic
    logic_test_passed = test_split_categorization()
    
    # Test the discover splits logic
    discover_test_passed = test_discover_splits_logic()
    
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"  Split Categorization Logic: {'✓ PASSED' if logic_test_passed else '✗ FAILED'}")
    print(f"  Discover Splits Logic: {'✓ PASSED' if discover_test_passed else '✗ FAILED'}")
    
    if logic_test_passed and discover_test_passed:
        print("\n✓ All tests passed!")
        print("\nThe improved split categorization should now properly identify:")
        print("- Place splits (Home/Away)")
        print("- Result splits (Win/Loss/Tie)")
        print("- Quarter splits (1st/2nd/3rd/4th Quarter)")
        print("- Score differential splits (Leading/Tied/Trailing)")
        print("- And many other split types")
        print("\nNext steps:")
        print("1. The enhanced scraper has been updated with improved split categorization")
        print("2. When you run the scraper again, it should properly categorize splits")
        print("3. You can update existing records or scrape new ones with the improved logic")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main() 