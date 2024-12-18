import logging
import requests
import xml.etree.ElementTree as ET
import json
import azure.functions as func
from azure.eventhub import EventHubProducerClient, EventData
import os

app = func.FunctionApp()

# Global variable to store the last processed gen_mw value
last_processed_gen_mw_natural_gas = None
last_processed_gen_mw_coal = None

@app.timer_trigger(schedule="* */3 * * * *", arg_name="myTimer", run_on_startup=True, use_monitor=False)
def function(myTimer: func.TimerRequest) -> None:
    logging.info('Timer trigger executed.')
    main(myTimer)

def load_last_processed_gen_mw(fuel_category):
    try:
        # Try to read the value from a file or other persistent storage
        with open(f'last_processed_gen_mw_{fuel_category}.json', 'r') as f:
            data = json.load(f)
            return data.get('gen_mw')
    except FileNotFoundError:
        return None  # No previous value found

def save_last_processed_gen_mw(fuel_category, gen_mw):
    try:
        # Save the latest gen_mw value to a file for persistence
        with open(f'last_processed_gen_mw_{fuel_category}.json', 'w') as f:
            json.dump({'gen_mw': gen_mw}, f)
    except Exception as e:
        logging.error(f"Error saving last_processed_gen_mw: {e}")

def main(mytimer: func.TimerRequest = None) -> None:
    global last_processed_gen_mw_natural_gas
    global last_processed_gen_mw_coal
    logging.info("Starting the function...")

    iso_ne_username = os.getenv("ISO_NE_USERNAME")
    iso_ne_password = os.getenv("ISO_NE_PASSWORD")
    event_hub_connection_string = os.getenv("EVENT_HUB_CONNECTION_STRING")
    
    natural_gas_url = "https://webservices.iso-ne.com/api/v1.1/genfuelmix/current/fuelCategoryRollup/Natural%20Gas"
    coal_url = "https://webservices.iso-ne.com/api/v1.1/genfuelmix/current/fuelCategoryRollup/Coal"
    namespace = {'ns': 'http://WEBSERV.iso-ne.com'}

    for fuel_category, url in [("natural_gas", natural_gas_url), ("coal", coal_url)]:
        try:
            logging.info(f"Fetching XML data for {fuel_category.capitalize()}...")
            response = requests.get(url, auth=(iso_ne_username, iso_ne_password))
            
            if response.status_code != 200:
                logging.error(f"Failed to fetch {fuel_category.capitalize()} data: {response.status_code}")
                continue

            logging.info(f"Raw XML Response ({fuel_category.capitalize()}): {response.text}")

            # Parse XML data
            logging.info(f"Parsing the {fuel_category.capitalize()} XML data...")
            root = ET.ElementTree(ET.fromstring(response.text)).getroot()

            # Extract gen_mw value
            gen_fuel_mix_elements = root.findall('.//ns:GenFuelMix', namespace)
            gen_mw = (
                gen_fuel_mix_elements[0].find('ns:GenMw', namespace).text
                if gen_fuel_mix_elements and gen_fuel_mix_elements[0].find('ns:GenMw', namespace) is not None
                else 'N/A'
            )

            logging.info(f"Before processing - GenMw for {fuel_category.capitalize()}: {gen_mw}")

            # Load the last processed gen_mw value
            last_processed_gen_mw = load_last_processed_gen_mw(fuel_category)

            # Log gen_mw values comparison
            if str(gen_mw).strip() == str(last_processed_gen_mw).strip():
                logging.info(f"The GenMw value for {fuel_category.capitalize()} hasn't changed. Skipping processing.")
                continue
            else:
                logging.info(f"GenMw for {fuel_category.capitalize()} has changed. Proceeding with processing.")
                save_last_processed_gen_mw(fuel_category, gen_mw)

                # Process the data
                transformed_data = []
                for element in gen_fuel_mix_elements:
                    transformed_data.append({
                        'begin_date': element.find('ns:BeginDate', namespace).text if element.find('ns:BeginDate', namespace) is not None else 'N/A',
                        'gen_mw': element.find('ns:GenMw', namespace).text if element.find('ns:GenMw', namespace) is not None else 'N/A',
                        'fuel_category_rollup': element.find('ns:FuelCategoryRollup', namespace).text if element.find('ns:FuelCategoryRollup', namespace) is not None else 'N/A',
                        'fuel_category': element.find('ns:FuelCategory', namespace).text if element.find('ns:FuelCategory', namespace) is not None else 'N/A',
                        'marginal_flag': element.find('ns:MarginalFlag', namespace).text if element.find('ns:MarginalFlag', namespace) is not None else 'N/A'
                    })

                logging.info(f"Transformed data for {fuel_category.capitalize()}: {json.dumps(transformed_data, indent=2)}")

                # Send to Event Hub
                send_to_event_hub(event_hub_connection_string, transformed_data)

        except requests.RequestException as e:
            logging.error(f"HTTP request error: {e}")
        except ET.ParseError as e:
            logging.error(f"Error parsing XML: {e}")
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
