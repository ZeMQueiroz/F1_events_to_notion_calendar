import requests 
from notion_client import Client
import os
from dotenv import load_dotenv
import logging

# Load environment variables from a .env file
load_dotenv()

# Notion API Key and Database ID
NOTION_TOKEN = os.getenv("NOTION_TOKEN")  # Load from environment variables
DATABASE_ID = os.getenv("DATABASE_ID")  # Load from environment variables

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Notion client
notion = Client(auth=NOTION_TOKEN)

# Get F1 Schedule with additional details
def get_f1_schedule(year):
    url = f"https://ergast.com/api/f1/{year}.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data['MRData']['RaceTable']['Races']

# Fetch race results (e.g., last year's results for historical context)
def get_race_results(season, round):
    url = f"https://ergast.com/api/f1/{season}/{round}/results.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    if data['MRData']['total'] != "0":
        results = data['MRData']['RaceTable']['Races'][0]['Results']
        return results[0]['Driver']['familyName'] + " won the race."  # Example: Return winner name
    return "No data available."

# Add event to Notion with enhanced details
def add_event_to_notion(race):
    race_name = race['raceName']
    location = race['Circuit']['circuitName']
    race_date = race['date']
    round_number = race['round']
    circuit_location = f"{race['Circuit']['Location']['locality']}, {race['Circuit']['Location']['country']}"
    race_time = race.get('time', 'TBD')  # Add time if available

    # Fetch last season's results for historical context
    last_year_results = get_race_results(int(race['season']) - 1, round_number)

    try:
        # Attempt to create a new page in the Notion database
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": race_name}
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": f"{race_date}T{race_time}" if race_time != 'TBD' else race_date
                    }
                },
                "Location": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": f"{location} - {circuit_location}"}
                        }
                    ]
                },
                "Round": {
                    "number": int(round_number)
                },
                "Last Year’s Winner": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": last_year_results}
                        }
                    ]
                }
            },
            icon={"emoji": "🏎️"},
            cover={
                "external": {
                    "url": "https://example.com/circuit_image.jpg"  # Add actual circuit image URLs here
                }
            }
        )
        logging.info(f"Added {race_name} to Notion.")
    except Exception as e:
        logging.error(f"Failed to add {race_name}: {e}")

def main():
    """
    Main function to fetch F1 schedule and add events to Notion.
    """
    try:
        f1_schedule = get_f1_schedule(2024)
        for race in f1_schedule:
            add_event_to_notion(race)
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching F1 schedule: {e}")

if __name__ == "__main__":
    main()