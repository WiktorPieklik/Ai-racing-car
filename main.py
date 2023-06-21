from src.game import OnePlayerController, MapType, PlayerVersusNeatController
import neat
from pathlib import Path


if __name__ == "__main__":
    CONFIG_PATH = Path("src/ai/neat/configs/pwr.ini")
    BEST_GENOME = Path("checkopoints/pwr/best_genome")
    config = neat.Config(
        genome_type=neat.DefaultGenome,
        stagnation_type=neat.DefaultStagnation,
        reproduction_type=neat.DefaultReproduction,
        species_set_type=neat.DefaultSpeciesSet,
        filename=str(CONFIG_PATH.resolve())
    )
    controller = PlayerVersusNeatController(
        map_type=MapType.W_SHAPED,
        config=config,
        genome_path=str(BEST_GENOME.resolve()),
        max_angular_velocity=6.,
        draw_radars=True,
    )
    controller.run()
