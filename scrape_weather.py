"""
Description: Weather Processing App Group 9
Author: Lance Fuentes, Al Hochbaum, Christian Requerme
Section Number: FTO01
Date Created: 03/20/24
Credit:
Updates:

"""
from datetime import datetime
from lxml import html
from dateutil.relativedelta import relativedelta
import requests
from prod_util import ProdUtil

class ScrapeWeather:
    """
    Summary:
    - A Weather scraper class that work on https://climate.weather.gc.ca
    """

    def __init__(self, date_instance = datetime.now(), station_id = 27174) -> None:
        """
        Initialize the ScrapeWeather class.

        Args:
        - date_instance (datetime): The date instance for which weather data is scraped.
          Defaults to current date and time.
        - station_id (int): The ID of the weather station. Defaults to 27174.

        Returns:
        None
        """
        self.date_instance  = date_instance
        self.station_id     = station_id
        self.web_address    = """
            https://climate.weather.gc.ca/climate_data/daily_data_e.html?StationID={}&timeframe=2&StartYear=1840&EndYear=2018&Year={}&Month={}#"""
        self.end_year       = self.get_data_end_point()

    def get_data_end_point(self, page_year = 1840) -> int:
        """
        Get the end year for data retrieval based on the current date.

        Args:
        - page_year (int): The starting year for data retrieval. Defaults to 1840.

        Returns:
        - int: The end year for data retrieval.
        """
        try:
            request = self.web_address.format(self.station_id, page_year, self.date_instance.month)
            response_body = requests.get(request, timeout=120)

        except requests.exceptions.HTTPError as e:
            ProdUtil.system_log(e, e.args)

        except requests.exceptions.ConnectionError as e:
            ProdUtil.system_log(e, e.args)

        except requests.exceptions.Timeout as e:
            ProdUtil.system_log(e, e.args)

        except requests.exceptions.RequestException as e:
            ProdUtil.system_log(e, e.args)

        return int(self.get_xpath_year(html.fromstring(response_body.content)))

    def get_xpath_year(self, tree_doc) -> int:
        """
        Extract the year from the webpage content.

        Args:
        - tree_doc: The parsed HTML tree of the webpage content.

        Returns:
        - int: The year extracted from the webpage.
        """
        year = -1

        try:
            year = (str(tree_doc.xpath('//*[@id="climateNav"]/div[3]/section/div[1]/ \
                                       form/fieldset/legend/text()'))
                                .split('(')[1].split(')')[0])

        except TypeError as e:
            ProdUtil.system_log(e, e.args)

        return year

    def _format_payload_for_insert(
            self,
            list_data: list,
            location_payload: list,
            insert_collection: list[tuple],
            step: int) -> list[tuple]:
        """
        Format scraped data for insertion into the database.

        Args:
        - list_data (list): List of scraped data.
        - location_payload (list): List containing location information.
        - insert_collection (list): List of tuples for database insertion.
        - step (int): Step size for iterating over the scraped data list.

        Returns:
        - list: Formatted list of tuples for insertion.
        """
        for location_element in location_payload:

            if location_element[0] == '' or location_element[0] is None:
                location_element = 'NULL'

        index = 0
        while index < len(list_data):

            try:
                insert_collection.append(((
                    ProdUtil.format_date(str(list_data[index])),
                    str(location_payload[0]).split(' ', maxsplit=1)[0],
                    str(location_payload[1]).strip(),
                    float(list_data[index + 1]),
                    float(list_data[index + 2]),
                    float(list_data[index + 3]))))

            except TypeError as e:
                index =  index - step + 1
                ProdUtil.system_log(e, (list_data[index],
                                        location_payload[0],
                                        location_payload[1],
                                        list_data[index + 1],
                                        list_data[index + 2],
                                        list_data[index + 3]))

            except ValueError as e:
                index =  index - step + 1
                ProdUtil.system_log(e, (list_data[index],
                                        location_payload[0],
                                        location_payload[1],
                                        list_data[index + 1],
                                        list_data[index + 2],
                                        list_data[index + 3]))

            except IndexError as e:
                index =  index - step + 1
                ProdUtil.system_log(e, (list_data[index],
                                        location_payload[0],
                                        location_payload[1],
                                        list_data[index + 1],
                                        list_data[index + 2],
                                        list_data[index + 3]))

            finally:
                # Continue Incrementation
                index += step

        return insert_collection

    def get_xpath_page_values(self, trees) -> list:
        """
        Extract values from the parsed HTML trees.

        Args:
        - trees: List of parsed HTML trees.

        Returns:
        - list: List of tuples for insertion into the database.
        """
        insert_values = []

        for tree in trees:

            try:

                if tree.xpath('//td[position()<4]/text()'):
                    city_path     = '//main/div/p/text()'
                    province_path = '//main/div/br/text()'
                    location_payload = tree.xpath(f"{city_path} | {province_path}")

                    date_path        = '//table/tbody/tr[position()< last() -3]/th/abbr/@title'
                    temperature_path = '//tr[position()< last() -3]/td[position()<4]/text()'
                    table_load = tree.xpath(f"{date_path} | {temperature_path}")

                    insert_values = self._format_payload_for_insert(
                        table_load,
                        location_payload,
                        insert_values,
                        4)

            except IndexError as e:
                ProdUtil.system_log(e, e.args)

        return insert_values

    def _months_between_dates(self, end_date) -> int:
        """
        Check if the year and month of two datetime objects are equal.

        Args:
            datetime_start (datetime): The first datetime object.
            datetime_end (datetime): The second datetime object.

        Returns:
            bool: True if the year and month of both datetime objects are equal, False otherwise.
        """
        # Calculate the difference in days
        delta = self.date_instance - end_date
        days = delta.days

        try:
            # Calculate the approximate difference in months
            months = days / 30.4375

        except ZeroDivisionError as e:
            ProdUtil.system_log(e, e.args)

        return int(months) + 1

    def web_scrape_call(self, st_year = None, st_month = None, data_end_point = None) -> list:
        """
        Perform the web scraping call to retrieve weather data.

        Args:
        - st_year (int): The starting year for scraping.   Defaults to None.
        - st_month (int): The starting month for scraping. Defaults to None.
        - data_end_point (datetime): Used to update missing data. Defaults to None.

        Returns:
        - list: List of parsed HTML trees containing weather data.
        """
        month_counter    = 0
        month            = 0
        previous_data    = html.fromstring('<body><main><td>Null</td></main></body>')
        termination_flag = True
        tree_pages       = []

        if st_year is not None and st_month is not None:
            working_date = datetime(st_year, st_month, 1)
            month_range  = working_date.month

        else:
            working_date = self.date_instance
            month_range  = self._months_between_dates(data_end_point)

        while termination_flag and month_counter < month_range:
            month      = working_date.month
            year       = working_date.year

            try:
                request = self.web_address.format(self.station_id, year, month)
                response_body = requests.get(request, timeout=120)

                if (response_body.status_code == 200 and
                    html.fromstring(response_body.content).xpath('//table/tbody')):
                    tree = html.fromstring(response_body.content)

                    if (tree.xpath('//td[position()<4]/text()') !=
                        previous_data.xpath('//td[position()<4]/text()')):

                        previous_data = tree
                        tree_pages.append(tree)
                        month_counter += 1

                    else:
                        termination_flag = False

            except IndexError as e:
                ProdUtil.system_log(e, e.args)

            except requests.exceptions.HTTPError as e:
                ProdUtil.system_log(e, e.args)

            except requests.exceptions.ConnectionError as e:
                ProdUtil.system_log(e, e.args)

            except requests.exceptions.Timeout as e:
                ProdUtil.system_log(e, e.args)

            except requests.exceptions.RequestException as e:
                ProdUtil.system_log(e, e.args)

            # Decrementing the time frame.
            working_date -= relativedelta(months=1)
            month_counter += 1
            #sm

        return tree_pages
