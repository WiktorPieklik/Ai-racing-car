from src.game import OnePlayerController, MapType, PlayerVersusNeatController, PlayerVersusDqnController
from src.ai.dqn import CarRacingEnv
import neat
from pathlib import Path


if __name__ == "__main__":
    CHECKPOINT = Path("dqn_best")
    CONFIG_PATH = Path("src/ai/neat/configs/pwr.ini")
    BEST_GENOME = Path("checkopoints/pwr/best_genome")
    config = neat.Config(
        genome_type=neat.DefaultGenome,
        stagnation_type=neat.DefaultStagnation,
        reproduction_type=neat.DefaultReproduction,
        species_set_type=neat.DefaultSpeciesSet,
        filename=str(CONFIG_PATH.resolve())
    )
    # controller = PlayerVersusDqnController(
    #     map_type=MapType.CIRCLE,
    #     checkpoint_path=str(CHECKPOINT.resolve()),
    #     max_angular_velocity=5.7,
    #     draw_radars=True
    #     # env=env,
    # )
    # env = CarRacingEnv.tf_environment(with_gui=False, get_observation=controller.get_observation)
    # controller.set_env(env)
    controller = PlayerVersusNeatController(
        map_type=MapType.PWR,
        config=config,
        genome_path=str(BEST_GENOME.resolve()),
        max_angular_velocity=6.,
        draw_radars=True,
    )
    controller.run()
