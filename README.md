# Air Quality Twitter Bot

This project is a Twitter bot that monitors air quality in various American cities and posts alerts when the air quality changes. The bot is implemented in Python, containerized with Docker, and deployed on Google Cloud Run.

## Features

- Fetches air quality data for 75 U.S. cities
- Generates maps with air quality overlays
- Posts tweets with air quality alerts and maps
- Runs as a Flask service on Google Cloud Run

## Prerequisites

- Python 3.12
- Docker
- Google Cloud account
- Twitter Developer account
- AirNow API key
- Redis instance

## Environment Variables

The following environment variables need to be set:

- `X_API_KEY`: Twitter API key
- `X_API_KEY_SECRET`: Twitter API key secret
- `X_ACCESS_TOKEN`: Twitter access token
- `X_ACCESS_TOKEN_SECRET`: Twitter access token secret
- `REDIS_HOST`: Redis host
- `REDIS_PORT`: Redis port
- `REDIS_PASSWORD`: Redis password
- `AIRNOW_API_URL`: AirNow API URL
- `AIRNOW_API_KEY`: AirNow API key
- `SRC_DIR`: Source directory (set to `/app` in the Dockerfile)

## Project Structure

- `app.py`: Main Flask application
- `alert.py`: Core logic for fetching AQI data and posting tweets
- `map.py`: Functions for generating maps with AQI overlays
- `constants.py`: Contains data for American cities (not provided in the snippet)
- `Dockerfile`: Instructions for building the Docker image
- `requirements.txt`: List of Python dependencies

## Setup and Deployment

1. Clone the repository
2. Set up the required environment variables
3. Build the Docker image:
   ```
   docker build -t air-quality-bot .
   ```
4. Deploy to Google Cloud Run:
   ```
   gcloud run deploy --image air-quality-bot --platform managed
   ```

## Usage

The bot exposes a single endpoint:

- `/run-aqi-tweet` (POST): Triggers the AQI data fetch and tweet process

You can set up a Cloud Scheduler job to hit this endpoint at regular intervals to automate the tweeting process.
