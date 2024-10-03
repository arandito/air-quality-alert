import os
import random
import redis
import requests
import tweepy
from constants import AMERICAN_CITIES, AMERICAN_CITIES_LAT_LONG
from map import generate_map_with_overlay
from dotenv import load_dotenv

load_dotenv()
SRC_DIR = os.getenv("SRC_DIR")

session = requests.Session()
client = tweepy.Client(
    consumer_key=os.environ["X_API_KEY"],
    consumer_secret=os.environ["X_API_KEY_SECRET"],
    access_token=os.environ["X_ACCESS_TOKEN"],
    access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"]
)
auth = tweepy.OAuthHandler(
    os.environ["X_API_KEY"], 
    os.environ["X_API_KEY_SECRET"]
)
auth.set_access_token(
    os.environ["X_ACCESS_TOKEN"],
    os.environ["X_ACCESS_TOKEN_SECRET"]
)
api = tweepy.API(auth, wait_on_rate_limit=True)

redis_pool = redis.ConnectionPool(
    host=os.environ["REDIS_HOST"],
    port=int(os.environ["REDIS_PORT"]),
    password=os.environ["REDIS_PASSWORD"]
)
db = redis.Redis(connection_pool=redis_pool)

def tweet_alert(city, prev_category, curr_category, aqi, main_pollutant):
    aqi_map_image = os.path.join(SRC_DIR, "assets/aqi_map.png")
    media_id = api.media_upload(filename=aqi_map_image).media_id_string
    tweet_str = (
        f'ALERT: Air quality in {city.upper()} is now {curr_category.upper()} with an '
        f'AQI of {aqi}. The main pollutant is {main_pollutant.upper()}. Air quality '
        f'was previously {prev_category.upper()}.'
    )
    res = client.create_tweet(text=tweet_str, media_ids=[media_id])
    print(res)

def parse_aqi_data(aqi_data):
    parsed_aqi_data = {"AQI": -1, "Category": "", "MainPollutant": ""}
    for pollutant in aqi_data:
        if pollutant["AQI"] > parsed_aqi_data["AQI"]:
            parsed_aqi_data["AQI"] = pollutant["AQI"]
            parsed_aqi_data["Category"] = pollutant["Category"]["Name"]
            parsed_aqi_data["MainPollutant"] = pollutant["ParameterName"]
    return parsed_aqi_data

def aqi_alert():
    tweets = 0
    shuffled_cities = list(AMERICAN_CITIES.items())
    random.shuffle(shuffled_cities)
    for city, zipcode in shuffled_cities:
        aqi_api_url = (
            f"{os.environ['AIRNOW_API_URL']}?format=application/json&"
            f"zipCode={zipcode}&distance=10&API_KEY={os.environ['AIRNOW_API_KEY']}"
        )
        response = session.get(aqi_api_url)
        aqi_data = response.json()
        parsed_aqi_data = parse_aqi_data(aqi_data)

        prev_category = db.get(city)
        if prev_category is not None:
            prev_category = prev_category.decode("utf-8")
        else:
            print(f"No previous data for {city}")
            prev_category = ""

        curr_category = parsed_aqi_data["Category"]
        print(f"{city.upper()} -> prev: {prev_category}, curr: {curr_category}")
        lat, lon = AMERICAN_CITIES_LAT_LONG[city]
        if prev_category != curr_category:
            db.set(city, curr_category)
            generate_map_with_overlay(lat, lon, parsed_aqi_data["AQI"], os.path.join(SRC_DIR, "assets"))
            tweet_alert(city, prev_category, curr_category, parsed_aqi_data["AQI"], parsed_aqi_data["MainPollutant"])
            tweets += 1

        # Max tweet count per day is 50 and we are running this code twice a day.
        if tweets == 25:
            break

    print("Posted tweets:", tweets)
