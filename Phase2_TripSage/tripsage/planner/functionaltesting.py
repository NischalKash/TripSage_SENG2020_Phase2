from __future__ import absolute_import
import xmltodict
import yaml
import requests, json
import googlemaps
import time
import datetime
from geotext import GeoText

def Places_Recommendation(gmaps, Place, PlaceType):
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
        "kids": ["amusement_park", "museum", "restaurant"],
        "relaxing": ["art_gallery", "church", "spa","park"],
        "other": ["hospital","police"],
    }

    if type1 == "adventures":
        dictionary = {}
        if city not in dictionary:
            dictionary[city] = {}
        dictionary[city]["tourist_attraction"] = Places_Recommendation(gmaps, city, "tourist_attraction")
        dictionary[city]["stadium"] = Places_Recommendation(gmaps, city, "stadium")[:3]
        dictionary[city]["zoo"] = Places_Recommendation(gmaps, city, "zoo")[:3]
        return dictionary

    elif type1 == "kids":
        dictionary = {}
        if city not in dictionary:
            dictionary[city] = {}
        dictionary[city]["amusement_park"] = Places_Recommendation(gmaps, city, "amusement_park")[:3]
        dictionary[city]["museum"] = Places_Recommendation(gmaps, city, "museum")[:3]
        dictionary[city]["restaurant"] = Places_Recommendation(gmaps, city, "restaurant")[:3]
        return dictionary

    elif type1 == "relaxing":
        dictionary = {}
        if city not in dictionary:
            dictionary[city] = {}
        dictionary[city]["art_gallery"] = Places_Recommendation(gmaps, city, "art_gallery")[:3]
        dictionary[city]["church"] = Places_Recommendation(gmaps, city, "church")[:3]
        dictionary[city]["spa"] = Places_Recommendation(gmaps, city, "spa")[:3]
        dictionary[city]["park"] = Places_Recommendation(gmaps, city, "park")[:3]
        return dictionary

    elif type1 == "other":
        dictionary = {}
        if city not in dictionary:
            dictionary[city] = {}
        dictionary[city]["hospital"] = Places_Recommendation(gmaps, city, "hospital")[:3]
        dictionary[city]["police"] = Places_Recommendation(gmaps, city, "police")[:3]
        return dictionary
    else:
        return "Please Enter the correct options"

def find_spots(city):
    tourist_spots2 = ""
    tourist_spots1 = getRecommendation(city, type1)
    if type2 != 'none':
        tourist_spots2 = getRecommendation(city, type2)
    return [tourist_spots1,tourist_spots2]

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

    f = open("meta_functional.yaml", "w+")
    yaml.dump(results, f, allow_unicode=True)

    with open("meta_functional.yaml", "r") as stream:
        try:
            yaml_content = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    path = []
    contents = yaml_content["DirectionsResponse"]["route"]["leg"]["step"]
    start_location = yaml_content["DirectionsResponse"]["route"]["leg"]["start_address"]
    end_location = yaml_content["DirectionsResponse"]["route"]["leg"]["end_address"]

    for i in contents:
        directions = i["html_instructions"].replace("<b>", "")
        directions = directions.replace("</b>", "")
        directions = directions.replace("<wbr/>", "")
        directions = directions.replace("<div style=\"font-size:0.9em\">", "")
        directions = directions.replace("</div>", "")
        path.append([i["distance"]["text"], i["duration"]["text"], directions])
    f = open("sentences_functional.txt", "w")
    f.write("")
    f.close()

    f = open("sentences_functional.txt", "a")
    f.write(start_location + "\n")
    f.close()

    for i in path:
        f = open("sentences_functional.txt", "a")
        f.write(i[2] + "\n")
        f.close()

    f = open("sentences_functional.txt", "a")
    f.write(end_location + "\n")
    f.close()
    return path

def directions(origin,destination,date_type,time_started):
    start_time = date_type + " " + time_started + ":00.00000"
    start_time_obj = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f')
    direct = myfunction(origin,destination)
    cities = []
    duration_list = []
    duration_list.append("Departed from "+origin)
    start = start_time_obj
    for i in direct:
        places = GeoText(i[2])
        for j in places.cities:
            if j not in cities:
                cities.append(j)
        num_of_hours = 0
        a = i[1].split()
        if 'hours' in a:
            num_of_hours = int(a[0])
            num_of_mins = int(a[2])
        else:
            num_of_mins = int(a[0])
        hours_added = datetime.timedelta(hours=num_of_hours, minutes=num_of_mins)
        start += hours_added
        string_time = start.strftime("%m/%d/%Y, %H:%M:%S")
        duration_list.append(i[2]+" Arrival Time : "+string_time)

    duration_list.append("Arrived at "+destination)
    final_dictionary = {'directions': duration_list, 'cities': cities}
    return final_dictionary

global type1
global type2
origin = "Raleigh"
destination = "Seattle"
type1 = "adventures"
type2 = "kids"
date_type = "2020-10-29"
time_started = "22:48"

