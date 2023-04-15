from abc import ABC
from typing import Tuple, Optional, Callable
from math import radians, cos, sin

from pygame import Color, Mask

from .utils import Window, Image, rotate_image, scale_image, get_mask
from .assets import CAR


class Car(ABC):
    def __init__(
            self,
            img: Image,
            start_position: Tuple[int, int],
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

    def move(self) -> None:
        if self.alive:
            rad = radians(self._angle)
            dx = cos(rad) * self._velocity
            dy = sin(rad) * self._velocity
            self._x += dx
            self._y -= dy

    def inertia(self):
        self._velocity = max(self._velocity - self._acceleration / 2, 0)
        self.move()

    def bounce(self):
        self._velocity = - self._velocity
        self.move()

    def is_colliding(self, mask: Mask, x: int = 0, y: int = 0) -> Optional[Tuple[int, int]]:
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(self._mask, offset)  # point of intersection

        return poi

    def radar(self, window: Window, angle: float):
        length = 0
        x, y = self.get_rect_center()

        while window.get_at((x, y)) != Color(0, 0, 0, 0) and length < 200:
            length += 1
            x, y = self.get_rect_center()
            x = int(x + cos(radians(self._angle + angle)) * length)
            y = int(y - sin(radians(self._angle + angle)) * length)

        line = ((255, 255, 255), self.get_rect_center(), (x, y), 1)
        circle = ((0, 255, 0) if length == 200 else (255, 0, 0), (x, y), 3)

        return line, circle

    def reset(self, x: int, y: int, angle: int) -> None:
        self._x = x
        self._y = y
        self._angle = angle
        self._velocity = 0
        self.alive = True


class PlayerCar(Car):
    def __init__(
            self,
            max_velocity: float,
            rotation_velocity: float,
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
            acceleration=acceleration
        )
