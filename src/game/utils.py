from typing import Union, Tuple, List
from math import sqrt

from pygame import Surface, SurfaceType, Mask
from pygame.mask import from_surface
from pygame.transform import scale, rotate
from pygame.font import SysFont

from .controls import CarMovement
from .assets import K_UP, K_DOWN, K_LEFT, K_RIGHT

Window = Union[Surface, SurfaceType]
Image = Union[Surface, SurfaceType]
Point = Tuple[int, int]


def scale_image(img: Image, factor: float) -> Image:
    size = round(img.get_width() * factor), round(img.get_height() * factor)

    return scale(img, size)


def rotate_image(window: Window, image: Image, top_left: Tuple[int, int], angle: float) -> None:
    rotated = rotate(image, angle)
    new_rectangle = rotated.get_rect(center=image.get_rect(topleft=top_left).center)
    window.blit(rotated, new_rectangle.topleft)


def get_mask(surface: Image, inverted: bool = False) -> Mask:
    mask = from_surface(surface)
    if inverted:
        mask.invert()

    return mask


def display_text(
        window: Window,
        text: str,
        font: SysFont,
        pos: Point,
        color: Tuple[int, int, int] = (255, 255, 255)
) -> None:
    render = font.render(text, True, color)
    window.blit(render, pos)


def display_text_center(
        window: Window,
        text: str,
        font: SysFont,
        color: Tuple[int, int, int] = (255, 255, 255)
) -> None:
    render = font.render(text, True, color)
    center_x = window.get_width() / 2 - render.get_width() / 2
    center_y = window.get_height() / 2 - render.get_height() / 2
    display_text(window, text, font, (center_x, center_y), color)


def distance(a: Point, b: Point) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]

    return sqrt(dx**2 + dy**2)


def get_alpha_arrows(ai_movements: List[CarMovement]) -> Tuple[bool, bool, bool, bool]:
    """ left, up, right, down """

    arrows = False, False, False, False
    if CarMovement.LEFT in ai_movements:
        arrows = False, True, True, True
    elif CarMovement.LEFT_UP in ai_movements:
        arrows = False, False, True, True
    elif CarMovement.UP in ai_movements:
        arrows = True, False, True, True
    elif CarMovement.RIGHT_UP in ai_movements:
        arrows = True, False, False, True
    elif CarMovement.RIGHT in ai_movements:
        arrows = True, True, False, True
    elif CarMovement.SLOW_DOWN in ai_movements:
        arrows = True, True, True, False
    elif CarMovement.LEFT_SLOW_DOWN in ai_movements:
        arrows = False, True, True, False
    elif CarMovement.RIGHT_SLOW_DOWN in ai_movements:
        arrows = True, True, False, False
    elif CarMovement.NOTHING in ai_movements:
        arrows = True, True, True, True

    return arrows


def draw_ai_controls(window: Window, ai_movements: List[CarMovement]) -> None:
    k_up = scale_image(K_UP, .2)
    k_down = scale_image(K_DOWN, .2)
    k_left = scale_image(K_LEFT, .2)
    k_right = scale_image(K_RIGHT, .2)
    alpha = 60
    which_to_alpha = get_alpha_arrows(ai_movements)
    for should_alpha, arrow in zip(which_to_alpha, (k_left, k_up, k_right, k_down)):
        if should_alpha:
            arrow.set_alpha(alpha)

    window.blit(k_up, (950, 10))
    window.blit(k_down, (950, 105))
    window.blit(k_left, (855, 105))
    window.blit(k_right, (1045, 105))
