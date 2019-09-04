# Download NHTSA NCAP Data
Download data, photos, and videos from NHTSA NCAP tests using their public API
and web-scraping.  This is an exercise to learn web-scraping in Python and to
provide as a useful resource for downloading the publicly available crash safety data.

## What is NHTSA?

## What is NCAP?


## NHTSA API and database
API source: https://webapi.nhtsa.gov/Default.aspx?SafetyRatings/API/5
Crash test database (for scraping): https://www-nrd.nhtsa.dot.gov/database/VSR/veh/TestDetail.aspx

## Data download map
#### 1. User selects Year-Make-Model

#### 2. Get JSON data from API
This is mainly just to get the test IDs for the front, side MDB, and side pole tests.
These IDs will then be used in the crash database URLs to get the data, report, photos, and videos.

#### 3. Get test info using the test ID

#### 4. Python script sets up folder structures
The folder naming will be according to the test info associated with the test ID and Year-Make-Model

#### 5. Download data

#### 6. Rename files
