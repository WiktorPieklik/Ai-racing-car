from typing import Union, Tuple
from math import sqrt

from pygame import Surface, SurfaceType, Mask
from pygame.mask import from_surface
from pygame.transform import scale, rotate
from pygame.font import SysFont

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


def display_text_center(
        window: Window,
        text: str,
        font: SysFont,
        color: Tuple[int, int, int] = (255, 255, 255)
) -> None:
    render = font.render(text, True, color)
    center_x = window.get_width() / 2 - render.get_width() / 2
    center_y = window.get_height() / 2 - render.get_height() / 2
    window.blit(render, (center_x, center_y))


def distance(a: Point, b: Point) -> float:
    dx = a[0] - b[0]
    dy = a[1] - b[1]

    return sqrt(dx**2 + dy**2)
