import math
import random

from numpy import random as rand
import numpy as np
import pandas as pd

class WeatherSim:

  def calculate_es(self, T):
      """Calculate saturation vapor pressure."""
      result = 0.6108 * np.exp((17.27 * T) / (T + 237.3))
      return round(result, 2)

  def calculate_ea(self, es, RH2M):
      """Calculate actual vapor pressure."""
      result = (RH2M/100) * es
      return round(result, 2)

  def calculate_slope_curve(self, T, es):
    """Calculate the slope of the saturation vapor pressure curve."""
    result = (4098 * es) / ((T + 237.3) ** 2)
    return round(result, 2)
  
  # Function to calculate specific humidity (q) from QV2M
  def calculate_specific_humidity(self, QV2M):
      """
      QV2M: Specific humidity at 2 meters
      """
      # Avoid division by zero
      if 1 - QV2M == 0:
          return QV2M
      else:
          return QV2M / (1 - QV2M)

  # Function to calculate specific heat at constant pressure (c_p)
  def calculate_specific_heat(self, T, q):
      # Constants
      c_pd = 1005  # Specific heat of dry air at constant pressure (J/(kg·°C))
      R_v = 461    # Specific gas constant for water vapor (J/(kg·°C))
      return c_pd + (q * R_v / T)

  def calculate_ps(self, c_p, PS):
      """Calculate the psychrometric constant.
      PS: surface pressure (Kpa)
      """
      result = 0.00163 * PS / c_p
      return result

    # NET RADIATION OF THE MONTH 22 Year Climatology Average From : https://power.larc.nasa.gov/data-access-viewer/
    # January: 3.71 kWh/m2/day×3.6 MJ/kWh=13.356 MJ/m2/day3.71kWh/m2/day×3.6MJ/kWh=13.356MJ/m2/day
    # February: 5.62 kWh/m2/day×3.6 MJ/kWh=20.232 MJ/m2/day5.62kWh/m2/day×3.6MJ/kWh=20.232MJ/m2/day
    # March: 6.58 kWh/m2/day×3.6 MJ/kWh=23.688 MJ/m2/day6.58kWh/m2/day×3.6MJ/kWh=23.688MJ/m2/day
    # April: 8.02 kWh/m2/day×3.6 MJ/kWh=28.872 MJ/m2/day8.02kWh/m2/day×3.6MJ/kWh=28.872MJ/m2/day
    # May: 7.71 kWh/m2/day×3.6 MJ/kWh=27.756 MJ/m2/day7.71kWh/m2/day×3.6MJ/kWh=27.756MJ/m2/day
    # June: 8.3 kWh/m2/day×3.6 MJ/kWh=29.88 MJ/m2/day8.3kWh/m2/day×3.6MJ/kWh=29.88MJ/m2/day
    # July: 8.49 kWh/m2/day×3.6 MJ/kWh=30.564 MJ/m2/day8.49kWh/m2/day×3.6MJ/kWh=30.564MJ/m2/day
    # August: 8.45 kWh/m2/day×3.6 MJ/kWh=30.42 MJ/m2/day8.45kWh/m2/day×3.6MJ/kWh=30.42MJ/m2/day
    # September: 6.89 kWh/m2/day×3.6 MJ/kWh=24.804 MJ/m2/day6.89kWh/m2/day×3.6MJ/kWh=24.804MJ/m2/day
    # October: 5.12 kWh/m2/day×3.6 MJ/kWh=18.432 MJ/m2/day5.12kWh/m2/day×3.6MJ/kWh=18.432MJ/m2/day
    # November: 3.92 kWh/m2/day×3.6 MJ/kWh=14.112 MJ/m2/day3.92kWh/m2/day×3.6MJ/kWh=14.112MJ/m2/day
    # December: 3.23 kWh/m2/day×3.6 MJ/kWh=11.628 MJ/m2/day3.23kWh/m2/day×3.6MJ/kWh=11.628MJ/m2/day

  def distribute_net_radiation_sici(sici, Rn_monthly, days_in_month):
    """
    Distribute Net Radiation based on Sky Insolation Clearness Index (SICI).

    Parameters:
    - sici: Sky Insolation Clearness Index
    - Rn_monthly: Monthly Total Net Radiation
    - days_in_month: Number of days in the month

    Returns:
    - Rn_daily: Estimated Daily Net Radiation
    """

    # Calculate Rn_daily using SICI
    Rn_daily = sici * (Rn_monthly / days_in_month)

    return Rn_daily

  def calculate_soil_heat_flux(self, net_radiation):
    # The value of α can vary depending on the soil type, 
    # land cover, and other environmental factors. Typically, 
    # it falls in the range of 0.1 to 0.3. This fraction is 
    # essentially an empirical coefficient that captures 
    # the efficiency with which the soil conducts heat 
    # compared to the total incoming radiation.
    # Generate a random fraction alpha between 0.1 and 0.3
    alpha = random.uniform(0.1, 0.3)
    
    # Calculate soil heat flux density (G)
    soil_heat_flux = alpha * net_radiation
    
    return soil_heat_flux

  def penman_monteith(R_n, G, T, u2, es, ea, delta, gamma):
      """Calculate reference evapotranspiration (ET0)."""
      numerator = 0.408 * delta * (R_n - G) + gamma * (900 / (T + 273)) * u2 * (es - ea)
      denominator = delta + gamma * (1 + 0.34 * u2)
      return numerator / denominator

  # Provided parameters
  T2M = 25.0  # Air temperature at 2 meters (°C)
  RH2M = 50.0  # Relative humidity at 2 meters (%)
  QV2M = 8.0  # Specific humidity at 2 meters (g/kg)
  PS = 101.3  # Surface pressure (kPa)
  WS2M = 3.0  # Wind speed at 2 meters (m/s)
  c_p = 1.013  # Specific heat of air at constant pressure (kJ/kg°C)

