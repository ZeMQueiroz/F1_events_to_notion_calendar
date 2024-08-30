import requests
from notion_client import Client
import os
from dotenv import load_dotenv
import logging

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")  
DATABASE_ID = os.getenv("DATABASE_ID")  

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

notion = Client(auth=NOTION_TOKEN)

def get_f1_schedule():
    url = f"https://ergast.com/api/f1/current.json"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return data['MRData']['RaceTable']['Races']

def add_session_to_notion(session_name, date, time, location, round_number):
    try:
        notion.pages.create(
            parent={"database_id": DATABASE_ID},
            properties={
                "Name": {
                    "title": [
                        {
                            "type": "text",
                            "text": {"content": session_name}
                        }
                    ]
                },
                "Date": {
                    "date": {
                        "start": f"{date}T{time}" if time != 'TBD' else date
                    }
                },
                "Location": {
                    "rich_text": [
                        {
                            "type": "text",
                            "text": {"content": location}
                        }
                    ]
                },
                "Round": {
                    "number": int(round_number)
                }
            },
            cover={
                "external": {
                    "url": "https://example.com/circuit_image.jpg"  
                }
            }
        )
        logging.info(f"Added {session_name} to Notion.")
    except Exception as e:
        logging.error(f"Failed to add {session_name}: {e}")

def main():
    try:
        f1_schedule = get_f1_schedule()
        for race in f1_schedule:
            race_name = race['raceName']
            location = f"{race['Circuit']['circuitName']} - {race['Circuit']['Location']['locality']}, {race['Circuit']['Location']['country']}"
            round_number = race['round']

            if 'FirstPractice' in race:
                add_session_to_notion(
                    session_name=f"🏎️ {race_name} - Practice 1",
                    date=race['FirstPractice']['date'],
                    time=race['FirstPractice'].get('time', 'TBD'),
                    location=location,
                    round_number=round_number
                )

            if 'SecondPractice' in race:
                add_session_to_notion(
                    session_name=f"🏎️ {race_name} - Practice 2",
                    date=race['SecondPractice']['date'],
                    time=race['SecondPractice'].get('time', 'TBD'),
                    location=location,
                    round_number=round_number
                )

            if 'ThirdPractice' in race:
                add_session_to_notion(
                    session_name=f"🏎️ {race_name} - Practice 3",
                    date=race['ThirdPractice']['date'],
                    time=race['ThirdPractice'].get('time', 'TBD'),
                    location=location,
                    round_number=round_number
                )

            if 'Qualifying' in race:
                add_session_to_notion(
                    session_name=f"🏎️ {race_name} - Qualifying",
                    date=race['Qualifying']['date'],
                    time=race['Qualifying'].get('time', 'TBD'),
                    location=location,
                    round_number=round_number
                )

            if 'Sprint' in race:
                add_session_to_notion(
                    session_name=f"🏎️ {race_name} - Sprint",
                    date=race['Sprint']['date'],
                    time=race['Sprint'].get('time', 'TBD'),
                    location=location,
                    round_number=round_number
                )

            # Main race event
            add_session_to_notion(
                session_name=f"🏎️ {race_name} - Race",
                date=race['date'],
                time=race.get('time', 'TBD'),
                location=location,
                round_number=round_number
            )
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching F1 schedule: {e}")

if __name__ == "__main__":
    main()