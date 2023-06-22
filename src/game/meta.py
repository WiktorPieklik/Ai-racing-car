from __future__ import annotations

from time import time
from enum import Enum
from typing import Union, Tuple, List

import pygame
from pygame import Mask, Surface, Rect

from .utils import get_mask, Point
from .assets import (
    CIRCLE_TRACK,
    FINISH_LINE_CIRCLE_TRACK,
    W_TRACK,
    FINISH_LINE_W_TRACK,
    PWR_TRACK,
    FINISH_LINE_PWR_TRACK
)


class Checkpoint:
    def __init__(self, rect: Rect):
        self._rect = rect
        self._active = True
        self._mask = pygame.mask.Mask((rect.width, rect.height), True)

    @property
    def active(self) -> bool:
        return self._active

    @property
    def rect(self) -> Rect:
        return self._rect

    @property
    def mask(self) -> pygame.mask.Mask:
        return self._mask

    def deactivate(self) -> None:
        self._active = False

    def activate(self) -> None:
        self._active = True


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
    CIRCLE = 0
    W_SHAPED = 1
    PWR = 2


Position = Tuple[Point, Point]


class MapMeta:
    def __init__(self, map_type: MapType):
        self._map_type = map_type
        self._track, self._finish_line = self._load_assets()
        self._car_initial_pos, self._car_initial_angle = self._get_positions()
        self._finish_line_crossing_point = self._get_crossing_point()
        self._checkpoints = self._get_checkpoints()

    @property
    def map_type(self) -> MapType:
        return self._map_type

    @property
    def track(self) -> Surface:
        return self._track

    @property
    def finish_line(self) -> Surface:
        return self._finish_line

    @property
    def checkpoints(self) -> List[Checkpoint]:
        return self._checkpoints

    @property
    def track_mask(self) -> Mask:
        return get_mask(self._track)

    @property
    def borders_mask(self) -> Mask:
        return get_mask(self._track, inverted=True)

    @property
    def finish_line_mask(self) -> Mask:
        return get_mask(self._finish_line)

    @property
    def finish_line_crossing_point(self) -> int:
        return self._finish_line_crossing_point

    @property
    def car_initial_pos(self) -> Point:
        return self._car_initial_pos

    @property
    def car_initial_angle(self) -> int:
        return self._car_initial_angle

    def _load_assets(self) -> Tuple[Surface, Surface]:
        """ Returns (track, finish_line) """

        if self.map_type == MapType.CIRCLE:
            track = CIRCLE_TRACK
            finish_line = FINISH_LINE_CIRCLE_TRACK
        elif self.map_type == MapType.W_SHAPED:
            track = W_TRACK
            finish_line = FINISH_LINE_W_TRACK
        else:
            track = PWR_TRACK
            finish_line = FINISH_LINE_PWR_TRACK

        return track, finish_line

    def _get_positions(self) -> Tuple[Point, int]:
        """ Returns (car_initial_pos, car_angle)) """

        if self.map_type == MapType.CIRCLE:
            car_initial_pos = (462, 713)
            car_angle = 310
        elif self.map_type == MapType.W_SHAPED:
            car_initial_pos = (490, 763)
            car_angle = 300
        else:
            car_initial_pos = (115, 703)
            car_angle = 275

        return car_initial_pos, car_angle

    def _get_crossing_point(self) -> int:
        if self.map_type == MapType.CIRCLE:
            return 660
        elif self.map_type == MapType.W_SHAPED:
            return 720
        else:
            return 640

    def _get_checkpoints(self) -> List[Checkpoint]:
        if self.map_type == MapType.W_SHAPED:
            return [Checkpoint(rect) for rect in [
                Rect(1059, 762, 100, 100),
                Rect(1485, 610, 100, 100),
                Rect(1452, 242, 100, 100),
                Rect(1005, 336, 100, 100),
                Rect(598, 286, 100, 100),
                Rect(325, 358, 100, 100)]
            ]
        elif self.map_type == MapType.PWR:
            return [Checkpoint(rect) for rect in [
                Rect(735, 903, 100, 100),
                Rect(1180, 923, 100, 100),
                Rect(1669, 708, 100, 100),
                Rect(1667, 381, 100, 100),
                Rect(1433, 111, 100, 100),
                Rect(1010, 501, 100, 100),
                Rect(691, 391, 100, 100),
                Rect(394, 178, 100, 100),
                Rect(106, 331, 100, 100)]
            ]
        else:
            return []
