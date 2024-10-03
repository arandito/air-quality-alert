from flask import Flask
from alert import aqi_alert
import os 

app = Flask(__name__)

@app.route('/run-aqi-tweet', methods=['POST'])
def run_aqi_tweet():
    aqi_alert()
    return "AQI tweet process completed", 200

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))