import tensorflow as tf
from tf_agents.utils.common import function, Checkpointer

from src.ai.dqn import (
    CarRacingEnv,
    get_ann,
    get_agent,
    compute_avg_return,
    get_replay_buffer,
    collect_step
)


if __name__ == "__main__":
    batch_size = 1
    # env = CarRacingEnv.tf_batched_environment(batch_size)
    env = CarRacingEnv.tf_environment()
    model = get_ann(5, 9)
    agent = get_agent(model, env)
    num_iterations = 10_000
    collect_steps_per_iteration = 12
    replay_buffer = get_replay_buffer(agent, batch_size=env.batch_size)
    for _ in range(10):
        collect_step(env, agent.policy, replay_buffer)

    checkpointer = Checkpointer(
        ckpt_dir='pwr_shaped',
        max_to_keep=50,
        agent=agent,
        policy=agent.policy,
        global_step=agent.train_step_counter
    )
    checkpointer.initialize_or_restore()
    dataset = replay_buffer.as_dataset(
        num_parallel_calls=3,
        sample_batch_size=64,
        num_steps=2,
        single_deterministic_pass=False
    ).prefetch(3)
    iterator = iter(dataset)
    env.reset()
    agent.train = function(agent.train)  # optimizations
    for _ in range(5):
        with tf.device('/GPU:0'):
            for _ in range(num_iterations):
                for __ in range(collect_steps_per_iteration):
                    collect_step(env, agent.policy, replay_buffer)
                # Sample data from buffer and feed to network
                experience, unused_info = next(iterator)
                train_loss = agent.train(experience).loss
                step = agent.train_step_counter.numpy()
                checkpointer.save(step)
                if step % 10 == 0:
                    print(f"Step = {step}, Loss = {train_loss}, Average Return = {compute_avg_return(env, agent.policy)}")
