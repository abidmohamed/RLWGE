import gym
import gym.utils.seeding
from gym import spaces
import numpy as np
from IPython.display import clear_output, display
import time
from WeatherSim import WeatherSim
from CropSim import CropSim, WheatGrowthModel
from DateSim import DateSIM
from SoilSim import SoilSim
from RWGE_renderer import WheatGrowthRenderer
import torch

class WheatGrowthEnv(gym.Env):
  def __init__(self, start_month, start_day, end_month, end_day, render_mode='human'):
    super(WheatGrowthEnv).__init__()
    # self.render_mode = render_mode
    # self.renderer = WheatGrowthRenderer(self)
    
    # Initialize instances of CropSim and WeatherSim
    self.crop_sim = CropSim()
    self.wheat_growth = WheatGrowthModel()
    self.weather_sim = WeatherSim()
    self.date_sim = DateSIM(start_day, start_month, 0)
    self.soil_sim = SoilSim()

    # Define action space (irrigation amount)
    self.action_space = spaces.Box(low=0, high=11, shape=(1,), dtype=float)

    # Define observation space
    self.observation_space = spaces.Dict({
            "current_day": spaces.Discrete(365),
            "current_month": spaces.Discrete(12),
            "current_month_day": spaces.Discrete(31),
            "current_year": spaces.Discrete(3000),
            "daily_temperature": spaces.Box(low=0, high=50, shape=(1,), dtype=np.float32),
            "growth_stage": spaces.Box(low=0, high=13, shape=(1,), dtype=np.float32),
            "accumulated_gdd": spaces.Box(low=0, high=3000, shape=(1,), dtype=np.float32),
            "accumulated_scarcity": spaces.Box(low=0, high=1000, shape=(1,), dtype=np.float32),
            "accumulated_excess": spaces.Box(low=0, high=1000, shape=(1,), dtype=np.float32),
            "soil_moisture_content": spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32),
            "water_needs": spaces.Box(low=0, high=11, shape=(1,), dtype=np.float32),
            "etc": spaces.Box(low=0, high=2, shape=(1,), dtype=np.float32),
            "rainfall": spaces.Box(low=0, high=11, shape=(1,), dtype=np.float32),
            "harvest": spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32),
            "humidity": spaces.Box(low=0, high=100, shape=(1,), dtype=np.float32),
            "is_raining": spaces.Discrete(2),
            "sky_clearness": spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
            "is_cloudy": spaces.Discrete(2),
            "rn_daily": spaces.Box(low=0, high=1, shape=(1,), dtype=np.float32),
            "qv2m": spaces.Box(low=0, high=11, shape=(1,), dtype=np.float32),
            "PS": spaces.Box(low=0, high=11, shape=(1,), dtype=np.float32),
            "wind_speed": spaces.Box(low=0, high=11, shape=(1,), dtype=np.float32),
            "is_crop_sick": spaces.Discrete(2),

        })
    
    # Initialize state variables
    self.current_day = 0
    self.current_month_day = start_day
    self.current_month = start_month
    self.current_year = 2015  # You can set the initial year as needed
    self.daily_temperature = 0.0
    self.growth_stage = 0.0
    self.accumulated_gdd = 0
    self.accumulated_excess = 0
    self.accumulated_scarcity = 0
    self.soil_moisture_content = 0
    self.irrigation_amount = 0
    self.water_needs = 0
    self.harvest = 100
    self.etc = 0
    self.et0 = 0.0
    self.rainfall = 0
    self.humidity = 0
    self.is_raining = 0
    self.sky_clearness = 0
    self.is_cloudy = 0
    self.rn_daily = 0
    self.qv2m = 0
    self.PS = 0
    self.wind_speed = 0
    self.is_crop_sick = 0
    self.is_success = False

    # Start and end dates
    self.start_month = start_month
    self.start_day = start_day
    self.end_month = end_month
    self.end_day = end_day

  def seed(self, seed=None):
      self.np_random, seed = gym.utils.seeding.np_random(seed)
      return [seed]

  def reset(self):
    
    # Initialize state variables
    self.current_day = 0
    self.is_leap = 0
    self.current_month_day = self.start_day
    self.current_month = self.start_month
    self.current_year = 2015  # You can set the initial year as needed
    self.daily_temperature = 0.0
    self.growth_stage = 0.0
    self.accumulated_gdd = 0
    self.accumulated_excess = 0
    self.accumulated_scarcity = 0
    self.soil_moisture_content = 0
    self.irrigation_amount = 0
    self.water_needs = 0
    self.harvest = 100
    self.etc = 0
    self.rainfall = 0
    self.humidity = 0
    self.is_raining = 0
    self.sky_clearness = 0
    self.is_cloudy = 0
    self.rn_daily = 0
    self.qv2m = 0
    self.PS = 0
    self.wind_speed = 0
    self.is_crop_sick = 0
    self.is_success = False
    self.current_day = 1
    
    # Return initial observation
    return self._get_observation()
  
  def _simulate_growth(self, action):
    # Get Weather related values
    self.daily_temperature,self.humidity, self.wind_speed, self.is_raining, self.rainfall, self.sky_clearness, self.is_cloudy, self.et0, self.rn_daily, self.qv2m, self.PS, es, ea, delta, G,gamma  = self.weather_sim.sim_weather(self.current_month)
    # Get Crop Related Values
    daily_gdd = self.wheat_growth.calculate_gdd(self.daily_temperature)
    self.accumulated_gdd += daily_gdd
    
    
    stage_info, description, gdd_required, self.gdd_accumulated = self.wheat_growth.get_growth_stage_info(self.accumulated_gdd)
    self.growth_stage = stage_info
    # print("--------------------Growth STAGE -----------------", self.growth_stage)
    self.etc = self.wheat_growth._get_etc(self.growth_stage, self.et0)

    self.water_needs = self.wheat_growth.calculate_water_needs(self.daily_temperature, self.growth_stage)
    
    self.water_needs += self.etc
    
    # Get soil Related values
    self.soil_moisture_content += self.soil_sim.get_surface_soil_wetness(self.current_month)

    # add Action
    self.soil_moisture_content += action

    # get water needs
    self.soil_moisture_content -= self.water_needs

    # Calculate water excess and deficit
    water_deficit = min(0, self.soil_moisture_content)
    water_excess = max(0, self.soil_moisture_content)

    self.accumulated_scarcity += water_deficit * -1
    self.accumulated_excess += water_excess

    # Check water usage effect on harvest and update it
    self.harvest = self.crop_sim.calculate_water_effect_on_yield(self.harvest, self.accumulated_excess, self.accumulated_scarcity)

    # Check diseases
    disease_type = self.crop_sim.determine_disease_type(self.accumulated_scarcity, self.accumulated_excess)
    
    if self.crop_sim.is_crop_sick(self.accumulated_scarcity, self.accumulated_excess, disease_type):
      self.is_crop_sick = 1
    else:
      self.is_crop_sick = 0
    
    # update date
    self.current_month, self.current_day, self.is_leap = self.date_sim._update_month_and_day(self.is_leap, self.current_month, self.current_day)
    

  def step(self, action):
    done = False
    # Call simulate_growth Function
    self._simulate_growth(action)
    # Call render with the action
    if self.render_mode == 'rgb_array':
        self.renderer.render(action)
    # Return observation, reward, done, and info
    observation = self._get_observation()
    # Action represents the irrigation amount
    reward = self._calculate_reward(action, self.water_needs, self.soil_moisture_content)
    #done = self.growth_stage >= 12 or self.harvest < 30
    # Additional check to prevent premature episode termination
    if isinstance(self.growth_stage, str) and self.growth_stage == "Done" or self.growth_stage >= 12 and self.harvest >= 30:
        done = True  # End episode only if both conditions are met
    elif isinstance(self.growth_stage, str) and self.growth_stage == "Done" or self.growth_stage >= 12:
        # Adjust harvest threshold to prevent premature termination
        done = self.harvest < 10  # Ensure harvest doesn't fall too low before episode ends
    elif self.harvest < 30:
        # Adjust growth stage threshold to prevent premature termination
        done = self.growth_stage >= 3  # Allow some progress before ending due to low harvest
        #done = self.harvest < 10  # Ensure harvest doesn't fall too low before episode ends


    if done:
         if isinstance(self.growth_stage, str) and self.growth_stage == "Done" or self.growth_stage >= 12 and self.harvest > 30 and self.growth_stage != 0: 
                self.is_success = True

    info = {
       "is_success": self.is_success,
       "termination_reason": "Growth stage reached 12 and harvest >= 30" if isinstance(self.growth_stage, str) and self.growth_stage == "Done" or self.growth_stage >= 12 and self.harvest >= 30
                              else "Harvest fell below 10 before growth stage reached 12" if isinstance(self.growth_stage, str) and self.growth_stage == "Done" or self.growth_stage >= 12
                                   else "Growth stage reached 5 before harvest fell below 30",  # Provide appropriate termination reason
    }  # Any additional diagnostic information


    return observation, reward, done, info 


  # def _get_observation(self):
  #   # Assuming all your attributes (self.current_day, self.daily_temperature, etc.) are either
  #   # scalars or arrays that can be directly converted to tensors.

  #   # Create a list of all observation components
  #   obs_components = [
  #       self.current_day,
  #       self.current_month,
  #       self.current_month_day,
  #       self.current_year,
  #       self.daily_temperature,
  #       self.growth_stage,
  #       self.accumulated_gdd,
  #       self.accumulated_scarcity,
  #       self.accumulated_excess,
  #       self.soil_moisture_content,
  #       self.water_needs,
  #       self.etc,
  #       self.rainfall,
  #       self.harvest,
  #       self.humidity,
  #       self.is_raining,
  #       self.sky_clearness,
  #       self.is_cloudy,
  #       self.rn_daily,
  #       self.qv2m,
  #       self.PS,
  #       self.wind_speed,
  #       self.is_crop_sick,
  #   ]

  #   # Convert each component to a tensor and flatten if necessary
  #   tensor_components = [torch.tensor([item]).float() if isinstance(item, (int, float)) else torch.tensor(item).float() for item in obs_components]

  #   # Concatenate all components into a single tensor
  #   observation_tensor = torch.cat(tensor_components).view(1, -1)  # Reshape to 1 x N tensor

  #   # Assuming 'device' is defined in your environment 
  #   self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
  #   observation_tensor = observation_tensor.to(self.device)  # Move tensor to the correct device

  #   return observation_tensor


  def _get_observation(self):
    # Return current state variables as observation
    return {
        "current_day": self.current_day,
        "current_month": self.current_month,
        "current_month_day": self.current_month_day,
        "current_year": self.current_year,
        "daily_temperature": self.daily_temperature,
        "growth_stage": self.growth_stage,
        "accumulated_gdd": self.accumulated_gdd,
        "accumulated_scarcity": self.accumulated_scarcity,
        "accumulated_excess": self.accumulated_excess,
        "soil_moisture_content": self.soil_moisture_content,
        "water_needs": self.water_needs,
        "etc": self.etc,
        "rainfall": self.rainfall,
        "harvest": self.harvest,
        "humidity": self.humidity,
        "is_raining": self.is_raining,
        "sky_clearness": self.sky_clearness,
        "is_cloudy": self.is_cloudy,
        "rn_daily": self.rn_daily,
        "qv2m": self.qv2m,
        "PS": self.PS,
        "wind_speed": self.wind_speed,
        "is_crop_sick": self.is_crop_sick
    }


  def _calculate_yield_reward(self):
