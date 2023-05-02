from typing import Tuple, List
from abc import ABC, abstractmethod

import pygame
from decouple import config
from neat.nn.feed_forward import FeedForwardNetwork

from .meta import GameState, MapMeta, MapType
from .utils import Window, display_text_center, display_text, scale_image
from .assets import MAIN_FONT, K_UP, K_DOWN, K_LEFT, K_RIGHT
from .cars import PlayerCar, Car, AiCar
from ..ai import CarMovement


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

    def _init_monit(self) -> None:
        display_text_center(self._window, f"Press any key to start {self._state.level} level!", MAIN_FONT)
        pygame.display.update()

    @staticmethod
    def _player_controls(car: Car) -> None:
        keys = pygame.key.get_pressed()
        changing_velocity = False

        if keys[pygame.K_LEFT]:
            car.rotate(left=True)
        if keys[pygame.K_RIGHT]:
            car.rotate(left=False)
        if keys[pygame.K_UP]:
            changing_velocity = True
            car.accelerate()
        if keys[pygame.K_DOWN]:
            changing_velocity = True
            car.decelerate()

        if not changing_velocity:
            car.inertia()

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

    def _draw(self) -> None:
        super()._draw()
        pygame.display.update()

    def _handle_idleness(self) -> None:
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

    def _game_loop_step(self) -> bool:
        game_over = False
        for car in filter(lambda _car: isinstance(_car, PlayerCar), self._cars):
            self._player_controls(car)
            if car.is_colliding(self._map_meta.borders_mask):
                car.alive = False
                game_over = True
            crossed_finish_line_poi = car.is_colliding(self._map_meta.finish_line_mask)
            if crossed_finish_line_poi:
                if crossed_finish_line_poi[1] > self._map_meta.finish_line_crossing_point:
                    car.bounce()
                    print(crossed_finish_line_poi[1])
                else:
                    self._reset_car(car)
                    self._state.next_level()

        return game_over

    def run(self) -> None:
        while self._run:
            self._clock.tick(self._fps)
            self._draw()
            # region game idle & stop
            if not self._state.level_started:
                self._init_monit()
                self._handle_idleness()

            if pygame.event.get(pygame.QUIT):
                self._run = False
                break
            # endregion
            game_over = self._game_loop_step()
            if game_over:
                display_text(self._window, "You loser!", MAIN_FONT, (810, 0))
                self._state.reset()
                self._init_monit()
                self._handle_idleness()

        pygame.quit()


class PlayerVersusAiController(OnePlayerController, ABC):
    def __init__(
            self,
            map_type: MapType,
            max_velocity: float = 10.,
            max_angular_velocity: float = 4.,
            max_acceleration: float = .15,
            max_levels: int = 5,
            draw_radars: bool = False,
            hardcore: bool = False,
            draw_ai_controls: bool = True
    ):
        super().__init__(
            map_type=map_type,
            max_velocity=max_velocity,
            max_angular_velocity=max_angular_velocity,
            max_acceleration=max_acceleration,
            max_levels=max_levels,
            draw_radars=draw_radars,
            hardcore=hardcore
        )
        self._draw_ai_controls = draw_ai_controls
        self._ai_movements: List[int] = []

    @abstractmethod
    def _handle_ai_movement(self, car: AiCar, movement: CarMovement) -> None:
        raise NotImplementedError()

    def _draw_ai_controls(self) -> None:
        k_up = scale_image(K_UP, .2)
        k_down = scale_image(K_DOWN, .2)
        k_left = scale_image(K_LEFT, .2)
        k_right = scale_image(K_RIGHT, .2)
        alpha = 60

        if CarMovement.LEFT not in self._ai_movements:
            k_left.set_alpha(alpha)

        if CarMovement.LEFT_UP not in self._ai_movements:
            k_left.set_alpha(alpha)
            k_up.set_alpha(alpha)

        if CarMovement.UP not in self._ai_movements:
            k_up.set_alpha(alpha)

        if CarMovement.RIGHT_UP not in self._ai_movements:
            k_up.set_alpha(alpha)
            k_right.set_alpha(alpha)

        if CarMovement.RIGHT not in self._ai_movements:
            k_right.set_alpha(alpha)

        if CarMovement.SLOW_DOWN not in self._ai_movements:
            k_down.set_alpha(alpha)

        if CarMovement.LEFT_SLOW_DOWN not in self._ai_movements:
            k_left.set_alpha(alpha)
            k_down.set_alpha(alpha)

        if CarMovement.RIGHT_SLOW_DOWN not in self._ai_movements:
            k_right.set_alpha(alpha)
            k_down.set_alpha(alpha)

        self._window.blit(k_up, (950, 10))
        self._window.blit(k_down, (950, 105))
        self._window.blit(k_left, (855, 105))
        self._window.blit(k_right, (1045, 105))


class PlayerVersusNeatController(PlayerVersusAiController):
    def __init__(
            self,
            map_type: MapType,
            genome_path: str,
            max_velocity: float = 10.,
            max_angular_velocity: float = 4.,
            max_acceleration: float = .15,
            max_levels: int = 5,
            draw_radars: bool = False,
            hardcore: bool = False,
            draw_ai_controls: bool = True
    ):
        super().__init__(
            map_type=map_type,
            max_velocity=max_velocity,
            max_angular_velocity=max_angular_velocity,
            max_acceleration=max_acceleration,
            max_levels=max_levels,
            draw_radars=draw_radars,
            hardcore=hardcore,
            draw_ai_controls=draw_ai_controls
        )
        self.__genome_path = genome_path

    def _handle_ai_movement(self, car: AiCar, movement: CarMovement) -> None:
        pass
