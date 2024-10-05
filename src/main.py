import json
import socket

import threading
import time

from DCS_link.dcs_link import DCS_Link
#from src.Submodules.Artillery_Sim.src.artillery_sim import ArtillerySim as arty
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

def simulate_gun(fire_order: dict) -> None:

    for key, message in fire_order.items():
    
        if key == "fire_order":
            number_of_rounds = message["number_of_rounds"]

            for index in range(number_of_rounds):
                location = {
                    "system": message["target_location"]["system"],
                    "coordinate": {
                        "UTMZone": message["target_location"]["coordinate"]["UTMZone"],
                        "MGRSDigraph": message["target_location"]["coordinate"]["MGRSDigraph"],
                        "Easting": random.normal(message["target_location"]["coordinate"]["Easting"], 35),
                        "Northing": random.normal(message["target_location"]["coordinate"]["Northing"], 35)
                    },
                    "elevation": message["target_location"]["elevation"]
                }    
                shot = {
                    'simulated_shot': {
                        'time_fired': get_current_mission_time(),
                        'location' : location,
                        'time_of_flight': random.normal(5, 0.25),
                        'ammunition_type': message["ammunition"],
                        'fuze': message["fuze"],
                        'caliber': 155,
                        'direction': message["direction"],
                        'impact_angle': message["impact_angle"]
                    }
                }
                DCS_Link.insert_shot(shot)
                time.sleep(random.normal(8.5, 0.5))




    return

def handle_messages(messages: list[dict]) -> None:

    for key, message in messages.items():

        if key == "Call For Fire":
            elevation = int(message["Location"]["Elevation"])
            fuze = message["Fuze"]
            direction = message["direction"]
            impact_angle = message["impact_angle"]

            match (message["Warning Order"]):

                case "adjust_fire":
                    ammunition_type = "high_explosive"
                    number_of_rounds = 1
                    number_of_guns = 1

                case "fire_for_effect":
                    ammunition_type = "high_explosive"
                    number_of_rounds = message["Number Of Rounds"]
                    number_of_guns = message["Number Of Guns"]

                case "surpress":
                    ammunition_type = "high_explosive"
                    number_of_rounds = message["Number Of Rounds"]
                    number_of_guns = message["Number Of Guns"]

                case "mark":
                    ammunition_type = "illumination"
                    number_of_rounds = 1
                    number_of_guns = 1

                case "illumination":
                    ammunition_type = "illumination"
                    number_of_rounds = 1
                    number_of_guns = 1
                    elevation += 600
                    fuze = "time"

                case _:

                    raise ValueError("That shouldn't happen! Somehow the desired effect is unknown to me!")

            coordinate_system = message["Location"]["System"]
            
            match (coordinate_system): 

                case "mgrs":
                    parts = str(message["Location"]["Coordinate"]).split(' ')

                    if len(parts) != 4:

                        raise ValueError("Somehow the coordinate doesn't match!")
                    
                    location = {
                        "UTMZone": parts[0],
                        "MGRSDigraph": parts[1],
                        "Easting": int(parts[2]),
                        "Northing": int(parts[3])
                    }

                case _:

                    raise ValueError("That shouldn't happen the coordinate system is unknown to me!")


            
            
            fire_order = {
                "fire_order": {
                    "target_location": {
                        "system": coordinate_system,
                        "coordinate": location,
                        "elevation": elevation
                    },
                    "ammunition": ammunition_type,
                    "fuze": fuze,
                    "number_of_rounds": number_of_rounds,
                    "time_on_target": 0,
                    "direction": direction,
                    "impact_angle": impact_angle
                }
            }
            print(type(fire_order))

            guns: list[threading.Thread] = []

            for index in range(number_of_guns):
                new_gun = threading.Thread(target = simulate_gun, args = (fire_order,))
                new_gun.start()
                guns.append(new_gun)

            for gun in guns:
                gun.join()

            print("Rounds complete!")

        else:

            raise ValueError("Message is unknown to me!")
        
    return

def data_polling() -> None:
    global current_mission_time

    while True:
        current_mission_time = DCS_Link.get_mission_time()
        #arty.update(int(current_mission_time / 1000))
        messages = Webserver.main.polling_data()

        if messages:
            handle_messages_thread = threading.Thread(target = handle_messages, args = messages)
            handle_messages_thread.start()

    return

def setup() -> None:

    return

if __name__ == "__main__":
    setup()
    print("Calling DCS-Link Start!")
    DCS_Link.start()
    print("Calling Webserver Start")
    webserver_thread = threading.Thread(target = Webserver.main.start())
    webserver_thread.start()
    print("Calling polling start!")
    data_polling()
 
