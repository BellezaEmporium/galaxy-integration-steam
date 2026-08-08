from .cache_proto import ProtoCache
import logging

logger = logging.getLogger(__name__)


class StatsCache(ProtoCache):
    def __init__(self):
        self._games_to_import: set = set()
        super(StatsCache, self).__init__()
        self._update_ready_state()

    def start_game_stats_import(self, game_ids):
        self._games_to_import |= set(game_ids)
        self._update_ready_state()

    def finish_game_stats_import(self):
        self._games_to_import = set()
        self._update_ready_state()

    @property
    def import_in_progress(self):
        return not self._ready_event.is_set()

    def __iter__(self):
        yield from self._info_map.items()

    def update_stats(self, game_id, stats, achievements):
        if game_id not in self._info_map:
            self._info_map[game_id] = dict()
        self._info_map[game_id]['stats'] = stats
        self._info_map[game_id]['achievements'] = achievements
        self._games_to_import.discard(game_id)
        self._update_ready_state()

    def _update_ready_state(self):
        if not self._games_to_import:
            if self._ready_event.is_set():
                return
            logger.info("Setting stats cache state to ready")
            self._ready_event.set()
        else:
            self._ready_event.clear()