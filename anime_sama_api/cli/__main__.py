import asyncio
import logging

import httpx
from rich import get_console
from rich.logging import RichHandler

from . import config, downloader, internal_player
from .utils import safe_input, select_one, select_range, keyboard_inter

from ..top_level import AnimeSama

# Initializing the console for rich printing with customized spinner and logging
console = get_console()
console._highlight = False
logging.basicConfig(format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
spinner = lambda text: console.status(text, spinner_style="cyan")

# Download function for one season of any anime
async def download_season(season, episodes) :
    '''Download on season of any anime'''
    # print(episodes[0])
    if config.DOWNLOAD:
        downloader.multi_download(
            episodes,
            config.DOWNLOAD_PATH,
            config.CONCURRENT_DOWNLOADS,
            config.PREFER_LANGUAGES,
        )
    else:
        command = internal_player.play_episode(
            episodes[0], config.PREFER_LANGUAGES
        )
        if command is not None:
            command.wait()

# Main function
async def main():
    # Getting the anime
    query = safe_input("Anime name: \033[0;34m", str)
    with spinner(f"Searching for [blue]{query}"):
        catalogues = await AnimeSama(config.URL, httpx.AsyncClient()).search(query)
    catalogue = select_one(catalogues)

    # Getting the season or seasons to download
    with spinner(f"Getting season list for [blue]{catalogue.name}"):
        seasons = await catalogue.seasons()
    seasons_to_download = select_range(seasons)

    # Select the different episodes to download by season
    episodes_to_download = {}
    for season in seasons_to_download :
        # For all seasons selected search all episodes of the season and request User what episode he want to download.
        with spinner(f"Getting episode list for [blue]{season.name}"):
            episodes = await season.episodes()
        console.print(f"\n[cyan bold underline]{season.serie_name} - {season.name}")
        episodes_to_download[season] = select_range(episodes, msg="Choose episode(s)", print_choices=True)

    # Download selected seasons
    for s in seasons_to_download :
        # NOTE: This result creates a bad user experience (UX) because:
        # - The user will see the "Downloaded" bar multiple times.
        # - Multiple progress bars for one episode will be displayed.
        # - The user may not realize that these progress bars are from different seasons.
        await download_season(season=s, episodes=episodes_to_download[s])

try:
    asyncio.run(main())
except (KeyboardInterrupt, asyncio.exceptions.CancelledError, EOFError):
    keyboard_inter()
