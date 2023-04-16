from typing import Tuple, List
from abc import ABC, abstractmethod

import pygame
from decouple import config

from .meta import GameState, MapMeta, MapType
from .utils import Window, display_text_center, display_text
from .assets import MAIN_FONT
from .cars import PlayerCar, Car


class Controller(ABC):
    def __init__(
            self,
            map_type: MapType,
            max_levels: int = 5,
            draw_radars: bool = False,
            hardcore: bool = False
    ):
        self._map_meta = MapMeta(map_type)
        self._draw_radars = draw_radars or hardcore
        self._hardcore = hardcore
        self._state = GameState(max_levels=max_levels)
        self._cars: List[Car] = []
        self._fps = config('FPS', cast=int)
        self._window, self._clock = self._init_game()
        self._run = True

    @staticmethod
    def _init_game() -> Tuple[Window, pygame.time.Clock]:
        pygame.init()
        width = config('WIDTH', cast=int)
        height = config('HEIGHT', cast=int)
        pygame.display.set_caption("AI racing car")

        return pygame.display.set_mode((width, height)), pygame.time.Clock()

    def _reset_car(self, car: Car) -> None:
        car.reset(*self._map_meta.car_initial_pos, self._map_meta.car_initial_angle)

    def _draw(self) -> None:
        self._window.fill((0, 0, 0))
        if not self._hardcore:
            self._window.blit(self._map_meta.track, (0, 0))
            self._window.blit(self._map_meta.finish_line, (0, 0))
        for car in self._cars:
            car.draw(self._window)
            if self._draw_radars:
                car.draw_radars(self._window)

        lvl_text = MAIN_FONT.render(f"Level {self._state.level}", True, (255, 255, 255))
        time_text = MAIN_FONT.render(f"Time {self._state.level_time():.3f}s", True, (255, 255, 255))
        self._window.blit(lvl_text, (10, self._window.get_height() - lvl_text.get_height() - 70))
        self._window.blit(time_text, (10, self._window.get_height() - time_text.get_height() - 20))

        pygame.display.update()

    def _init_monit(self) -> None:
        display_text_center(self._window, f"Press any key to start {self._state.level} level!", MAIN_FONT)
        pygame.display.update()

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError()


class OnePlayerController(Controller):
    def __init__(
            self,
            map_type: MapType,
            max_velocity: float = 10.,
            max_angular_velocity: float = 4.,
            max_acceleration: float = .15,
            max_levels: int = 5,
            draw_radars: bool = False,
            hardcore: bool = False
    ):
        super().__init__(
            map_type=map_type,
            max_levels=max_levels,
            draw_radars=draw_radars,
            hardcore=hardcore
        )
        self._cars.append(PlayerCar(
            max_velocity=max_velocity,
            rotation_velocity=max_angular_velocity,
            track=self._map_meta.track,
            start_position=self._map_meta.car_initial_pos,
            start_angle=self._map_meta.car_initial_angle,
            acceleration=max_acceleration
        ))

    def __player_controls(self) -> None:
        keys = pygame.key.get_pressed()
        changing_velocity = False

        if keys[pygame.K_LEFT]:
            self._cars[0].rotate(left=True)
        if keys[pygame.K_RIGHT]:
            self._cars[0].rotate(left=False)
        if keys[pygame.K_UP]:
            changing_velocity = True
            self._cars[0].accelerate()
        if keys[pygame.K_DOWN]:
            changing_velocity = True
            self._cars[0].decelerate()

        if not changing_velocity:
            self._cars[0].inertia()

    def __handle_idleness(self) -> None:
        pygame.event.clear()
        while True:
            keydown = pygame.event.get(pygame.KEYDOWN)
            should_quit = pygame.event.get(pygame.QUIT)
            if should_quit:
                self._run = False
                break
            if keydown:
                self._state.start_level()
                self._reset_car(self._cars[0])
                self._run = True
                break

    def __game_loop_step(self) -> bool:
        game_over = False
        self.__player_controls()
        if self._cars[0].is_colliding(self._map_meta.borders_mask):
            self._cars[0].alive = False
            game_over = True
        crossed_finish_line_poi = self._cars[0].is_colliding(self._map_meta.finish_line_mask)
        if crossed_finish_line_poi:
            if crossed_finish_line_poi[1] > self._map_meta.finish_line_crossing_point:
                self._cars[0].bounce()
                print(crossed_finish_line_poi[1])
            else:
                self._reset_car(self._cars[0])
                self._state.next_level()

        return game_over

    def run(self) -> None:
        while self._run:
            self._clock.tick(self._fps)
            self._draw()
            # region game idle & stop
            if not self._state.level_started:
                self._init_monit()
                self.__handle_idleness()

            if pygame.event.get(pygame.QUIT):
                self._run = False
                break
            # endregion
            game_over = self.__game_loop_step()
            if game_over:
                display_text(self._window, "You loser!", MAIN_FONT, (810, 0))
                self._state.reset()
                self._init_monit()
                self.__handle_idleness()

        pygame.quit()
