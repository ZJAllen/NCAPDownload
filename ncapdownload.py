#!/usr/bin/python3.7

import requests
from bs4 import BeautifulSoup
import json

# Set API endpoints
vehicle_api = "https://vpic.nhtsa.dot.gov/api"

# Get full list of makes, which will be used to validate user input
## TODO: Make this a drop-down in a GUI
vehicle_makes_api = "/vehicles/GetAllMakes?format=json"

selected_year = input("Enter vehicle model year: ")

get_makes = requests.get(vehicle_api + vehicle_makes_api)
makes_dict = json.loads(get_makes.text)
makes_result = makes_dict["Results"]

makes_set = set()

try:
    for x in makes_result:
        makes_set.add(x["Make_Name"])
except:
    "JSON format error"

selected_make = input("Enter vehicle make: ")

while not selected_make in makes_set:
    print("Invalid input.  Check spelling and capitilization")
    selected_make = input("Enter vehicle make: ")

# For the given make and model year, get all of the available models.
## TODO: Make this a drop-down, which is populated once the make is selected
vehicle_models_api = f"/vehicles/GetModelsForMakeYear/make/{selected_make}/modelyear/{selected_year}?format=json"

get_models = requests.get(vehicle_api + vehicle_models_api)
models_dict = json.loads(get_models.text)
models_result = models_dict["Results"]

models_set = set()

try:
    for x in models_result:
        models_set.add(x["Model_Name"])
except:
    "JSON format error"

selected_model = input("Enter vehicle model: ")

while not selected_model in models_set:
    print("Invalid input.  Check spelling and capitilization")
    selected_model = input("Enter vehicle model: ")

print("\n")
print(f"Your chosen vehicle is a {selected_year} {selected_make} {selected_model}.")
