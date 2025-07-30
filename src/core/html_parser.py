#!/usr/bin/env python3
"""
HTML Parser for NFL QB Data
Handles all data extraction from Pro Football Reference HTML content.
"""

import logging
from typing import List, Dict, Optional, Union, Any
from bs4 import BeautifulSoup, Tag
import re

logger = logging.getLogger(__name__)


class HTMLParser:
    """Extracts structured QB data from Pro Football Reference HTML."""

    def parse_html(self, html_content: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML content into BeautifulSoup object.
        
        Args:
            html_content: Raw HTML content
            
        Returns:
            BeautifulSoup object if successful, None otherwise
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup
        except Exception as e:
            logger.error(f"Failed to parse HTML: {e}")
            return None

    def parse_passing_stats_table(self, soup: BeautifulSoup, season: int) -> List[Dict[str, Union[str, int, float]]]:
        """
        Parses the main passing stats table for a given season.

        Args:
            soup: BeautifulSoup object of the season passing stats page.
            season: The season year.

        Returns:
            A list of dictionaries, where each dictionary represents a player's stats.
        """
        stats_list = []
        table = soup.find('table', id='passing')
        if not table or not isinstance(table, Tag) or not table.tbody:
            logger.warning(f"Could not find passing stats table for season {season}")
            return []

        rows = table.tbody.find_all('tr')
        for row in rows:
            if row.get('class') and 'thead' in row.get('class'):
                continue

            # Extract position to filter for QBs only
            pos_cell = row.find('td', {'data-stat': 'pos'})
            if not pos_cell or not isinstance(pos_cell, Tag) or pos_cell.text.strip().upper() != 'QB':
                continue

            # Extract player URL and PFR ID
            player_cell = row.find('td', {'data-stat': 'player'})
            if not player_cell or not isinstance(player_cell, Tag):
                player_cell = row.find('td', {'data-stat': 'name_display'})
            
            if not player_cell or not isinstance(player_cell, Tag):
                continue
                
            player_link = player_cell.find('a')
            if not player_link or not isinstance(player_link, Tag):
                continue
                
            player_url = player_link.get('href', '')
            pfr_id = self._extract_pfr_id(player_url) if player_url else None
            
            if not pfr_id:
                continue

            # Helper function to safely get cell text
            def get_cell_text(stat_name: str) -> str:
                cell = row.find('td', {'data-stat': stat_name})
                return cell.text.strip() if cell and isinstance(cell, Tag) else ''

            # Helper function to safely get cell value as int
            def get_cell_int(stat_name: str) -> int:
                return self._safe_int(get_cell_text(stat_name))

            # Helper function to safely get cell value as float
            def get_cell_float(stat_name: str) -> float:
                return self._safe_float(get_cell_text(stat_name))

            stats = {
                'pfr_id': pfr_id,
                'player_url': f"https://www.pro-football-reference.com{player_url}",
                'season': season,
                'player_name': player_link.text.strip(),
                'team': self._normalize_pfr_team_code(get_cell_text('team')),
                'age': get_cell_int('age'),
                'pos': get_cell_text('pos').strip(),
                'g': get_cell_int('g'),
                'gs': get_cell_int('gs'),
                'qb_rec': get_cell_text('qb_rec'),
                'cmp': get_cell_int('pass_cmp'),
                'att': get_cell_int('pass_att'),
                'cmp_pct': get_cell_float('pass_cmp_perc'),
                'yds': get_cell_int('pass_yds'),
                'td': get_cell_int('pass_td'),
                'td_pct': get_cell_float('pass_td_perc'),
                'int': get_cell_int('pass_int'),
                'int_pct': get_cell_float('pass_int_perc'),
                'first_downs': get_cell_int('pass_first_down'),
                'succ_pct': get_cell_float('pass_success_perc'),
                'lng': get_cell_int('pass_long'),
                'y_a': get_cell_float('pass_yds_per_att'),
                'ay_a': get_cell_float('pass_adj_yds_per_att'),
                'y_c': get_cell_float('pass_yds_per_cmp'),
                'y_g': get_cell_float('pass_yds_per_g'),
                'rate': get_cell_float('pass_rating'),
                'qbr': get_cell_float('qbr'),
                'sk': get_cell_int('sacked'),
                'sk_yds': get_cell_int('sacked_yds'),
                'sk_pct': get_cell_float('sacked_perc'),
                'ny_a': get_cell_float('net_yds_per_pass_att'),
                'any_a': get_cell_float('adj_net_yds_per_pass_att'),
                'four_qc': get_cell_int('comebacks'),
                'gwd': get_cell_int('gwd'),
                'awards': get_cell_text('awards'),
                'player_additional': get_cell_text('player_additional'),
                # Add some missing fields with defaults
                'rk': get_cell_int('rank_offense') or get_cell_int('rk')
            }
            stats_list.append(stats)
            
        return stats_list

    def parse_splits_tables(self, soup: BeautifulSoup, player_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Parse splits tables from a player's splits page.
        
        Args:
            soup: BeautifulSoup object of the player's splits page
            player_info: Dictionary containing player info
            
        Returns:
            List of split statistics dictionaries
        """
        all_splits = []
        
        # Find all tables on the page
        tables = soup.find_all('table')
        logger.info(f"Found {len(tables)} tables on splits page for {player_info.get('player_name', 'Unknown')}")
        
        for table in tables:
            if self._is_splits_table(table):
                table_id = table.get('id', 'unknown')
                logger.info(f"Processing splits table: {table_id}")
                splits = self._process_splits_table(table, player_info)
                logger.info(f"Extracted {len(splits)} splits from table {table_id}")
                all_splits.extend(splits)
        
        return all_splits

    def _is_splits_table(self, table: Tag) -> bool:
        """
        Determine if a table contains splits data.
        
        Args:
            table: BeautifulSoup table element
            
        Returns:
            True if the table appears to contain splits data
        """
        table_id = table.get('id', '')
        table_class = table.get('class', [])
        
        # Look for specific splits table patterns
        splits_indicators = [
            'passing_splits', 'splits', 'home_away', 'by_half', 'by_quarter',
            'vs_div', 'vs_conf', 'monthly', 'weekly', 'situational'
        ]
        
        # Check table ID
        for indicator in splits_indicators:
            if indicator in table_id.lower():
                return True
        
        # Check table classes
        if isinstance(table_class, list):
            for cls in table_class:
                for indicator in splits_indicators:
                    if indicator in cls.lower():
                        return True
        
        # Check table caption
        caption = table.find('caption')
        if caption and isinstance(caption, Tag):
            caption_text = caption.get_text().lower()
            for indicator in splits_indicators:
                if indicator in caption_text:
                    return True
        
        # Check if table has passing statistics columns
        header_row = table.find('tr')
        if header_row and isinstance(header_row, Tag):
            headers = [th.get_text().strip().lower() for th in header_row.find_all(['th', 'td'])]
            passing_headers = ['cmp', 'att', 'cmp%', 'yds', 'td', 'int', 'rate']
            matching_headers = sum(1 for header in passing_headers if any(h in header for h in headers))
            
            # If we find multiple passing-related headers, it's likely a splits table
            if matching_headers >= 4:
                return True
        
        return False

    def _process_splits_table(self, table: Tag, player_info: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Process a single splits table and extract all split statistics.
        
        Args:
            table: BeautifulSoup table element
            player_info: Dictionary containing player info
            
        Returns:
            List of split statistics dictionaries
        """
        splits = []
        table_id = table.get('id', 'unknown')
        split_type = self._determine_split_type(table_id)
        
        # Find tbody
        tbody = table.find('tbody')
        if not tbody or not isinstance(tbody, Tag):
            logger.warning(f"No tbody found in splits table {table_id}")
            return splits
        
        # Process each row
        rows = tbody.find_all('tr')
        for row in rows:
            # Skip header rows
            if row.get('class') and 'thead' in row.get('class'):
                continue
            
            # Extract split data
            split_data = self._extract_split_row_stats(row)
            if split_data:
                # Add player info
                split_data.update({
                    'pfr_id': player_info.get('pfr_id'),
                    'player_name': player_info.get('player_name'),
                    'season': player_info.get('season'),
                    'split_type': split_type,
                    'table_id': table_id
                })
                splits.append(split_data)
        
        return splits

    def _determine_split_type(self, table_id: str) -> str:
        """
        Determine the type of split based on table ID.
        
        Args:
            table_id: Table ID string
            
        Returns:
            Split type string
        """
        table_id_lower = table_id.lower()
        
        if 'home' in table_id_lower or 'away' in table_id_lower:
            return 'home_away'
        elif 'quarter' in table_id_lower:
            return 'by_quarter'
        elif 'half' in table_id_lower:
            return 'by_half'
        elif 'month' in table_id_lower:
            return 'monthly'
        elif 'week' in table_id_lower:
            return 'weekly'
        elif 'div' in table_id_lower:
            return 'vs_division'
        elif 'conf' in table_id_lower:
            return 'vs_conference'
        elif 'situational' in table_id_lower:
            return 'situational'
        else:
            return 'general'

    def _extract_split_row_stats(self, row: Tag) -> Optional[Dict[str, Union[str, int, float]]]:
        """Extract statistics from a single split row."""
        def get_cell_text(stat_name: str) -> str:
            cell = row.find('td', {'data-stat': stat_name})
            return cell.text.strip() if cell and isinstance(cell, Tag) else ''

        def get_cell_int(stat_name: str) -> int:
            return self._safe_int(get_cell_text(stat_name))

        def get_cell_float(stat_name: str) -> float:
            return self._safe_float(get_cell_text(stat_name))

        # Extract split identifier
        split_cell = row.find('td', {'data-stat': 'split'})
        value_cell = row.find('td', {'data-stat': 'value'})
        
        if not split_cell or not value_cell:
            return None
        
        split_name = split_cell.text.strip()
        split_value = value_cell.text.strip()
        
        if not split_name or not split_value:
            return None

        # Extract all available statistics
        stats = {
            'split': split_name,
            'value': split_value,
            'g': get_cell_int('g'),
            'w': get_cell_int('w'),
            'l': get_cell_int('l'),
            't': get_cell_int('t'),
            'cmp': get_cell_int('pass_cmp'),
            'att': get_cell_int('pass_att'),
            'inc': get_cell_int('pass_inc'),
            'cmp_pct': get_cell_float('pass_cmp_perc'),
            'yds': get_cell_int('pass_yds'),
            'td': get_cell_int('pass_td'),
            'int': get_cell_int('pass_int'),
            'rate': get_cell_float('pass_rating'),
            'sk': get_cell_int('pass_sacked'),
            'sk_yds': get_cell_int('pass_sacked_yds'),
            'y_a': get_cell_float('pass_yds_per_att'),
            'ay_a': get_cell_float('pass_adj_yds_per_att'),
            'a_g': get_cell_float('pass_att_per_g'),
            'y_g': get_cell_float('pass_yds_per_g'),
            'rush_att': get_cell_int('rush_att'),
            'rush_yds': get_cell_int('rush_yds'),
            'rush_y_a': get_cell_float('rush_yds_per_att'),
            'rush_td': get_cell_int('rush_td'),
            'rush_a_g': get_cell_float('rush_att_per_g'),
            'rush_y_g': get_cell_float('rush_yds_per_g'),
            'total_td': get_cell_int('all_td'),
            'pts': get_cell_int('scoring'),
            'fmb': get_cell_int('fumbles'),
            'fl': get_cell_int('fumbles_lost'),
            'ff': get_cell_int('fumbles_forced'),
            'fr': get_cell_int('fumbles_rec'),
            'fr_yds': get_cell_int('fumbles_rec_yds'),
            'fr_td': get_cell_int('fumbles_rec_td')
        }
        
        return stats

    def _extract_pfr_id(self, player_url: str) -> Optional[str]:
        """Extract PFR ID from player URL."""
        if not player_url:
            return None
        
        # Extract ID from URL pattern like /players/B/BurrJo01.htm
        match = re.search(r'/players/[A-Z]/([A-Za-z0-9]+)\.htm', player_url)
        return match.group(1) if match else None

    def _normalize_pfr_team_code(self, team_code: str) -> str:
        """Normalize PFR team code."""
        if not team_code:
            return ''
        
        # Remove any extra whitespace and normalize
        return team_code.strip().upper()

    def _safe_int(self, value: str) -> int:
        """Safely convert string to integer."""
        if not value or value.strip() == '':
            return 0
        
        try:
            # Remove any non-numeric characters except minus sign
            cleaned = re.sub(r'[^\d\-]', '', value.strip())
            if cleaned:
                return int(cleaned)
        except (ValueError, TypeError):
            pass
        
        return 0

    def _safe_float(self, value: str) -> float:
        """Safely convert string to float."""
        if not value or value.strip() == '':
            return 0.0
        
        try:
            # Remove any non-numeric characters except minus sign and decimal point
            cleaned = re.sub(r'[^\d\-\.]', '', value.strip())
            if cleaned:
                return float(cleaned)
        except (ValueError, TypeError):
            pass
        
        return 0.0 