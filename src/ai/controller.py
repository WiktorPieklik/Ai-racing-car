from abc import ABC, abstractmethod

from src.game import Controller, AiCar
from .controls import CarMovement


class AiController(Controller, ABC):
    @staticmethod
    def _handle_car_movement(car: AiCar, movement: CarMovement) -> float:
        dxdy = None
        reward = -2
        promote = False
        if movement == CarMovement.LEFT:
            car.rotate(left=True)
        if movement == CarMovement.LEFT_UP:
            car.rotate(left=True)
            dxdy = car.accelerate()
            promote = True
        if movement == CarMovement.UP:
            dxdy = car.accelerate()
            promote = True
        if movement == CarMovement.RIGHT_UP:
            car.rotate(left=False)
            dxdy = car.accelerate()
            promote = True
        if movement == CarMovement.RIGHT:
            car.rotate(left=False)
        if movement == CarMovement.SLOW_DOWN:
            dxdy = car.decelerate()
        if movement == CarMovement.LEFT_SLOW_DOWN:
            car.rotate(left=True)
            dxdy = car.decelerate()
        if movement == CarMovement.RIGHT_SLOW_DOWN:
            car.rotate(left=False)
            dxdy = car.decelerate()
        if movement == CarMovement.NOTHING:
            dxdy = car.inertia()
            car.stagnation += 5

        if dxdy is not None:
            reward = dxdy[0] + dxdy[1] + car.velocity
            if promote:
                reward *= 1.25

        return reward
