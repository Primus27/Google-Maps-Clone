"""
Title: GUI for an application that collects and outputs live route planning
            and weather information based on user input
Author: Primus27
Date: 05/2019
"""

# Import packages
from flask import Flask, render_template, request, session, redirect
import travel_logic
import weather_logic
import validate
import datetime as dt
import random
import string
import utils

app = Flask(__name__)
# Session key
app.secret_key = "".join(random.SystemRandom().choice(
    string.ascii_uppercase + string.digits) for i in range(6))


@app.route("/")
@app.route("/home")
def home_page():
    """
    Home page
    :return: A render of the home page
    """
    return render_template("home.html")


@app.route("/route-options", methods=["GET", "POST"])
def route_options():
    """
    Calls route-options page. After a form has been completed, input validation
        is carried out. Lastly, these are assigned to session keys
    :return: If invalid form input, return the same page with an appropriate
        error message. If the form validates, redirect to route-results
    """
    # Validate User Input
    if request.method == "POST":
        # Assign the result of validation checks
        start_postcode_valid = validate.is_valid_postcode(
            request.form["start_postcode"])
        end_postcode_valid = validate.is_valid_postcode(
            request.form["end_postcode"])
        time = validate.is_valid_time(request.form["time"])
        date = validate.is_valid_date(request.form["date"])
        selected_modes = ["foot"]

        # Invalid Postcode
        if isinstance(start_postcode_valid, tuple):
            return render_template("route-options.html",
                                   error_message=start_postcode_valid[1])
        elif start_postcode_valid is False:
            return render_template("route-options.html",
                                   error_message="Please enter a valid "
                                                 "'FROM' postcode")
        elif isinstance(end_postcode_valid, tuple):
            return render_template("route-options.html",
                                   error_message=end_postcode_valid[1])
        elif end_postcode_valid is False:
            return render_template("route-options.html",
                                   error_message="Please enter a valid "
                                                 "'TO' postcode")
        # "When" has been altered - likely using inspect element
        elif not (request.form["when"] == "at" or
                  request.form["when"] == "by"):
            return render_template("route-options.html",
                                   error_message="Please do not change the "
                                                 "values from the on-screen "
                                                 "options")
        # Invalid Time
        elif time is False:
            return render_template("route-options.html",
                                   error_message="The time must have the "
                                                 "format HH:MM")
        # Invalid Date
        elif date is False:
            return render_template("route-options.html",
                                   error_message="The date must have the "
                                                 "format DD/MM/YY")
        else:
            # "Mode" checkbox results
            if "mode1" in request.form:
                selected_modes.append("bus")
            if "mode2" in request.form:
                selected_modes.append("train")
            if "mode3" in request.form:
                selected_modes.append("boat")
            modes = "-".join(selected_modes)

            # Create session data
            session["start_postcode"] = request.form["start_postcode"]
            session["end_postcode"] = request.form["end_postcode"]
            session["when"] = request.form["when"]
            session["time"] = request.form["time"]
            session["date"] = request.form["date"]
            session["modes"] = modes
            return redirect("/route-results")
    return render_template("route-options.html")


@app.route("/route-results")
def route_results():
    """
    Results page. Informs user of their choices and outputs route information
        in a table including addresses, timings and transport modes
    :return: A render of the route-results page.
    """
    # Create TravelInformation object
    travel_obj = travel_logic.TravelInformation(
        modes=session["modes"], source_pc=session["start_postcode"],
        destination_pc=session["end_postcode"], dep_arri=session["when"],
        date=session["date"], time=session["time"])
    route_info = travel_obj.format_travel_request()

    # If weather_info is a dictionary, the api call was successful
    if isinstance(route_info, dict):
        # Assign session data to dictionary
        session_data = {
            "source": str(session["start_postcode"]).upper(),
            "destination": str(session["end_postcode"]).upper(),
            "time": str(dt.datetime.strptime(travel_obj.date, "%Y-%m-%d").
                        strftime("%d/%m/%y") + "  " + session["when"] + "  "
                        + travel_obj.time),
            "modes": str(session["modes"]).replace("-", ", ").capitalize()
        }
        return render_template("route-results.html", session_data=session_data,
                               routes=route_info, flag=False)
    else:
        return render_template("route-results.html", routes=route_info,
                               flag=True)


# Weather Page
@app.route("/weather-results")
def weather_results():
    """
    Weather results. It presents the current weather (of their destination),
        alongside additional information such as temperature
    :return: A render of the weather results page
    """
    # Create WeatherInformation object
    weather_obj = weather_logic.WeatherInformation(destination_pc=
                                                   session["end_postcode"])
    weather_info = weather_obj.get_weather_info()

    # If weather_info is a dictionary, the api call was successful
    if isinstance(weather_info, dict):
        postcode = utils.format_pc(str(session["end_postcode"]))
        return render_template("weather-results.html", postcode=postcode,
                               weather=weather_info, flag=False)
    else:
        return render_template("weather-results.html", weather=weather_info,
                               flag=True)


@app.errorhandler(404)
def not_found(error):
    """
    Error groups of code 400 are where the user inputs invalid data (such as a
        page not existing (404)). If a 404 needs to be handled, users are sent
        to this page.
    :param error: Error code 404
    :return: A render of the "404 - Page Not Found" Page
    """
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    """
    Error groups of code 500 are server side errors (such as not being able to
        process the request. If a 500 needs to be handled, users are sent
        to this page.
    :param error: Error code 500
    :return: A render of the "500 - Internal Server Error" Page
    """
    return render_template("500.html"), 500


if __name__ == '__main__':
    app.run()
