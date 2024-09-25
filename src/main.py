import json
import random
import socket
import threading
import time

import numpy

shots: list[dict] = []
PORT = 15000
current_mission_time_lock = threading.Lock()
current_mission_time: float = 0

def read_current_mission_time():

    with current_mission_time_lock:

        return current_mission_time

def write_current_mission_time(value: float):
    global current_mission_time 

    with current_mission_time_lock:
        current_mission_time = value

    return

def create_random_shots():
    ammunition_types = [
        "High Explosive",
        "High Explosive Airburst",
        "Illumination",
        "Smoke"
        ]
    last_time = 0

    while True:
        x = input("Latitude: ")
        y = input("Longitude: ")
        number_of_rounds = input("Number of Rounds: ")
        time_between_rounds = input("Time between rounds: ")
        print("Ammunition Type\n1 - HE\n2 - HE A/B\n3 - Illum\n4 - Smoke")
        ammunition_type = input("Type: ")
        print(ammunition_type)

        for index in range(int(number_of_rounds)):
            shot = {
                'Simulated Shot': {
                    'Time Fired': current_mission_time,
                    'Location' : {
                        'System': "MGRS",
                        'Latitude': numpy.random.normal(float(x), 35),
                        'Longitude': numpy.random.normal(float(y), 35),
                        'Elevation': 60,
                    },
                    'Time Of Flight': numpy.random.normal(5, 1),
                    'Ammunition Type': ammunition_types[int(ammunition_type) - 1],
                    'Caliber': 60
                }
            }
            shots.append(shot)
            time.sleep(max(numpy.random.normal(8.5, 1.0), float(time_between_rounds)))

    return

def start_socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', PORT))  # Bind to localhost and Port 12345
    server_socket.listen(5)  # Listen for up to 5 connections
    print(f"Server listening on port {PORT}...")
    client_socket, addr = server_socket.accept()  # Accept a new connection
    print(f"Connection from {addr}")
    create_shots_thread = threading.Thread(target = create_random_shots)
    create_shots_thread.start()
    
    while True:
        message = client_socket.recv(4096)
        message = message.decode("utf-8")

        if message == "quit":

            break
        
        try:
            message_parsed = json.loads(message)
        
        except:
            print("error parsing message!")
        
        if "Missiontime" in message_parsed:
            #add logic to give time to artillery sim
            #print(message_parsed["Missiontime"])
            write_current_mission_time(message_parsed["Missiontime"])

            for shot in shots[:]:
                message = json.dumps(shot)
                client_socket.send(f'{message}\n'.encode("utf-8"))
                shots.remove(shot)




        # Beispielbefehl an den Client senden (du kannst hier den gewünschten Befehl einfügen)
        #command = "trigger.action.outText('Empfangener Befehl: Feuer!', 10)"
        #client_socket.sendall(command.encode('utf-8'))  # Sende den Befehl an den Lua-Client
        
        # Schließe die Verbindung
        #client_socket.close()

if __name__ == "__main__":
    app.run(debug = True)
    start_socket_server()