#       # Define thresholds for full reward, half reward, and penalty
#       full_reward_threshold = 80
#       half_reward_threshold = 50

#       # Calculate yield reward based on thresholds
#       if self.harvest >= full_reward_threshold:
#           yield_reward = 1.0  # Full reward
#       elif half_reward_threshold <= self.harvest < full_reward_threshold:
#           yield_reward = 0.5  # Half reward
#       else:
#           # Penalize for yield below 50%
#           yield_reward = -0.5  # You can adjust the penalty value

#       return yield_reward
        # Smoother reward function based on harvest percentage
#         max_harvest = 100  # Assume 100% is the maximum possible yield
#         yield_reward = (self.harvest / max_harvest) * 2 - 1  # Normalize to [-1, 1]
#         return yield_reward
        if self.harvest >= 30:
            yield_reward = 1  # Full reward if harvest is not below 30%
        else:
            yield_reward = -1  # Penalty if harvest is below 30%
        return yield_reward


  def _calculate_water_use_penalty(self, irrigation, water_needs):
    # Penalize excessive irrigation more severely
#     if irrigation > water_needs:
#         excess_irrigation = irrigation - water_needs
#         penalty = 1 + excess_irrigation * 0.1  # Increase penalty proportionally to excess irrigation
#         return -penalty
    
