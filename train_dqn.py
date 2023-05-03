from src.ai.dqn import (
    CarRacingEnv,
    get_ann,
    get_agent,
    compute_avg_return,
    get_replay_buffer,
    collect_step
)


if __name__ == "__main__":
    env = CarRacingEnv.tf_environment()
    model = get_ann(5, 9)
    agent = get_agent(model, env)
    num_iterations = 1000000
    collect_steps_per_iteration = 1
    batch_size = 1
    replay_buffer = get_replay_buffer(agent, batch_size=batch_size)
    dataset = replay_buffer.as_dataset(
        num_parallel_calls=3,
        sample_batch_size=batch_size,
        num_steps=2,
        single_deterministic_pass=False
    ).prefetch(3)
    iterator = iter(dataset)
    env.reset()
    for _ in range(batch_size):
        collect_step(env, agent.policy, replay_buffer)
    for _ in range(num_iterations):
        for __ in range(collect_steps_per_iteration):
            collect_step(env, agent.policy, replay_buffer)
        # Sample data from buffer and feed to network
        experience, unused_info = next(iterator)
        train_loss = agent.train(experience).loss

        step = agent.train_step_counter.numpy()
        if step % 200 == 0:
            print(f"Step = {step}, Loss = {train_loss}")
        if step % 1000 == 0:
            avg_return = compute_avg_return(env, agent.policy)
            print(f"Step = {step}, Average Return = {avg_return}")
