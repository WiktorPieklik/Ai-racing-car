from pathlib import Path
from pygame.image import load

RAW_DIR = Path(".") / "raw"

CAR = load(RAW_DIR / "car.png")
CIRCLE_TRACK = load(RAW_DIR / "circle_track.png")
W_TRACK = load(RAW_DIR / "w_track.png")
PWR_TRACK = load(RAW_DIR / "pwr_track.png")
