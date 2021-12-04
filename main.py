import numpy as np
import pprint
from agents import RandomAgent
pp = pprint.PrettyPrinter(indent=2)

from solitaire import Game

env = Game()

agent = RandomAgent(env)

for iteration in range(2):
    
    state = env.reset()
    done = False
    print("New game")
    pp.pprint(env.get_game_elements())
    # env.print_in_order()
    
    while not done and env.count < 500:
        
        action = agent.act(state)
        next_state, reward, done, _ = env.step(action)
        if reward > 0:
            print(action)
        agent.learn(state, next_state, action, reward)
        
        state = next_state
    print(agent.total_reward)
    pp.pprint(env.get_game_elements())
    agent.finalize()
    print("End Game")
    
# env.close()


    
    