import numpy as np
import pygame

class WheatGrowthRenderer:
    def __init__(self, env):
        self.env = env
        pygame.init()
        self.window_width = 800
        self.window_height = 600
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Wheat Growth Environment")
        self.font = pygame.font.SysFont('Arial', 20)  # Choose a font and size
        self.clock = pygame.time.Clock()

    def draw_wheat(self, wheat_height):
      base_x = self.window_width // 2
      base_y = self.window_height
      for i in range(-3, 4):  # Draw multiple curved lines for wheat
          pygame.draw.arc(self.screen, (34, 177, 76), (base_x + i * 5, base_y - wheat_height, 10, wheat_height), np.pi, 2 * np.pi, 3)


    def render(self, action=None):
        self.screen.fill((255, 255, 255))  # Fill background with white

        # Drawing logic
        # Draw wheat plant
        
        # wheat_color = (34, 177, 76)  # Green for wheat plant
        # wheat_width = 50  # Width of the wheat plant
        wheat_height = int(self.window_height * self.env.growth_stage / 13)  # Height based on growth stage
        self.draw_wheat(wheat_height)

        # # Position the wheat plant in the center of the window
        # wheat_x = (self.window_width - wheat_width) // 2
        # wheat_y = self.window_height - wheat_height

        # Draw a rectangle to represent wheat growth stage
        #pygame.draw.rect(self.screen, wheat_color, pygame.Rect(wheat_x, wheat_y, wheat_width, wheat_height))

        # Displaying the date
        date_str = f"Date: {self.env.current_day}-{self.env.current_month}-{self.env.current_year}"
        date_text = self.font.render(date_str, True, (0, 0, 0))  # Black color for text
        self.screen.blit(date_text, (10, 10))  # Position the text on screen

        # Displaying temperature
        temp_str = f"Temp: {self.env.daily_temperature}°C"
        temp_text = self.font.render(temp_str, True, (0, 0, 0))
        self.screen.blit(temp_text, (10, 35))  # Adjust position as needed

        # Displaying the last action (irrigation amount)
        if action is not None:
            action_str = f"Action: {action[0]:.2f}"  # Assuming action is a NumPy array
            action_text = self.font.render(action_str, True, (0, 0, 0))
            self.screen.blit(action_text, (10, 60))  # Adjust position as needed


        # Update display
        pygame.display.flip()
        self.clock.tick(60)  # Limit to 60 frames per second

    def close(self):
        pygame.quit()
