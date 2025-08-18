import platform
import os

if platform.system().lower() == "windows":
    from galaxy.registry_monitor import RegistryMonitor

else:
    class FileRegistryMonitor:
        def __init__(self, filename):
            self._filename = filename
            self._stat = self._get_stat()

        def _get_stat(self):
            try:
                st = os.stat(self._filename)
                return (st.st_size, st.st_mtime_ns)
            except OSError:
                return (0, 0)

        def is_updated(self):
            current_stat = self._get_stat()
            updated = current_stat != self._stat
            self._stat = current_stat
            return updated

        def close(self):
            pass

def get_steam_registry_monitor():
    if platform.system().lower() == "windows":
        return RegistryMonitor(0x80000001, r"Software\Valve\Steam\Apps")
    else:
        return FileRegistryMonitor(os.path.expanduser("~/Library/Application Support/Steam/registry.vdf"))
