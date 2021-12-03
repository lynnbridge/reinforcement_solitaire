import numpy as np
import pprint
from agents import RandomAgent
pp = pprint.PrettyPrinter(indent=2)

from solitaire import Game

env = Game()

agent = RandomAgent(env)

for iteration in range(1):
    
    state = env.reset()
    done = False
    pp.pprint(env.get_game_elements())
    
    while not done and env.count < 100:
    
        action = agent.act(state)
        next_state, reward, done, _ = env.step(action)
        agent.learn(state, next_state, action, reward)
        
        state = next_state
    print(agent.total_reward)
    pp.pprint(env.get_game_elements())
    
# env.close()


    
    