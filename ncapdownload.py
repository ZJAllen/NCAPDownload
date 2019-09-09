#!/usr/bin/python3.7

import os
import time
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd ## TODO: Look into using pandas for JSON parsing
import tkinter as tk
from tkinter.filedialog import askdirectory
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions

# Set API endpoints
vehicle_api = "https://vpic.nhtsa.dot.gov/api"
safety_ratings_api = "https://webapi.nhtsa.gov/api/SafetyRatings"

crash_database = "https://www-nrd.nhtsa.dot.gov/database/VSR/veh/TestDetail.aspx?"

'''
crash_report = f"https://www-nrd.nhtsa.dot.gov/database/VSR/SearchMedia.aspx?database=v&tstno={test_id}&mediatype=r&r_tstno={test_id}"
crash_photo = f"https://www-nrd.nhtsa.dot.gov/database/VSR/SearchMedia.aspx?database=v&tstno={test_id}&mediatype=p&p_tstno={test_id}"
crash_video = f"https://www-nrd.nhtsa.dot.gov/database/VSR/SearchMedia.aspx?database=v&tstno={test_id}&mediatype=v&v_tstno={test_id}"
'''

'''
Get vehicle info from user
'''

def get_vehicle_info(api_endpoint):
    get_vehicle = requests.get(vehicle_api + api_endpoint)
    vehicle_dict = json.loads(get_vehicle.text)
    vehicle_result = vehicle_dict["Results"]

    return vehicle_result

# Get full list of makes, which will be used to validate user input
## TODO: Make this a drop-down in a GUI
vehicle_makes_api = "/vehicles/GetMakesForVehicleType/car?format=json"
makes_result = get_vehicle_info(vehicle_makes_api)

## TODO: Add validation for user input
selected_year = input("Enter vehicle model year: ")

selected_make = input("Enter vehicle make: ")

while next((item for item in makes_result if item["MakeName"].lower() == selected_make.lower()),None) == None:
    print("Invalid input.  Check spelling and try again")
    selected_make = input("Enter vehicle make: ")


# For the given make and model year, get all of the available models.
## TODO: Make this a drop-down, which is populated once the make is selected
vehicle_models_api = f"/vehicles/GetModelsForMakeYear/make/{selected_make}/modelyear/{selected_year}?format=json"
models_result = get_vehicle_info(vehicle_models_api)

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

'''
Create folder structure
'''

# Get top level folder
root = tk.Tk()
root.wm_withdraw()
save_path = askdirectory(title="Select folder in which to save the crash test data")
root.destroy()

# Top level folder: [Model Year] [Make] [Model]
lev1_folder = f"{save_path}/{selected_year.upper()} {selected_make.upper()} {selected_model.upper()}"
## TODO: add try/except to catch FileExistsError
os.mkdir(lev1_folder)

# Second Level folder: [Test ID] - [Model Year] [Make] [Model] - [Test Mode]
lev2_folder = []
lev2_folder.append(f"{lev1_folder}/{front_test_id} - FRONT - {selected_year.upper()} {selected_make.upper()} {selected_model.upper()}")
lev2_folder.append(f"{lev1_folder}/{side_mdb_test_id} - SIDE MDB - {selected_year.upper()} {selected_make.upper()} {selected_model.upper()}")
lev2_folder.append(f"{lev1_folder}/{side_pole_test_id} - SIDE POLE - {selected_year.upper()} {selected_make.upper()} {selected_model.upper()}")

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
def get_file_name(webpage_url):
    get_webpage = requests.get(webpage_url)
    html_content = BeautifulSoup(get_webpage.content, 'html.parser')
    tb = html_content.find('table', id="tblData")
    success = 0
    while success == 0:
        try:
            file_name = tb.find_all('td')[2].text.replace("&nbsp", "").strip()
            success = 1
        except:
            pass

    return file_name

def get_file_names(webpage_url):
    driver = webdriver.Firefox()
    driver.get(webpage_url)

    # Delay to allow for page to load
    time.sleep(1)

    file_names = []

    status = 0

    while status == 0:
        # Get table, parse into pandas dataframe, extract photo names
        table = driver.execute_script("return document.getElementById('tblData').outerHTML")
        file_table = pd.read_html(table)[0]

        for i in range(file_table.shape[0]):
            file_names.append(file_table.iloc[i,2])

        # Check if end of table --> if Next button is not present
        if driver.execute_script("return document.getElementById('cmdNext')") is None:
            status = 1
            break


        ready = ""
        while ready != "complete":
            ready = driver.execute_script("return document.readyState")

        # Go to the next page --> act on the aspx form
        driver.execute_script("document.forms['searchmedia'].__EVENTTARGET.value = 'cmdNext'")
        driver.execute_script("document.forms['searchmedia'].__EVENTARGUMENT.value = ''")
        driver.execute_script("document.forms['searchmedia'].submit()")

        # Delay to allow for next page to load
        time.sleep(1)

        ready = ""
        while ready != "complete":
            ready = driver.execute_script("return document.readyState")

        # The next button usually causes the page to crash, so go back and try again
        success = 0
        while success == 0:
            try:
                driver.find_element_by_id("tblData")
                success = 1
            except:
                while driver.execute_script("return document.getElementById('cmdNext')") is None:
                    driver.refresh()
                    driver.switch_to.alert.accept()

                    # Delay to allow for next page to load
                    time.sleep(1)


    driver.close()

    return file_names


'''
Download report
'''

# Download report from database using test ID
def get_report(test_id, test_path):
    report_url = f"https://www-nrd.nhtsa.dot.gov/database/MEDIA/GetMedia.aspx?tstno={test_id}&index=1&database=V&type=R"
    r = requests.get(report_url)
    with open(f"{test_path}/{get_file_name(report_url)}", "wb") as f:
        f.write(r.content)


'''
Download data
'''

## TODO: make the following a function with the test ID as the input.
# Download test data
def get_data(test_id, test_path):
    data_url = f"https://www-nrd.nhtsa.dot.gov/database/VSR/Download.aspx?tstno={test_id}&curno=&database=v&name=v{test_id}&format="
    crash_data_formats = ["tdms", "xml", "json"]

    data_path = f"{test_path}/DATA"

    for i in range(len(crash_data_formats)):
        url = data_url + crash_data_formats[i]
        r = requests.get(url)
        with open(f"{data_path}/v{test_id}{crash_data_formats[i]}.zip", "wb") as f:
            f.write(r.content)


'''
Download images
'''

def download_images(test_id, test_path):
    image_url = f"https://www-nrd.nhtsa.dot.gov/database/MEDIA/GetMedia.aspx?tstno={test_id}&index=1&database=V&type=P"
    r = requests.get(image_url)
    with open(f"{test_path}/{get_file_names(image_url)}", "wb") as f:
        f.write(r.content)


'''
Download videos
'''

def get_video_names(test_id):
    pass

def download_videos(test_id):
    pass