returned_output = directions(origin,destination,date_type,time_started)
expected_output = {'directions': ['Departed from Raleigh', 'Head north on S Wilmington St toward New Bern Pl Arrival Time : 10/29/2020, 22:49:00', 'Turn left onto E Edenton St Arrival Time : 10/29/2020, 22:50:00', 'Turn right onto N McDowell St Arrival Time : 10/29/2020, 22:51:00', 'N McDowell St turns slightly right and becomes Capital Blvd Arrival Time : 10/29/2020, 22:52:00', 'Take the ramp to Wade Ave Arrival Time : 10/29/2020, 22:53:00', 'Continue onto Wade Ave Arrival Time : 10/29/2020, 22:54:00', 'Slight left to stay on Wade Ave Arrival Time : 10/29/2020, 22:55:00', 'Continue straight to stay on Wade Ave Arrival Time : 10/29/2020, 23:01:00', 'Keep left to continue on Wade Avenue, follow signs for I-40 W/RDU Intl Airport/Durham/Blue Ridge Rd Arrival Time : 10/29/2020, 23:04:00', 'Merge onto I-40 W Arrival Time : 10/29/2020, 23:57:00', 'Take exit 131 for I-40 W toward I-785 N/Greensboro/Winston-Salem Arrival Time : 10/29/2020, 23:58:00', 'Keep left to continue on I-40 W/I-85BL S Arrival Time : 10/30/2020, 00:05:00', 'Keep right at the fork to continue on I-40 W/US-220 S, follow signs for Interstate 40 W/Winston - SalemContinue to follow I-40 W Arrival Time : 10/30/2020, 00:16:00', 'Take exit 206 for US-421 N toward I-40BL/Kernersville/Winston-Salem/Downtown Arrival Time : 10/30/2020, 00:17:00', 'Continue onto US-421 N Arrival Time : 10/30/2020, 00:29:00', 'Take exit 232B for US-52 N/US-311 N/NC-8 N toward Mount Airy/Smith Reynolds/Airport Arrival Time : 10/30/2020, 00:30:00', 'Merge onto NC-8 N/US-52 NContinue to follow US-52 N Arrival Time : 10/30/2020, 00:59:00', 'Continue onto I-74 W Arrival Time : 10/30/2020, 01:09:00', 'Take the exit onto I-74 W/I-77 N toward Wytheville Arrival Time : 10/30/2020, 01:11:00', 'Keep left to continue on I-77 NEntering Virginia Arrival Time : 10/30/2020, 01:43:00', 'Take the exit on the left onto I-77 N/I-81 S toward Bluefield/Wytheville Arrival Time : 10/30/2020, 01:51:00', 'Take exit 72 for I-77 N toward Bluefield/Charleston W.VA Arrival Time : 10/30/2020, 01:52:00', 'Continue onto I-77 NToll roadEntering West Virginia Arrival Time : 10/30/2020, 03:57:00', 'Keep left to continue on I-64 W Arrival Time : 10/30/2020, 04:14:00', 'Take exit 40 toward Winfield/Pt. Pleasant Arrival Time : 10/30/2020, 04:15:00', 'Merge onto US-35 NEntering Ohio Arrival Time : 10/30/2020, 04:16:00', 'Keep left at the fork to continue on US-35 W, follow signs for Dayton Arrival Time : 10/30/2020, 05:12:00', 'Take the US-35 W exit on the left toward Dayton Arrival Time : 10/30/2020, 05:13:00', 'Continue onto US-35 W Arrival Time : 10/30/2020, 05:27:00', 'Take the exit onto I-75 N toward Toledo Arrival Time : 10/30/2020, 05:35:00', 'Take exit 61 to merge onto I-70 W toward Airport/IndianapolisEntering Indiana Arrival Time : 10/30/2020, 05:36:00', 'Take exit 90 to merge onto I-465 N Arrival Time : 10/30/2020, 05:38:00', 'Keep left to stay on I-465 N Arrival Time : 10/30/2020, 05:39:00', 'Keep left to stay on I-465 N Arrival Time : 10/30/2020, 05:48:00', 'Keep left to continue on I-465 W Arrival Time : 10/30/2020, 05:54:00', 'Keep left at the fork to continue on I-865 W, follow signs for I-65 N/Chicago Arrival Time : 10/30/2020, 05:58:00', 'Merge onto I-65 N Arrival Time : 10/30/2020, 05:59:00', 'Keep left to stay on I-65 N Arrival Time : 10/30/2020, 06:00:00', 'Take exit 259A to merge onto I-80 W/I-94 W/US-6 W toward ChicagoContinue to follow I-80 WToll roadEntering Illinois Arrival Time : 10/30/2020, 06:19:00', 'Keep left at the fork to continue on I-294 NToll road Arrival Time : 10/30/2020, 06:52:00', 'Take exit 40 to merge onto I-90 W toward RockfordToll road Arrival Time : 10/30/2020, 06:54:00', 'Keep left at the fork to stay on I-90 WToll road Arrival Time : 10/30/2020, 07:02:00', 'Keep left to stay on I-90 WToll road Arrival Time : 10/30/2020, 07:14:00', 'Keep left at the fork to stay on I-90 WToll roadEntering Wisconsin Arrival Time : 10/30/2020, 10:03:00', 'Keep left at the fork to stay on I-90 W, follow signs for Tomah/La CrosseEntering Minnesota Arrival Time : 10/30/2020, 10:46:00', 'Keep left to stay on I-90 W Arrival Time : 10/30/2020, 10:50:00', 'Take exit 267 toward Nodine Arrival Time : 10/30/2020, 10:51:00', 'Merge onto I-90 WEntering South Dakota Arrival Time : 10/30/2020, 20:00:00', 'Take exit 23 for SD-34 W toward Whitewood Arrival Time : 10/30/2020, 20:01:00', 'Turn right onto SD-34 W Arrival Time : 10/30/2020, 20:18:00', 'Turn right onto US-85 N/5th AveContinue to follow US-85 NPass by Pizza Hut (on the left in 0.6&nbsp;mi) Arrival Time : 10/30/2020, 20:24:00', 'Turn left onto US-212 W/N Alzada RdContinue to follow US-212 WPassing through WyomingEntering Montana Arrival Time : 10/30/2020, 20:25:00', 'Turn left onto US-212 W/Holt StContinue to follow US-212 W Arrival Time : 10/30/2020, 20:26:00', 'Merge onto I-90 W/US-212 W/US-87 N via the ramp to Billings Arrival Time : 10/30/2020, 21:11:00', 'Take the I-90 W exit on the left toward Billings Arrival Time : 10/30/2020, 21:12:00', 'Continue onto I-90 WPassing through IdahoEntering Washington Arrival Time : 10/31/2020, 05:59:00', 'Keep left to stay on I-90 W Arrival Time : 10/31/2020, 09:14:00', 'Take exit 2C for I-5 N Arrival Time : 10/31/2020, 09:15:00', 'Keep right, follow signs for Madison St/Convention Center and merge onto 7th Ave Arrival Time : 10/31/2020, 09:16:00', 'Turn left after Blink Optical at The Polyclinic (on the right) Arrival Time : 10/31/2020, 09:17:00', 'Arrived at Seattle'], 'cities': ['New Bern', 'Durham', 'Greensboro', 'Winston-Salem', 'Kernersville', 'Charleston', 'Virginia', 'Dayton', 'Toledo', 'Chicago', 'Montana', 'Billings', 'Washington']}

