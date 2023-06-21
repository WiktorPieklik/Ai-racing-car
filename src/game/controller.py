from typing import Tuple, List
from abc import ABC, abstractmethod

import pygame
from decouple import config
from neat.nn.feed_forward import FeedForwardNetwork
from neat.config import Config
from dill import loads
from numpy import argmax
from tf_agents.utils.common import Checkpointer
from tf_agents.environments.tf_environment import TFEnvironment
from tf_agents.agents import DqnAgent

from .meta import GameState, MapMeta, MapType
from .utils import Window, display_text_center, display_text, draw_ai_controls
from .assets import MAIN_FONT
from .cars import PlayerCar, Car, AiCar
from .controls import CarMovement
from ..ai import (
    get_ann,
    get_agent
)


class Controller(ABC):
    def __init__(
            self,
            map_type: MapType,
            max_levels: int = 5,
            draw_radars: bool = False,
            hardcore: bool = False,
            draw_checkpoints: bool = False,
    ):
        self._map_meta = MapMeta(map_type)
        self._draw_radars = draw_radars or hardcore
        self._draw_checkpoints = draw_checkpoints
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
        if self._draw_checkpoints:
            self.__draw_checkpoints()

        lvl_text = MAIN_FONT.render(f"Level {self._state.level}", True, (255, 255, 255))
        time_text = MAIN_FONT.render(f"Time {self._state.level_time():.3f}s", True, (255, 255, 255))
        self._window.blit(lvl_text, (10, self._window.get_height() - lvl_text.get_height() - 70))
        self._window.blit(time_text, (10, self._window.get_height() - time_text.get_height() - 20))

    def __draw_checkpoints(self) -> None:
        for checkpoint in self._map_meta.checkpoints:
            if checkpoint.active:
                pygame.draw.rect(self._window, (0, 255, 0), checkpoint)

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


class AiController(Controller, ABC):
    def __init__(
            self,
            map_type: MapType,
            max_levels: int = 5,
            draw_radars: bool = False,
            hardcore: bool = False,
            draw_checkpoints: bool = False
    ):
        super().__init__(
            map_type=map_type,
            max_levels=max_levels,
            draw_radars=draw_radars,
            hardcore=hardcore,
            draw_checkpoints=draw_checkpoints
        )
        self._ai_movements: List[CarMovement] = []

    def _handle_car_movement(self, car: AiCar, movement: CarMovement) -> float:
        dxdy = None
        reward = -2
        promote = False
        self._ai_movements = []
        if movement == CarMovement.LEFT:
            car.rotate(left=True)
            self._ai_movements.append(CarMovement.LEFT)
        elif movement == CarMovement.LEFT_UP:
            car.rotate(left=True)
            dxdy = car.accelerate()
            promote = True
            self._ai_movements.append(CarMovement.LEFT_UP)
        elif movement == CarMovement.UP:
            dxdy = car.accelerate()
            promote = True
            self._ai_movements.append(CarMovement.UP)
        elif movement == CarMovement.RIGHT_UP:
            car.rotate(left=False)
            dxdy = car.accelerate()
            promote = True
            self._ai_movements.append(CarMovement.RIGHT_UP)
        elif movement == CarMovement.RIGHT:
            car.rotate(left=False)
            self._ai_movements.append(CarMovement.RIGHT)
        elif movement == CarMovement.SLOW_DOWN:
            dxdy = car.decelerate()
            self._ai_movements.append(CarMovement.SLOW_DOWN)
        elif movement == CarMovement.LEFT_SLOW_DOWN:
            car.rotate(left=True)
            dxdy = car.decelerate()
            self._ai_movements.append(CarMovement.LEFT_SLOW_DOWN)
        elif movement == CarMovement.RIGHT_SLOW_DOWN:
            car.rotate(left=False)
            dxdy = car.decelerate()
            self._ai_movements.append(CarMovement.RIGHT_SLOW_DOWN)
        elif movement == CarMovement.NOTHING:
            dxdy = car.inertia()
            car.stagnation += 5

        if dxdy is not None:
            reward = dxdy[0] + dxdy[1] + car.velocity
            if promote:
                reward *= 1.25

        return reward


