from __future__ import absolute_import
from django.shortcuts import render
import xmltodict
import yaml
from places_recommendation import *
from geotext import GeoText
import datetime
import urllib.parse

# Mapping of types to subtypes
TYPES_PLACE_MAP = {
    "adventures": ["tourist_attraction", "stadium"],
    "kids": ["amusement_park", "museum"],
    "relaxing": ["art_gallery", "church", "spa"],
}

#Base Function, which displays the home page
def home(request):
    return render(request, "planner/home.html")

# Function for parsing information from the dictionary.
def getItemsForMapping(city, dict, subtype, locations):
    for item in dict[city][subtype]:
        temp = []
        string = item['name']
                
        temp.append(string)

        googleURL = 'https://www.google.com/maps/search/?api=1&query=' + urllib.parse.quote(item['name'])
        
        temp.append(googleURL)

        locations.append(temp)
    return locations

# We must parse information from a variety of subtypes based on given type
def getMapString(city, dicts, types, locations):
    if(types == "adventures"):
        locations = getItemsForMapping(city, dicts, "tourist_attraction", locations)
        locations = getItemsForMapping(city, dicts, "stadium", locations)
        locations = getItemsForMapping(city, dicts, "zoo", locations)
    elif(types == "kids"):
        locations = getItemsForMapping(city, dicts, "amusement_park", locations)
        locations = getItemsForMapping(city, dicts, "museum", locations)
        locations = getItemsForMapping(city, dicts, "restaurant", locations)
    elif(types == "relaxing"):
        locations = getItemsForMapping(city, dicts, "art_gallery", locations)
        locations = getItemsForMapping(city, dicts, "church", locations)
        locations = getItemsForMapping(city, dicts, "spa", locations)
        locations = getItemsForMapping(city, dicts, "park", locations)
    elif(types == "other"):
        locations = getItemsForMapping(city, dicts, "hospital", locations)
        locations = getItemsForMapping(city, dicts, "police", locations)  
    
    return locations
    
    
def find_spots(request):
    if request.method == "POST":
        #Receive the city name that the user wants to review through as per his wish
        city = request.POST.get("city", "")

        #This could be none as well thats why we have assigned it initially as empty
        tourist_spots2 = {}

        #Call the function in places_recommendations.py file which we have imported which will return a dictionary of all the
        #suggested tourist spots according to the city entry by User
        type1 = request.session['type1']
        type2 = request.session['type2']
        
        tourist_spots1 = getRecommendation(city,type1)
        if type2 != 'none':
            tourist_spots2 = getRecommendation(city,type2)
        
        locations = []
        # Retrieve all tourist locations from source to destination based on filters
        locations = getMapString(city, tourist_spots1, type1, locations)

        if type2 != 'none':
            locations = getMapString(city, tourist_spots2, type2, locations)

        
        # Pass the context object to output page.
        context = {"location": locations, "source": request.session['src'], "destination": request.session['dest'], 'type1': type1.title(), 'type2': '' if type2 == 'none' else type2.title()}

        return render(request, "planner/recommendations.html", context)


def myfunction(origin, destination):
    #Query google api to find out the directions from origin to destination
    api = (
        "https://maps.googleapis.com/maps/api/directions/xml?"
        + "origin="
        + origin
        + "&destination="
        + destination
        + "&key=AIzaSyAQ5u_nKOFgS_fsmE7cjDLxrqIuFRnjnk8"
    )
    #Receive the data from Google Cloud in XML Format
    data_dict = xmltodict.parse(requests.get(api).content)
    #Convert XML Formal to JSON
    results = json.loads(json.dumps(data_dict))

    #Put the Json data into meta.yaml file so inorder to have better readability
    f = open("meta.yaml", "w+")
    yaml.dump(results, f, allow_unicode=True)

    with open("meta.yaml", "r") as stream:
        try:
            yaml_content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    path = []

    #Access the yaml file contains to obtain total_distance,total_distance,start_location and end_location
    contents = yaml_content["DirectionsResponse"]["route"]["leg"]["step"]
    total_distance = yaml_content["DirectionsResponse"]["route"]["leg"]["distance"][
        "text"
    ]
    total_duration = yaml_content["DirectionsResponse"]["route"]["leg"]["duration"][
        "text"
    ]
    start_location = yaml_content["DirectionsResponse"]["route"]["leg"]["start_address"]
    end_location = yaml_content["DirectionsResponse"]["route"]["leg"]["end_address"]

    #Data Cleaning
    for i in contents:
        directions = i["html_instructions"].replace("<b>", "")
        directions = directions.replace("</b>", "")
        directions = directions.replace("<wbr/>", "")
        directions = directions.replace('<div style="font-size:0.9em">', "")
        directions = directions.replace("</div>", "")
        path.append([i["distance"]["text"], i["duration"]["text"], directions])

    #Create and store the directions into sentences.txt to have a developer friendly document
    f = open("sentences.txt", "w")
    f.write("")
    f.close()

    f = open("sentences.txt", "a")
    f.write(start_location + "\n")
    f.close()

    for i in path:
        f = open("sentences.txt", "a")
        f.write(i[2] + "\n")
        f.close()

    f = open("sentences.txt", "a")
    f.write(end_location + "\n")
    f.close()
    return path, total_distance, total_duration

#This function takes in the information from the user to form trip itenary!
def directions(request):
    if request.method == "POST":
        #receive origin and destination from the user
        origin = request.POST.get("origin", "")
        destination = request.POST.get("dest", "")

        #receive preference type of trip from the users, we take in two types
        request.session['type1'] = request.POST.get("type", "")
        request.session['type2'] = request.POST.get("type2", "")
        request.session['src'] = origin
        request.session['dest'] = destination
        #Receive the start of the trip with data and time from the user
        date_type = request.POST.get("date_start", "")
        time_started = request.POST.get("start_time", "")

        #Convert the string time type to datetime object
        start_time = date_type + " " + time_started + ":00.00000"
        start_time_obj = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")

        #Call this function which determines the directions user has to follow from origin to destination!
        direct, total_distance, total_duration = myfunction(origin, destination)

        request.session['total_distance'] = total_distance
        request.session['total_duration'] = total_duration

        cities = []
        duration_list = []
        duration_list.append("Departed from " + origin)
        start = start_time_obj

        #This block of code is determine the ETA of the user at each direction points
        #Also determine the cities that the user encounters while travelling through this route!
        for i in direct:
            places = GeoText(i[2])
            for j in places.cities:
                if j not in cities:
                    cities.append(j)
            num_of_hours = 0
            a = i[1].split()
            if "hours" in a:
                num_of_hours = int(a[0])
                num_of_mins = int(a[2])
            else:
                num_of_mins = int(a[0])
            hours_added = datetime.timedelta(hours=num_of_hours, minutes=num_of_mins)
            start += hours_added
            string_time = start.strftime("%m/%d/%Y, %H:%M:%S")
            duration_list.append(i[2]+" Arrival Time : "+string_time)

        duration_list.append("Arrived at " + destination)
        final_dictionary = {"directions": duration_list, "cities": cities, "total_duration": total_duration, "total_distance": total_distance}
        return render(request, "planner/directions.html", final_dictionary)