# # Calculate ET0
# et0 = penman_monteith(R_n, G, T2M, WS2M, es, ea, delta, gamma)

# print(f"Reference Evapotranspiration (ET0): {et0:.2f} mm/day")

  def calculate_slope_saturation_vapor_pressure_curve(T):
    """
    Calculate the slope of the saturation vapor pressure curve (delta).

    Parameters:
    - T: Air temperature in degrees Celsius.

    Returns:
    - Delta: Slope of the saturation vapor pressure curve in kPa/°C.
    """
    delta = (4098 * (0.6108 * math.exp((17.27 * T) / (T + 237.3)))) / ((T + 237.3) ** 2)
    return delta

# Example usage:
# temperature = 25  # Example temperature in degrees Celsius
# delta_result = calculate_slope_saturation_vapor_pressure_curve(temperature)
# print(f"Slope of Saturation Vapor Pressure Curve (Delta): {delta_result:.6f} kPa/°C")

  def calculate_et0(self, delta, Rn, G, gamma, T, u2, es, ea):
    """
    Calculate reference evapotranspiration (ET0) using the Penman-Monteith equation.

    Parameters:
    - delta: Slope of the saturation vapor pressure curve (kPa/°C)
    - Rn: Net radiation at the crop surface (MJ/m^2/day)
    - G: Soil heat flux density (MJ/m^2/day)
    - gamma: Psychrometric constant (kPa/°C)
    - T: Air temperature at 2 meters above the crop surface (°C)
    - u2: Wind speed at 2 meters above the crop surface (m/s)
    - es: Saturation vapor pressure (kPa)
    - ea: Actual vapor pressure (kPa)

    Returns:
    - ET0: Reference evapotranspiration (mm/day)
    """
    ET0 = 0.408 * delta * (Rn - G) + gamma * (900 / (T + 273)) * u2 * (es - ea) / (delta + gamma * (1 + 0.34 * u2))
    return ET0

# Example usage:
# delta = 0.409  # Example value for delta (slope of saturation vapor pressure curve)
# Rn = 12.5      # Example value for net radiation (MJ/m^2/day)
# G = 0.1        # Example value for soil heat flux density (MJ/m^2/day)
# gamma = 0.066  # Example value for psychrometric constant (kPa/°C)
# T = 25         # Example value for air temperature (°C)
# u2 = 2         # Example value for wind speed at 2 meters (m/s)
# es = 2.6       # Example value for saturation vapor pressure (kPa)
# ea = 1.2       # Example value for actual vapor pressure (kPa)

