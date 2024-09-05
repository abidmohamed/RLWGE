from prettytable import PrettyTable
from CropSim import CropSim
from WeatherSim import WeatherSim
import numpy as np

class DateSIM:
    # Constants representing seasons
    SEASONS = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}

    def __init__(self, day, month, num_days, daily_irrigation=0):
        # Initialize instances of CropSim and WeatherSim
        self.crop_sim = CropSim()
        self.weather_sim = WeatherSim()

        # Initialize class variables
        self.daily_irrigation = daily_irrigation
        self.day, self.month, self.num_days = day, month, num_days
        self.season = self._calculate_season(self.month)

    def _calculate_season(self, month):
        # Calculate the season based on the month
        if 3 <= month < 6: return 1  # Spring
        elif 6 <= month < 8: return 2  # Summer
        elif 8 <= month < 12: return 3  # Fall
        else: return 4  # Winter

    def _update_month_and_day(self, is_leap, month, day):
        # Update the month and day based on leap year conditions
        if is_leap == 4 and day == 28 and month == 2:
            month, day = month + 1, 1
        elif is_leap < 4 and day == 29 and month == 2:
            is_leap += 1
            month, day = month + 1, 1
        elif (is_leap == 4 and day == 31) or (is_leap < 4 and day == 30):
            month, day = month + 1, 1
            if month > 12:
                month = 1
        else:
            day = day + 1
        return month, day, is_leap

    def _update_knuckle(self):
        # Update knuckle condition based on month
        if self.month == 8 or self.month > 12:
            return True
        return self.day == 31

    def run_date(self):
        # Initialize PrettyTable for tabular data representation
        t = PrettyTable(['Month', 'Day', 'N_days', "Season", "Temperature", "Humidity",
                         "Wind_Speed", "Is_Raining", "Rain_Quantity", 
                         "Is_Cloudy", "Sky Clearness", "Evaporation", "Sun Radiation", "QV2M", "PS", "ES", "EA", "Pressure curve", "G", "Gamma"])

        is_leap, is_31, season_days = 0, True, 1

        while self.num_days > 0:
            if self.day <= 31:
                if self.num_days <= 0:
                    break

                # Call the weather sim function
                temperature, humidity, wind_speed, is_raining, rain_quantity, cloud_prob, is_cloudy, evaporation, rn_daily, qv2m, PS, es, ea, delta, G, gamma= \
                    self.weather_sim.sim_weather(self.month)
                
                # Call The crop sim functions
                crop, water_need = self.crop_sim.crop_type(1, temperature)
                self.daily_irrigation = 0 #self.crop_sim.irrigation_amount(water_need, rain_quantity, evaporation, season_days)

                self.num_days = self.num_days - 1
                t.add_row([self.month, self.day, self.num_days, self.SEASONS[self.season], temperature, humidity,
                           wind_speed, is_raining, rain_quantity, is_cloudy, cloud_prob, evaporation,
                           rn_daily, qv2m, PS, es, ea, delta, G, gamma])

                self.month, self.day, is_leap = self._update_month_and_day(is_leap, self.month, self.day)
                is_31 = not is_31 if self.day == 31 else is_31

            self.season = self._calculate_season(self.month)
            knuckle = self._update_knuckle()

        print(t)
        data = t.get_csv_string()

        with open('data.csv', 'w') as f:
            f.write(data)

        return t

    def render(self):
        dtype = '<U2'
        displ_board = np.zeros((1, 17), dtype=dtype)
        displ_board[:] = ' '

        # Call the weather sim function
        temperature, humidity, wind_speed, rain_prob, is_raining, rain_quantity, cloud_prob, is_cloudy, evaporation = \
            self.weather_sim.sim_weather(self.month)
        # Call The crop sim functions
        crop, water_need = self.crop_sim.crop_type(1, temperature)
        season_days = 1
        if season_days > 90:
            season_days = 0
        # self.daily_irrigation = self.crop_sim.calculate_water_effect_on_yield(water_need, rain_quantity, evaporation, season_days)

        components = [[temperature, humidity, wind_speed]]
        for item in components:
            print(item)
        print(displ_board)


def main():
    foo = DateSIM(1, 4, 2192)
    t = foo.run_date()


if __name__ == "__main__":
    main()