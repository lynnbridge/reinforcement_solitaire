import os, shutil, random
import numpy as np
import matplotlib.pyplot as plt


class RandomAgent(object):
    def __init__(self, environment):
        self.environment = environment
        self.total_reward = 0

    #  *_  eats any number of arguments
    def act(self, *_):
        current = random.randrange(0, self.environment.action_space)
        next_loc = random.randrange(0, self.environment.action_space)
        number = random.randrange(0, len(self.environment.state[current].get_flipped_cards())+1)
        act = {
            'current_location': current,
            'next_location': next_loc,
            'number': number
        }
        return act

    def convert_state(self, state):
        return state

    def learn(self, state, next_state, action, reward, *_):
        self.total_reward += reward
        
    def finalize(self):
        # Graphing here?
        self.total_reward = 0