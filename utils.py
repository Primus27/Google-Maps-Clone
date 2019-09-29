"""
Title: Provides functions for the program
Author: Primus27
Date: 05/2019
"""


def format_pc(raw_postcode):
    """
    Format the postcode to ignore spaces and convert to uppercase
    :param raw_postcode: The original postcode
    :return: The formatted postcode
    """
    formatted_postcode = raw_postcode.replace(" ", "").upper()
    return formatted_postcode
