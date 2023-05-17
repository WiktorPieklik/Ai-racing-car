from src.game import OnePlayerController, MapType


if __name__ == "__main__":
    controller = OnePlayerController(MapType.PWR, draw_radars=True)
    controller.run()
