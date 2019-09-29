"""
Title: Config file for API keys.
Author: Primus27
Date: 05/2019
"""
# Import packages
import os

# OpenWeather API
weather_key = os.environ.get("OPENWEATHER_KEY")

# Transport API
transport_id = os.environ.get("TRANSPORT_ID")
transport_key = os.environ.get("TRANSPORT_KEY")