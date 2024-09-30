#from flask import Flask
from flask import Flask
import sys
import os
import threading
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Webserver.routes import init_routes
from Webserver.data import data_queue

app = Flask(__name__)
webserver_thread = None
running = False

def start():

    if running:

        return
    
    print("Starting Webserver!")
    init_routes(app)
    webserver_thread = threading.Thread(target=lambda: app.run(debug=False))
    webserver_thread.start()

    return

def polling_data() -> list[dict]:
    new_list = []

    while not data_queue.empty():
        new_list.append(data_queue.get())

    return new_list

if __name__ == '__main__':
    start()