import numpy as np
import pprint
from agents import RandomAgent, DeepQNetwork
pp = pprint.PrettyPrinter(indent=2)

from solitaire import Game

env = Game()

# agent = RandomAgent(env)
agent = DeepQNetwork(env)


for iteration in range(20000):
    
    state = env.reset()
    done = False
    print("Iteration", iteration)
    # pp.pprint(env.get_game_elements())
    # env.print_in_order()
    
    while not done and env.count < 300:
        
        action = agent.act(state)
        next_state, reward, done, _ = env.step(action)
        agent.learn(state, next_state, action, reward, done)
        
        state = next_state
    # print(agent.total_reward)
    if done:
        agent.games_won.append(1)
    else:
        agent.games_won.append(0)
    if iteration % 250 == 0:
        pp.pprint(env.get_game_elements())
    agent.finalize(iteration)
    # print("End Game")
    
# env.close()


    
    