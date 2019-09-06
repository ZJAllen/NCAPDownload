#!/usr/bin/python3.7

import os
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd ## TODO: Look into using pandas for JSON parsing
import tkinter as tk
from tkinter.filedialog import askdirectory


# Set API endpoints
vehicle_api = "https://vpic.nhtsa.dot.gov/api"
safety_ratings_api = "https://webapi.nhtsa.gov/api/SafetyRatings"

crash_database = "https://www-nrd.nhtsa.dot.gov/database/VSR/veh/TestDetail.aspx?"

crash_report = f"https://www-nrd.nhtsa.dot.gov/database/VSR/SearchMedia.aspx?database=v&tstno=10364&mediatype=r&r_tstno=10364"
crash_photo = f"https://www-nrd.nhtsa.dot.gov/database/VSR/SearchMedia.aspx?database=v&tstno=10364&mediatype=p&p_tstno=10364"
crash_video = f"https://www-nrd.nhtsa.dot.gov/database/VSR/SearchMedia.aspx?database=v&tstno=10364&mediatype=v&v_tstno=10364"

'''
Get vehicle info from user
'''

# Get full list of makes, which will be used to validate user input
## TODO: Make this a drop-down in a GUI
vehicle_makes_api = "/vehicles/GetMakesForVehicleType/car?format=json"

selected_year = input("Enter vehicle model year: ")

## TODO: make the following in a function. Identical with next query/search
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

## TODO: make the following in a function
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
Use vehicle info to get Vehicle ID from NCAP API. Vehicle ID is then used
to get the test ID, which will be used to get data from crash database.
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

## TODO: make the following in a function?
def get_test_id(test_info):

    test_mode = ["FrontCrashPicture", "SideCrashPicture", "SidePolePicture"]
    test_id = []

    for i in test_mode:
        test_photo = test_info[i]
        test_id.append(test_photo[test_photo.rindex("/")+2:test_photo.rindex("P")])

    return test_id

test_id = get_test_id(test_info_result)
front_test_id = test_id[0]
side_mdb_test_id = test_id[1]
side_pole_test_id = test_id[2]

# Create folder structure

# Get top level folder
root = tk.Tk()
root.wm_withdraw()
save_path = askdirectory(title="Select folder in which to save the crash test data")
root.destroy()

# Top level folder: [Model Year] [Make] [Model]
lev1_folder = f"{save_path}/{selected_year.upper()} {selected_make.upper()} {selected_model.upper()}"
os.mkdir(lev1_folder)

# Second Level folder: [Test ID] - [Model Year] [Make] [Model] - [Test Mode]
lev2_folder = []
lev2_folder.append(f"{lev1_folder}/{front_test_id} - {selected_year.upper()} {selected_make.upper()} {selected_model.upper()} - FRONT")
lev2_folder.append(f"{lev1_folder}/{side_mdb_test_id} - {selected_year.upper()} {selected_make.upper()} {selected_model.upper()} - SIDE MDB")
lev2_folder.append(f"{lev1_folder}/{side_pole_test_id} - {selected_year.upper()} {selected_make.upper()} {selected_model.upper()} - SIDE POLE")

for x in lev2_folder:
    os.mkdir(x)

front_folder = lev2_folder[0]
side_mdb_folder = lev2_folder[1]
side_pole_folder = lev2_folder[2]

# Third level folder: DATA, PHOTOS, VIDEO
lev3_folder = ["DATA", "PHOTOS", "VIDEO"]

for x in lev2_folder:
    for y in lev3_folder:
        os.mkdir(f"{x}/{y}")

# Get filename of report from table on webpage
def get_report_name(test_id):
    webpage_url = f"https://www-nrd.nhtsa.dot.gov/database/VSR/SearchMedia.aspx?database=v&tstno={test_id}&mediatype=r&r_tstno={test_id}"
    get_webpage = requests.get(webpage_url)
    soup = BeautifulSoup(get_webpage.content, 'html.parser')
    tb = soup.find('table', id="tblData")
    report_name = tb.find_all('td')[2].text.replace("&nbsp", "").strip()

    return report_name

# Download report from database using test ID
def get_report(test_id, report_path):
    report_url = f"https://www-nrd.nhtsa.dot.gov/database/MEDIA/GetMedia.aspx?tstno={test_id}&index=1&database=V&type=R"
    r = requests.get(report_url)
    with open(f"{report_path}/{get_report_name(test_id)}", "wb") as f:
        f.write(r.content)

## TODO: make the following a function with the test ID as the input.
# Download test data
def download_data(test_id):
    database_url = f"https://www-nrd.nhtsa.dot.gov/database/VSR/Download.aspx?tstno=10364&curno=&database=v&name=v{test_id}&format="
    crash_data_tdms = database_url + "tdms"
    crash_data_xml = database_url + "xml"
    crash_data_json = database_url + "json"

    report_url = f"https://www-nrd.nhtsa.dot.gov/database/MEDIA/GetMedia.aspx?tstno={test_id}&index=1&database=V&type=R"
