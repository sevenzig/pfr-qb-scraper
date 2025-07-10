#!/usr/bin/env python3
"""
Batch Operations Manager for NFL QB Data Scraping
Handles large-scale operations with session management and resumability
"""

import json
import logging
import sys
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from core.scraper import CoreScraper
    from database.db_manager import DatabaseManager
    from config.config import config
except ImportError:
    try:
        from src.core.scraper import CoreScraper
        from src.database.db_manager import DatabaseManager
        from src.config.config import config
    except ImportError:
        # Fallback for testing
        CoreScraper = None
        DatabaseManager = None
        config = None

logger = logging.getLogger(__name__)


class BatchStatus(Enum):
    """Batch operation status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"


@dataclass
class BatchItem:
    """Individual item in a batch operation"""
    id: str
    name: str
    status: BatchStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'result': self.result,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatchItem':
        """Create from dictionary"""
        return cls(
            id=data['id'],
            name=data['name'],
            status=BatchStatus(data['status']),
            created_at=datetime.fromisoformat(data['created_at']),
            started_at=datetime.fromisoformat(data['started_at']) if data['started_at'] else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data['completed_at'] else None,
            error_message=data['error_message'],
            result=data['result'],
            retry_count=data['retry_count'],
            max_retries=data['max_retries']
        )


@dataclass
class BatchProgress:
    """Progress tracking for batch operations"""
    total_items: int = 0
    completed_items: int = 0
    failed_items: int = 0
    pending_items: int = 0
    running_items: int = 0
    start_time: Optional[datetime] = None
    estimated_completion: Optional[datetime] = None
    
    def update_progress(self, completed: int = 0, failed: int = 0, running: int = 0):
        """Update progress counters"""
        self.completed_items += completed
        self.failed_items += failed
        self.running_items = running
        self.pending_items = self.total_items - self.completed_items - self.failed_items - self.running_items
    
    def calculate_eta(self) -> Optional[datetime]:
        """Calculate estimated time of completion"""
        if not self.start_time or self.completed_items == 0:
            return None
        
        elapsed = datetime.now() - self.start_time
        rate = self.completed_items / elapsed.total_seconds()
        
        if rate > 0:
            remaining_items = self.total_items - self.completed_items - self.failed_items
            remaining_time = remaining_items / rate
            return datetime.now() + timedelta(seconds=remaining_time)
        
        return None
    
    def get_completion_percentage(self) -> float:
        """Get completion percentage"""
        if self.total_items == 0:
            return 0.0
        return (self.completed_items + self.failed_items) / self.total_items * 100


class BatchSession:
    """Session management for batch operations"""
    
    def __init__(self, session_id: str, session_dir: str = "batch_sessions"):
        """Initialize batch session"""
        self.session_id = session_id
        self.session_dir = Path(session_dir)
        self.session_dir.mkdir(exist_ok=True)
        
        self.session_file = self.session_dir / f"{session_id}.json"
        self.items: Dict[str, BatchItem] = {}
        self.progress = BatchProgress()
        self.status = BatchStatus.PENDING
        self.config: Dict[str, Any] = {}
        
        # Load existing session if it exists
        self.load_session()
    
    def add_item(self, item: BatchItem):
        """Add item to batch session"""
        self.items[item.id] = item
        self.progress.total_items = len(self.items)
        self.save_session()
    
    def update_item(self, item_id: str, **kwargs):
        """Update item in batch session"""
        if item_id in self.items:
            item = self.items[item_id]
            for key, value in kwargs.items():
                if hasattr(item, key):
                    setattr(item, key, value)
            self.save_session()
    
    def get_item(self, item_id: str) -> Optional[BatchItem]:
        """Get item by ID"""
        return self.items.get(item_id)
    
    def get_pending_items(self) -> List[BatchItem]:
        """Get all pending items"""
        return [item for item in self.items.values() if item.status == BatchStatus.PENDING]
    
    def get_failed_items(self) -> List[BatchItem]:
        """Get all failed items"""
        return [item for item in self.items.values() if item.status == BatchStatus.FAILED]
    
    def get_completed_items(self) -> List[BatchItem]:
        """Get all completed items"""
        return [item for item in self.items.values() if item.status == BatchStatus.COMPLETED]
    
    def mark_item_started(self, item_id: str):
        """Mark item as started"""
        self.update_item(item_id, status=BatchStatus.RUNNING, started_at=datetime.now())
        self.progress.running_items += 1
    
    def mark_item_completed(self, item_id: str, result: Dict[str, Any] = None):
        """Mark item as completed"""
        self.update_item(item_id, status=BatchStatus.COMPLETED, completed_at=datetime.now(), result=result)
        self.progress.completed_items += 1
        self.progress.running_items -= 1
    
    def mark_item_failed(self, item_id: str, error_message: str):
        """Mark item as failed"""
        item = self.items.get(item_id)
        if item:
            item.retry_count += 1
            if item.retry_count >= item.max_retries:
                self.update_item(item_id, status=BatchStatus.FAILED, error_message=error_message)
                self.progress.failed_items += 1
                self.progress.running_items -= 1
            else:
                # Retry
                self.update_item(item_id, status=BatchStatus.PENDING, error_message=error_message)
                self.progress.running_items -= 1
    
    def save_session(self):
        """Save session to file"""
        session_data = {
            'session_id': self.session_id,
            'status': self.status.value,
            'config': self.config,
            'progress': asdict(self.progress),
            'items': {item_id: item.to_dict() for item_id, item in self.items.items()},
            'last_updated': datetime.now().isoformat()
        }
        
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
    
    def load_session(self):
        """Load session from file"""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    session_data = json.load(f)
                
                self.status = BatchStatus(session_data['status'])
                self.config = session_data.get('config', {})
                
                # Load progress
                progress_data = session_data.get('progress', {})
                self.progress = BatchProgress(**progress_data)
                
                # Load items
                items_data = session_data.get('items', {})
                self.items = {
                    item_id: BatchItem.from_dict(item_data)
                    for item_id, item_data in items_data.items()
                }
                
            except Exception as e:
                logger.error(f"Failed to load session {self.session_id}: {e}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get session summary"""
        return {
            'session_id': self.session_id,
            'status': self.status.value,
            'progress': asdict(self.progress),
            'item_counts': {
                'total': len(self.items),
                'pending': len(self.get_pending_items()),
                'running': self.progress.running_items,
                'completed': len(self.get_completed_items()),
                'failed': len(self.get_failed_items())
            },
            'last_updated': datetime.now().isoformat()
        }


