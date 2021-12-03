import os, shutil, random
import numpy as np
import matplotlib.pyplot as plt


class RandomAgent(object):
    def __init__(self, environment):
        self.environment = environment
        self.total_reward = 0

    #  *_  eats any number of arguments
    def act(self, *_):
        act = {
            'current_location': random.randrange(0, self.environment.action_space - 1),
            'next_location': random.randrange(0, self.environment.action_space - 1),
            'number': random.randrange(0, 13)
        }
        return act

    def convert_state(self, state):
        return state

    def learn(self, state, next_state, action, reward, *_):
        self.total_reward += reward