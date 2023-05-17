from enum import Enum


class CarMovement(Enum):
    LEFT = 0
    LEFT_UP = 1
    UP = 2
    RIGHT_UP = 3
    RIGHT = 4
    SLOW_DOWN = 5
    LEFT_SLOW_DOWN = 6
    RIGHT_SLOW_DOWN = 7
    NOTHING = 8
