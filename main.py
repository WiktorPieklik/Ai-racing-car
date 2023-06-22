import os

import neat
from pathlib import Path
from bullet import Bullet, Check, styles, YesNo

from src.game import OnePlayerController, MapType, PlayerVersusNeatController, PlayerVersusDqnController
from src.ai.dqn import CarRacingEnv


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
    os.system("clear")
    maps = ['Circle', 'W', 'PWR']
    options = ['Draw radars', 'Hardcore mode']

    prompt = YesNo("Would U like to play against AI?", default='y')
    multiplayer = prompt.launch()
    if multiplayer:
        prompt = Bullet(
            prompt="NEAT or DQN? ",
            choices=["NEAT", "DQN"],
            indent=0,
            align=5,
            margin=2,
            shift=0,
            pad_right=5,
        )
        ai = prompt.launch()
    prompt = Bullet(
        prompt="\nChoose a map: ",
        choices=maps,
        indent=0,
        align=5,
        margin=2,
        shift=0,
        pad_right=5,
        return_index=True
    )
    map_type = MapType(prompt.launch()[1])
    prompt = Check(
        prompt="Choose options: ",
        choices=options
    )
    options = prompt.launch()

    # building game
    if multiplayer:
        if "NEAT" in ai:
            print("Running NEAT\n")
            controller = PlayerVersusNeatController(
                map_type=map_type,
                config=config,
                genome_path=str(BEST_GENOME.resolve()),
                max_angular_velocity=6.,
                draw_radars="Draw radars" in options,
                hardcore="Hardcore mode" in options
            )
        else:
            print("Running DQN\n")
            controller = PlayerVersusDqnController(
                map_type=map_type,
                checkpoint_path=str(CHECKPOINT.resolve()),
                max_angular_velocity=5.7,
                draw_radars="Draw radars" in options,
                hardcore="Hardcore mode" in options
            )
            env = CarRacingEnv.tf_environment(with_gui=False, get_observation=controller.get_observation)
            controller.set_env(env)
    else:
        controller = OnePlayerController(
            map_type=map_type,
            max_angular_velocity=6.,
            draw_radars="Draw radars" in options,
            hardcore="Hardcore mode" in options
        )
    controller.run()
