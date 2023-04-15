from __future__ import annotations

from time import time
from enum import Enum
from typing import Union, Tuple
from utils import get_mask
from pygame import Mask
from assets import (
    CIRCLE_TRACK,
    FINISH_LINE_CIRCLE_TRACK,
    W_TRACK,
    FINISH_LINE_W_TRACK,
    PWR_TRACK,
    FINISH_LINE_PWR_TRACK
)


class GameState:
    def __init__(self, level: int = 1, max_levels: int = 5):
        self._level = level
        self._max_levels = max_levels
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
        return self._level > self._max_levels

    def start_level(self) -> None:
        self._started = True
        self._start_time = time()

    def level_time(self) -> Union[int, float]:
        if not self._started:
            return 0
        return time() - self._start_time


class MapType(Enum):
    CIRCLE = 1
    W_SHAPED = 2
    PWR = 3


Point = Tuple[int, int]
Position = Tuple[Point, Point]


class MapMeta:
    def __init__(self, map_type: MapType):
        self._map_type = map_type
        self._track, self._borders, self._finish_line = self._load_assets()
        self._finish_line_coord, (self._car_initial_pos, self._car_initial_angle) = self._get_positions()

    @property
    def map_type(self) -> MapType:
        return self._map_type

    @property
    def track(self) -> Mask:
        return self._track

    @property
    def borders(self) -> Mask:
        return self._borders

    @property
    def finish_line(self) -> Mask:
        return self._finish_line

    @property
    def finish_line_coord(self) -> Position:
        return self._finish_line_coord

    @property
    def car_initial_pos(self) -> Point:
        return self._car_initial_pos

    @property
    def car_initial_angle(self) -> int:
        return self._car_initial_angle

    def _load_assets(self) -> Tuple[Mask, Mask, Mask]:
        """ Returns (track, borders, finish_line) """

        if self.map_type == MapType.CIRCLE:
            track = get_mask(CIRCLE_TRACK)
            borders = get_mask(CIRCLE_TRACK, inverted=True)
            finish_line = get_mask(FINISH_LINE_CIRCLE_TRACK)
        elif self.map_type == MapType.W_SHAPED:
            track = get_mask(W_TRACK)
            borders = get_mask(W_TRACK, inverted=True)
            finish_line = get_mask(FINISH_LINE_W_TRACK)
        else:
            track = get_mask(PWR_TRACK)
            borders = get_mask(PWR_TRACK, inverted=True)
            finish_line = get_mask(FINISH_LINE_PWR_TRACK)

        return track, borders, finish_line

    def _get_positions(self) -> Tuple[Position, Tuple[Point, int]]:
        """ Returns (finish_line_coord, (car_initial_pos, car_angle)) """

        if self.map_type == MapType.CIRCLE:
            finish_line_coord = ((377, 740), (546, 646))
            car_initial_pos = (462, 713)
            car_angle = 310
        elif self.map_type == MapType.W_SHAPED:
            finish_line_coord = ((0, 0), (0, 0))  # TODO: update later
            car_initial_pos = (0, 0)
            car_angle = 0
        else:
            finish_line_coord = ((0, 0), (0, 0))  # TODO: update later
            car_initial_pos = (0, 0)
            car_angle = 0

        return finish_line_coord, (car_initial_pos, car_angle)
