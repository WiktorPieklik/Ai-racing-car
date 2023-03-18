from abc import ABC
from utils import Window, Image, rotate_image
from assets import CAR
from typing import Tuple
import pygame


class Car(ABC):
    def __init__(
            self,
            img: Image,
            start_position: Tuple[int, int],
            max_velocity: float,
            rotation_velocity: float,
            start_angle: float = .0
    ):
        self._img = img
        self._x, self._y = start_position
        self._max_velocity = max_velocity
        self._velocity = .0
        self._rotation_velocity = rotation_velocity
        self._angle = start_angle

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

    def rotate(self, left: bool = False) -> None:
        if left:
            self._angle += self._rotation_velocity
        else:
            self._angle -= self._rotation_velocity

    def draw(self, window: Window) -> None:
        rotate_image(window=window, image=self._img, top_left=(self._x, self._y), angle=self._angle)


class PlayerCar(Car):
    def __init__(
            self,
            max_velocity: float,
            rotation_velocity: float,
            start_position: Tuple[int, int] = (0, 0),
            start_angle: float = .0
    ):
        super().__init__(
            img=CAR,
            start_position=start_position,
            max_velocity=max_velocity,
            rotation_velocity=rotation_velocity,
            start_angle=start_angle
        )
