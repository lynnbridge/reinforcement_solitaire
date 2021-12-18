import os, shutil, random
import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras import models
from collections import deque

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Input
from tensorflow.keras import layers
from tensorflow.keras.optimizers import Adam
import keras.backend as K
import tensorflow as tf

class RandomAgent(object):
    def __init__(self, environment):
        self.environment = environment
        self.total_reward = 0
        self.reward_overall = []

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
        
    def finalize(self, iteration):
        reward_file = open("random_agent.csv", "a")
        reward_file.write("{0} {1} \n".format(iteration, self.total_reward))
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
        self.exploration_decay = 0.8/10000
        
        # Build Network
        self.model = self.build_model()
        self.batch_size=128
        
        # Memory Replay
        self.memories = deque(maxlen=5000)
        
        # Plotting variables
        self.file_names = []
        self.trajectory = []
        self.reward_list = []
        self.invalid_moves = []
        self.games_won = []
        self.average_reward_list = []
        self.total_reward = 0
        self.invalid_count = 0
        self.plotting_iterations = 250
        self.image_path = "./temp_images"
        self.model_directory = "./model_dir"
        if os.path.exists(self.image_path):
            shutil.rmtree(self.image_path)
        os.mkdir(self.image_path)

        
    def build_model(self):
        value_inputs = Input(shape=(97), name="value")
        suit_inputs = Input(shape=(97), name="suit")
        color_inputs = Input(shape=(97), name="color")
        
        inputs = layers.concatenate([value_inputs, suit_inputs, color_inputs])
        
        # Head
        head = Dense(256,activation = 'tanh')(inputs)
        head = Dense(64,activation = 'tanh')(head)
        # head = Dense(64,activation = 'tanh')(head)
        # Tail
        cur = Dense(97, activation='linear')(head)
        nex = Dense(97, activation='linear')(head)
        
        model = tf.keras.models.Model(inputs=[value_inputs, suit_inputs, color_inputs], outputs=[cur, nex])
        optimizer = Adam(self.learning_rate)
        model.compile(optimizer, loss="mse")
        model.summary()
        # keras.utils.plot_model(model, "solitaire_model.png", show_shapes=True)
        print('\nAgent Initialized\n')
        return model
        
    def act(self, state):
        if np.random.random() < self.exploration_rate:
            return super().act(state)
        else:
            # Passing in observable space instead of state
            local_state = self.convert_state(state)
            actions = self.model.predict({"value": local_state[0][np.newaxis,...], "suit": local_state[1][np.newaxis,...], "color": local_state[2][np.newaxis,...]})
            current, next_loc = actions
            current = np.argmax(current)
            next_loc = np.argmax(next_loc)
            
            return {
                'current_location': current,
                'next_location': next_loc
            }

    def convert_state(self, state):
        value_inputs = np.empty(shape=(97,1), dtype=int)
        suit_inputs = np.empty(shape=(97,1), dtype=int)
        color_inputs = np.empty(shape=(97,1), dtype=int)        
        for ind in range(0, len(state)):
            value_inputs[ind] = state[ind].value
            suit_inputs[ind] = state[ind].suit.value
            color_inputs[ind] = state[ind].suit.get_color_number()
        return np.array([value_inputs, suit_inputs, color_inputs])
            
    def learn(self, state, next_state, action, reward, done, *_):
        self.total_reward += reward
        if reward == -1:
            self.invalid_count += 1
        currents = action["current_location"]
        next_locs = action["next_location"]
        
        local_state = self.convert_state(state)
        next_local_state = self.convert_state(next_state)
        
        # The update is set to a temporary value (1.0) for now.
        # The real value is computed inside the memory replay.
        self.memories.append([local_state, next_local_state, currents, next_locs, reward])

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
        preds = self.model.predict({"value": state[0], "suit": state[1], "color": state[2]})
        cur = np.amax(preds[:, 0])
        nex = np.amax(preds[:, 1])
        return np.array([cur, nex])
        
    def get_currq(self, state, currents, next_locs):
        preds = self.model.predict({"value": state[0], "suit": state[1], "color": state[2]})
        cur, nex = [], []
        
        for index in range(len(state[0])):
            cur.append(preds[index][currents[index]])
            nex.append(preds[index][next_locs[index]])
            
        return np.array([np.array(cur), np.array(nex)])
                
    def batch_memories(self, n):
        # np.random.shuffle(self.memories)
        self.memories = self.memories[np.argsort(self.memories[:,4])]
        
        states = np.empty(shape=(3))
        states[0] = np.empty(shape=(n, 97), dtype=float)
        states[1] = np.empty(shape=(n, 97), dtype=float)
        states[2] = np.empty(shape=(n, 97), dtype=float)
        next_states = np.empty(shape=(n, 97), dtype=float)
        currents = np.empty(shape=(n, 97), dtype=int)
        next_locs = np.empty(shape=(n, 97), dtype=int)
        rewards = np.empty(shape=(n, 1), dtype=int)

        for index in range(len(self.memories)-1, len(self.memories)-n, -1):
            state, next_state, current, next_loc, reward, done = self.memories[index]

            states[0][index] = state[0]
            states[1][index] = state[1]
            states[2][index] = state[2]
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
        # print(self.invalid_moves)
        
        if len(self.reward_list) > 250:
            self.average_reward_list.append(np.mean(np.array(self.reward_list[-250:])))
        else:
            self.average_reward_list.append(np.mean(self.reward_list))

        if (iteration + 1) % self.plotting_iterations == 0:
            self.plot(iteration + 1)
            self.export_model(iteration)
        
        self.invalid_count = 0
        self.total_reward = 0
        
    def plot(self, iteration):
        # print("Iteration", iteration)
        fig = plt.figure(figsize=(20,4), facecolor="white")
        fig.subplots_adjust(wspace=1)
        fig.suptitle(f"Iteration {iteration}")
        
        reward = fig.add_subplot(1, 3, 1)
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
        reward.set_ylim([-300, 100])
        
        invalid_move = fig.add_subplot(1, 3, 2)
        invalid_move.plot([i for i in range(0,len(self.invalid_moves))], self.invalid_moves, c="k")
        invalid_move.set_title("Invalid Moves over time")
        invalid_move.set_xlabel("Iterations")
        invalid_move.set_ylabel("Number of Invalid Moves")
        invalid_move.set_ylim([0, 300])
        
        won_games = fig.add_subplot(1, 3, 3)
        won_games.plot([i for i in range(0,len(self.games_won))], self.games_won, c="k")
        won_games.set_title("Games won")
        won_games.set_xlabel("Iteration")
        won_games.set_ylabel("Game Won")
        won_games.set_ylim([0, 1])

        file_name = f"{self.image_path}/{iteration}.png"
        self.file_names.append(file_name)
        plt.savefig(file_name)
        plt.close("all")
        
    def export_model(self, iteration):
        export_path = os.path.join(self.model_directory, str(iteration))
        tf.keras.models.save_model(
            self.model,
            export_path,
            overwrite=True,
            include_optimizer=True,
            save_format=None,
            signatures=None,
            options=None
        )