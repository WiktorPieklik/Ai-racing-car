from pathlib import Path

import neat
from dill import dumps

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
        neat.DefaultStagnation,
        config_path
    )
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(show_species_detail=True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    population.add_reporter(neat.Checkpointer(generation_interval=10, time_interval_seconds=None))
    best_genome = population.run(controller.run, 100)
    with open('best_genome', 'wb') as tf:
        tf.write(dumps(best_genome))
    with open('statistics', 'wb') as tf:
        tf.write(dumps(stats))