returned_output2 = find_spots(destination)
print(returned_output2)
expected_output2 = [{'Seattle': {'tourist_attraction': [{'formatted_address': '9404 E Marginal Way S, Seattle, WA 98108, USA', 'formatted_phone_number': '(206) 764-5700', 'geometry': {'location': {'lat': 47.5185379, 'lng': -122.2968545}}, 'name': 'The Museum of Flight', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1700'}, 'open': {'day': 0, 'time': '1000'}}, {'close': {'day': 1, 'time': '1700'}, 'open': {'day': 1, 'time': '1000'}}, {'close': {'day': 4, 'time': '1700'}, 'open': {'day': 4, 'time': '1000'}}, {'close': {'day': 5, 'time': '1700'}, 'open': {'day': 5, 'time': '1000'}}, {'close': {'day': 6, 'time': '1700'}, 'open': {'day': 6, 'time': '1000'}}], 'weekday_text': ['Monday: 10:00 AM – 5:00 PM', 'Tuesday: Closed', 'Wednesday: Closed', 'Thursday: 10:00 AM – 5:00 PM', 'Friday: 10:00 AM – 5:00 PM', 'Saturday: 10:00 AM – 5:00 PM', 'Sunday: 10:00 AM – 5:00 PM']}, 'website': 'http://www.museumofflight.org/'}, {'formatted_address': '400 Broad St, Seattle, WA 98109, USA', 'formatted_phone_number': '(206) 905-2100', 'geometry': {'location': {'lat': 47.6205063, 'lng': -122.3492774}}, 'name': 'Space Needle', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '2100'}, 'open': {'day': 0, 'time': '1100'}}, {'close': {'day': 1, 'time': '1800'}, 'open': {'day': 1, 'time': '1100'}}, {'close': {'day': 2, 'time': '1800'}, 'open': {'day': 2, 'time': '1100'}}, {'close': {'day': 3, 'time': '1800'}, 'open': {'day': 3, 'time': '1100'}}, {'close': {'day': 4, 'time': '2100'}, 'open': {'day': 4, 'time': '1100'}}, {'close': {'day': 5, 'time': '2100'}, 'open': {'day': 5, 'time': '1100'}}, {'close': {'day': 6, 'time': '2100'}, 'open': {'day': 6, 'time': '1100'}}], 'weekday_text': ['Monday: 11:00 AM – 6:00 PM', 'Tuesday: 11:00 AM – 6:00 PM', 'Wednesday: 11:00 AM – 6:00 PM', 'Thursday: 11:00 AM – 9:00 PM', 'Friday: 11:00 AM – 9:00 PM', 'Saturday: 11:00 AM – 9:00 PM', 'Sunday: 11:00 AM – 9:00 PM']}, 'website': 'https://www.spaceneedle.com/'}, {'formatted_address': '305 Harrison St, Seattle, WA 98109, USA', 'formatted_phone_number': '(206) 753-4940', 'geometry': {'location': {'lat': 47.620563, 'lng': -122.350466}}, 'name': 'Chihuly Garden and Glass', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1700'}, 'open': {'day': 0, 'time': '1100'}}, {'close': {'day': 1, 'time': '1700'}, 'open': {'day': 1, 'time': '1100'}}, {'close': {'day': 2, 'time': '1700'}, 'open': {'day': 2, 'time': '1100'}}, {'close': {'day': 3, 'time': '1700'}, 'open': {'day': 3, 'time': '1100'}}, {'close': {'day': 4, 'time': '1700'}, 'open': {'day': 4, 'time': '1100'}}, {'close': {'day': 5, 'time': '1700'}, 'open': {'day': 5, 'time': '1100'}}, {'close': {'day': 6, 'time': '1700'}, 'open': {'day': 6, 'time': '1100'}}], 'weekday_text': ['Monday: 11:00 AM – 5:00 PM', 'Tuesday: 11:00 AM – 5:00 PM', 'Wednesday: 11:00 AM – 5:00 PM', 'Thursday: 11:00 AM – 5:00 PM', 'Friday: 11:00 AM – 5:00 PM', 'Saturday: 11:00 AM – 5:00 PM', 'Sunday: 11:00 AM – 5:00 PM']}, 'website': 'http://chihulygardenandglass.com/'}, {'formatted_address': '325 5th Ave N, Seattle, WA 98109, USA', 'formatted_phone_number': '(206) 770-2700', 'geometry': {'location': {'lat': 47.6214824, 'lng': -122.3481245}}, 'name': 'Museum of Pop Culture', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1800'}, 'open': {'day': 0, 'time': '1000'}}, {'close': {'day': 5, 'time': '1800'}, 'open': {'day': 5, 'time': '1000'}}, {'close': {'day': 6, 'time': '1800'}, 'open': {'day': 6, 'time': '1000'}}], 'weekday_text': ['Monday: Closed', 'Tuesday: Closed', 'Wednesday: Closed', 'Thursday: Closed', 'Friday: 10:00 AM – 6:00 PM', 'Saturday: 10:00 AM – 6:00 PM', 'Sunday: 10:00 AM – 6:00 PM']}, 'website': 'http://www.mopop.org/'}, {'formatted_address': '305 Harrison St, Seattle, WA 98109, USA', 'formatted_phone_number': '(206) 684-7200', 'geometry': {'location': {'lat': 47.62191259999999, 'lng': -122.3516787}}, 'name': 'Seattle Center', 'website': 'http://www.seattlecenter.com/'}, {'formatted_address': '1000 4th Ave, Seattle, WA 98104, USA', 'formatted_phone_number': '(206) 386-4636', 'geometry': {'location': {'lat': 47.6067006, 'lng': -122.3325009}}, 'name': 'Seattle Public Library-Central Library', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 2, 'time': '1800'}, 'open': {'day': 2, 'time': '1200'}}, {'close': {'day': 4, 'time': '1800'}, 'open': {'day': 4, 'time': '1200'}}, {'close': {'day': 6, 'time': '1800'}, 'open': {'day': 6, 'time': '1200'}}], 'weekday_text': ['Monday: Closed', 'Tuesday: 12:00 – 6:00 PM', 'Wednesday: Closed', 'Thursday: 12:00 – 6:00 PM', 'Friday: Closed', 'Saturday: 12:00 – 6:00 PM', 'Sunday: Closed']}, 'website': 'https://www.spl.org/hours-and-locations/central-library'}, {'formatted_address': '6046 West Lake Sammamish Pkwy NE, Redmond, WA 98052, USA', 'formatted_phone_number': '(206) 477-7275', 'geometry': {'location': {'lat': 47.6594346, 'lng': -122.1087919}}, 'name': 'Marymoor Park', 'website': 'https://www.kingcounty.gov/services/parks-recreation/parks/parks-and-natural-lands/popular-parks/marymoor.aspx'}, {'formatted_address': '5500 Phinney Ave N, Seattle, WA 98103, USA', 'formatted_phone_number': '(206) 548-2500', 'geometry': {'location': {'lat': 47.6685161, 'lng': -122.3543444}}, 'name': 'Woodland Park Zoo', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1600'}, 'open': {'day': 0, 'time': '0930'}}, {'close': {'day': 1, 'time': '1600'}, 'open': {'day': 1, 'time': '0930'}}, {'close': {'day': 2, 'time': '1600'}, 'open': {'day': 2, 'time': '0930'}}, {'close': {'day': 3, 'time': '1300'}, 'open': {'day': 3, 'time': '0930'}}, {'close': {'day': 4, 'time': '1600'}, 'open': {'day': 4, 'time': '0930'}}, {'close': {'day': 5, 'time': '1600'}, 'open': {'day': 5, 'time': '0930'}}, {'close': {'day': 6, 'time': '1600'}, 'open': {'day': 6, 'time': '0930'}}], 'weekday_text': ['Monday: 9:30 AM – 4:00 PM', 'Tuesday: 9:30 AM – 4:00 PM', 'Wednesday: 9:30 AM – 1:00 PM', 'Thursday: 9:30 AM – 4:00 PM', 'Friday: 9:30 AM – 4:00 PM', 'Saturday: 9:30 AM – 4:00 PM', 'Sunday: 9:30 AM – 4:00 PM']}, 'website': 'http://www.zoo.org/'}, {'formatted_address': 'Aurora Ave N, Seattle, WA 98103, USA', 'formatted_phone_number': '(360) 705-7000', 'geometry': {'location': {'lat': 47.6467948, 'lng': -122.3473586}}, 'name': 'Aurora Bridge', 'opening_hours': {'open_now': True, 'periods': [{'open': {'day': 0, 'time': '0000'}}], 'weekday_text': ['Monday: Open 24 hours', 'Tuesday: Open 24 hours', 'Wednesday: Open 24 hours', 'Thursday: Open 24 hours', 'Friday: Open 24 hours', 'Saturday: Open 24 hours', 'Sunday: Open 24 hours']}, 'website': 'http://www.wsdot.wa.gov/'}, {'formatted_address': '704 Terry Ave, Seattle, WA 98104, USA', 'formatted_phone_number': '(206) 622-9250', 'geometry': {'location': {'lat': 47.6074789, 'lng': -122.324545}}, 'name': 'Frye Art Museum', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1700'}, 'open': {'day': 0, 'time': '1100'}}, {'close': {'day': 4, 'time': '1700'}, 'open': {'day': 4, 'time': '1100'}}, {'close': {'day': 5, 'time': '1700'}, 'open': {'day': 5, 'time': '1100'}}, {'close': {'day': 6, 'time': '1700'}, 'open': {'day': 6, 'time': '1100'}}], 'weekday_text': ['Monday: Closed', 'Tuesday: Closed', 'Wednesday: Closed', 'Thursday: 11:00 AM – 5:00 PM', 'Friday: 11:00 AM – 5:00 PM', 'Saturday: 11:00 AM – 5:00 PM', 'Sunday: 11:00 AM – 5:00 PM']}, 'website': 'https://fryemuseum.org/'}, {'formatted_address': '3801 Discovery Park Blvd, Seattle, WA 98199, USA', 'formatted_phone_number': '(206) 386-4236', 'geometry': {'location': {'lat': 47.65730199999999, 'lng': -122.405496}}, 'name': 'Discovery Park', 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2000'}, 'open': {'day': 0, 'time': '0400'}}, {'close': {'day': 1, 'time': '2000'}, 'open': {'day': 1, 'time': '0400'}}, {'close': {'day': 2, 'time': '2000'}, 'open': {'day': 2, 'time': '0400'}}, {'close': {'day': 3, 'time': '2000'}, 'open': {'day': 3, 'time': '0400'}}, {'close': {'day': 4, 'time': '2000'}, 'open': {'day': 4, 'time': '0400'}}, {'close': {'day': 5, 'time': '2000'}, 'open': {'day': 5, 'time': '0400'}}, {'close': {'day': 6, 'time': '2000'}, 'open': {'day': 6, 'time': '0400'}}], 'weekday_text': ['Monday: 4:00 AM – 8:00 PM', 'Tuesday: 4:00 AM – 8:00 PM', 'Wednesday: 4:00 AM – 8:00 PM', 'Thursday: 4:00 AM – 8:00 PM', 'Friday: 4:00 AM – 8:00 PM', 'Saturday: 4:00 AM – 8:00 PM', 'Sunday: 4:00 AM – 8:00 PM']}, 'website': 'http://www.seattle.gov/parks/find/parks/discovery-park'}, {'formatted_address': '2101 N Northlake Way, Seattle, WA 98103, USA', 'formatted_phone_number': '(206) 684-4075', 'geometry': {'location': {'lat': 47.6456308, 'lng': -122.3343532}}, 'name': 'Gas Works Park', 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2200'}, 'open': {'day': 0, 'time': '0600'}}, {'close': {'day': 1, 'time': '2200'}, 'open': {'day': 1, 'time': '0600'}}, {'close': {'day': 2, 'time': '2200'}, 'open': {'day': 2, 'time': '0600'}}, {'close': {'day': 3, 'time': '2200'}, 'open': {'day': 3, 'time': '0600'}}, {'close': {'day': 4, 'time': '2200'}, 'open': {'day': 4, 'time': '0600'}}, {'close': {'day': 5, 'time': '2200'}, 'open': {'day': 5, 'time': '0600'}}, {'close': {'day': 6, 'time': '2200'}, 'open': {'day': 6, 'time': '0600'}}], 'weekday_text': ['Monday: 6:00 AM – 10:00 PM', 'Tuesday: 6:00 AM – 10:00 PM', 'Wednesday: 6:00 AM – 10:00 PM', 'Thursday: 6:00 AM – 10:00 PM', 'Friday: 6:00 AM – 10:00 PM', 'Saturday: 6:00 AM – 10:00 PM', 'Sunday: 6:00 AM – 10:00 PM']}, 'website': 'http://www.seattle.gov/parks/find/parks/gas-works-park'}, {'formatted_address': '2901 Western Ave, Seattle, WA 98121, USA', 'formatted_phone_number': '(206) 654-3100', 'geometry': {'location': {'lat': 47.6166028, 'lng': -122.3553167}}, 'name': 'Olympic Sculpture Park', 'website': 'http://www.seattleartmuseum.org/visit/olympic-sculpture-park'}, {'formatted_address': '8011 Fauntleroy Way SW, Seattle, WA 98136, USA', 'formatted_phone_number': '(206) 684-4075', 'geometry': {'location': {'lat': 47.53057099999999, 'lng': -122.395992}}, 'name': 'Lincoln Park', 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2000'}, 'open': {'day': 0, 'time': '0400'}}, {'close': {'day': 1, 'time': '2000'}, 'open': {'day': 1, 'time': '0400'}}, {'close': {'day': 2, 'time': '2000'}, 'open': {'day': 2, 'time': '0400'}}, {'close': {'day': 3, 'time': '2000'}, 'open': {'day': 3, 'time': '0400'}}, {'close': {'day': 4, 'time': '2000'}, 'open': {'day': 4, 'time': '0400'}}, {'close': {'day': 5, 'time': '2000'}, 'open': {'day': 5, 'time': '0400'}}, {'close': {'day': 6, 'time': '2000'}, 'open': {'day': 6, 'time': '0400'}}], 'weekday_text': ['Monday: 4:00 AM – 8:00 PM', 'Tuesday: 4:00 AM – 8:00 PM', 'Wednesday: 4:00 AM – 8:00 PM', 'Thursday: 4:00 AM – 8:00 PM', 'Friday: 4:00 AM – 8:00 PM', 'Saturday: 4:00 AM – 8:00 PM', 'Sunday: 4:00 AM – 8:00 PM']}, 'website': 'http://www.seattle.gov/parks/find/parks/lincoln-park'}, {'formatted_address': '8498 Seaview Pl NW, Seattle, WA 98117, USA', 'formatted_phone_number': '(206) 684-4075', 'geometry': {'location': {'lat': 47.6917517, 'lng': -122.4030912}}, 'name': 'Golden Gardens Park', 'website': 'http://www.seattle.gov/parks/find/parks/golden-gardens-park'}, {'formatted_address': '1400 E Prospect St, Seattle, WA 98112, USA', 'formatted_phone_number': '(206) 654-3100', 'geometry': {'location': {'lat': 47.6302814, 'lng': -122.3142336}}, 'name': 'Asian Art Museum', 'website': 'http://www.seattleartmuseum.org/'}, {'formatted_address': '1101 Alaskan Way Pier 55, Suite 201, Seattle, WA 98101, USA', 'formatted_phone_number': '(206) 623-1445', 'geometry': {'location': {'lat': 47.60505999999999, 'lng': -122.340267}}, 'name': 'Argosy Cruises - Seattle Waterfront', 'website': 'https://www.argosycruises.com/?utm_source=local&utm_medium=organic&utm_campaign=gmb'}, {'formatted_address': '4300 15th Ave NE, Seattle, WA 98105, USA', 'formatted_phone_number': '(206) 543-7907', 'geometry': {'location': {'lat': 47.660332, 'lng': -122.3115487}}, 'name': 'Burke Museum of Natural History and Culture', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1700'}, 'open': {'day': 0, 'time': '1000'}}, {'close': {'day': 2, 'time': '1700'}, 'open': {'day': 2, 'time': '1000'}}, {'close': {'day': 3, 'time': '1700'}, 'open': {'day': 3, 'time': '1000'}}, {'close': {'day': 4, 'time': '1700'}, 'open': {'day': 4, 'time': '1000'}}, {'close': {'day': 5, 'time': '1700'}, 'open': {'day': 5, 'time': '1000'}}, {'close': {'day': 6, 'time': '1700'}, 'open': {'day': 6, 'time': '1000'}}], 'weekday_text': ['Monday: Closed', 'Tuesday: 10:00 AM – 5:00 PM', 'Wednesday: 10:00 AM – 5:00 PM', 'Thursday: 10:00 AM – 5:00 PM', 'Friday: 10:00 AM – 5:00 PM', 'Saturday: 10:00 AM – 5:00 PM', 'Sunday: 10:00 AM – 5:00 PM']}, 'website': 'http://www.burkemuseum.org/'}, {'formatted_address': '5900 Lake Washington Blvd S, Seattle, WA 98118, USA', 'formatted_phone_number': '(206) 684-4396', 'geometry': {'location': {'lat': 47.5496046, 'lng': -122.2573574}}, 'name': 'Seward Park', 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2000'}, 'open': {'day': 0, 'time': '0600'}}, {'close': {'day': 1, 'time': '2000'}, 'open': {'day': 1, 'time': '0600'}}, {'close': {'day': 2, 'time': '2000'}, 'open': {'day': 2, 'time': '0600'}}, {'close': {'day': 3, 'time': '2000'}, 'open': {'day': 3, 'time': '0600'}}, {'close': {'day': 4, 'time': '2000'}, 'open': {'day': 4, 'time': '0600'}}, {'close': {'day': 5, 'time': '2000'}, 'open': {'day': 5, 'time': '0600'}}, {'close': {'day': 6, 'time': '2000'}, 'open': {'day': 6, 'time': '0600'}}], 'weekday_text': ['Monday: 6:00 AM – 8:00 PM', 'Tuesday: 6:00 AM – 8:00 PM', 'Wednesday: 6:00 AM – 8:00 PM', 'Thursday: 6:00 AM – 8:00 PM', 'Friday: 6:00 AM – 8:00 PM', 'Saturday: 6:00 AM – 8:00 PM', 'Sunday: 6:00 AM – 8:00 PM']}, 'website': 'http://www.seattle.gov/parks/find/parks/seward-park'}, {'formatted_address': '8415 Paine Field Blvd, Mukilteo, WA 98275, USA', 'formatted_phone_number': '(800) 464-1476', 'geometry': {'location': {'lat': 47.9212293, 'lng': -122.2901598}}, 'name': 'Boeing Future of Flight\u200b', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1700'}, 'open': {'day': 0, 'time': '0900'}}, {'close': {'day': 1, 'time': '1700'}, 'open': {'day': 1, 'time': '0900'}}, {'close': {'day': 4, 'time': '1700'}, 'open': {'day': 4, 'time': '0900'}}, {'close': {'day': 5, 'time': '1700'}, 'open': {'day': 5, 'time': '0900'}}, {'close': {'day': 6, 'time': '1700'}, 'open': {'day': 6, 'time': '0900'}}], 'weekday_text': ['Monday: 9:00 AM – 5:00 PM', 'Tuesday: Closed', 'Wednesday: Closed', 'Thursday: 9:00 AM – 5:00 PM', 'Friday: 9:00 AM – 5:00 PM', 'Saturday: 9:00 AM – 5:00 PM', 'Sunday: 9:00 AM – 5:00 PM']}, 'website': 'https://www.boeingfutureofflight.com/'}], 'stadium': [{'formatted_address': '3800 Montlake Blvd NE, Seattle, WA 98195, USA', 'formatted_phone_number': '(206) 543-2210', 'geometry': {'location': {'lat': 47.65035, 'lng': -122.3016111}}, 'name': 'Husky Stadium', 'website': 'http://www.gohuskies.com/'}, {'formatted_address': '401 5th Ave N, Seattle, WA 98109, USA', 'formatted_phone_number': '(206) 252-1800', 'geometry': {'location': {'lat': 47.62332459999999, 'lng': -122.3489324}}, 'name': 'Memorial Stadium'}, {'formatted_address': '9809 NE 188th St, Bothell, WA 98011, USA', 'formatted_phone_number': '(425) 408-6001', 'geometry': {'location': {'lat': 47.7642479, 'lng': -122.20966}}, 'name': 'Pop Keeney Stadium', 'website': 'http://www.bothellfootball.net/stadium.html'}], 'zoo': [{'formatted_address': '5500 Phinney Ave N, Seattle, WA 98103, USA', 'formatted_phone_number': '(206) 548-2500', 'geometry': {'location': {'lat': 47.6685161, 'lng': -122.3543444}}, 'name': 'Woodland Park Zoo', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1600'}, 'open': {'day': 0, 'time': '0930'}}, {'close': {'day': 1, 'time': '1600'}, 'open': {'day': 1, 'time': '0930'}}, {'close': {'day': 2, 'time': '1600'}, 'open': {'day': 2, 'time': '0930'}}, {'close': {'day': 3, 'time': '1300'}, 'open': {'day': 3, 'time': '0930'}}, {'close': {'day': 4, 'time': '1600'}, 'open': {'day': 4, 'time': '0930'}}, {'close': {'day': 5, 'time': '1600'}, 'open': {'day': 5, 'time': '0930'}}, {'close': {'day': 6, 'time': '1600'}, 'open': {'day': 6, 'time': '0930'}}], 'weekday_text': ['Monday: 9:30 AM – 4:00 PM', 'Tuesday: 9:30 AM – 4:00 PM', 'Wednesday: 9:30 AM – 1:00 PM', 'Thursday: 9:30 AM – 4:00 PM', 'Friday: 9:30 AM – 4:00 PM', 'Saturday: 9:30 AM – 4:00 PM', 'Sunday: 9:30 AM – 4:00 PM']}, 'website': 'http://www.zoo.org/'}, {'formatted_address': '5400 N Pearl St, Tacoma, WA 98407, USA', 'formatted_phone_number': '(253) 404-3800', 'geometry': {'location': {'lat': 47.30490829999999, 'lng': -122.5208083}}, 'name': 'Point Defiance Zoo & Aquarium', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1600'}, 'open': {'day': 0, 'time': '0900'}}, {'close': {'day': 1, 'time': '1600'}, 'open': {'day': 1, 'time': '0900'}}, {'close': {'day': 4, 'time': '1600'}, 'open': {'day': 4, 'time': '0900'}}, {'close': {'day': 5, 'time': '1600'}, 'open': {'day': 5, 'time': '0900'}}, {'close': {'day': 6, 'time': '1600'}, 'open': {'day': 6, 'time': '0900'}}], 'weekday_text': ['Monday: 9:00 AM – 4:00 PM', 'Tuesday: Closed', 'Wednesday: Closed', 'Thursday: 9:00 AM – 4:00 PM', 'Friday: 9:00 AM – 4:00 PM', 'Saturday: 9:00 AM – 4:00 PM', 'Sunday: 9:00 AM – 4:00 PM']}, 'website': 'http://www.pdza.org/'}, {'formatted_address': '19525 SE 54th St, Issaquah, WA 98027, USA', 'formatted_phone_number': '(425) 391-5508', 'geometry': {'location': {'lat': 47.5525131, 'lng': -122.0807986}}, 'name': 'Cougar Mountain Zoo', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1700'}, 'open': {'day': 0, 'time': '0930'}}, {'close': {'day': 3, 'time': '1700'}, 'open': {'day': 3, 'time': '0930'}}, {'close': {'day': 4, 'time': '1700'}, 'open': {'day': 4, 'time': '0930'}}, {'close': {'day': 5, 'time': '1700'}, 'open': {'day': 5, 'time': '0930'}}, {'close': {'day': 6, 'time': '1700'}, 'open': {'day': 6, 'time': '0930'}}], 'weekday_text': ['Monday: Closed', 'Tuesday: Closed', 'Wednesday: 9:30 AM – 5:00 PM', 'Thursday: 9:30 AM – 5:00 PM', 'Friday: 9:30 AM – 5:00 PM', 'Saturday: 9:30 AM – 5:00 PM', 'Sunday: 9:30 AM – 5:00 PM']}, 'website': 'http://www.cougarmountainzoo.org/'}]}}, {'Seattle': {'amusement_park': [{'formatted_address': '7300 Fun Center Way, Tukwila, WA 98188, USA', 'formatted_phone_number': '(425) 228-7300', 'geometry': {'location': {'lat': 47.46561699999999, 'lng': -122.242975}}, 'name': "Tukwila Family Fun Center & Bullwinkle's Restaurant", 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '2000'}, 'open': {'day': 0, 'time': '1100'}}, {'close': {'day': 1, 'time': '2000'}, 'open': {'day': 1, 'time': '1200'}}, {'close': {'day': 2, 'time': '2000'}, 'open': {'day': 2, 'time': '1200'}}, {'close': {'day': 3, 'time': '2000'}, 'open': {'day': 3, 'time': '1200'}}, {'close': {'day': 4, 'time': '2000'}, 'open': {'day': 4, 'time': '1200'}}, {'close': {'day': 5, 'time': '2100'}, 'open': {'day': 5, 'time': '1200'}}, {'close': {'day': 6, 'time': '2100'}, 'open': {'day': 6, 'time': '1100'}}], 'weekday_text': ['Monday: 12:00 – 8:00 PM', 'Tuesday: 12:00 – 8:00 PM', 'Wednesday: 12:00 – 8:00 PM', 'Thursday: 12:00 – 8:00 PM', 'Friday: 12:00 – 9:00 PM', 'Saturday: 11:00 AM – 9:00 PM', 'Sunday: 11:00 AM – 8:00 PM']}, 'website': 'http://www.fun-center.com/'}, {'formatted_address': '1719 Maple Valley Hwy, Renton, WA 98057, USA', 'formatted_phone_number': '(425) 430-6780', 'geometry': {'location': {'lat': 47.4817697, 'lng': -122.1949815}}, 'name': 'Henry Moses Aquatic Center', 'opening_hours': {'open_now': True, 'periods': [{'close': {'day': 0, 'time': '1400'}, 'open': {'day': 0, 'time': '1100'}}, {'close': {'day': 0, 'time': '1800'}, 'open': {'day': 0, 'time': '1500'}}, {'close': {'day': 1, 'time': '1400'}, 'open': {'day': 1, 'time': '1100'}}, {'close': {'day': 1, 'time': '1800'}, 'open': {'day': 1, 'time': '1500'}}, {'close': {'day': 1, 'time': '2030'}, 'open': {'day': 1, 'time': '1830'}}, {'close': {'day': 2, 'time': '1400'}, 'open': {'day': 2, 'time': '1100'}}, {'close': {'day': 2, 'time': '1800'}, 'open': {'day': 2, 'time': '1500'}}, {'close': {'day': 2, 'time': '2030'}, 'open': {'day': 2, 'time': '1930'}}, {'close': {'day': 3, 'time': '1400'}, 'open': {'day': 3, 'time': '1100'}}, {'close': {'day': 3, 'time': '1800'}, 'open': {'day': 3, 'time': '1500'}}, {'close': {'day': 3, 'time': '2030'}, 'open': {'day': 3, 'time': '1830'}}, {'close': {'day': 4, 'time': '1400'}, 'open': {'day': 4, 'time': '1100'}}, {'close': {'day': 4, 'time': '1800'}, 'open': {'day': 4, 'time': '1500'}}, {'close': {'day': 4, 'time': '2030'}, 'open': {'day': 4, 'time': '1930'}}, {'close': {'day': 5, 'time': '1400'}, 'open': {'day': 5, 'time': '1100'}}, {'close': {'day': 5, 'time': '1800'}, 'open': {'day': 5, 'time': '1500'}}, {'close': {'day': 5, 'time': '2030'}, 'open': {'day': 5, 'time': '1830'}}, {'close': {'day': 6, 'time': '1400'}, 'open': {'day': 6, 'time': '1100'}}, {'close': {'day': 6, 'time': '1800'}, 'open': {'day': 6, 'time': '1500'}}], 'weekday_text': ['Monday: 11:00 AM – 2:00 PM, 3:00 – 6:00 PM, 6:30 – 8:30 PM', 'Tuesday: 11:00 AM – 2:00 PM, 3:00 – 6:00 PM, 7:30 – 8:30 PM', 'Wednesday: 11:00 AM – 2:00 PM, 3:00 – 6:00 PM, 6:30 – 8:30 PM', 'Thursday: 11:00 AM – 2:00 PM, 3:00 – 6:00 PM, 7:30 – 8:30 PM', 'Friday: 11:00 AM – 2:00 PM, 3:00 – 6:00 PM, 6:30 – 8:30 PM', 'Saturday: 11:00 AM – 2:00 PM, 3:00 – 6:00 PM', 'Sunday: 11:00 AM – 2:00 PM, 3:00 – 6:00 PM']}, 'website': 'https://rentonwa.gov/city_hall/community_services/facilities/henry_moses_aquatic_center'}, {'formatted_address': '36201 Enchanted Pkwy S, Federal Way, WA 98003, USA', 'formatted_phone_number': '(253) 661-8000', 'geometry': {'location': {'lat': 47.2731529, 'lng': -122.3126059}}, 'name': 'Wild Waves Theme and Water Park', 'website': 'http://www.wildwaves.com/'}], 'museum': [{'formatted_address': '9404 E Marginal Way S, Seattle, WA 98108, USA', 'formatted_phone_number': '(206) 764-5700', 'geometry': {'location': {'lat': 47.5185379, 'lng': -122.2968545}}, 'name': 'The Museum of Flight', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1700'}, 'open': {'day': 0, 'time': '1000'}}, {'close': {'day': 1, 'time': '1700'}, 'open': {'day': 1, 'time': '1000'}}, {'close': {'day': 4, 'time': '1700'}, 'open': {'day': 4, 'time': '1000'}}, {'close': {'day': 5, 'time': '1700'}, 'open': {'day': 5, 'time': '1000'}}, {'close': {'day': 6, 'time': '1700'}, 'open': {'day': 6, 'time': '1000'}}], 'weekday_text': ['Monday: 10:00 AM – 5:00 PM', 'Tuesday: Closed', 'Wednesday: Closed', 'Thursday: 10:00 AM – 5:00 PM', 'Friday: 10:00 AM – 5:00 PM', 'Saturday: 10:00 AM – 5:00 PM', 'Sunday: 10:00 AM – 5:00 PM']}, 'website': 'http://www.museumofflight.org/'}, {'formatted_address': '305 Harrison St, Seattle, WA 98109, USA', 'formatted_phone_number': '(206) 753-4940', 'geometry': {'location': {'lat': 47.620563, 'lng': -122.350466}}, 'name': 'Chihuly Garden and Glass', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1700'}, 'open': {'day': 0, 'time': '1100'}}, {'close': {'day': 1, 'time': '1700'}, 'open': {'day': 1, 'time': '1100'}}, {'close': {'day': 2, 'time': '1700'}, 'open': {'day': 2, 'time': '1100'}}, {'close': {'day': 3, 'time': '1700'}, 'open': {'day': 3, 'time': '1100'}}, {'close': {'day': 4, 'time': '1700'}, 'open': {'day': 4, 'time': '1100'}}, {'close': {'day': 5, 'time': '1700'}, 'open': {'day': 5, 'time': '1100'}}, {'close': {'day': 6, 'time': '1700'}, 'open': {'day': 6, 'time': '1100'}}], 'weekday_text': ['Monday: 11:00 AM – 5:00 PM', 'Tuesday: 11:00 AM – 5:00 PM', 'Wednesday: 11:00 AM – 5:00 PM', 'Thursday: 11:00 AM – 5:00 PM', 'Friday: 11:00 AM – 5:00 PM', 'Saturday: 11:00 AM – 5:00 PM', 'Sunday: 11:00 AM – 5:00 PM']}, 'website': 'http://chihulygardenandglass.com/'}, {'formatted_address': '325 5th Ave N, Seattle, WA 98109, USA', 'formatted_phone_number': '(206) 770-2700', 'geometry': {'location': {'lat': 47.6214824, 'lng': -122.3481245}}, 'name': 'Museum of Pop Culture', 'opening_hours': {'open_now': False, 'periods': [{'close': {'day': 0, 'time': '1800'}, 'open': {'day': 0, 'time': '1000'}}, {'close': {'day': 5, 'time': '1800'}, 'open': {'day': 5, 'time': '1000'}}, {'close': {'day': 6, 'time': '1800'}, 'open': {'day': 6, 'time': '1000'}}], 'weekday_text': ['Monday: Closed', 'Tuesday: Closed', 'Wednesday: Closed', 'Thursday: Closed', 'Friday: 10:00 AM – 6:00 PM', 'Saturday: 10:00 AM – 6:00 PM', 'Sunday: 10:00 AM – 6:00 PM']}, 'website': 'http://www.mopop.org/'}], 'restaurant': [{'formatted_address': '411 University St, Seattle, WA 98101, USA', 'formatted_phone_number': '(206) 621-1700', 'geometry': {'location': {'lat': 47.608063, 'lng': -122.3339998}}, 'name': 'Fairmont Olympic Hotel - Seattle', 'opening_hours': {'open_now': True, 'periods': [{'open': {'day': 0, 'time': '0000'}}], 'weekday_text': ['Monday: Open 24 hours', 'Tuesday: Open 24 hours', 'Wednesday: Open 24 hours', 'Thursday: Open 24 hours', 'Friday: Open 24 hours', 'Saturday: Open 24 hours', 'Sunday: Open 24 hours']}, 'website': 'https://www.fairmont.com/seattle/?goto=fiche_hotel&code_hotel=A580&merchantid=seo-maps-US-A580&sourceid=aw-cen&utm_medium=seo+maps&utm_source=google+Maps&utm_campaign=seo+maps&y_source=1_MTIzNjEzODEtNzE1LWxvY2F0aW9uLmdvb2dsZV93ZWJzaXRlX292ZXJyaWRl'}, {'formatted_address': '1100 5th Ave, Seattle, WA 98101, USA', 'formatted_phone_number': '(206) 624-8000', 'geometry': {'location': {'lat': 47.6076086, 'lng': -122.3325799}}, 'name': 'Kimpton Hotel Vintage Seattle', 'opening_hours': {'open_now': True, 'periods': [{'open': {'day': 0, 'time': '0000'}}], 'weekday_text': ['Monday: Open 24 hours', 'Tuesday: Open 24 hours', 'Wednesday: Open 24 hours', 'Thursday: Open 24 hours', 'Friday: Open 24 hours', 'Saturday: Open 24 hours', 'Sunday: Open 24 hours']}, 'website': 'https://www.hotelvintage-seattle.com/?cm_mmc=GoogleMaps-_-cp-_-US-_-VPK'}, {'formatted_address': '405 Olive Way, Seattle, WA 98101, USA', 'formatted_phone_number': '(206) 623-8700', 'geometry': {'location': {'lat': 47.612168, 'lng': -122.3381135}}, 'name': 'Mayflower Park Hotel', 'opening_hours': {'open_now': True, 'periods': [{'open': {'day': 0, 'time': '0000'}}], 'weekday_text': ['Monday: Open 24 hours', 'Tuesday: Open 24 hours', 'Wednesday: Open 24 hours', 'Thursday: Open 24 hours', 'Friday: Open 24 hours', 'Saturday: Open 24 hours', 'Sunday: Open 24 hours']}, 'website': 'http://www.mayflowerpark.com/'}]}}]

if returned_output==expected_output:
    print("First Case Passed")
else:
    print("First Case Failed")

if returned_output2==expected_output2:
    print("Second Case Passed")
else:
    print("Second Case Failed")
