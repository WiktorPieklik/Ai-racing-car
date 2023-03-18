from pygame import Surface, SurfaceType
from pygame.transform import scale, rotate
from typing import Union, Tuple

Window = Union[Surface, SurfaceType]
Image = Union[Surface, SurfaceType]


def scale_image(img: Image, factor: float) -> Image:
    size = round(img.get_width() * factor), round(img.get_height() * factor)

    return scale(img, size)


def rotate_image(window: Window, image: Image, top_left: Tuple[int, int], angle: float) -> None:
    rotated = rotate(image, angle)
    new_rectangle = rotated.get_rect(center=image.get_rect(topleft=top_left).center)
    window.blit(rotated, new_rectangle.topleft)
