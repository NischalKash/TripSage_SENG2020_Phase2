from __future__ import absolute_import
from django.shortcuts import render
import xmltodict
import yaml
from places_recommendation import *
from geotext import GeoText


TYPES_PLACE_MAP = {
    "adventures": ["tourist_attraction", "stadium"],
    "kids": ["amusement_park", "museum"],
    "relaxing": ["art_gallery", "church", "spa"],
}


def home(request):
    return render(request, "planner/home.html")


def find_spots(request):
    if request.method == "POST":
        city = request.POST.get("city", "")
        tourist_spots1 = getRecommendation(city,type1)
        tourist_spots2 = getRecommendation(city,type2)
        f = open('user_recommended1.yaml', 'w+')
        yaml.dump(tourist_spots1, f, allow_unicode=True)
        f = open('user_recommended2.yaml', 'w+')
        yaml.dump(tourist_spots2, f, allow_unicode=True)

        # tourist_spots contains all the recommended places a user can visit when he traverses through his trip!
        # render a html template here but make sure that he can enter a city again if he wants in the following template

def myfunction(origin,destination):
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

def directions(request):
    if request.method == "POST":
        origin = request.POST.get("origin", "")
        destination = request.POST.get("dest", "")
        global type1
        global type2
        type1 = request.POST.get("type", "")
        type2 = request.POST.get("type2", "")
        direct = myfunction(origin,destination)
        cities = []
        for i in direct:
            places = GeoText(i[2])
            for j in places.cities:
                if j not in cities:
                    cities.append(j)
        #Here in the directions.html, you have to display the routes and the cities users can enter!
        #Also display the total_distance and total_duration taken to travel
        return render(request, 'planner/directions.html')
