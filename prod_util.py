"""
Description: Weather Data Table
Author: Lance Fuentes, Al Hochbaum, Christian Requerme
Section Number: FTO01
Date Created: 03/21/24
Credit:
Description: Weather Data Table
Author: Lance Fuentes, Al Hochbaum, Christian Requerme
Section Number: FTO01
Date Created: 04/03/24
Credit:
Updates:
"""
from datetime import datetime
import traceback
import logging
import logging.handlers
import os

class ProdUtil():
    """
    Summary:
    - A Production version Utility static class
    """

    # @staticmethod
    # def system_log(exception: Exception, data_entre=None) -> None:
    #     """
    #     Summary:
    #     - Opens and writes error logs to a file
    #     when issues arise from web-scrapping

    #     Args:
    #     - Exception object from the event
    #     - A data object of the corrupted data.

    #     Return:
    #     - None
    #     """
    #     #  base field something click -.> object
    #     # Windows event viewer
    #     log_date = datetime.now().strftime('%Y-%m-%d')
    #     log_name_path = f'web_scraping_{log_date}.log'

    #     if not os.path.exists(log_name_path):
    #         logging.basicConfig(
    #             filename=log_name_path,
    #             level=logging.DEBUG,
    #             format='%(asctime)s - %(name)s - %(levelname)s  - %(funcName)s - %(message)s')

    #     trace_body = traceback.extract_tb(exception.__traceback__)
    #     method_name = 'Unknown'

    #     if trace_body:
    #         _, _, method_name, _ = trace_body[-1]

    #     logger = logging.getLogger(__name__)

    #     # Log the exception and data_entre
    #     logger.error('\nError: %s\nFunction Name: %s\nData Corruption:\n%s\n\n', \
    #                  exception, method_name,data_entre)

    @staticmethod
    def system_log(exception: Exception, data_entre=None) -> None:
        """
        Summary:
        - Opens and writes error logs to a file
        when issues arise from web-scrapping

        Args:
        - Exception object from the event
        - A data object of the corrupted data.

        Return:
        - None
        """
        # Windows event viewer
        logger = logging.getLogger(__name__)

        try:
            # Windows Event Viewer handler
            event_handler = logging.handlers.NTEventLogHandler('weather_processor')
            formatter = logging.Formatter('%(levelname)s: %(message)s')
            event_handler.setFormatter(formatter)
            logger.addHandler(event_handler)

            # Log the exception and data_entre
            log_date = datetime.now().strftime('%Y-%m-%d')
            log_name_path = f'web_scraping_{log_date}.log'

            if not os.path.exists(log_name_path):
                logging.basicConfig(
                    filename=log_name_path,
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s  - %(funcName)s - %(message)s')

            trace_body = traceback.extract_tb(exception.__traceback__)
            method_name = 'Unknown'

            if trace_body:
                _, _, method_name, _ = trace_body[-1]

            logger.error('\nError: %s\nFunction Name: %s\nData Corruption:\n%s\n\n', 
                            exception, method_name,data_entre)


        finally:
            # Remove the event handler to prevent duplicate logs
            logger.removeHandler(event_handler)

    @staticmethod
    def format_date(unformatted_date: str) -> str:
        """
        Summary:
        - Re-formates string date data

        Args:
        - An unformated date as a string

        Return:
        - A formated date
        """
        return datetime.strptime(unformatted_date, '%B %d, %Y').strftime('%Y-%m-%d')
