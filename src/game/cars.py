from abc import ABC
from utils import Window, Image, rotate_image, scale_image
from assets import CAR
from typing import Tuple
from math import radians, cos, sin


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
        self._x, self._y = start_position
        self._max_velocity = max_velocity
        self._velocity = .0
        self._rotation_velocity = rotation_velocity
        self._angle = start_angle
        self._acceleration = acceleration

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
        rad = radians(self._angle)
        dx = cos(rad) * self._velocity
        dy = sin(rad) * self._velocity
        self._x += dx
        self._y -= dy

    def inertia(self):
        self._velocity = max(self._velocity - self._acceleration / 2, 0)
        self.move()


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
