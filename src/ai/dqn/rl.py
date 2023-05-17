import tensorflow as tf
from tf_agents.agents import DqnAgent
from tf_agents.environments.tf_environment import TFEnvironment
from tf_agents.utils.common import element_wise_squared_loss
from tf_agents.replay_buffers.tf_uniform_replay_buffer import TFUniformReplayBuffer
from tf_agents.trajectories.trajectory import from_transition
from tf_agents.networks.sequential import Sequential


def get_ann(n_observations: int, n_actions: int) -> tf.keras.models.Model:
    return Sequential([
        tf.keras.layers.InputLayer((1, n_observations)),
        tf.keras.layers.Dense(512, activation='relu'),
        tf.keras.layers.Dropout(.4),
        tf.keras.layers.Dense(256, activation='relu'),
        tf.keras.layers.Dropout(.3),
        tf.keras.layers.Dense(n_actions, activation='linear')
    ])


def get_agent(model: tf.keras.models.Model, env: TFEnvironment) -> DqnAgent:
    train_step_counter = tf.Variable(0)
    agent = DqnAgent(
        time_step_spec=env.time_step_spec(),
        action_spec=env.action_spec(),
        q_network=model,
        optimizer=tf.keras.optimizers.legacy.Adam(),
        td_errors_loss_fn=element_wise_squared_loss,
        train_step_counter=train_step_counter,
    )
    agent.initialize()

    return agent


def compute_avg_return(env: TFEnvironment, policy, num_episodes: int = 10) -> float:
    total_return = .0
    for _ in range(num_episodes):
        ts = env.reset()
        episode_return = .0
        while not ts.is_last():
            action_step = policy.action(ts)
            ts = env.step(action_step.action)
            episode_return += ts.reward
        total_return += episode_return
    avg_return = total_return / num_episodes

    return avg_return


def get_replay_buffer(agent: DqnAgent, max_length: int = 100000, batch_size: int = 64) -> TFUniformReplayBuffer:
    return TFUniformReplayBuffer(
        data_spec=agent.collect_data_spec,
        batch_size=batch_size,
        max_length=max_length
    )


def collect_step(env: TFEnvironment, policy, buffer: TFUniformReplayBuffer) -> None:
    ts = env.current_time_step()
    action_step = policy.action(ts)
    next_ts = env.step(action_step.action)
    trajectory = from_transition(ts, action_step, next_ts)
    buffer.add_batch(trajectory)