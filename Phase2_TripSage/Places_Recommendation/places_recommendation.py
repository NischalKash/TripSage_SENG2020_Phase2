import requests, json
import googlemaps
import pprint
import time
from datetime import datetime
#from geopy.geocoders import Nominatim
#import pandas as pd
from geotext import GeoText
import os

def Places_Recommendation(gmaps, Place, PlaceType):
    Address = Place
    geocode_result = gmaps.geocode(Address)
    x = geocode_result[0]['geometry']['location']['lat']
    y = geocode_result[0]['geometry']['location']['lng']
    coordinate_string = str(x) + ',' + str(y)
    
    places_result  = gmaps.places_nearby(location= coordinate_string, radius = 40000, open_now =False , type = PlaceType)
    time.sleep(3)

    place_result  = gmaps.places_nearby(page_token = places_result['next_page_token'])
    stored_results = []

    # loop through each of the places in the results, and get the place details.      
    for place in places_result['results']:

        # define the place id, needed to get place details. Formatted as a string.
        my_place_id = place['place_id']

        # define the fields you would liked return. Formatted as a list.
        my_fields = ['name','formatted_phone_number','website','geometry/location','opening_hours', 'formatted_address']

        # make a request for the details.
        places_details  = gmaps.place(place_id= my_place_id , fields= my_fields)

        # store the results in a list object.
        stored_results.append(places_details['result'])
    
    return stored_results

# Define the Client
API_KEY = 'AIzaSyCOUCDt77J8v4d2BnWcarXbHzsJpIAhNVQ'
gmaps = googlemaps.Client(key = API_KEY)

# Main Dictionary
fileDir = os.path.dirname(os.path.realpath('__file__'))
filename = os.path.join(fileDir, '../tripsage/sentences.txt')
with open(filename, 'r') as reader:
    lines = reader.read()

cities_list = GeoText(lines).cities
dictionary = {}

# Fetching the tourist attraction near source and destination. 
for city in set(cities_list):
    # Grepping all the tourist attraction.
    if city not in dictionary:
        dictionary[city] = {}
    dictionary[city]['tourist_attraction'] = Places_Recommendation(gmaps, city, 'tourist_attraction')

print(dictionary)






