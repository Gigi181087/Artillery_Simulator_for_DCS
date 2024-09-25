import json
import socket

import threading
import time

from DCS_link.dcs_link import DCS_Link
import Webserver.main

from numpy import random

shots: list[dict] = []
PORT = 15000
current_mission_time_lock = threading.Lock()
current_mission_time: float = 0
webserver_thread = None

def get_current_mission_time() -> float:
    global current_mission_time

    return current_mission_time

def parse_coordinate(coordinate: str, system: str):
    parts = coordinate.split(' ')
    
    return parts[0], parts[1]

def handle_messages(messages: list[dict]) -> None:

    for key, message in messages.items():
        #check message needs to be implemented properly
        if key == "Call For Fire":
            number_of_rounds = message["Number Of Rounds"]
            latitude, longitude = parse_coordinate(message["Location"]["Coordinate"], message["Location"]["System"])

            print("Shot!")

            for index in range(int(number_of_rounds)):

                for i in range(message["Number Of Guns"]):
                    shot = {
                        'Simulated Shot': {
                            'Time Fired': get_current_mission_time(),
                            'Location' : {
                                'System': message["Location"]["System"],
                                'Latitude': random.normal(float(latitude), 35),
                                'Longitude': random.normal(float(longitude), 35),
                                'Elevation': 60,
                            },
                            'Time Of Flight': 15,
                            'Ammunition Type': message["Ammunition"],
                            'Caliber': 60
                        }
                    }
                    DCS_Link.insert_shot(shot)
                    time.sleep(random.normal(1, 0.1))

                time.sleep(random.normal(8.5, 1.0))

            print("Rounds complete!")


def data_polling() -> None:
    global current_mission_time

    while True:
        current_mission_time = DCS_Link.get_mission_time()
        messages = Webserver.main.polling_data()

        if messages:
            handle_messages_thread = threading.Thread(target = handle_messages, args = messages)
            handle_messages_thread.start()

    return

if __name__ == "__main__":
    print("Calling DCS-Link Start!")
    DCS_Link.start()
    print("Calling Webserver Start")
    webserver_thread = threading.Thread(target = Webserver.main.start())
    webserver_thread.start()
    print("Calling polling start!")
    data_polling()
 
