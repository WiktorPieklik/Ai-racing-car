from typing import Tuple, List, Optional

import pygame
import numpy as np
from tf_agents.environments.py_environment import PyEnvironment
from tf_agents.environments.tf_environment import TFEnvironment
from tf_agents.environments.tf_py_environment import TFPyEnvironment
from tf_agents.specs.array_spec import BoundedArraySpec
from tf_agents.trajectories import time_step as ts

from src.game import MapType, AiCar, draw_ai_controls, CarMovement, Point
from ..controller import AiController


class DqnController(AiController):
    def __init__(
            self,
            map_type: MapType,
            max_levels: int = 5,
            hardcore: bool = False,
            draw_controls: bool = False
    ):
        super().__init__(
            map_type=map_type,
            max_levels=max_levels,
            draw_radars=True,
            hardcore=hardcore
        )
        self._draw_controls = draw_controls
        self._cars: List[AiCar] = []  # just for typing issues
        self.spawn_car()

    def start_level(self) -> None:
        self._state.start_level()

    def get_state(self) -> Tuple[Point, float, float]:
        return (
            (self._cars[0].x, self._cars[0].y),
            self._cars[0].velocity,
            self._cars[0].angle,
        )

    def set_state(self, pos: Point, velocity: float, angle: float) -> None:
        self.start_level()
        self.spawn_car(pos, angle, velocity)
        self._draw()

    def spawn_car(
            self,
            position: Optional[Point] = None,
            angle: Optional[float] = None,
            velocity: float = .0
    ) -> None:
        self._cars = []
        self._cars.append(AiCar(
            max_velocity=10,
            rotation_velocity=6.,
            acceleration=.15,
            track=self._map_meta.track,
            start_position=self._map_meta.car_initial_pos if position is None else position,
            start_angle=self._map_meta.car_initial_angle if angle is None else angle,
            use_threshold=True,
            movement_threshold=600,
            velocity=velocity
        ))

    def get_observation(self) -> List[float]:
        return self._cars[0].radars_distances()

    @staticmethod
    def quit() -> None:
        pygame.quit()

    def reset(self) -> None:
        self.start_level()
        self.spawn_car()
        self._draw()


    def _draw(self) -> None:
        super()._draw()
        if self._draw_controls:
            draw_ai_controls(self._window, self._ai_movements)
        pygame.display.update()

    def run(self, action: int) -> Tuple[bool, float]:
        """ Return done, reward """
        movement = CarMovement(action)
        reward = -5
        if movement == CarMovement.SLOW_DOWN:
            reward -= 10
        elif movement == CarMovement.UP:
            reward += 10
        done = False
        car = self._cars[0]
        if car.alive:
            reward += self._handle_car_movement(car, movement) + car.velocity
            if car.is_colliding(self._map_meta.borders_mask):
                car.alive = False
                done = True
            crossed_finish_line_poi = car.is_colliding(self._map_meta.finish_line_mask)
            if crossed_finish_line_poi:
                if crossed_finish_line_poi[1] > self._map_meta.finish_line_crossing_point:
                    car.bounce()
                    reward -= 100
                else:
                    print("Yeah! Did it!!!")
                    self._state.next_level()
                    reward += 1000
                    car.alive = False
                    done = True
        else:
            reward = -100
            done = True
        self._clock.tick(self._fps)
        self._draw()

        return done, reward


class CarRacingEnv(PyEnvironment):
    def __init__(self):
        self._action_spec = BoundedArraySpec(
            shape=(), dtype=np.int32, minimum=0, maximum=8, name='action')
        self._observation_spec = BoundedArraySpec(
            shape=(5,), dtype=np.float, name='observation')
        self._observation: List[float] = []
        self._episode_ended = False
        self._controller = DqnController(MapType.W_SHAPED, draw_controls=True)

    def observation_spec(self):
        return self._observation_spec

    def action_spec(self):
        return self._action_spec

    def get_info(self):
        pass

    def close(self) -> None:
        self._controller.quit()

    def get_state(self):
        return self._controller.get_state()

    def set_state(self, state):
        self._controller.set_state(state[0], state[1], state[2])

    def _step(self, action):
        if self._episode_ended:
            return self._reset()
        if 0 <= action <= 8:
            done, reward = self._controller.run(action)
            self._observation = self._controller.get_observation()
            if done:
                self._episode_ended = True

                return ts.termination(np.array(self._observation, dtype=np.float), reward)
            else:
                return ts.transition(
                    np.array(self._observation, dtype=np.float), reward=reward, discount=1.)
        else:
            raise ValueError("action must be in range [0, 8]")

    def _reset(self):
        self._controller.reset()
        self._observation = self._controller.get_observation()
        self._episode_ended = False

        return ts.restart(np.array(self._observation, dtype=np.float))

    @staticmethod
    def tf_environment() -> TFEnvironment:
        return TFPyEnvironment(CarRacingEnv())
