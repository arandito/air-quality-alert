import tweepy
from keys import config
import requests

import gspread

# tweepy v2
"""
client = tweepy.Client(consumer_key=config.API_KEY,
                       consumer_secret=config.API_KEY_SECRET,
                       access_token=config.ACCESS_TOKEN,
                       access_token_secret=config.ACCESS_TOKEN_SECRET)
"""

auth = tweepy.OAuth1UserHandler(config.API_KEY, config.API_KEY_SECRET)
auth.set_access_token(config.ACCESS_TOKEN, config.ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

gc = gspread.service_account('credentials.json')
wks = gc.open("air-quality-alert").sheet1

zipcode_hash = {
    "New York, NY": "10027",
    "Los Angeles, CA": "90011",
    "Chicago, IL": "60610",
    "Houston, TX": "77083",
    "Phoenix, AZ": "85032",
    "Philadelphia, PA": "19120",
    "San Antonio, TX": "78245",
    "San Diego, CA": "92154",
    "Dallas, TX": "75217",
    "San Jose, CA": "95112",
    "Austin,TX": "78745",
    "Jacksonville, FL": "32210",
    "Fort Worth, TX": "76102",
    "Columbus, OH": "43230",
    "Indianapolis, IN": "46227",
    "Charlotte, NC": "28269",
    "San Francisco, CA": "94112",
    "Seattle, WA": "98115",
    "Denver, CO": "80219",
    "Washington, DC": "20005",
    "Nashville, TN": "37211",
    "Oklahoma City, OK": "73160",
    "El Paso, TX": "79936",
    "Boston, MA": "02110",
    "Portland, OR": "97229",
    "Las Vegas, NV": "89108",
    "Detroit, MI": "48228",
    "Memphis, TN": "38128",
    "Louisville, KY": "40214",
    "Baltimore, MD": "21215",
    "Milwaukee, WI": "53215",
    "Albuquerque, NM": "87121",
    "Kansas City, MO": "64118",
    "Mesa, AZ": "85204",
    "Atlanta, GA": "30349",
    "Omaha, NE": "68104",
    "Colorado Springs, CO": "80918",
    "Virginia Beach, VA": "23464",
    "Miami, FL": "33186",
    "Oakland, CA": "94612",
    "Minneapolis, MN": "55407",
    "Bakersfield, CA": "93307",
    "Wichita, KS": "67212",
    "Arlington, TX": "76010",
    "Tampa, FL": "33647",
    "New Orleans, LA": "70119",
    "Honolulu, HI": "96818",
    "Cleveland, OH": "44130",
    "St. Louis, MO": "63129",
    "Pittsburgh, PA": "15237"
}

image_hash = {
    "Good": "good.png",
    "Moderate": "moderate.png",
    "Unhealthy for Sensitive Groups": "sensitive.png",
    "Unhealthy": "unhealthy.png",
    "Very Unhealthy": "very_unhealthy.png",
    "Hazardous": "hazardous.png"
}

aqi_api_key = config.AQI_API_KEY


def tweet_alert(index, aqi, category, zip_key):
    val = wks.acell('B' + str(index)).value
    if val != category:
        wks.update("B" + str(index), category)
        tweet_str = f'Air quality in {zip_key} is now "{category}" with an ' \
                    f'AQI of {aqi}. Air quality was previously "{val}".'
        file = image_hash[category]
        res = api.update_status(status=tweet_str, filename=file)
        print(res)
    return


i = 1
for key in zipcode_hash:
    api_url = f"https://www.airnowapi.org/aq/observation/zipCode/current/?format=application/json&zipCode" \
              f"={zipcode_hash[key]}&distance=1&API_KEY={aqi_api_key}"

    response = requests.get(api_url.format(zipcode_hash[key], aqi_api_key))
    data = response.json()
    print(data)

    if len(data) > 1:
        data_dict = data[1]
        aqi_value = data_dict['AQI']
        category_dict = data_dict['Category']
        aqi_category = category_dict["Name"]

        tweet_alert(i, aqi_value, aqi_category, key)
        wks.update("A" + str(i), data_dict['AQI'])
        # print(str(dataHash['AQI']) + " - " + dataHash['ParameterName'])
    elif len(data) == 1:
        data_dict = data[0]
        aqi_value = data_dict['AQI']
        category_dict = data_dict['Category']
        aqi_category = category_dict["Name"]
        tweet_alert(i, aqi_value, aqi_category, key)

        wks.update("A" + str(i), data_dict['AQI'])
        # print(str(dataHash['AQI']) + " - " + dataHash['ParameterName'])
    else:
        print('')
    i += 1
