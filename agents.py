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

        act = {
            'current_location': current,
            'next_location': next_loc
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
        self.invalid_moves = []
        self.average_reward_list = []
        self.total_reward = 0
        self.invalid_count = 0
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
        
        model = tf.keras.models.Model(inputs=inputs, outputs=[cur, nex])
        optimizer = Adam(self.learning_rate)
        model.compile(optimizer, loss="mse")
        model.summary()
        print('\nAgent Initialized\n')
        return model
        
    def act(self, state):
        if np.random.random() < self.exploration_rate:
            return super().act(state)
        else:
            # Passing in observable space instead of state
            actions = self.model.predict(state[np.newaxis, ...])
            actions = actions[0]
            current, next_loc = actions
            current = np.argmax(current)
            next_loc = np.argmax(next_loc)
            # number = get cards on top from location
            
            return {
                'current_location': current,
                'next_location': next_loc
            }
            
    def learn(self, state, next_state, action, reward, done, *_):
        self.total_reward += reward
        if reward == -1:
            self.invalid_count += 1
        currents = action["current_location"]
        next_locs = action["next_location"]
        
        # The update is set to a temporary value (1.0) for now.
        # The real value is computed inside the memory replay.
        self.memories.append([state, next_state, currents, next_locs, reward])

        if done:
            self.memory_replay()
       
    # Perform a TD update on every memory
    def memory_replay(self):
        n = min(64, len(self.memories))
        states, next_states, currents, next_locs, rewards = self.batch_memories(n)

        state_qualities = self.get_currq(states, currents, next_locs)
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
        return np.array([cur, nex])
        
    def get_currq(self, state, currents, next_locs):
        preds = self.model.predict(state)
        cur, nex = [], []
        
        for index in range(len(state)):
            cur.append(preds[index][currents[index]])
            nex.append(preds[index][next_locs[index]])
            
        return np.array([np.array(cur), np.array(nex)])
                
    def batch_memories(self, n):
        np.random.shuffle(self.memories)

        states = np.empty(shape=(n, 97), dtype=float)
        next_states = np.empty(shape=(n, 97), dtype=float)
        currents = np.empty(shape=(n, 97), dtype=int)
        next_locs = np.empty(shape=(n, 97), dtype=int)
        rewards = np.empty(shape=(n, 1), dtype=int)

        for index in range(n):
            state, next_state, current, next_loc, reward, done = self.memories[index]

            states[index] = state
            next_states[index] = next_state
            currents[index] = current
            next_locs[index] = next_loc
            rewards[index] = reward + (not done)
        return states, next_states, currents, next_locs, rewards
        
        
    def finalize(self, iteration):
        
        self.exploration_rate -= self.exploration_decay
        self.exploration_rate = max(self.exploration_rate, self.min_exploration_rate)
        self.reward_list.append(self.total_reward)
        self.invalid_moves.append(self.invalid_count)
        
        if len(self.reward_list) > 250:
            self.average_reward_list.append(np.mean(np.array(self.reward_list[-250:])))
        else:
            self.average_reward_list.append(np.mean(self.reward_list))

        if (iteration + 1) % self.plotting_iterations == 0:
            self.plot(iteration + 1)
        
        self.invalid_count = 0
        super().finalize()
        
    def plot(self, iteration):
        fig = plt.figure(figsize=(20,4), facecolor="white")
        fig.subplots_adjust(wspace=1)
        fig.suptitle(f"Iteration {iteration}")
        
        reward = fig.add_subplot(1, 2, 1)
        reward.plot([i for i in range(0,len(self.reward_list))], self.reward_list, c="k")
        reward.plot(
            np.arange(len(self.reward_list)),
            self.average_reward_list,
            c="r",
            linewidth=2,
        )
        reward.set_title("Rewards over time")
        reward.set_xlabel("iterations")
        reward.set_ylabel("reward")
        reward.set_ylim([-500, 10])
        
        invalid_move = fig.add_subplot(1, 2, 2)
        invalid_move.plot([i for i in range(0,len(self.invalid_moves))], self.invalid_moves, c="k")
        invalid_move.set_title("Invalid Moves over time")
        invalid_move.set_xlabel("Iterations")
        invalid_move.set_ylabel("Number of Invalid Moves")
        invalid_move.set_ylim([-500, 10])

        file_name = f"{self.image_path}/{iteration}.png"
        self.file_names.append(file_name)
        plt.savefig(file_name)
        plt.close("all")