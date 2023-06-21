import tensorflow as tf
from tf_agents.agents import DqnAgent
from tf_agents.utils.common import element_wise_squared_loss
from tf_agents.networks import Sequential


def get_ann(n_observations: int, n_actions: int) -> tf.keras.models.Model:
    return Sequential([
        tf.keras.layers.InputLayer((1, n_observations)),
        tf.keras.layers.Dense(24, activation='relu'),
        tf.keras.layers.Dense(16, activation='relu'),
        tf.keras.layers.Dense(n_actions, activation=None)
    ])


def get_agent(model: tf.keras.models.Model, time_step_spec, action_spec) -> DqnAgent:
    train_step_counter = tf.Variable(0)
    agent = DqnAgent(
        time_step_spec=time_step_spec,
        action_spec=action_spec,
        q_network=model,
        optimizer=tf.keras.optimizers.legacy.Adam(),
        td_errors_loss_fn=element_wise_squared_loss,
        train_step_counter=train_step_counter,
        epsilon_greedy=None,
        boltzmann_temperature=1.
    )
    agent.initialize()

    return agent
