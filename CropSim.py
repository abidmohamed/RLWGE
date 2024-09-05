import random


class WheatGrowthModel:
    def __init__(self):
        self.gdd_accumulated = 0
        self.growth_stages = []


    def calculate_gdd(self, temperature, base_temperature=0):
        """
        Calculate Growing Degree Days (GDD) based on daily temperature.

        Parameters:
        - temperature: Daily temperature in Celsius.
        - base_temperature: Base temperature for GDD calculation (default is 0°C).

        Returns:
        - gdd: Daily Growing Degree Days.
        """
        gdd = max(0, temperature - base_temperature)
        return gdd

    def calculate_water_needs(self, temperature, stage):
        """
        Calculate random water needs based on daily temperature.

        Returns:
        - water_needs: Grass water needs in millimeters. + 10% for wheat
        """
        if temperature < 15:
            base_water_needs = random.uniform(4, 6)
        elif 15 <= temperature <= 25:
            base_water_needs = random.uniform(7, 8)
        else:
            base_water_needs = random.uniform(9, 10)
        # Apply 10% increase for wheat
        water_needs = base_water_needs * 1.1
        
        #print("The Stage: ", stage)
        
        if isinstance(stage, str) and stage == "Done":
            water_needs = 0
        elif 0.5 <= stage <= 6.0:
            # 50% of needed water Early stage
            water_needs = 0.5 * water_needs
        elif 7.0 <= stage <= 10.2:
            # 100% of needed water Mid stage
            water_needs = water_needs
        elif 11.0 <= stage <= 12.0:
            # 25% of needed water late
            water_needs = 0.25 * water_needs

        return water_needs
        

    def simulate_growth(self, data, start_day, start_month):
        """
        Simulate wheat crop growth based on daily temperature.
        Parameters:
        - data: DataFrame with a column 'T2M' representing daily temperatures in Celsius.
        Returns:
        - growth_stages: List of growth stages reached each day.
        """
        filtered_data = filter_data_from_date(start_day, start_month, data)
        for _, row in filtered_data.iterrows():
            temperature = row['T2M']
            daily_gdd = self.calculate_gdd(temperature)
            self.gdd_accumulated += daily_gdd

            # Check growth stages and update
            stage, description, gdd_required, accumulated_gdd = self.get_growth_stage_info()

            # Calculate random water needs
            water_needs = self.calculate_water_needs(temperature)

            # Append growth stage information
            self.growth_stages.append({
                "Day": len(self.growth_stages) + 1,
                "Temperature": temperature,
                "Water Needs": water_needs,
                "Stage": stage,
                "Description": description,
                "GDD Required": gdd_required,
                "Accumulated GDD": accumulated_gdd,
                "Days for Next Stage": self.get_days_for_next_stage(daily_gdd),
                "Duration of Previous Stage": self.get_duration_of_previous_stage(),
            })

            if stage == "Done":
              break

        return self.growth_stages

    def get_growth_stage_info(self, gdd_accumulated):
        """
        Get information about the current growth stage based on accumulated GDD.

        Returns:
        - stage: Growth stage.
        - description: Description of the growth stage.
        - gdd_required: GDD required for the current stage.
        - accumulated_gdd: Total accumulated GDD.
        """
        if gdd_accumulated < 180:
            stage, description, gdd_required = 0.5, "Emergence Date", 180
        elif gdd_accumulated < 252:
            stage, description, gdd_required = 1.0, "Leaf 1 fully extended", 72
        elif gdd_accumulated < 395:
            stage, description, gdd_required = 2.0, "Leaf 2 fully extended", 143
        elif gdd_accumulated < 538:
            stage, description, gdd_required = 3.0, "Leaf 3 (Tillers Begin To Emerge)", 143
        elif gdd_accumulated < 681:
            stage, description, gdd_required = 4.0, "Leaf 4 fully extended", 143
        elif gdd_accumulated < 824:
            stage, description, gdd_required = 5.0, "Leaf 5 (Tillering ends)", 143
        elif gdd_accumulated < 967:
            stage, description, gdd_required = 6.0, "Leaf 6 (Tillering ends)", 143
        elif gdd_accumulated < 1110:
            stage, description, gdd_required = 7.0, "Leaf 7 fully extended", 143
        elif gdd_accumulated < 1181:
            stage, description, gdd_required = 7.5, "Flag Leaf Visible", 71
        elif gdd_accumulated < 1255:
            stage, description, gdd_required = 8.0, "Flag Leaf Emerged", 72
        elif gdd_accumulated < 1396:
            stage, description, gdd_required = 9.0, "Boot Swelling Begins", 143
        elif gdd_accumulated < 1539:
            stage, description, gdd_required = 10.0, "Boot Completed", 143
        elif gdd_accumulated < 1567:
            stage, description, gdd_required = 10.2, "Heading Begins", 28
        elif gdd_accumulated < 1682:
            stage, description, gdd_required = 11.0, "Headed (Head Extension Begins)", 115
        elif gdd_accumulated < 1739:
            stage, description, gdd_required = 11.4, "Flowering Begins", 57
        elif gdd_accumulated < 1768:
            stage, description, gdd_required = 11.6, "Flowering Completed", 29
        elif gdd_accumulated < 1825:
            stage, description, gdd_required = 12.0, "Kernel Watery Ripe", 57
        else:
            stage, description, gdd_required = "Done", "Crop Growth Complete", 0

        return stage, description, gdd_required, self.gdd_accumulated

    def get_days_for_next_stage(self, daily_gdd):
        """
        Get the estimated number of days required to reach the next growth stage.

        Returns:
        - days_for_next_stage: Estimated days required for the next stage.
        """
        next_stage_info = self.get_growth_stage_info()
        next_stage_gdd_required = next_stage_info[2]
        return next_stage_gdd_required / max(1, daily_gdd)

    def get_duration_of_previous_stage(self):
        """
        Get the duration of the previous growth stage.

        Returns:
        - duration_of_previous_stage: Duration of the previous stage.
        """
        if len(self.growth_stages) > 1:
            previous_stage_info = self.growth_stages[0]
            return len(self.growth_stages) - previous_stage_info["Day"] + 1
        else:
            return 0

    def get_kc(self, stage):
          if isinstance(stage, str) and stage == "Done":
              # late stage Kc
              return random.uniform(0.2, 0.5)  
          else:
            if 0.5 <= stage <= 6.0:
              # Early stage Kc
              return random.uniform(0.2, 0.53)
            elif 7.0 <= stage <= 10.2:
              # Mid stage Kc
              return random.uniform(0.45, 1.03)
            else:
              # late stage Kc
              return random.uniform(0.2, 0.5)
      
    # Add the following method to get ETc (crop evapotranspiration)
    def _get_etc(self, stage, et0):
        et_c = self.get_kc(stage) * et0
        return et_c

