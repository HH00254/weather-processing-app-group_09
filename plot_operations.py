"""
Description: Weather Processing App Group 9
Author: Lance Fuentes, Al Hochbaum, Christian Requerme
Section Number: FTO01
Date Created: 03/20/24
Credit:
Updates:
"""
import calendar
import matplotlib.pyplot as plt
from prod_util import ProdUtil

class PlotOperations:
    """
    Handles plotting operations for generating box plots and line plots of weather data.

    Methods:
    - create_boxplot(): Generates a box plot for mean temperatures for each month
      of each year in the weather data.
    - create_lineplot(month, year): Generates a line plot for mean daily temperatures
      of a specified month and year.
    """
    def __init__(self, weather_data):
        self.weather_data = weather_data

    def create_boxplot(self):
        """
        Generates a box plot for mean temperatures for each month of each year in the weather data.
        """

        try:
            # Dictionary to store mean temperatures for each month
            monthly_means = [[] for _ in range(12)]

            # Calculate mean temperatures for each month across all years
            for year_data in self.weather_data:
                month = int(year_data[0][5:7])  # Extract month from sample date
                # Append mean temperature (if january is 1, subtract 1 and put it on index 0)
                monthly_means[month - 1].append(year_data[5])

            # Create a single boxplot for all the months
            plt.figure()
            plt.boxplot(monthly_means)
            # Extract years from the weather data
            years = [year_data[0][:4] for year_data in self.weather_data]
            plt.title(f'Monthly Temperature Distribution for: {min(years)} to {max(years)}')
            plt.xlabel('Month')
            plt.ylabel('Mean Temperature (°C)')
            plt.xticks(range(1, 13))  # Set x-axis ticks to be from 1 to 12
            plt.show()

        except IndexError as e:
            ProdUtil.system_log(e, e.args)

        except ValueError as e:
            ProdUtil.system_log(e, e.args)

        except TypeError as e:
            ProdUtil.system_log(e, e.args)

    def create_lineplot(self, month, year):
        """
        Generates a line plot for mean daily temperatures of a specified month and year.

        Args:
        - month (int): The month for which to generate the line plot.
        - year (int): The year for which to generate the line plot.
        """
        try:
            monthly_weather_data = (
                [data for data in self.weather_data if 
                 str(data[0]).startswith(f"{year}-{month:02}")])

            # Create a list to store mean temperatures for each day of the selected month
            daily_temperatures = []

            # Calculate the number of days in the selected month
            num_days_in_month = calendar.monthrange(year, month)[1]

            # Iterate over each day of the month
            for day in range(1, num_days_in_month + 1):
                # Filter the weather data for the current day
                day_data = (
                    [data for data in monthly_weather_data if \
                     str(data[0]).startswith(f"{year}-{month:02}-{day:02}")])

                # If data is available for the current day, calculate the mean temperature
                if day_data:
                    # Calculate the mean temperature for the current day
                    mean_temp = sum(data[5] for data in day_data) / len(day_data)
                    # Append the mean temperature to the daily_temperatures list
                    daily_temperatures.append(mean_temp)
                else:
                    # If no data is available for the current day,
                    #   append None to maintain the day-to-day mapping
                    daily_temperatures.append(None)

            # Plot the line plot
            plt.figure()
            plt.plot(range(1, num_days_in_month + 1), daily_temperatures, marker='o')
            plt.title(f'Mean Daily Temperatures Lineplot - {calendar.month_name[month]} {year}')
            plt.xlabel('Day')
            plt.ylabel('Mean Temperature (°C)')
            # Set x-axis ticks to show the days of the month
            plt.xticks(range(1, num_days_in_month + 1))
            plt.grid(True)
            plt.show()

        except IndexError as e:
            ProdUtil.system_log(e, e.args)

        except ValueError as e:
            ProdUtil.system_log(e, e.args)

        except TypeError as e:
            ProdUtil.system_log(e, e.args)
