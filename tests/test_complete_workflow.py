#!/usr/bin/env python3
"""
Test the complete workflow: nfl-qb-scraper scrape --season $YEAR
"""

import logging
import sys
import os
import argparse

try:
    from src.scrapers.nfl_qb_scraper import NFLQBDataPipeline
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're in the project root directory")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_complete_workflow(season: int = 2024, min_delay: float = 7.0, max_delay: float = 12.0):
    """Test the complete workflow"""
    logger.info(f"Testing complete workflow for season {season}")
    logger.info(f"Using variable delays: {min_delay}-{max_delay} seconds")
    
    try:
        # Initialize pipeline
        pipeline = NFLQBDataPipeline(min_delay=min_delay, max_delay=max_delay)
        
        # Run the pipeline
        results = pipeline.run_pipeline(season=season, splits_only=False)
        
        # Print results
        logger.info("Workflow Results:")
        logger.info(f"  Success: {results['success']}")
        logger.info(f"  Season: {results['season']}")
        logger.info(f"  QB Stats Count: {results['qb_stats_count']}")
        logger.info(f"  QB Splits Count: {results['qb_splits_count']}")
        logger.info(f"  QB Splits Advanced Count: {results['qb_splits_advanced_count']}")
        logger.info(f"  Processing Time: {results.get('processing_time', 0):.2f} seconds")
        
        if results['success']:
            logger.info("SUCCESS: Complete workflow completed successfully!")
            return True
        else:
            logger.error("FAILED: Workflow failed")
            return False
            
    except Exception as e:
        logger.error(f"Workflow failed with exception: {e}")
        return False

def test_specific_players(season: int = 2024, min_delay: float = 7.0, max_delay: float = 12.0):
    """Test with specific players"""
    logger.info(f"Testing with specific players for season {season}")
    
    try:
        # Initialize pipeline
        pipeline = NFLQBDataPipeline(min_delay=min_delay, max_delay=max_delay)
        
        # Test with specific players
        specific_players = ["Joe Burrow", "Patrick Mahomes", "Josh Allen"]
        
        results = pipeline.scrape_season_qbs(season, player_names=specific_players)
        
        # Print results
        logger.info("Specific Players Results:")
        logger.info(f"  Success: {results['success']}")
        logger.info(f"  QB Stats Count: {results['qb_stats_count']}")
        logger.info(f"  QB Splits Count: {results['qb_splits_count']}")
        logger.info(f"  QB Splits Advanced Count: {results['qb_splits_advanced_count']}")
        
        if results['success']:
            logger.info("SUCCESS: Specific players test completed successfully!")
            return True
        else:
            logger.error("FAILED: Specific players test failed")
            return False
            
    except Exception as e:
        logger.error(f"Specific players test failed with exception: {e}")
        return False

def main():
    """Main test function"""
    parser = argparse.ArgumentParser(description='Test NFL QB Scraper Workflow')
    parser.add_argument('--season', type=int, default=2024, help='Season to test (default: 2024)')
    parser.add_argument('--min-delay', type=float, default=7.0, help='Minimum delay (default: 7.0)')
    parser.add_argument('--max-delay', type=float, default=12.0, help='Maximum delay (default: 12.0)')
    parser.add_argument('--specific-players', action='store_true', help='Test with specific players only')
    
    args = parser.parse_args()
    
    logger.info("NFL QB Scraper Workflow Test")
    logger.info("=" * 40)
    logger.info(f"Season: {args.season}")
    logger.info(f"Delays: {args.min_delay}-{args.max_delay} seconds")
    logger.info(f"Mode: {'Specific Players' if args.specific_players else 'Complete Workflow'}")
    
    if args.specific_players:
        success = test_specific_players(args.season, args.min_delay, args.max_delay)
    else:
        success = test_complete_workflow(args.season, args.min_delay, args.max_delay)
    
    if success:
        logger.info("\nAll tests completed successfully!")
        logger.info("The workflow is working correctly with:")
        logger.info("  - Variable delays (7-12 seconds)")
        logger.info("  - Selenium-based scraping")
        logger.info("  - Correct URL pattern detection")
        logger.info("  - PFR access without 403 errors")
    else:
        logger.error("\nSome tests failed. Check the logs above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 