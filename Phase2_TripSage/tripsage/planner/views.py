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
        city = request.POST.get("city", "")
        tourist_spots2 = ""
        tourist_spots1 = getRecommendation(city,type1)
        if type2 != 'none':
            tourist_spots2 = getRecommendation(city,type2)
        f = open('user_recommended1.yaml', 'w+')
        yaml.dump(tourist_spots1, f, allow_unicode=True)
        f = open("user_recommended2.yaml", "w+")
        yaml.dump(tourist_spots2, f, allow_unicode=True)


        # tourist_spots contains all the recommended places a user can visit when he traverses through his trip!
        # render a html template here but make sure that he can enter a city again if he wants in the following template


def myfunction(origin, destination):
    api = (
        "https://maps.googleapis.com/maps/api/directions/xml?"
        + "origin="
        + origin
        + "&destination="
        + destination
        + "&key=AIzaSyAQ5u_nKOFgS_fsmE7cjDLxrqIuFRnjnk8"
    )
    data_dict = xmltodict.parse(requests.get(api).content)
    results = json.loads(json.dumps(data_dict))

    f = open("meta.yaml", "w+")
    yaml.dump(results, f, allow_unicode=True)

    with open("meta.yaml", "r") as stream:
        try:
            yaml_content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    path = []
    contents = yaml_content["DirectionsResponse"]["route"]["leg"]["step"]
    total_distance = yaml_content["DirectionsResponse"]["route"]["leg"]["distance"][
        "text"
    ]
    total_duration = yaml_content["DirectionsResponse"]["route"]["leg"]["duration"][
        "text"
    ]
    start_location = yaml_content["DirectionsResponse"]["route"]["leg"]["start_address"]
    end_location = yaml_content["DirectionsResponse"]["route"]["leg"]["end_address"]

    for i in contents:
        directions = i["html_instructions"].replace("<b>", "")
        directions = directions.replace("</b>", "")
        directions = directions.replace("<wbr/>", "")
        directions = directions.replace('<div style="font-size:0.9em">', "")
        directions = directions.replace("</div>", "")
        path.append([i["distance"]["text"], i["duration"]["text"], directions])
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
        origin = request.POST.get("origin", "")
        destination = request.POST.get("dest", "")
        global type1
        global type2
        type1 = request.POST.get("type", "")
        type2 = request.POST.get("type2", "")
        date_type = request.POST.get("date_start", "")
        time_started = request.POST.get("start_time", "")
        print(date_type,type(date_type))
        print(time_started,type(time_started))
        start_time = date_type + " " + time_started + ":00.00000"
        start_time_obj = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S.%f")
        direct = myfunction(origin, destination)
        cities = []
        duration_list = []
        duration_list.append("Departed from " + origin)
        start = start_time_obj
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
