from __future__ import absolute_import
import json
from django.shortcuts import render
from django.http import HttpResponse
import requests
import xmltodict

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
                    + "&key=AIzaSyAIsboWfXVchmgBxPGKG5lUF9AENUKcSI8"
                )
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
        return HttpResponse(json.dumps(final_data))
