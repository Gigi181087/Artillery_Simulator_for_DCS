import queue
import socket
import json
import threading

class DCS_Link:
    _instance = None
    _queue = queue.Queue()
    _running = False
    _mission_time = 0
    _loop_thread = None
    _mission_time_lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        
        if not cls._instance:
            cls._instance = super(DCS_Link, cls).__new__(cls, *args, **kwargs)

        return cls._instance
    
    @classmethod
    def start(cls, ip: str = 'localhost', port: int = 15000) -> None:
        print("Start called!")

        if cls._running:

            return
        
        cls._running = True
        cls._loop_thread = threading.Thread(target = cls._loop, args = (ip, port))
        cls._loop_thread.start()

        return

    @classmethod    
    def stop(cls) -> None:
        cls._running = False
        threading.Thread.join(cls._loop_thread)

        return
    
    @classmethod
    def insert_shot(cls, shot: dict) -> None:

        #add routine to check if shot data is correct
        cls._queue.put(shot)

        return
    
    @classmethod
    def _loop(cls, ip:str, port: int) -> None:
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        new_socket.bind(('localhost', port))  # Bind to localhost and Port 12345
        new_socket.listen(5)  # Listen for up to 5 connections
        print(f"Server listening on port {port}...")
        _dcs_socket, addr = new_socket.accept()  # Accept a new connection
        print(f"Connection from {addr}")

        while cls._running:
            data = _dcs_socket.recv(4096)
            data = data.decode("utf-8")
            messages = [message for message in data.split('\n') if message]

            for message in messages:

                if message == "quit":

                    break
                
                try:
                    message_parsed = json.loads(message)

                except:
                    print("error parsing message!")
                
                if "Missiontime" in message_parsed:
                    #add logic to give time to artillery sim
                    #print(message_parsed["Missiontime"])
                    cls._set_mission_time(float(message_parsed["Missiontime"]))

                    while not cls._queue.empty():
                        shot = cls._queue.get()
                        message = json.dumps(shot)
                        _dcs_socket.send(f'{message}\n'.encode("utf-8"))




        return
    
    @classmethod
    def get_mission_time(cls) -> float:

        with cls._mission_time_lock:

            return cls._mission_time
        
        
    @classmethod
    def _set_mission_time(cls, mission_time: float) -> None:

        with cls._mission_time_lock:

            cls._mission_time = mission_time

        return



