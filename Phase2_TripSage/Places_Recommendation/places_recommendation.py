import requests, json
import googlemaps
import pprint
import time
from datetime import datetime
from geotext import GeoText
import os
import itertools
from more_itertools import unique_everseen


def Places_Recommendation(gmaps, Place, PlaceType):
    print(Place)
    Address = Place
    geocode_result = gmaps.geocode(Address)
    x = geocode_result[0]["geometry"]["location"]["lat"]
    y = geocode_result[0]["geometry"]["location"]["lng"]
    coordinate_string = str(x) + "," + str(y)

    places_result = gmaps.places_nearby(
        location=coordinate_string, radius=40000, open_now=False, type=PlaceType
    )
    time.sleep(3)

    # place_result  = gmaps.places_nearby(page_token = places_result['next_page_token'])
    stored_results = []

    # loop through each of the places in the results, and get the place details.
    for place in places_result["results"]:

        # define the place id, needed to get place details. Formatted as a string.
        my_place_id = place["place_id"]

        # define the fields you would liked return. Formatted as a list.
        my_fields = [
            "name",
            "formatted_phone_number",
            "website",
            "geometry/location",
            "opening_hours",
            "formatted_address",
        ]

        # make a request for the details.
        places_details = gmaps.place(place_id=my_place_id, fields=my_fields)

        # store the results in a list object.
        stored_results.append(places_details["result"])

    return stored_results


def getRecommendation(city, type1):
    # Define the Client
    API_KEY = "AIzaSyCOUCDt77J8v4d2BnWcarXbHzsJpIAhNVQ"
    gmaps = googlemaps.Client(key=API_KEY)
    TYPES_PLACE_MAP = {
        "adventures": ["tourist_attraction", "stadium", "zoo"],
        "kids": ["amusement_park", "museum", "food"],
        "relaxing": ["art_gallery", "church", "spa"],
        "other": ["hospital"],
    }

    if type1 == "adventures":
        dictionary = {}
        if city not in dictionary:
            dictionary[city] = {}
        dictionary[city]["tourist_attraction"] = Places_Recommendation(
            gmaps, city, "tourist_attraction"
        )
        dictionary[city]["stadium"] = Places_Recommendation(gmaps, city, "stadium")
        dictionary[city]["zoo"] = Places_Recommendation(gmaps, city, "zoo")
        dictionary = take(3, dictionary.iteritems())
        return dictionary

    elif type1 == "kids":
        dictionary = {}
        if city not in dictionary:
            dictionary[city] = {}
        dictionary[city]["amusement_park"] = Places_Recommendation(
            gmaps, city, "amusement_park"
        )
        dictionary[city]["museum"] = Places_Recommendation(gmaps, city, "museum")
        dictionary[city]["food"] = Places_Recommendation(gmaps, city, "food")
        dictionary = take(3, dictionary.iteritems())
        return dictionary

    elif type1 == "relaxing":
        dictionary = {}
        if city not in dictionary:
            dictionary[city] = {}
        dictionary[city]["art_gallery"] = Places_Recommendation(
            gmaps, city, "art_gallery"
        )
        dictionary[city]["church"] = Places_Recommendation(gmaps, city, "church")
        dictionary[city]["spa"] = Places_Recommendation(gmaps, city, "spa")
        dictionary = take(3, dictionary.iteritems())
        return dictionary

    elif type1 == "other":
        dictionary = {}
        if city not in dictionary:
            dictionary[city] = {}
        dictionary[city]["hospital"] = Places_Recommendation(gmaps, city, "hospital")
        dictionary = take(3, dictionary.iteritems())
        return dictionary

    else:
        return "Please Enter the correct options"
