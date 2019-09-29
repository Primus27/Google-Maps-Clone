"""
Title: A collection of functions that verify user input
Author: Primus27
Date: 05/2019
"""

# Import packages
import datetime as dt
import requests


def is_valid_postcode(location_str):
    """
    Check whether the input postcode exists
    :param location_str: The postcode as a string (format irrelevant)
    :return: Value of type: boolean on whether the postcode exists
    """
    url = "https://api.postcodes.io/postcodes/{postcode}/validate"\
        .format(postcode=location_str)

    try:
        r = requests.get(url)
        r.raise_for_status()
    except requests.exceptions.HTTPError:  # status_code != 200
        return -1, "Error! Could not retrieve live info. " \
                   "Please check your information"
    except requests.exceptions.ConnectionError:
        return -1, "Connection Error! Please check your network and " \
                   "try again"
    except requests.exceptions.Timeout:
        return -1, "Request Timeout! Please try again"
    except requests.exceptions.TooManyRedirects:
        return -1, "Redirect Error! Max redirections reached"
    except requests.exceptions.RequestException:
        return -1, "Something went wrong! Please try again"
    else:
        try:
            # Decode JSON
            json_info = r.json()
        except ValueError:
            # Decoding failed
            # Response is a 204 (No Content) or contains invalid JSON
            return -1, "Error! Couldn't process postcode data"
        else:
            return json_info["result"]


def is_valid_date(date_str):
    """
    Check whether the input date is in the correct format (DD/MM/YY)
    :param date_str: The date input as a string
    :return: Value of type: boolean on whether the format is correct
    """
    if date_str == "":
        return True  # Date string can be empty when form left blank
    else:
        try:
            dt.datetime.strptime(date_str, "%d/%m/%y")
        # User input for date is not in the correct format
        except ValueError:
            return False
        else:
            return True


def is_valid_time(time_str):
    """
    Check whether the input time is in the correct format (HH:MM)
    :param time_str: The time input as a string
    :return: Value of type: boolean on whether the format is correct
    """
    if time_str == "":
        return True  # Time string can be empty when form left blank
    else:
        try:
            dt.datetime.strptime(time_str, "%H:%M")
        # User input for time is not in the correct format
        except ValueError:
            return False
        else:
            return True
