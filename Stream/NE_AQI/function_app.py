import logging
import requests
import json
import azure.functions as func
from azure.eventhub import EventHubProducerClient, EventData
import os

app = func.FunctionApp()

@app.timer_trigger(schedule="* */3 * * * *", arg_name="myTimer", run_on_startup=True, use_monitor=False)
def function(myTimer: func.TimerRequest) -> None:
    logging.info('Timer trigger executed.')
    main(myTimer)

def main(mytimer: func.TimerRequest = None) -> None:
    logging.info("Starting the function...")

    # Configuration
    api_url = os.getenv("API_URL")
    api_key = os.getenv("API_KEY")

    event_hub_connection_string = os.getenv("EVENT_HUB_CONNECTION_STRING")

    try:
        # Fetch data from the API
        logging.info("Fetching data from the Ambee API...")
        headers = {"x-api-key": api_key}
        response = requests.get(api_url, headers=headers)

        if response.status_code != 200:
            logging.error(f"Failed to fetch data: {response.status_code} - {response.text}")
            return

        # Parse the JSON response
        data = response.json()
        logging.info(f"Raw JSON Response: {json.dumps(data, indent=2)}")

        # Extract and transform the required data
        if "stations" not in data or not data["stations"]:
            logging.warning("No station data found in the response.")
            return

        station_data = data["stations"][0]  # Assuming we process the first station

        transformed_data = {
            "CO": station_data.get("CO", "N/A"),
            "NO2": station_data.get("NO2", "N/A"),
            "OZONE": station_data.get("OZONE", "N/A"),
            "PM10": station_data.get("PM10", "N/A"),
            "PM25": station_data.get("PM25", "N/A"),
            "SO2": station_data.get("SO2", "N/A"),
            "city": station_data.get("city", "N/A"),
            "state": station_data.get("state", "N/A"),
            "AQI": station_data.get("AQI", "N/A"),
            "pollutant": station_data.get("aqiInfo", {}).get("pollutant", "N/A"),
            "concentration": station_data.get("aqiInfo", {}).get("concentration", "N/A"),
            "category": station_data.get("aqiInfo", {}).get("category", "N/A"),
            "updatedAt": station_data.get("updatedAt", "N/A"),
        }

        logging.info(f"Transformed data: {json.dumps(transformed_data, indent=2)}")

        # Send to Event Hub
        send_to_event_hub(event_hub_connection_string, [transformed_data])

    except requests.RequestException as e:
        logging.error(f"HTTP request error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

def send_to_event_hub(connection_string, data):
    try:
        producer = EventHubProducerClient.from_connection_string(connection_string)
        with producer:
            event_data_batch = producer.create_batch()
            for item in data:
                event_data_batch.add(EventData(json.dumps(item)))
            producer.send_batch(event_data_batch)
        logging.info("Data sent to Event Hub successfully.")
    except Exception as e:
        logging.error(f"Error while sending data to Event Hub: {e}")

# This part ensures the main function runs when the script is executed directly (locally)
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Running immediately...")
    main()
