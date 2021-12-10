import os, shutil, random
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras import models
from collections import deque

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras.optimizers import Adam
import keras.backend as K
import tensorflow as tf


class RandomAgent(object):
    def __init__(self, environment):
        self.environment = environment
        self.total_reward = 0

    #  *_  eats any number of arguments
    def act(self, *_):
        current = random.randrange(0, self.environment.action_space)
        next_loc = random.randrange(0, self.environment.action_space)
        number = self.environment.get_playable_count(current)
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
        
class DeepQNetwork(RandomAgent):
    def __init__(self, environment):
        self.environment = environment
        self.action_space = environment.action_space
        self.observation_space = environment.observation_space
        self.parameters = []
        
        # Learning rates
        self.learning_rate = 0.001
        self.discount = 1
        
        # Exploration
        self.min_exploration_rate = 0.01
        self.exploration_rate = 1.0
        self.exploration_decay = 0.995
        
        # Build Network
        self.model = self.build_model()
        
        # Memory Replay
        self.memories = deque(maxlen=5000)
        
        # Plotting variables
        self.file_names = []
        self.trajectory = []
        self.reward_list = []
        self.average_reward_list = []
        self.total_reward = 0
        self.plotting_iterations = 25
        self.image_path = "./temp_images"
        if os.path.exists(self.image_path):
            shutil.rmtree(self.image_path)
        os.mkdir(self.image_path)

        
    def build_model(self):
        model = Sequential()
        inputs = Input(shape=(97))
        
        # Head
        head = Dense(256,activation = 'tanh')(inputs)
        head = Dense(64,activation = 'tanh')(head)
        # Tail
        cur = Dense(97, activation='linear')(head)
        nex = Dense(97, activation='linear')(head)
        num = Dense(13, activation='linear')(head)
        
        model = tf.keras.models.Model(inputs=inputs, outputs=[cur, nex, num])
        optimizer = Adam(self.learning_rate)
        model.compile(optimizer, loss="mse")
        model.summary()
        print('\nAgent Initialized\n')
        return model
        
    def act(self, state):
        if np.random.random() < self.exploration_rate:
            return super().act(state)
        else:
            # Reduce to to observable space instead of state
            actions = self.predict(state[np.newaxis, ...])
            actions = actions[0]
            current, next_loc, number = actions
            current = np.argmax(current)
            next_loc = np.argmax(next_loc)
            number = np.argmax(number)
            
            return {
                'current_location': current,
                'next_location': next_loc,
                'number': number
            }
            
    def learn(self, state, next_state, action, reward, done, *_):
        self.total_reward += reward
        currents = action["current_location"]
        next_locs = action["next_location"]
        numbers = action["number"]
        
        # The update is set to a temporary value (1.0) for now.
        # The real value is computed inside the memory replay.
        self.memories.append([state, next_state, currents, next_locs, numbers, reward])

        if done:
            self.memory_replay()
       
    # Perform a TD update on every memory
    def memory_replay(self):
        n = min(64, len(self.memories))
        states, next_states, currents, next_locs, numbers, rewards = self.batch_memories(n)

        state_qualities = self.get_currq(states, currents, next_locs, numbers)
        next_state_qualities = self.get_nextq(next_states)
        
        targets = []

        # Q update functionality
        for index in range(n):
            targets.append(rewards[index] + state_qualities[index] - next_state_qualities[index])

        self.model.fit(states, targets, batch_size=self.batch_size, verbose=0)
        
    def get_nextq(self, state):
        preds = self.model.predict(state)
        cur = np.amax(preds[:, 0])
        nex = np.amax(preds[:, 1])
        num = np.amax(preds[:, 2])
        return np.array([cur, nex, num])
        
    def get_currq(self, state, currents, next_locs, numbers):
        preds = self.model.predict(state)
        cur, nex, num = [], [], []
        
        for index in range(len(state)):
            cur.append(preds[index][currents[index]])
            nex.append(preds[index][next_locs[index]])
            num.append(preds[index][numbers[index]])
            
        return np.array([np.array(cur), np.array(nex), np.array(num)])
                
    def batch_memories(self, n):
        np.random.shuffle(self.memories)

        states = np.empty(shape=(n, 97), dtype=float)
        next_states = np.empty(shape=(n, 97), dtype=float)
        currents = np.empty(shape=(n, 97), dtype=int)
        next_locs = np.empty(shape=(n, 97), dtype=int)
        numbers = np.empty(shape=(n, 13), dtype=int)
        rewards = np.empty(shape=(n, 1), dtype=int)

        for index in range(n):
            state, next_state, current, next_loc, number, reward, done = self.memories[index]

            states[index] = state
            next_states[index] = next_state
            currents[index] = current
            next_locs[index] = next_loc
            numbers[index] = number
            rewards[index] = reward + (not done)
        return states, next_states, currents, next_locs, numbers, rewards
        
        
    def finalize(self):
        return super().finalize()