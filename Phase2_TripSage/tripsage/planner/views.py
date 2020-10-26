from __future__ import absolute_import
from django.shortcuts import render
import xmltodict
import yaml
from places_recommendation import *
from geotext import GeoText
import datetime

TYPES_PLACE_MAP = {
    "adventures": ["tourist_attraction", "stadium"],
    "kids": ["amusement_park", "museum"],
    "relaxing": ["art_gallery", "church", "spa"],
}

#Base Function, which displays the home page
def home(request):
    return render(request, "planner/home.html")

def find_spots(request):
    if request.method == "POST":
        #Receive the city name that the user wants to review through as per his wish
        city = request.POST.get("city", "")

        #This could be none as well thats why we have assigned it initially as empty
        tourist_spots2 = ""

        #Call the function in places_recommendations.py file which we have imported which will return a dictionary of all the
        #suggested tourist spots according to the city entry by User

        tourist_spots1 = getRecommendation(city,type1)
        if type2 != 'none':
            tourist_spots2 = getRecommendation(city,type2)

        #Dump the data into the yaml file so that we have a better code readability
        f = open('user_recommended1.yaml', 'w+')
        yaml.dump(tourist_spots1, f, allow_unicode=True)
        f = open("user_recommended2.yaml", "w+")
        yaml.dump(tourist_spots2, f, allow_unicode=True)

        # tourist_spots contains all the recommended places a user can visit when he traverses through his trip!
        # render a html template here but make sure that he can enter a city again if he wants in the following template

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
    total_distance = yaml_content["DirectionsResponse"]["route"]["leg"]["duration"][
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
    return path

#This function takes in the information from the user to form trip itenary!
def directions(request):
    if request.method == "POST":
        #receive origin and destination from the user
        origin = request.POST.get("origin", "")
        destination = request.POST.get("dest", "")
        global type1
        global type2

        #receive preference type of trip from the users, we take in two types
        type1 = request.POST.get("type", "")
        type2 = request.POST.get("type2", "")

        #Receive the start of the trip with data and time from the user
        date_type = request.POST.get("date_start", "")
        time_started = request.POST.get("start_time", "")

        #Convert the string time type to datetime object
        start_time = date_type + " " + time_started + ":00.00000"
        start_time_obj = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")

        #Call this function which determines the directions user has to follow from origin to destination!
        direct = myfunction(origin, destination)
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
        final_dictionary = {"directions": duration_list, "cities": cities}
        return render(request, "planner/directions.html", final_dictionary)