class CropSim:
  def __init__(self):
      pass

  def crop_type(self, crop, temperature, ):
    # 5 types 1- -30% less than grass,2- -10% less, 3-Same as grass
    # 4- more 10% than grass, 5- 20% more than grass
    # - concetration on wheat 10% more
    if crop==1:
      #name = "Wheat"
      name = 1
      water_need = 0

    return name, water_need
  
  
  def calculate_water_effect_on_yield(self, harvest, excess_water, water_deficit):

      """
      Calculate the combined effect of water excess and water deficit on yield.

      Args:
      - excess_water (float): Excess water level (0 to n).
      - water_deficit (float): Water deficit level (0 to n).

      Returns:
      - yield_effect (float): Combined effect on yield (0 to 100).
      """

      # Assuming each 0.01 unit increase in excess or deficit results in a 1% drop in yield
      excess_effect = 0.1 * (excess_water / 0.1 )
      deficit_effect = 0.1 * (water_deficit / 0.1)
      
#       excess_effect = 0.1 * (excess_water / 1.1 )
#       deficit_effect = 0.1 * (water_deficit / 1.1)

      # Calculate the combined effect on yield
      yield_effect = max(0, harvest - excess_effect - deficit_effect)

      return yield_effect
  
  def determine_disease_type(self, accumulated_scarcity, accumulated_excess):
    """
    Determine the type of disease based on water conditions.
    Parameters:
    - accumulated_scarcity: A measure of accumulated water scarcity.
    - accumulated_excess: A measure of accumulated water excess.

    Returns:
    - disease_type: The type of disease based on water conditions.
                    Possible values: 'FHB', 'LeafBlotch', 'PowderyMildew', 'Rust', 'NoDisease'.
    """
    # Define disease-specific thresholds based on the provided table
    disease_thresholds = {
        'FHB': {'scarcity': (300, 350), 'excess': (600, 650)},
        'LeafBlotch': {'scarcity': (250, 300), 'excess': (550, 600)},
        'PowderyMildew': {'scarcity': (200, 250), 'excess': (500, 550)},
        'Rust': {'scarcity': (200, 250), 'excess': (450, 500)},
    }

    # Evaluate water conditions and determine the disease type
    for disease, thresholds in disease_thresholds.items():
        scarcity_threshold = thresholds['scarcity']
        excess_threshold = thresholds['excess']

        if (
            accumulated_scarcity >= scarcity_threshold[0] and accumulated_scarcity <= scarcity_threshold[1] and
            accumulated_excess >= excess_threshold[0] and accumulated_excess <= excess_threshold[1]
        ):
            return disease

    # If no disease conditions are met, return 'NoDisease'
    return 'NoDisease'
  
  def disease_control(self, accumulated_scarcity, accumulated_excess, disease):
      """
      Implement a function for wheat disease control based on water conditions and specific disease thresholds.

      Parameters:
      - accumulated_scarcity: A measure of accumulated water scarcity.
      - accumulated_excess: A measure of accumulated water excess.
      - disease: The type of disease affecting the wheat crop.

      Returns:
      - control_action: A control action indicating the recommended disease control measure.
                        For example, 'irrigate', 'reduce_irrigation', 'apply_fungicide', 'no_action', etc.
      """

      # Define disease-specific thresholds based on the provided table
      disease_thresholds = {
          'FHB': {'scarcity': (300, 350), 'excess': (600, 650)},
          'LeafBlotch': {'scarcity': (250, 300), 'excess': (550, 600)},
          'PowderyMildew': {'scarcity': (200, 250), 'excess': (500, 550)},
          'Rust': {'scarcity': (200, 250), 'excess': (450, 500)},
      }

      if disease == 'NoDisease':
        return 'no_action'

      # Get the threshold values for the specified disease
      scarcity_threshold = disease_thresholds[disease]['scarcity']
      excess_threshold = disease_thresholds[disease]['excess']

      # Evaluate water conditions and recommend disease control measures
      if accumulated_scarcity < scarcity_threshold[0]:
          control_action = 'irrigate'  # Increase irrigation in case of water scarcity
      elif accumulated_excess > excess_threshold[1]:
          control_action = 'reduce_irrigation'  # Reduce irrigation in case of water excess
      else:
          control_action = 'no_action'  # No specific action needed

      return control_action
  
  def is_crop_sick(self, accumulated_scarcity, accumulated_excess, disease):
      """
      Check if the crop is sick based on water conditions and specific disease thresholds.

      Parameters:
      - accumulated_scarcity: A measure of accumulated water scarcity.
      - accumulated_excess: A measure of accumulated water excess.
      - disease: The type of disease affecting the wheat crop.

      Returns:
      - True if the crop is considered sick, False otherwise.
      """

      # Use the disease control function to get the recommended control action
      control_action = self.disease_control(accumulated_scarcity, accumulated_excess, disease)

      # Check if the recommended action implies that the crop is sick
      return control_action != 'no_action'

#   def irrigation_amount(self, water_needs, rain_quantity, evaporation, num_days):
#     # season days 90 day
#     planting_season = num_days
        
#     # calculating effective rain
#     if rain_quantity > 10:
#       pe = (rain_quantity-5) * 0.75
#       daily_irrigation = water_needs - pe
#     else:
#       daily_irrigation = water_needs
#     # calculate irrigation based on growing stage
#     # Day 0 - 28 initial stage => irrigation 50%
#     if planting_season <= 28:
#       daily_irrigation = daily_irrigation * 0.5
#     # Day 28 - 49 Crop Development & mid-season => irrigation 100%
#     if planting_season > 28 and planting_season <= 49:
#       daily_irrigation = daily_irrigation
#     # Day 49 - 90 or more Late season => Irrigation 25%
#     if planting_season > 49:
#       daily_irrigation = daily_irrigation * 0.25

#     return daily_irrigation
  
#   def crop_state(self, daily_irrigation, water_got):
    # getting less water
    #diff = water_got - daily_irrigation
    #print("Daily irrigation", daily_irrigation)
    #print("Water Got", water_got)
    #print("Diff", diff)
    #return diff