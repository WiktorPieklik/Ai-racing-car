from abc import ABC
from typing import Tuple, Optional, List
from math import radians, cos, sin

import pygame.draw
from pygame import Color, Mask, Surface

from .utils import Window, Image, rotate_image, scale_image, get_mask, Point, distance
from .assets import CAR


class Car(ABC):
    def __init__(
            self,
            img: Image,
            start_position: Tuple[int, int],
            track: Surface,
            max_velocity: float,
            rotation_velocity: float,
            start_angle: float = .0,
            acceleration: float = .15
    ):
        self._img = img
        self._mask = get_mask(self._img)
        self._x, self._y = start_position
        self._max_velocity = max_velocity
        self._velocity = .0
        self._rotation_velocity = rotation_velocity
        self._angle = start_angle
        self._acceleration = acceleration
        self.alive = True
        self._radars: List[Tuple[int, Point]] = []
        self._track = track

    def get_rect_center(self) -> Tuple[int, int]:
        return self.img.get_rect(topleft=(self._x, self._y)).center

    @property
    def max_velocity(self) -> float:
        return self._max_velocity

    @property
    def velocity(self) -> float:
        return self._velocity

    @property
    def rotation_velocity(self) -> float:
        return self._rotation_velocity

    @property
    def angle(self) -> float:
        return self._angle

    @property
    def img(self) -> Image:
        return self._img

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    @property
    def acceleration(self) -> float:
        return self._acceleration

    def rotate(self, left: bool = False) -> None:
        if left:
            self._angle += self._rotation_velocity
        else:
            self._angle -= self._rotation_velocity

    def draw(self, window: Window) -> None:
        rotate_image(window=window, image=self._img, top_left=(self._x, self._y), angle=self._angle)

    def accelerate(self) -> None:
        self._velocity = min(self._velocity + self._acceleration, self._max_velocity)
        self.move()

    def decelerate(self) -> None:
        self._velocity = max(self._velocity - 1.85 * self._acceleration, 0)
        self.move()

    def move(self) -> Optional[Tuple[float, float]]:
        if self.alive:
            rad = radians(self._angle)
            dx = cos(rad) * self._velocity
            dy = sin(rad) * self._velocity
            self._x += dx
            self._y -= dy
            self._calculate_radars()

            return dx, dy

    def inertia(self) -> Optional[Tuple[float, float]]:
        self._velocity = max(self._velocity - self._acceleration / 2, 0)

        return self.move()

    def bounce(self):
        self._velocity = - self._velocity
        self.move()

    def is_colliding(self, mask: Mask, x: int = 0, y: int = 0) -> Optional[Tuple[int, int]]:
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(self._mask, offset)  # point of intersection

        return poi

    def draw_radars(self, window: Window) -> None:
        for r_len, r_point in self._radars:
            line = ((255, 255, 255), self.get_rect_center(), r_point, 1)
            circle = ((0, 255, 0) if r_len == 200 else (255, 0, 0), r_point, 3)
            pygame.draw.line(window, *line)
            pygame.draw.circle(window, *circle)

    def _calculate_radars(self) -> None:
        radar_angles = (-60, -30, 0, 30, 60)
        self._radars = []
        for angle in radar_angles:
            length = 0
            x, y = self.get_rect_center()
            while self._track.get_at((x, y)) != Color(0, 0, 0, 0) and length < 200:
                length += 1
                x, y = self.get_rect_center()
                x = int(x + cos(radians(self._angle + angle)) * length)
                y = int(y - sin(radians(self._angle + angle)) * length)
            self._radars.append((length, (x, y)))

    def reset(self, x: int, y: int, angle: int) -> None:
        self._x = x
        self._y = y
        self._angle = angle
        self._velocity = 0
        self.alive = True
        self._calculate_radars()


class PlayerCar(Car):
    def __init__(
            self,
            max_velocity: float,
            rotation_velocity: float,
            track: Surface,
            start_position: Tuple[int, int] = (0, 0),
            start_angle: float = .0,
            acceleration: float = .15
    ):
        super().__init__(
            img=scale_image(CAR, .65),
            start_position=start_position,
            max_velocity=max_velocity,
            rotation_velocity=rotation_velocity,
            start_angle=start_angle,
            acceleration=acceleration,
            track=track
        )
