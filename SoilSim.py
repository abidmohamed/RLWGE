import numpy as np
import pandas as pd


class SoilSim:
  
  def __init__(self, *args, **kwargs):
    pass

  def get_surface_soil_wetness(self, month):
    file_path = "meteorological_data_statistics.csv"
    weather_stats_df = pd.read_csv(file_path)
    # Extract the row for the given month
    month_stats = weather_stats_df[weather_stats_df['Month'] == month]

    # Check if month_stats is not empty
    if month_stats.empty:
        raise ValueError(f"No data available for month {month}")
    
    mean_surface_moister = month_stats['GWETTOP_Mean'].iloc[0]
    std_dev_surface_moister = month_stats['GWETTOP_StdDev'].iloc[0]
    surface_moister = round(np.random.normal(mean_surface_moister, std_dev_surface_moister), 2)

    return surface_moister

  
  def get_premeability(texture):
    # Textures 1 Sand 2 loamy 3 sandy loam 4 silty loam
    if texture == 1:
      return 0.000176
    if texture == 2:
      return 0.000156
    if texture == 3:
      return 0.0000345
    if texture == 4:
      return 0.00000719

    