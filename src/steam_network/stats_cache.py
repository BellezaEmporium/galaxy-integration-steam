from datetime import datetime
from typing import Callable, Dict, List

from .cache_proto import ProtoCache
import logging

logger = logging.getLogger(__name__)


class StatsCache(ProtoCache):
    def __init__(self):
        self._games_to_import: set = set()
        self._last_update_time: Dict[str, datetime] = {}
        self._update_callbacks: List[Callable[[str], None]] = []
        super(StatsCache, self).__init__()
        self._update_ready_state()
    
    def add_update_callback(self, callback: Callable[[str], None]):
        """Add callback to be notified when game stats are updated."""
        self._update_callbacks.append(callback)
    
    def _notify_update(self, game_id: str):
        """Notify all callbacks about a game stats update."""
        for callback in self._update_callbacks:
            try:
                callback(game_id)
            except Exception as e:
                logger.warning(f"Error in stats update callback: {e}")
    
    def update_stats(self, game_id, stats, achievements):
        """Update stats and notify listeners."""
        previous_achievements = None
        if game_id in self._info_map:
            previous_achievements = self._info_map[game_id].get('achievements')
        
        if game_id not in self._info_map:
            self._info_map[game_id] = dict()
        self._info_map[game_id]['stats'] = stats
        self._info_map[game_id]['achievements'] = achievements
        self._games_to_import.discard(game_id)
        self._last_update_time[game_id] = datetime.now()
        self._update_ready_state()
        
        # Check if new achievements were unlocked
        if self._has_new_achievements(previous_achievements, achievements):
            logger.info(f"New achievements detected for {game_id}")
            self._notify_update(game_id)
    
    def _has_new_achievements(self, previous, current) -> bool:
        """Check if current achievements contain new unlocks compared to previous."""
        if previous is None:
            return bool(current)  # First time loading
        
        if not current:
            return False
        
        # Create sets of achievement identifiers
        prev_set = set()
        for ach in previous:
            if isinstance(ach, dict):
                prev_set.add((ach.get('name'), ach.get('unlock_time')))
        
        curr_set = set()
        for ach in current:
            if isinstance(ach, dict):
                curr_set.add((ach.get('name'), ach.get('unlock_time')))
        
        # Check if there are new achievements in current that aren't in previous
        return bool(curr_set - prev_set)
    
    def get_achievement_count(self, game_id: str) -> int:
        """Get the number of achievements for a game."""
        game_data = self._info_map.get(game_id, {})
        achievements = game_data.get('achievements', [])
        return len(achievements) if achievements else 0