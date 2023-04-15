from pathlib import Path
from pygame.image import load
from pygame.font import SysFont, init

RAW_DIR = Path(".") / "src/game/raw"

# Images
CAR = load(RAW_DIR / "car.png")
CIRCLE_TRACK = load(RAW_DIR / "circle_track.png")
FINISH_LINE_CIRCLE_TRACK = load(RAW_DIR / "finish_line_circle_track.png")
W_TRACK = load(RAW_DIR / "w_track.png")
FINISH_LINE_W_TRACK = load(RAW_DIR / "finish_line_w_track.png")
PWR_TRACK = load(RAW_DIR / "pwr_track.png")
FINISH_LINE_PWR_TRACK = load(RAW_DIR / "finish_line_pwr_track.png")

# Fonts
init()
MAIN_FONT = SysFont("comicsans", 44)
