from flask import render_template, request
from .data import data_queue

def init_routes(app):
    global data_queue

    @app.route('/')
    def form():
        return render_template('call_for_fire.html')

    @app.route('/submit', methods = ['POST'])
    def submit():
        grid = request.form.get('grid')
        elevation = request.form.get('elevation')
        desired_effect = request.form.get('desired_effect')
        number_of_rounds = request.form.get('number_of_rounds', type = int)
        number_of_guns = request.form.get('number_of_guns', type = int)

        new_call_for_fire = {
            "Call For Fire": {
                "Location": {
                    "System": "Internal",
                    "Coordinate": grid,
                    "Elevation": elevation
                },
                "Ammunition": desired_effect,
                "Number Of Rounds": number_of_rounds,
                "Number Of Guns": number_of_guns
            }
        }
        data_queue.put(new_call_for_fire)

        return render_template('call_for_fire.html')