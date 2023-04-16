from typing import List

import pygame
import neat

from src.game import Controller, MapType, AiCar, display_text, MAIN_FONT, GameState
from ..controls import CarMovement


class NeatController(Controller):
    def __init__(
            self,
            map_type: MapType,
            max_levels: int = 5,
            hardcore: bool = False
    ):
        super().__init__(
            map_type=map_type,
            max_levels=max_levels,
            draw_radars=True,
            hardcore=hardcore
        )
        self.__nets = []
        self.__generation = 0
        self._cars: List[AiCar] = []

    @property
    def cars_alive(self) -> int:
        count = 0
        for car in self._cars:
            if car.alive:
                count += 1

        return count

    def __init_car(self) -> AiCar:
        return AiCar(
            max_velocity=10.,
            rotation_velocity=4.,
            acceleration=.15,
            track=self._map_meta.track,
            start_position=self._map_meta.car_initial_pos,
            start_angle=self._map_meta.car_initial_angle,
            movement_threshold=30
        )

    @staticmethod
    def __handle_car_movement(car: AiCar, movement: CarMovement) -> float:
        dxdy = None
        reward = -3
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

        if dxdy is not None:
            reward = dxdy[0] + dxdy[1]
            if promote:
                reward *= 1.25

        return reward

    def __display_population_info(self) -> None:
        display_text(self._window, f"Generation: {self.__generation}", MAIN_FONT, (810, 0))
        display_text(self._window, f"Cars alive: {self.cars_alive}", MAIN_FONT, (810, 45))
        pygame.display.update()

    def _draw(self) -> None:
        super()._draw()
        self.__display_population_info()
        pygame.display.update()

    def run(self, genomes, config) -> None:
        self.__generation += 1
        self._cars = []
        self._run = True
        for _, genome in genomes:
            self.__nets.append(neat.nn.FeedForwardNetwork.create(genome, config))
            genome.fitness = 0
            self._cars.append(self.__init_car())
        self._state.start_level()
        while self._run:
            self._clock.tick(self._fps)
            self._draw()
            pygame.display.update()
            for i, car in enumerate(self._cars):
                if not car.alive:
                    continue
                output = self.__nets[i].activate(car.radars_distances())
                movement = CarMovement(output.index(max(output)))
                reward = self.__handle_car_movement(car, movement)

                if car.is_colliding(self._map_meta.borders_mask):
                    car.alive = False
                    continue
                crossed_finish_line_poi = car.is_colliding(self._map_meta.finish_line_mask)
                if crossed_finish_line_poi:
                    if crossed_finish_line_poi[1] > self._map_meta.finish_line_crossing_point:
                        car.bounce()
                        genomes[i][1].fitness -= 100
                    else:
                        print("Wow! You've made it!!!")
                        self._state.next_level()
                        genomes[i][1].fitness += 200 + reward
                        car.alive = False

                if car.alive:
                    genomes[i][1].fitness += reward
                if genomes[i][1].fitness < -45:
                    car.alive = False

            if self.cars_alive == 0:
                self._run = False
                break

        # pygame.quit()
