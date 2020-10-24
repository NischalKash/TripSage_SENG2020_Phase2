from __future__ import absolute_import
import json
from django.shortcuts import render
from django.http import HttpResponse
import requests
import xmltodict
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import yaml

TYPES_PLACE_MAP = {
    "adventures": ["tourist_attraction", "stadium"],
    "kids": ["amusement_park", "museum"],
    "relaxing": ["art_gallery", "church", "spa"],
}
def home(request):
    return render(request,'planner/home.html')

def data(request):
    if request.method == 'POST':
        origin = request.POST.get("origin", "")
        destination = request.POST.get("dest", "")
        type_trip = request.POST.get("type", "")
        final_data = {}
        complete_data = {}
        for place in TYPES_PLACE_MAP[type_trip]:
            api = (
                    "https://maps.googleapis.com/maps/api/" +
                    "place/textsearch/xml?query="
                    + place
                    + "+in+"
                    + destination
                    + "&key=AIzaSyAIsboWfXVchmgBxPGKG5lUF9AENUKcSI8")
            print(api)
            data_dict = xmltodict.parse(requests.get(api).content)
            results = json.loads(json.dumps(data_dict))

            list_items = []
            for item in results.items():
                list_items = item
            val = []
            for values in list_items[1].items():
                val.append(values)
            if len(val) > 1:
                for values in val[1][1][:3]:
                    loaded_r = json.loads(json.dumps(values))
                    complete_data[str(loaded_r["name"])] = str(loaded_r["rating"])
        final_data[destination] = complete_data
        api = (
                "https://maps.googleapis.com/maps/api/directions/xml?"
                + "origin="
                +origin+"&destination="
                +destination
                + "&key=AIzaSyAQ5u_nKOFgS_fsmE7cjDLxrqIuFRnjnk8"
        )
        data_dict = xmltodict.parse(requests.get(api).content)
        results = json.loads(json.dumps(data_dict))

        f = open('/Users/nischalkashyap/Downloads/Fall 2020/SE2020/meta.yaml', 'w+')
        yaml.dump(results, f, allow_unicode=True)

        with open("/Users/nischalkashyap/Downloads/Fall 2020/SE2020/meta.yaml", 'r') as stream:
            try:
                yaml_content = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        yaml_content['DirectionsResponse']['route']['leg']['step']
        geolocator = Nominatim(user_agent="Your_Name")
        location_origin = geolocator.geocode(origin)
        location_destination = geolocator.geocode(destination)
        location_origin = (location_origin.latitude,location_origin.longitude)
        location_destination = (location_destination.latitude,location_destination.longitude)
        distance_between = str(geodesic(location_origin, location_destination).km)+"kms"

        return HttpResponse(json.dumps(final_data))