class BatchOperationManager:
    """Manager for batch scraping operations"""
    
    def __init__(self, config=None, max_workers: int = 3):
        """Initialize batch operation manager"""
        self.config = config or self._create_mock_config()
        self.max_workers = max_workers
        self.sessions: Dict[str, BatchSession] = {}
        self.active_operations: Dict[str, threading.Event] = {}
        
        # Initialize scraper and database manager
        if CoreScraper is not None:
            self.scraper = CoreScraper(rate_limit_delay=2.0)
        else:
            self.scraper = None
        
        if DatabaseManager is not None:
            self.db_manager = DatabaseManager()
        else:
            self.db_manager = None
    
    def _create_mock_config(self):
        """Create mock config for testing"""
        class MockConfig:
            app = type('obj', (object,), {'target_season': 2024})()
            batch = type('obj', (object,), {'max_workers': 3})()
        return MockConfig()
    
    def create_session(self, session_id: str, operation_type: str, **kwargs) -> BatchSession:
        """Create a new batch session"""
        session = BatchSession(session_id)
        session.config = {
            'operation_type': operation_type,
            'created_at': datetime.now().isoformat(),
            **kwargs
        }
        session.status = BatchStatus.PENDING
        session.save_session()
        
        self.sessions[session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[BatchSession]:
        """Get session by ID"""
        if session_id not in self.sessions:
            # Try to load from file
            session = BatchSession(session_id)
            if session.session_file.exists():
                self.sessions[session_id] = session
                return session
        return self.sessions.get(session_id)
    
    def batch_scrape_season(self, season: int, session_id: str = None, 
                          resume: bool = False) -> BatchSession:
        """Scrape all QBs for a season with batch processing"""
        if not session_id:
            session_id = f"season_{season}_{int(time.time())}"
        
        # Get or create session
        if resume:
            session = self.get_session(session_id)
            if not session:
                raise ValueError(f"Session {session_id} not found for resume")
        else:
            session = self.create_session(session_id, "season_scrape", season=season)
        
        # Get list of QBs to scrape
        if not session.items:
            qb_list = self._get_season_qb_list(season)
            for qb_name in qb_list:
                item = BatchItem(
                    id=f"{session_id}_{qb_name.replace(' ', '_')}",
                    name=qb_name,
                    status=BatchStatus.PENDING,
                    created_at=datetime.now()
                )
                session.add_item(item)
        
        # Start batch processing
        self._start_batch_processing(session)
        
        return session
    
    def batch_scrape_players(self, player_names: List[str], session_id: str = None,
                           season: int = 2024) -> BatchSession:
        """Scrape specific players with batch processing"""
        if not session_id:
            session_id = f"players_{int(time.time())}"
        
        session = self.create_session(session_id, "player_scrape", 
                                    players=player_names, season=season)
        
        # Add items for each player
        for player_name in player_names:
            item = BatchItem(
                id=f"{session_id}_{player_name.replace(' ', '_')}",
                name=player_name,
                status=BatchStatus.PENDING,
                created_at=datetime.now()
            )
            session.add_item(item)
        
        # Start batch processing
        self._start_batch_processing(session)
        
        return session
    
    def _get_season_qb_list(self, season: int) -> List[str]:
        """Get list of QBs for a season"""
        if self.scraper is None:
            # Mock data for testing
            return ["Joe Burrow", "Patrick Mahomes", "Josh Allen"]
        
        # This would typically get the QB list from the season page
        # For now, return a mock list
        return ["Joe Burrow", "Patrick Mahomes", "Josh Allen", "Lamar Jackson"]
    
    def _start_batch_processing(self, session: BatchSession):
        """Start batch processing for a session"""
        if session.status == BatchStatus.RUNNING:
            logger.warning(f"Session {session.session_id} is already running")
            return
        
        session.status = BatchStatus.RUNNING
        session.progress.start_time = datetime.now()
        session.save_session()
        
        # Create stop event for this operation
        stop_event = threading.Event()
        self.active_operations[session.session_id] = stop_event
        
        # Start processing in background thread
        thread = threading.Thread(
            target=self._process_batch_session,
            args=(session, stop_event)
        )
        thread.daemon = True
        thread.start()
    
    def _process_batch_session(self, session: BatchSession, stop_event: threading.Event):
        """Process batch session items"""
        try:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all pending items
                future_to_item = {}
                for item in session.get_pending_items():
                    if stop_event.is_set():
                        break
                    
                    future = executor.submit(self._process_batch_item, session, item)
                    future_to_item[future] = item
                
                # Process completed futures
                for future in as_completed(future_to_item):
                    if stop_event.is_set():
                        break
                    
                    item = future_to_item[future]
                    try:
                        result = future.result()
                        session.mark_item_completed(item.id, result)
                    except Exception as e:
                        session.mark_item_failed(item.id, str(e))
                    
                    # Update progress
                    session.progress.estimated_completion = session.progress.calculate_eta()
                    session.save_session()
            
            # Mark session as completed
            if not stop_event.is_set():
                session.status = BatchStatus.COMPLETED
            else:
                session.status = BatchStatus.CANCELLED
            
            session.save_session()
            
        except Exception as e:
            logger.error(f"Batch processing failed for session {session.session_id}: {e}")
            session.status = BatchStatus.FAILED
            session.save_session()
        finally:
            # Clean up
            if session.session_id in self.active_operations:
                del self.active_operations[session.session_id]
    
    def _process_batch_item(self, session: BatchSession, item: BatchItem) -> Dict[str, Any]:
        """Process a single batch item"""
        session.mark_item_started(item.id)
        
        try:
            if self.scraper is None:
                # Mock processing for testing
                time.sleep(1)  # Simulate processing time
                return {
                    'success': True,
                    'player_name': item.name,
                    'processed_at': datetime.now().isoformat()
                }
            
            # Get season from session config
            season = session.config.get('season', 2024)
            
            # Scrape player data
            result = self.scraper.scrape_player_season(item.name, season)
            
            if result and result.get('success'):
                return {
                    'success': True,
                    'player_name': item.name,
                    'main_stats': result.get('main_stats'),
                    'splits_count': len(result.get('splits_data', [])),
                    'processed_at': datetime.now().isoformat()
                }
            else:
                raise Exception(f"Failed to scrape data for {item.name}")
                
        except Exception as e:
            logger.error(f"Error processing item {item.id}: {e}")
            raise
    
    def stop_session(self, session_id: str) -> bool:
        """Stop a running batch session"""
        if session_id in self.active_operations:
            self.active_operations[session_id].set()
            return True
        return False
    
    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a batch session"""
        session = self.get_session(session_id)
        if session:
            return session.get_summary()
        return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all batch sessions"""
        sessions = []
        for session_id in self.sessions:
            summary = self.get_session_status(session_id)
            if summary:
                sessions.append(summary)
        return sessions
    
    def cleanup_session(self, session_id: str) -> bool:
        """Clean up a batch session"""
        try:
            # Stop if running
            self.stop_session(session_id)
            
            # Remove from sessions
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            # Remove session file
            session_file = Path("batch_sessions") / f"{session_id}.json"
            if session_file.exists():
                session_file.unlink()
            
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup session {session_id}: {e}")
            return False 