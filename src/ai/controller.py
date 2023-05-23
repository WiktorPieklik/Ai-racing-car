from abc import ABC, abstractmethod
from typing import List

from src.game import Controller, AiCar, MapType, CarMovement


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
