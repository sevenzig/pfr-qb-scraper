#!/usr/bin/env python3
"""
Core package for NFL QB Data Scraping System
Contains unified scraper and core business logic
"""

from .scraper import CoreScraper, RateLimiter, ScrapingMetrics

__all__ = [
    'CoreScraper',
    'RateLimiter', 
    'ScrapingMetrics'
] 