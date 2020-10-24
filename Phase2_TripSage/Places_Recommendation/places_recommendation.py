import requests, json
import googlemaps
import pprint
import time
from datetime import datetime
#from geopy.geocoders import Nominatim
#import pandas as pd





API_KEY = 'AIzaSyCOUCDt77J8v4d2BnWcarXbHzsJpIAhNVQ'



# Define the Client
gmaps = googlemaps.Client(key = API_KEY)

# Do a simple nearby search where we specify the location
# in lat/lon format, along with a radius measured in meters

Address = 'Chicago'
geocode_result = gmaps.geocode(Address)
x = geocode_result[0]['geometry']['location']['lat']
y = geocode_result[0]['geometry']['location']['lng']
coordinate_string = str(x) + ',' + str(y)

places_result  = gmaps.places_nearby(location= coordinate_string, radius = 50000, open_now =False , type = 'tourist_attraction')
time.sleep(3)

place_result  = gmaps.places_nearby(page_token = places_result['next_page_token'])

stored_results = []

# loop through each of the places in the results, and get the place details.      
for place in places_result['results']:

    # define the place id, needed to get place details. Formatted as a string.
    my_place_id = place['place_id']

    # define the fields you would liked return. Formatted as a list.
    my_fields = ['name','formatted_phone_number','website']

    # make a request for the details.
    places_details  = gmaps.place(place_id= my_place_id , fields= my_fields)

    # print the results of the details, returned as a dictionary.
    #pprint.pprint(places_details['result'])

    # store the results in a list object.
    stored_results.append(places_details['result'])

pprint.pprint(stored_results)

