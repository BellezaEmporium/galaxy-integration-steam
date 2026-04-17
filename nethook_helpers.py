import sys
import pathlib
import shutil
import os
import typing as t
import psutil
import time
from collections import Counter


STEAM_PATH = R'C:\Program Files (x86)\Steam\steam.exe'
GALAXY_PATH = R'C:\Program Files (x86)\GOG Galaxy\GalaxyClient.exe'
NETHOOK_PATH = None  # R'C:COMPLETE_ME\\NetHook2\NetHook2.dll'


def find_steam_ps(initial: t.Optional[psutil.Process]=None) -> t.Optional[psutil.Process]:
    if initial and initial.is_running():
        return initial
    for p in psutil.process_iter(['exe'], ad_value=''):
        if STEAM_PATH == p.info['exe']:
            return p
    return None


def restart_steam():
    p = psutil.Popen([STEAM_PATH, "-shutdown", "-silent"])
    p.wait()
    steam_ps = find_steam_ps()
    if steam_ps:
        steam_ps.wait(timeout=10)
    return psutil.Popen(STEAM_PATH)


def restart_galaxy():
    p = psutil.Popen([GALAXY_PATH, '/command=shutdown'])
    p.wait()
    psutil.Popen(GALAXY_PATH)


def inject_nethook(steam_ps=None):
    """Requires running as admin"""
    timeout = time.time() + 10
    while True:
        steam_ps = find_steam_ps(steam_ps)
        assert steam_ps, 'NetHook requires Steam running'
        if time.time() > timeout:
            print('timeout on loading steamclint.dll by Steam')
            break
        if [dll for dll in steam_ps.memory_maps() if 'steamclient.dll' in dll.path]:
            print('steamclient.dll loaded. Injecting nethook')
            break
    cmd = f'rundll32 "{NETHOOK_PATH}",Inject'
    psutil.Popen(cmd)


def copy_results_to_common_dir(dest_dir, must_include=''):
    os.makedirs(dest_dir, exist_ok=True)
    steam_nethook_dir = pathlib.PurePath(STEAM_PATH).parent / 'nethook'
    for d in os.listdir(steam_nethook_dir):
        if steam_nethook_dir.name == d:  # avoid recursion
            continue
        for f in os.listdir(steam_nethook_dir / d):
            if must_include not in f:
                continue
            src = steam_nethook_dir / d / f
            dest = pathlib.PurePath(dest_dir) / (src.name + '_' + d + src.suffix)  # originalname_timestamp.bin
            shutil.copy(src, dest)


def print_statistics(first_signals=10):
    steam_nethook_dir = pathlib.PurePath(STEAM_PATH).parent / 'nethook'
    signals = Counter()
    for root, dirs, files in os.walk(steam_nethook_dir):
        signal_names = []
        for i, f in enumerate(sorted(files)):
            if i > first_signals:
                break
            signal_names.append(f.split('_')[-1])
        signals.update(signal_names)
    print(signals)


def main():
    if NETHOOK_PATH is None:
        print('set up nethook path in script first')

    try:
        no = int(sys.argv[1])
    except (IndexError, ValueError):
        print('Usage: <script> <number_of_restarts> <path_to_copy_chosen_signals>')
        return

    try:
        output = sys.argv[2]
    except IndexError:
        output = 'output_nethook'

    for i in range(no):
        try:
            print(f'Running {i+1}. time...')
            steam_proc: psutil.Popen = restart_steam()
            inject_nethook(steam_proc)
            time.sleep(12)  # Steam startup
        except Exception as e:
            print(repr(e))
            continue

    print_statistics()
    copy_results_to_common_dir(output, must_include='ClientLogOnResponse')


if __name__ == "__main__":
    main()