# ET0_result = calculate_et0(delta, Rn, G, gamma, T, u2, es, ea)
# print(f"Reference Evapotranspiration (ET0): {ET0_result:.2f} mm/day")


  def __init__(self):
      pass

  def sim_weather(self, month):
    file_path = "meteorological_data_statistics.csv"
    weather_stats_df = pd.read_csv(file_path)
    # Extract the row for the given month
    month_stats = weather_stats_df[weather_stats_df['Month'] == month]

    # Check if month_stats is not empty
    if month_stats.empty:
        raise ValueError(f"No data available for month {month}")

    # Generate weather parameters using Monte Carlo Simulation
    # Temperature
    mean_temp = month_stats['T2M_Mean'].iloc[0]
    std_dev_temp = month_stats['T2M_StdDev'].iloc[0]
    temperature = round(np.random.normal(mean_temp, std_dev_temp), 2)

    # Humidity
    humidity_mean = month_stats['RH2M_Mean'].iloc[0]
    humidity_std = month_stats['RH2M_StdDev'].iloc[0]
    humidity = round(np.random.normal(humidity_mean, humidity_std), 2)

    # Rain Quantity
    rain_mean = month_stats['PRECTOTCORR_Mean'].iloc[0]
    rain_std = month_stats['PRECTOTCORR_StdDev'].iloc[0]
    rain_quantity = round(np.random.normal(rain_mean, rain_std), 2)

    # Wind Speed
    wind_speed_mean = month_stats['WS2M_Mean'].iloc[0]
    wind_speed_std = month_stats['WS2M_StdDev'].iloc[0]
    wind_speed = round(np.random.normal(wind_speed_mean, wind_speed_std), 2)

    # Surface Pressure
    ps_mean = month_stats['PS_Mean'].iloc[0]
    ps_std = month_stats['PS_StdDev'].iloc[0]
    ps = round(np.random.normal(ps_mean, ps_std), 2)

    # Specific humidity
    qv2m_mean = month_stats['QV2M_Mean'].iloc[0]
    qv2m_std = month_stats['QV2M_StdDev'].iloc[0]
    qv2m = round(np.random.normal(qv2m_mean, qv2m_std), 2)

    # daily sun radiation
    rn_daily_mean = month_stats['rn_daily_Mean'].iloc[0]
    rn_daily_std = month_stats['rn_daily_StdDev'].iloc[0]
    rn_daily = round(np.random.normal(rn_daily_mean, rn_daily_std), 2)

    # sky clearness
    sky_clearness_mean = month_stats['ALLSKY_KT_Mean'].iloc[0]
    sky_clearness_std = month_stats['ALLSKY_KT_StdDev'].iloc[0]
    sky_clearness = round(np.random.normal(sky_clearness_mean, sky_clearness_std), 2)



    # 1- Calculate satured vapor pressure
    es = self.calculate_es(temperature)
    # 2- Calculate Actual vapor pressure
    ea = self.calculate_ea(es, humidity) 
    
    is_raining = False
    rain_quantity =  0
    if rain_quantity > 0:
      is_raining = True
    
    is_cloudy = False 
    if sky_clearness < 0.5:
      is_cloudy = True

    # 3- Calculate Slope curve
    delta = self.calculate_slope_curve(temperature, es)

    # 4- Calculate Soil heat flux
    G = self.calculate_soil_heat_flux(rn_daily)

    # 5- Calculate specific humidity
    q = self.calculate_specific_humidity(qv2m)

    # 6- Calculate specific heat
    c_p = self.calculate_specific_heat(temperature, q)

    # 7- Calculate gamma
    gamma = self.calculate_ps(c_p, ps)

    # 8- Calculate Evaporation 
    evaporation = self.calculate_et0(delta, rn_daily, G, gamma, temperature, wind_speed, es, ea)

    return (temperature,humidity, wind_speed, is_raining, rain_quantity, 
            sky_clearness, is_cloudy, evaporation, rn_daily, qv2m, ps, es, ea, delta, G, gamma) 
      