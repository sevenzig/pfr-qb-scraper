"""
Core module for NFL QB data scraping.

This module contains the core business logic for scraping, parsing, and processing
NFL quarterback data from Pro Football Reference.
"""

from .scraper import CoreScraper
from .request_manager import RequestManager
from .html_parser import HTMLParser
from .pfr_data_extractor import PFRDataExtractor, ExtractionResult
from .pfr_structure_analyzer import PFRStructureAnalyzer, TableInfo, DataStatMapping
from .selenium_manager import SeleniumManager, SeleniumConfig

__all__ = [
    'CoreScraper',
    'RequestManager', 
    'HTMLParser',
    'PFRDataExtractor',
    'ExtractionResult',
    'PFRStructureAnalyzer',
    'TableInfo',
    'DataStatMapping',
    'SeleniumManager',
    'SeleniumConfig'
] 