class OnePlayerController(Controller):
    def __init__(
            self,
            map_type: MapType,
            max_velocity: float = 10.,
            max_angular_velocity: float = 4.,
            max_acceleration: float = .15,
            max_levels: int = 5,
            draw_radars: bool = False,
            hardcore: bool = False,
            draw_checkpoints: bool = False
    ):
        super().__init__(
            map_type=map_type,
            max_levels=max_levels,
            draw_radars=draw_radars,
            hardcore=hardcore,
            draw_checkpoints=draw_checkpoints
        )
        self._cars.append(PlayerCar(
            max_velocity=max_velocity,
            rotation_velocity=max_angular_velocity,
            track=self._map_meta.track,
            start_position=self._map_meta.car_initial_pos,
            start_angle=self._map_meta.car_initial_angle,
            acceleration=max_acceleration
        ))

    def _draw(self, update: bool = True) -> None:
        super()._draw()
        if update:
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
                for car in self._cars:
                    self._reset_car(car)
                self._run = True
                break

    def _game_loop_step(self) -> bool:
        game_over = False
        next_level = False
        for car in filter(lambda _car: isinstance(_car, PlayerCar), self._cars):
            self._player_controls(car)
        for car in self._cars:
            for checkpoint in self._map_meta.checkpoints:
                if checkpoint.active:
                    if car.is_colliding(checkpoint.mask, checkpoint.rect.left, checkpoint.rect.top):
                        checkpoint.deactivate()
            if car.is_colliding(self._map_meta.borders_mask):
                car.alive = False
                if isinstance(car, PlayerCar):
                    game_over = True
            crossed_finish_line_poi = car.is_colliding(self._map_meta.finish_line_mask)
            if crossed_finish_line_poi:
                if crossed_finish_line_poi[1] > self._map_meta.finish_line_crossing_point:
                    car.bounce()
                    print(crossed_finish_line_poi[1])
                else:
                    if not isinstance(car, PlayerCar):
                        game_over = True
                    next_level = True
                    self._state.next_level()
        if next_level:
            for car in self._cars:
                self._reset_car(car)

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
            draw_controls: bool = True
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
        self._draw_controls = draw_controls
        self._ai_movements: List[CarMovement] = []

    def _handle_ai_movement(self, car: AiCar, movement: CarMovement) -> None:
        self._ai_movements = []
        if movement == CarMovement.LEFT:
            car.rotate(left=True)
            self._ai_movements.append(CarMovement.LEFT)
        elif movement == CarMovement.LEFT_UP:
            car.rotate(left=True)
            car.accelerate()
            self._ai_movements.append(CarMovement.LEFT_UP)
        elif movement == CarMovement.UP:
            car.accelerate()
            self._ai_movements.append(CarMovement.UP)
        elif movement == CarMovement.RIGHT_UP:
            car.rotate(left=False)
            car.accelerate()
            self._ai_movements.append(CarMovement.RIGHT_UP)
        elif movement == CarMovement.RIGHT:
            car.rotate(left=False)
            self._ai_movements.append(CarMovement.RIGHT)
        elif movement == CarMovement.SLOW_DOWN:
            car.decelerate()
            self._ai_movements.append(CarMovement.SLOW_DOWN)
        elif movement == CarMovement.LEFT_SLOW_DOWN:
            car.rotate(left=True)
            car.decelerate()
            self._ai_movements.append(CarMovement.LEFT_SLOW_DOWN)
        elif movement == CarMovement.RIGHT_SLOW_DOWN:
            car.rotate(left=False)
            car.decelerate()
            self._ai_movements.append(CarMovement.RIGHT_SLOW_DOWN)
        elif movement == CarMovement.NOTHING:
            car.inertia()

    def _draw(self, update: bool = True) -> None:
        super()._draw(update=False)
        if self._draw_controls:
            draw_ai_controls(self._window, self._ai_movements)
        if update:
            pygame.display.update()


