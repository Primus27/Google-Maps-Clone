"""
Title: Application that collects and outputs live weather information
            based on user input
Author: Primus27
Date: 05/2019
"""

# Import packages
import requests
import utils
import config


class WeatherInformation:
    """
    Contains the methods for the route planning and weather.
    Each object instance will have associated data such as route parts,
    starting location, etc.
    """
    def __init__(self, destination_pc):
        """
        Initialiser for user selected options
        :param destination_pc: Ending postcode location (format doesn't matter)
        """
        self.destination = utils.format_pc(destination_pc)
        self.weather_key = config.weather_key

    def postcode_to_coordinates(self):
        """
        API call to fetch coordinates from destination postcode
        :return: If successful, return a tuple containing coordinates.
                    Otherwise, return a tuple with -1 and an error message
        """
        url = "https://api.postcodes.io/postcodes/{postcode}" \
            .format(postcode=self.destination)

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
                lon = json_info["result"]["longitude"]
                lat = json_info["result"]["latitude"]
                return lat, lon

    def get_weather_info(self):
        """
        API call to fetch weather information
        :return: If successful, return a dictionary with the request response.
                    Otherwise, return a tuple with -1 and an error message
        """
        coords = self.postcode_to_coordinates()
        if coords[0] != -1:
            (lat, lon) = coords
            url = "http://api.openweathermap.org/data/2.5/weather?lat={lat}&" \
                  "lon={lon}&appid={app_id}".format(lat=lat, lon=lon,
                                                    app_id=self.weather_key)
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
                    # Response is a 204 (No Content)/contains invalid JSON
                    return -1, "Error! Could not retrieve live info. " \
                               "Please check your information"
                else:
                    info_dic = {
                        "name": json_info["name"],
                        "weather": json_info["weather"][0]["main"],
                        "image": "http://openweathermap.org/img/w/" +
                                 json_info["weather"][0]["icon"] + ".png",
                        "temp": "%.1f" % (json_info["main"]["temp"]-273.15)
                    }
                    return info_dic
        else:
            return coords[1]  # Return error message
