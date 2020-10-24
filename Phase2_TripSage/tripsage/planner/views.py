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

        f = open('meta.yaml', 'w+')
        yaml.dump(results, f, allow_unicode=True)

        with open("meta.yaml", 'r') as stream:
            try:
                yaml_content = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        path = []
        contents = yaml_content['DirectionsResponse']['route']['leg']['step']
        total_distance = yaml_content['DirectionsResponse']['route']['leg']['distance']['text']
        total_duration = yaml_content['DirectionsResponse']['route']['leg']['duration']['text']
        start_location = yaml_content['DirectionsResponse']['route']['leg']['end_address']
        end_location = yaml_content['DirectionsResponse']['route']['leg']['start_address']

        for i in contents:
            directions = i['html_instructions'].replace('<b>',"")
            directions = directions.replace('</b>', "")
            directions = directions.replace('<wbr/>', "")
            path.append([i['distance']['text'],i['duration']['text'],directions])
        f = open("sentences.txt", "w")
        f.write("")
        f.close()
        for i in path:
            f = open("sentences.txt", "a")
            f.write(i[2]+"\n")
            f.close()


        return HttpResponse(json.dumps(final_data))
