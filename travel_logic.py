"""
Title: Application that collects and outputs live route planning information
            based on user input
Author: Primus27
Date: 05/2019
"""

# Import packages
import requests
import datetime as dt
import utils
import config


class TravelInformation:
    """
    Contains the methods for the route planning and weather.
    Each object instance will have associated data such as route parts,
    starting location, etc.
    """
    def __init__(self, modes, source_pc, destination_pc, dep_arri="at",
                 date="", time=""):
        """
        Constructor for user selected options
        :param modes: Mode of transport. Can be "bus", "train" or "boat",
                        separated by dashes (-)
        :param source_pc: Starting postcode location (format does not matter)
        :param destination_pc: Ending postcode location (format doesn't matter)
        :param dep_arri: Depart/arrive at selected time. Can be "at" or "by"
        :param date: Date in the format DD/MM/YY
        :param time: Time in the format HH:MM
        """
        if date == "":
            self.date = dt.datetime.now().strftime("%Y-%m-%d")
        else:
            self.date = dt.datetime.strptime(date, "%d/%m/%y")\
                            .strftime("%Y-%m-%d")
        if time == "":
            self.time = dt.datetime.now().strftime("%H:%M")
        else:
            self.time = time
        self.source = utils.format_pc(source_pc)
        self.destination = utils.format_pc(destination_pc)
        self.modes = modes
        self.type = dep_arri
        self.transport_id = config.transport_id
        self.transport_key = config.transport_key

    def get_route_info(self):
        """
        API call to fetch route information
        :return: If successful, return a dictionary with the request response.
                    Otherwise, return a tuple with -1 and an error message
        """
        url = "https://transportapi.com/v3/uk/public/journey/from/postcode:" \
              "{source}/to/postcode:{destination}/{type}/{date}/{time}.json" \
              "?app_id={id}&app_key={key}&modes={modes}&service=southeast"\
            .format(source=self.source, destination=self.destination,
                    type=self.type, date=self.date, time=self.time,
                    id=self.transport_id, key=self.transport_key,
                    modes=self.modes)
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
                return -1, "Error! Could not retrieve live info. " \
                           "Please check your information"
            else:
                return json_info

    def format_travel_request(self):
        """
        Samples useful information from api request and formats it correctly.
        This allows each dictionary key to be on a new line and each value
                    (containing a dictionary) to be the columns
        :return: The formatted dictionary. If the data is an error message,
                    the message will be forwarded
        """
        request_data = self.get_route_info()

        # Sanitise if the data is a dictionary
        if isinstance(request_data, dict):
            sanitised_dict = {}
            length = len(request_data["routes"][0]["route_parts"])

            # Each part of the route (i.e bus, then walking)
            for i in range(0, length):
                temp_dict = {}

                # Place mode as first element
                for key, r_value in request_data["routes"][0]["route_parts"][
                                i].items():
                    if key == "mode":
                        temp_dict[key] = r_value

                # Add "line_name" as second element
                for key, r_value in request_data["routes"][0]["route_parts"][
                                i].items():
                    if key == "line_name":
                        key = "line"
                        if r_value == "":
                            r_value = "-"
                        temp_dict[key] = r_value

                for key, r_value in request_data["routes"][0]["route_parts"][
                        i].items():  # Add each route element
                    # Removed from final dict
                    if key not in ["destination", "duration", "coordinates",
                                   "line_name", "mode"]:
                        # Formatting
                        if key == "from_point_name":
                            key = "from"
                        elif key == "to_point_name":
                            key = "to"
                        elif key == "departure_time":
                            key = "departing"
                        elif key == "arrival_time":
                            key = "arriving"

                        temp_dict[key] = r_value

                sanitised_dict[i] = temp_dict
            return sanitised_dict
        return request_data[1]  # Return error message