#     elif irrigation < water_needs:
#         return -0.5  # Less penalty for under-irrigation
#     else:
#         return 1  # Full reward for exact irrigation
        
#         if irrigation > water_needs:
#             excess_irrigation = irrigation - water_needs
#             penalty = -1 - excess_irrigation * 0.1  # Proportional penalty
#         elif irrigation < water_needs:
#             penalty = -0.5  # Less penalty for under-irrigation
#         else:
#             penalty = 1  # Reward for exact irrigation
#         return penalty
        if irrigation == water_needs:
            penalty = 1  # Full reward for exact irrigation
        elif irrigation < water_needs:
            scarcity_irrigation = water_needs - irrigation
            penalty = -1 - scarcity_irrigation * 0.1  # Penalty for under-irrigation
        else:
            excess_irrigation = irrigation - water_needs
            penalty = -1 - excess_irrigation * 0.1  # Proportional penalty for over-irrigation
        return penalty
    
    
  def _calculate_soil_moisture_penalty(self):#, soil_moisture_content):
    
    # Penalize if soil moisture content falls below a certain threshold
#     if soil_moisture_content < 5:  # Adjust the threshold as needed
#         return -0.5  # Apply a penalty if soil moisture is too low
#     else:
#         return 1  # No penalty if soil moisture is above threshold
    # Smoother penalty function for soil moisture content
