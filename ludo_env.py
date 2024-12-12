from pedina import turn, check_end_position
import gym
from costanti import *


def move_token_one(dado, phase):
    observation, end = turn(tokens, dado, phase, 1)
    return observation, end


def move_token_two(dado, phase):
    observation, end = turn(tokens, dado, phase, 2)
    return observation, end


class ludo_env(gym.Env):
    def __init__(self):
        super(ludo_env, self).__init__()
        self.observations = observations
        self.action_space = gym.spaces.Discrete(2)  # Two possible actions
        self.observation_space = gym.spaces.Dict({
            'into the base': gym.spaces.Discrete(3),
            'in the path': gym.spaces.Discrete(3),
            'into the safe zone': gym.spaces.Discrete(3),
            'arrived at destination': gym.spaces.Discrete(3),
            'passed 1': gym.spaces.Discrete(2),
            'passed 2': gym.spaces.Discrete(2)
        })

    def reset(self):
        tokens[0].position = (2, 2)
        tokens[1].position = (2, 3)
        tokens[2].position = (2, 11)
        tokens[3].position = (2, 12)

    def step(self, action, dado, consecutive_sixes, phase):
        max_consecutive_sixes = 3

        if action not in [0, 1]:
            raise ValueError("Azione non valida")

        if action == 0:
            if check_end_position(action, tokens, phase):
                pass
            observation, end = move_token_one(dado, phase)
        elif action == 1:
            if check_end_position(action, tokens, phase):
                pass
            observation, end = move_token_two(dado, phase)

        dice_value = dado.value

        # If the dice returns 6, consecutive_sixes is increased
        if dice_value == 6:
            consecutive_sixes += 1
            dado.roll()
            if consecutive_sixes == max_consecutive_sixes:
                print(f"Giocatore ha ottenuto {max_consecutive_sixes} 6 consecutivi. Turno passa all'avversario.")
                consecutive_sixes = 0
        else:
            # If the dice does not return 6, consecutive_sixes resets
            consecutive_sixes = 0

        # If the dice does not return 6, it automatically changes the turn to the other player
        if dice_value != 6:
            dado.roll()

        return dado, observation, consecutive_sixes, end