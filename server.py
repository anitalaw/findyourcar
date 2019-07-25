import smartcar
from flask import Flask, redirect, render_template, request, jsonify
from flask_cors import CORS

import os


app = Flask(__name__)
app.secret_key = 'abcd1233134'
CORS(app)


client = smartcar.AuthClient(
    client_id=os.environ.get('CLIENT_ID'),
    client_secret=os.environ.get('CLIENT_SECRET'),
    redirect_uri=os.environ.get('REDIRECT_URI'),
    scope=['required:read_location', 'required:read_vehicle_info', 'required:read_odometer'],
    test_mode=True,
)


@app.route('/')
def home():
    """Display the homepage"""

    return render_template('index.html')


@app.route('/login')
def login():
    """User connects their car to the app using OAuth2 authenication"""

    #Launch Smartcar authentication dialog
    auth_url = client.get_auth_url()
    return redirect(auth_url)


@app.route('/exchange')
def exchange_code():
    """myApp exchanges code for access_token"""
    
    my_code = request.args.get('code')
    
    #  Request Step 1: Obtain an access token
    global access
    
    access = client.exchange_code(my_code)

    return redirect('/location')


@app.route('/location')
def locate():
    """Locate user's vehicle"""

    global access

    vehicle_ids = smartcar.get_vehicle_ids(access['access_token'])['vehicles']

    selected_vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])

    location = selected_vehicle.location()
    info = selected_vehicle.info()
    odometer = selected_vehicle.odometer()
    
    return render_template('locateme.html', location=location, info=info, odometer=odometer)    



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')