from src.game import GameController, MapType


if __name__ == "__main__":
    gc = GameController(MapType.PWR, draw_radars=True)
    gc.run()
