from time import time
from typing import Union


class GameState:
    def __init__(self, level: int = 1):
        self._level = level
        self._started = False
        self._start_time = 0

    @property
    def level_started(self) -> bool:
        return self._started

    @property
    def level(self) -> int:
        return self._level

    def next_level(self) -> None:
        self._level += 1
        self._started = False

    def reset(self) -> None:
        self._level = 1
        self._started = False
        self._start_time = 0

    def is_game_finished(self) -> bool:
        return self._level > 10  # 10 level by default so far

    def start_level(self) -> None:
        self._started = True
        self._start_time = time()

    def level_time(self) -> Union[int, float]:
        if not self._started:
            return 0
        return time() - self._start_time
