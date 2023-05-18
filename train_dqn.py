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
    model = get_ann(7, 9)
    agent = get_agent(model, env)
    num_iterations = 1000000
    collect_steps_per_iteration = 12
    replay_buffer = get_replay_buffer(agent, batch_size=batch_size)
    checkpointer = Checkpointer(
        ckpt_dir='dqn_best',
        max_to_keep=1,
        agent=agent,
        policy=agent.policy,
        global_step=agent.train_step_counter
    )
    dataset = replay_buffer.as_dataset(
        num_parallel_calls=3,
        sample_batch_size=batch_size,
        num_steps=2,
        single_deterministic_pass=False
    ).prefetch(3)
    iterator = iter(dataset)
    env.reset()
    agent.train = function(agent.train)  # optimizations
    with tf.device('/GPU:0'):
        for _ in range(num_iterations):
            for __ in range(collect_steps_per_iteration):
                collect_step(env, agent.policy, replay_buffer)
            # Sample data from buffer and feed to network
            experience, unused_info = next(iterator)
            train_loss = agent.train(experience).loss
            step = agent.train_step_counter.numpy()
            if step % 200 == 0:
                print(f"Step = {step}, Loss = {train_loss}, Average Return = {compute_avg_return(env, agent.policy)}")
            if step % 1000 == 0:
                avg_return = compute_avg_return(env, agent.policy)
                print(f"Step = {step}, Average Return = {avg_return}")
            if step % 1600 == 0:
                checkpointer.save(step)
