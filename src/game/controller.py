from typing import Tuple

import pygame
from decouple import config

from .meta import GameState, MapMeta, MapType
from .utils import Window, display_text_center, Point
from .assets import MAIN_FONT
from .cars import PlayerCar


class GameController:
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
        self._map_meta = MapMeta(map_type)
        self._draw_radars = draw_radars or hardcore
        self._hardcore = hardcore
        self._state = GameState(max_levels=max_levels)
        self._player_car = PlayerCar(
            max_velocity=max_velocity,
            rotation_velocity=max_angular_velocity,
            start_position=self._map_meta.car_initial_pos,
            start_angle=self._map_meta.car_initial_angle,
            acceleration=max_acceleration
        )
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

    def _reset_player_car(self) -> None:
        self._player_car.reset(*self._map_meta.car_initial_pos, self._map_meta.car_initial_angle)

    def _draw(self) -> None:
        self._window.fill((0, 0, 0))
        if not self._hardcore:
            self._window.blit(self._map_meta.track, (0, 0))
            self._window.blit(self._map_meta.finish_line, (0, 0))
        self._player_car.draw(self._window)
        if self._draw_radars:
            self._draw_player_car_radars()

        lvl_text = MAIN_FONT.render(f"Level {self._state.level}", True, (255, 255, 255))
        time_text = MAIN_FONT.render(f"Time {self._state.level_time():.3f}s", True, (255, 255, 255))
        self._window.blit(lvl_text, (10, self._window.get_height() - lvl_text.get_height() - 70))
        self._window.blit(time_text, (10, self._window.get_height() - time_text.get_height() - 20))

        pygame.display.update()

    def _draw_player_car_radars(self) -> None:
        radars_angle = (-60, -30, 0, 30, 60)
        for angle in radars_angle:
            line, circle = self._player_car.radar(self._map_meta.track, angle)
            pygame.draw.line(self._window, *line)
            pygame.draw.circle(self._window, *circle)

    def _player_controls(self) -> None:
        keys = pygame.key.get_pressed()
        changing_velocity = False

        if keys[pygame.K_LEFT]:
            self._player_car.rotate(left=True)
        if keys[pygame.K_RIGHT]:
            self._player_car.rotate(left=False)
        if keys[pygame.K_UP]:
            changing_velocity = True
            self._player_car.accelerate()
        if keys[pygame.K_DOWN]:
            changing_velocity = True
            self._player_car.decelerate()

        if not changing_velocity:
            self._player_car.inertia()

    def run(self) -> None:
        self._clock.tick(self._fps)

        while self._run:
            self._draw()
            #region game idle & stop
            if not self._state.level_started:
                display_text_center(self._window, f"Press any key to start {self._state.level} level!", MAIN_FONT)
                pygame.display.update()
                while True:
                    keydown = pygame.event.get(pygame.KEYDOWN)
                    should_quit = pygame.event.get(pygame.QUIT)
                    if should_quit:
                        self._run = False
                        break
                    if keydown:
                        self._state.start_level()
                        break

            if pygame.event.get(pygame.QUIT):
                self._run = False
                break
            #endregion
            self._player_controls()
            if self._player_car.is_colliding(self._map_meta.borders_mask):
                print("Out of the track")

            crossed_finish_line_poi = self._player_car.is_colliding(self._map_meta.finish_line_mask)
            if crossed_finish_line_poi:
                if crossed_finish_line_poi[1] > self._map_meta.finish_line_crossing_point:
                    print(crossed_finish_line_poi[1])
                    self._player_car.bounce()
                else:
                    self._reset_player_car()
                    self._state.next_level()

        pygame.quit()
