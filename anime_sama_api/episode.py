from collections.abc import Generator
import re
import logging
from dataclasses import dataclass

from .langs import flags, LANG, LANG_ID, id2lang, lang2ids

logger = logging.getLogger(__name__)


class Players(list[str]):
    def __call__(self, index: int) -> Generator[str]:
        yield from self[index % len(self) :] + self[: index % len(self)]


class Languages(dict[LANG_ID, Players]):
    def __post_init__(self):
        logger.warn("Everything normal")
        if not self:
            logger.warning(f"No player available for {self}")

    @property
    def availables(self) -> dict[LANG, list[Players]]:
        availables: dict[LANG, list[Players]] = {}
        for lang_id, players in self.items():
            if availables.get(id2lang[lang_id]) is None:
                availables[id2lang[lang_id]] = []
            availables[id2lang[lang_id]].append(players)
        return availables

    def consume_player(
        self, prefer_languages: list[LANG], index: int
    ) -> Generator[str]:
        for prefer_language in prefer_languages:
            for players in self.availables.get(prefer_language, []):
                if players:
                    yield from players(index)

        for language in lang2ids:
            for players in self.availables.get(language, []):
                if players:
                    logger.warning(
                        f"Language preference not respected. Using {language}"
                    )
                    yield from players(index)


@dataclass(frozen=True)
class Episode:
    languages: Languages
    serie_name: str = ""
    season_name: str = ""
    name: str = ""
    index: int = 1

    @property
    def fancy_name(self):
        return f"{self.name} " + " ".join(
            flags[lang] for lang in self.languages.availables
        )

    @property
    def season_number(self):
        match_season_number = re.search(r"\d+", self.season_name)
        return int(match_season_number.group(0)) if match_season_number else 0

    @property
    def long_name(self):
        return f"{self.season_name} - {self.name}"

    @property
    def short_name(self):
        return f"{self.serie_name} S{self.season_number:02}E{self.index:02}"

    def __str__(self):
        return self.fancy_name

    def consume_player(self, prefer_languages: list[LANG]) -> Generator[str]:
        yield from self.languages.consume_player(prefer_languages, self.index)

    def best(self, prefer_languages: list[LANG]) -> str | None:
        try:
            return next(self.consume_player(prefer_languages))
        except StopIteration:
            return None
