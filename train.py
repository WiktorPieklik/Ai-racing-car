from pathlib import Path

import neat

from src.ai.neat import NeatController
from src.game import MapType


if __name__ == "__main__":
    controller = NeatController(MapType.W_SHAPED)
    CONFIGS_PATH = Path("src/ai/neat") / "configs"
    config_path = str((CONFIGS_PATH / "w_shaped.ini").resolve())
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation, config_path
    )
    population = neat.Population(config)