#     optimal_moisture = 2  # Adjust as needed
#     if soil_moisture_content < optimal_moisture:
#         penalty = (soil_moisture_content / optimal_moisture) * 2 - 1  # Normalize to [-1, 1]
#     else:
#         penalty = 1  # No penalty if soil moisture is above the optimal threshold
#     return penalty
        if self.soil_moisture_content <= 2:
            penalty = 1  # No penalty if soil moisture is within the threshold
        else:
            penalty = -1  # Penalty if soil moisture exceeds the threshold
        return penalty
    
  
  def _calculate_reward(self, irrigation, water_needs, soil_moisture_content):
#     # Implement reward calculation
#     # yield reward calculation
#     yield_reward = self._calculate_yield_reward()
#     # Placeholder for water use penalty calculation
#     water_use_penalty = self._calculate_water_use_penalty(irrigation, water_needs)

#     # Placeholder for soil moisture penalty calculation
#     soil_moisture_penalty = self._calculate_soil_moisture_penalty(soil_moisture_content)
    
#     if isinstance(self.growth_stage, str) and self.growth_stage == "Done":
#         total_reward = 0.6 * yield_reward + 0.2 * water_use_penalty + 0.2 * soil_moisture_penalty + 13
#     elif self.harvest == 0:
#         total_reward = 0.8 * water_use_penalty + 0.1 * soil_moisture_penalty + self.growth_stage
#     else:
#         # Combine rewards and penalties with appropriate weights or factors
#         total_reward = 0.1 * yield_reward + 0.8 * water_use_penalty + 0.1 * soil_moisture_penalty + self.growth_stage #+ self.growth_stage - 12
      
#     if irrigation == 0:
#         total_reward = total_reward - 13
        

#     return total_reward
    # Yield reward calculation
#     yield_reward = self._calculate_yield_reward()
    
#     # Water use penalty calculation
#     water_use_penalty = self._calculate_water_use_penalty(irrigation, water_needs)

#     # Soil moisture penalty calculation
#     soil_moisture_penalty = self._calculate_soil_moisture_penalty(soil_moisture_content)

#     # Normalize growth stage to [0, 1] if needed
#     max_growth_stage = 13  # Assume 13 is the maximum growth stage
#     normalized_growth_stage = self.growth_stage / max_growth_stage

#     # Adjust weights based on growth stage or other factors
#     if isinstance(self.growth_stage, str) and self.growth_stage == "Done":
#         total_reward = 0.6 * yield_reward + 0.2 * water_use_penalty + 0.2 * soil_moisture_penalty + 1
#     elif self.harvest == 0:
#         total_reward = 0.8 * water_use_penalty + 0.1 * soil_moisture_penalty + normalized_growth_stage
#     else:
#         intermediate_reward = 0.8 * water_use_penalty + 0.2 * soil_moisture_penalty
#         total_reward = 0.1 * yield_reward + 0.8 * intermediate_reward + 0.1 * (intermediate_reward / max_growth_stage)

#         #total_reward = 0.1 * yield_reward + 0.8 * water_use_penalty + 0.1 * soil_moisture_penalty + normalized_growth_stage

#     # Additional penalty if no irrigation
# #     if irrigation == 0:
# #         total_reward -= 1

#     return total_reward

    # Yield reward calculation
        yield_reward = self._calculate_yield_reward()
        
        # Water use penalty calculation
        water_use_penalty = self._calculate_water_use_penalty(irrigation, water_needs)

        # Soil moisture penalty calculation
        soil_moisture_penalty = self._calculate_soil_moisture_penalty()

        # Combine rewards and penalties
        total_reward = 0.4 * yield_reward + 0.4 * water_use_penalty + 0.2 * soil_moisture_penalty

        return total_reward
  
  def render(self, mode='human'):
    if self.render_mode == 'human':
        output = (f"Day: {self.current_day}, Month: {self.current_month}\n"
              f"Temperature: {self.daily_temperature}°C, Humidity: {self.humidity}%\n"
              f"Growth Stage: {self.growth_stage}, Soil Moisture: {self.soil_moisture_content}\n"
              f"Water Excess: {self.accumulated_excess}, Water Scarcity: {self.accumulated_scarcity}\n"
              f"Harvest: {self.harvest}, Is Crop Sick: {'Yes' if self.is_crop_sick else 'No'}\n")
        print(output)
        time.sleep(0.5)  # To slow down the loop for visibility
    elif self.render_mode == 'rgb_array':
        # Logic for rgb_array mode if needed
        return self.renderer.render()
    else:
        raise NotImplementedError(f"Render mode {self.render_mode} not implemented")
