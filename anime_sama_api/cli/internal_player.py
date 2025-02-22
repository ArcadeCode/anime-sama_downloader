import os
import sys
import subprocess
from pathlib import Path

from rich import print

from anime_sama_api.langs import LANG

from .config import INTERNAL_PLAYER_COMMAND
from ..episode import Episode


def open_silent_process(command: list[str]) -> subprocess.Popen:
    try:

        if os.name in ("nt", "dos"):
            return subprocess.Popen(command)
        else:
            return subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL
            )

    except FileNotFoundError as e:
        print(f"[red]Error: {e}")
        sys.exit()


def play_episode(
    episode: Episode,
    prefer_languages: list[LANG],
    args: list[str] | None = None,
) -> subprocess.Popen | None:
    best = episode.best(prefer_languages)
    if best is None:
        print("[red]No player available")
        return None

    player_command = INTERNAL_PLAYER_COMMAND + [best]
    if args is not None:
        player_command += args

    # Check by the caller
    # if isinstance(self._sub_proc, sp.Popen):
    #     self.kill_player()

    return open_silent_process(player_command)

    # self._write_hist(entry)
    # self._start_dc_presence(entry)


def play_file(path: Path, args: list[str] | None = None) -> subprocess.Popen:
    player_command = INTERNAL_PLAYER_COMMAND + [str(path)]
    if args is not None:
        player_command += args

    return open_silent_process(player_command)