class PlayerVersusDqnController(PlayerVersusAiController):
    def __init__(
            self,
            map_type: MapType,
            checkpoint_path: str,
            max_velocity: float = 10.,
            max_acceleration: float = .15,
            max_angular_velocity: float = 4.,
            max_levels: int = 5,
            draw_radars: bool = False,
            hardcore: bool = False,
            draw_controls: bool = True
    ):
        super().__init__(
            map_type=map_type,
            max_velocity=max_velocity,
            max_angular_velocity=max_angular_velocity,
            max_acceleration=max_acceleration,
            max_levels=max_levels,
            draw_radars=draw_radars,
            hardcore=hardcore,
            draw_controls=draw_controls
        )
        self._cars.append(AiCar(
            max_velocity=max_velocity,
            rotation_velocity=max_angular_velocity,
            track=self._map_meta.track,
            start_position=self._map_meta.car_initial_pos,
            start_angle=self._map_meta.car_initial_angle,
            acceleration=max_acceleration,
            use_threshold=False
        ))
        self._env = None
        self._current_ts = None
        self._ts = None
        self._agent = None
        self._checkpoint_path = checkpoint_path
        # self._env.reset()

    def set_env(self, env: TFEnvironment) -> None:
        self._env = env
        self._agent = self.load_dqn(self._checkpoint_path)
        self._env.reset()

    def load_dqn(self, path: str) -> DqnAgent:
        ann = get_ann(5, 9)
        agent = get_agent(ann, self._env.time_step_spec(), self._env.action_spec())
        checkpointer = Checkpointer(
            ckpt_dir=path,
            agent=agent,
            policy=agent.policy
        )
        checkpointer.initialize_or_restore()

        return agent

    def get_observation(self) -> List[float]:
        for ai_car in filter(lambda car: isinstance(car, AiCar), self._cars):
            ai_car: AiCar

            return ai_car.radars_distances()

    def _handle_ai_movement(self, car: AiCar, movement: CarMovement) -> None:
        if car.alive:
            if self._ts is None:
                self._ts = self._env.current_time_step()
            action_step = self._agent.policy.action(self._ts)
            self._ts = self._env.step(action_step.action)
            movement = CarMovement(action_step.action)
            super()._handle_ai_movement(car, movement)

    def _game_loop_step(self) -> bool:
        for ai_car in filter(lambda car: isinstance(car, AiCar), self._cars):
            ai_car: AiCar
            ts = self._env.current_time_step()
            action_step = self._agent.policy.action(ts)
            movement = CarMovement(action_step.action)
            self._handle_ai_movement(ai_car, movement)

        return super()._game_loop_step()


class PlayerVersusNeatController(PlayerVersusAiController):
    def __init__(
            self,
            map_type: MapType,
            genome_path: str,
            config: Config,
            max_velocity: float = 10.,
            max_angular_velocity: float = 4.,
            max_acceleration: float = .15,
            max_levels: int = 5,
            draw_radars: bool = False,
            hardcore: bool = False,
            draw_controls: bool = True
    ):
        super().__init__(
            map_type=map_type,
            max_velocity=max_velocity,
            max_angular_velocity=max_angular_velocity,
            max_acceleration=max_acceleration,
            max_levels=max_levels,
            draw_radars=draw_radars,
            hardcore=hardcore,
            draw_controls=draw_controls
        )
        self.__ann = self.__load_ann(genome_path, config)
        self._cars.append(AiCar(
            max_velocity=max_velocity,
            rotation_velocity=max_angular_velocity,
            track=self._map_meta.track,
            start_position=self._map_meta.car_initial_pos,
            start_angle=self._map_meta.car_initial_angle,
            acceleration=max_acceleration,
            use_threshold=False
        ))

    def _game_loop_step(self) -> bool:
        # TODO: associate single net with single AiCar
        for car in filter(lambda _car: isinstance(_car, AiCar), self._cars):
            car: AiCar  # just for syntax highlighting
            output = self.__ann.activate(car.radars_distances())
            movement = CarMovement(argmax(output))
            self._handle_ai_movement(car, movement)

        return super()._game_loop_step()

    @staticmethod
    def __load_ann(genome_path: str, config: Config) -> FeedForwardNetwork:
        with open(genome_path, 'rb') as fh:
            genome = loads(fh.read())

        return FeedForwardNetwork.create(genome, config)
