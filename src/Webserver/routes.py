from flask import render_template, request
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from Webserver.data import data_queue

def init_routes(app):
    global data_queue

    @app.route('/')
    def form():
        return render_template('call_for_fire.html')

    @app.route('/submit', methods = ['POST'])
    def submit():
        warning_order = request.form.get('warning_order')
        coordinate_system = request.form.get('coordinate_system')
        coordinate = request.form.get('grid')
        elevation = request.form.get('elevation')
        fuze = request.form.get('fuze')
        number_of_rounds = request.form.get('number_of_rounds', type = int)
        number_of_guns = request.form.get('number_of_guns', type = int)

        new_call_for_fire = {
            "Call For Fire": {
                "Warning Order": warning_order,
                "Location": {
                    "System": coordinate_system,
                    "Coordinate": coordinate,
                    "Elevation": elevation
                },
                "Fuze": fuze,
                "Number Of Rounds": number_of_rounds,
                "Number Of Guns": number_of_guns
            }
        }
        data_queue.put(new_call_for_fire)

        return render_template('call_for_fire.html')