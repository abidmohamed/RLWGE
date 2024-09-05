import numpy as np
import random
import gym
from RWGE import WheatGrowthEnv  # Replace with your actual module
from RWGE_renderer import WheatGrowthRenderer
import pygame
# Initialize your environment
env = WheatGrowthEnv(start_month=1, start_day=1, end_month=12, end_day=31, render_mode='rgb_array')

# Define possible actions
possible_actions = [np.array([action]) for action in np.linspace(0, 10, num=10)]
env.reset()
renderer = WheatGrowthRenderer(env)
# Testing loop
running = True
while running:
    # Select a random action from the possible actions
    action = random.choice(possible_actions)
    observation, reward, done, info = env.step(action)

    # Render the environment
    env.render(mode='rgb_array')

    # Check for Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if done:
        obs = env.reset()

# Close the environment and renderer
env.close()
pygame.quit()