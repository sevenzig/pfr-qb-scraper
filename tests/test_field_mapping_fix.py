#!/usr/bin/env python3
"""
Test script to verify field mapping fixes for QB splits extraction.
Tests that the field names in the extraction logic match the dataclass field names exactly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.models.qb_models import QBSplitsType1, QBSplitsType2
from src.scrapers.splits_extractor import SplitsExtractor
from src.core.selenium_manager import SeleniumManager
from src.config.config import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_field_mapping_alignment():
    """Test that field names in extraction logic match dataclass field names"""
    
    print("=== Testing Field Mapping Alignment ===")
    
    # Test QBSplitsType1 (Basic Splits)
    print("\n--- QBSplitsType1 (Basic Splits) ---")
    print("Dataclass fields:")
    qb_splits_type1_fields = [field.name for field in QBSplitsType1.__dataclass_fields__.values()]
    for field in qb_splits_type1_fields:
        print(f"  {field}")
    
    print("\nExtraction logic fields:")
    for field in SplitsExtractor.QB_SPLITS_FIELDS:
        print(f"  {field}")
    
    # Check for mismatches
    extraction_fields = set(SplitsExtractor.QB_SPLITS_FIELDS)
    dataclass_fields = set(qb_splits_type1_fields)
    
    missing_in_extraction = dataclass_fields - extraction_fields
    extra_in_extraction = extraction_fields - dataclass_fields
    
    if missing_in_extraction:
        print(f"\n❌ Fields missing in extraction logic: {missing_in_extraction}")
    else:
        print("\n✅ All dataclass fields present in extraction logic")
    
    if extra_in_extraction:
        print(f"\n❌ Extra fields in extraction logic: {extra_in_extraction}")
    else:
        print("\n✅ No extra fields in extraction logic")
    
    # Test QBSplitsType2 (Advanced Splits)
    print("\n--- QBSplitsType2 (Advanced Splits) ---")
    print("Dataclass fields:")
    qb_splits_type2_fields = [field.name for field in QBSplitsType2.__dataclass_fields__.values()]
    for field in qb_splits_type2_fields:
        print(f"  {field}")
    
    print("\nExtraction logic fields:")
    for field in SplitsExtractor.QB_SPLITS_ADVANCED_FIELDS:
        print(f"  {field}")
    
    # Check for mismatches
    extraction_fields = set(SplitsExtractor.QB_SPLITS_ADVANCED_FIELDS)
    dataclass_fields = set(qb_splits_type2_fields)
    
    missing_in_extraction = dataclass_fields - extraction_fields
    extra_in_extraction = extraction_fields - dataclass_fields
    
    if missing_in_extraction:
        print(f"\n❌ Fields missing in extraction logic: {missing_in_extraction}")
    else:
        print("\n✅ All dataclass fields present in extraction logic")
    
    if extra_in_extraction:
        print(f"\n❌ Extra fields in extraction logic: {extra_in_extraction}")
    else:
        print("\n✅ No extra fields in extraction logic")

def test_dataclass_instantiation():
    """Test that dataclasses can be instantiated with the expected field names"""
    
    print("\n=== Testing Dataclass Instantiation ===")
    
    # Test QBSplitsType1
    print("\n--- Testing QBSplitsType1 instantiation ---")
    try:
        qb_splits_1 = QBSplitsType1(
            pfr_id="test123",
            player_name="Test Player",
            season=2024,
            split="Home",
            value="Home",
            g=16,
            w=10,
            l=6,
            t=0,
            cmp=300,
            att=500,
            inc=200,
            cmp_pct=60.0,
            yds=3500,
            td=25,
            int=10,
            rate=95.0,
            sk=30,
            sk_yds=200,
            y_a=7.0,
            ay_a=7.5,
            a_g=31.25,
            y_g=218.75,
            rush_att=50,
            rush_yds=200,
            rush_y_a=4.0,
            rush_td=2,
            rush_a_g=3.125,
            rush_y_g=12.5,
            total_td=27,
            pts=162,
            fmb=3,
            fl=2,
            ff=1,
            fr=1,
            fr_yds=10,
            fr_td=0
        )
        print("✅ QBSplitsType1 instantiation successful")
    except Exception as e:
        print(f"❌ QBSplitsType1 instantiation failed: {e}")
    
    # Test QBSplitsType2
    print("\n--- Testing QBSplitsType2 instantiation ---")
    try:
        qb_splits_2 = QBSplitsType2(
            pfr_id="test123",
            player_name="Test Player",
            season=2024,
            split="Down",
            value="1st",
            cmp=150,
            att=250,
            inc=100,
            cmp_pct=60.0,
            yds=1800,
            td=12,
            first_downs=80,
            int=5,
            rate=92.0,
            sk=15,
            sk_yds=100,
            y_a=7.2,
            ay_a=7.8,
            rush_att=25,
            rush_yds=100,
            rush_y_a=4.0,
            rush_td=1,
            rush_first_downs=8
        )
        print("✅ QBSplitsType2 instantiation successful")
    except Exception as e:
        print(f"❌ QBSplitsType2 instantiation failed: {e}")

if __name__ == "__main__":
    test_field_mapping_alignment()
    test_dataclass_instantiation()
    print("\n=== Field Mapping Test Complete ===") 