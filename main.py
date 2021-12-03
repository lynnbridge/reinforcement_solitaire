import numpy as np
import pprint
pp = pprint.PrettyPrinter(indent=2)

from solitaire import Game

env = Game()

agent = RandomAgent(env)

for iteration in range(5):
    
    state = env.reset()
    win = False
    
    while not win:
    
        action = agent.act(state)
        next_state, reward, done, _ = env.step(action)
        # agent.learn(state, next_state, action, reward)
        
        state = next_state
        
    env.display()
    
env.close()


    
    