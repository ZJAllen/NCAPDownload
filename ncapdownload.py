#!/usr/bin/python3.7

import requests
from bs4 import BeautifulSoup
import json
import pandas as pd ## TODO: Look into using pandas for JSON parsing

# Set API endpoints
vehicle_api = "https://vpic.nhtsa.dot.gov/api"
safety_ratings_api = "https://webapi.nhtsa.gov/api/SafetyRatings"
crash_database = "https://www-nrd.nhtsa.dot.gov/database/VSR/veh/TestDetail.aspx?"
crash_data = ""
crash_report = ""
crash_photo = ""
crash_video = ""

'''
Get vehicle info from user
'''

# Get full list of makes, which will be used to validate user input
## TODO: Make this a drop-down in a GUI
vehicle_makes_api = "/vehicles/GetMakesForVehicleType/car?format=json"

selected_year = input("Enter vehicle model year: ")

get_makes = requests.get(vehicle_api + vehicle_makes_api)
makes_dict = json.loads(get_makes.text)
makes_result = makes_dict["Results"]

selected_make = input("Enter vehicle make: ")

while next((item for item in makes_result if item["MakeName"].lower() == selected_make.lower()),None) == None:
    print("Invalid input.  Check spelling and try again")
    selected_make = input("Enter vehicle make: ")

# For the given make and model year, get all of the available models.
## TODO: Make this a drop-down, which is populated once the make is selected
vehicle_models_api = f"/vehicles/GetModelsForMakeYear/make/{selected_make}/modelyear/{selected_year}?format=json"

get_models = requests.get(vehicle_api + vehicle_models_api)
models_dict = json.loads(get_models.text)
models_result = models_dict["Results"]

selected_model = input("Enter vehicle model: ")

while next((item for item in models_result if item["Model_Name"].lower() == selected_model.lower()), None) == None:
    print("Invalid input.  Check spelling and try again")
    selected_model = input("Enter vehicle model: ")



print("\n")
print(f"Your chosen vehicle is a {selected_year} {selected_make} {selected_model}.")


'''
Use vehicle info to get Vehicle ID from NCAP API. Vehicle ID will be used to
get data from crash database
'''

vehicle_id_api = f"/modelyear/{selected_year}/make/{selected_make}/model/{selected_model}?format=json"

get_vehicle_id = requests.get(safety_ratings_api + vehicle_id_api)
vehicle_id_dict = json.loads(get_vehicle_id.text)
vehicle_id_result = vehicle_id_dict["Results"]

vehicle_id_set = set()

for x in vehicle_id_result:
    vehicle_id_set.add(x["VehicleId"])

vehicle_id = vehicle_id_set.pop()

test_info_api = f"/VehicleId/{vehicle_id}?format=json"

get_test_info = requests.get(safety_ratings_api + test_info_api)
test_info_dict = json.loads(get_test_info.text)
test_info_result = test_info_dict["Results"][0]

# Get Front Crash test ID
front_test_photo = test_info_result["FrontCrashPicture"]
front_test_id = front_test_photo[front_test_photo.rindex("/")+2:front_test_photo.rindex("P")]
print(front_test_photo)

# Get Side MDB test ID
side_mdb_test_photo = test_info_result["SideCrashPicture"]
side_mdb_test_id = side_mdb_test_photo[side_mdb_test_photo.rindex("/")+2:side_mdb_test_photo.rindex("P")]
print(side_mdb_test_photo)

# Get Side Pole test ID
side_pole_test_photo = test_info_result["SidePolePicture"]
side_pole_test_id = side_pole_test_photo[side_pole_test_photo.rindex("/")+2:side_pole_test_photo.rindex("P")]
print(side_pole_test_photo)
