import smartcar
from flask import Flask, redirect, render_template, request, jsonify
from flask_cors import CORS

import os


app = Flask(__name__)
app.secret_key = 'abcd1233134'
CORS(app)

#setup client, smartcar credentials
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

    return redirect('/locateme')

@app.route('/vehicle')
def vehicle():
    """Get vehicle ids in order to send a request to a vehicle"""


    # Access the global variable to retrieve our access tokens
    global access
    
    #   Request Step 2: the list of vehicle ids
    vehicle_ids = smartcar.get_vehicle_ids(
        access['access_token'])['vehicles']
    
    #   Request Step 3: Create a vehicle. Instantiate the first vehicle in the vehicle id list
    selected_vehicle = smartcar.Vehicle(vehicle_ids[1], access['access_token'])

    #   Request Step 4: Make a request to Smartcar API
    info = selected_vehicle.info()
    print(info)

    return jsonify(info)

@app.route('/locateme')
def locate():
    """Locate user's vehicle"""

    global access

    vehicle_ids = smartcar.get_vehicle_ids(access['access_token'])['vehicles']

    selected_vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])

    location = selected_vehicle.location()
    print(location)

    return render_template('locateme.html', location=location)    

@app.route('/location')
def location():
    "Get vehicle ids in order to send a request to retrieve the vehicle's location"
    
    global access

    vehicle_ids = smartcar.get_vehicle_ids(
    access['access_token'])['vehicles']

    selected_vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])

    location = selected_vehicle.location()
    print(location)

    return jsonify(location)

@app.route('/odometer')
def odometer():
    "Get vehicle ids in order to send a request to retrieve the vehicle's odometer"

    global access
    print('show me this', access)
    vehicle_ids = smartcar.get_vehicle_ids(access['access_token'])['vehicles']

    selected_vehicle = smartcar.Vehicle(vehicle_ids[0], access['access_token'])

    odometer = selected_vehicle.odometer()
    print(odometer)

    return jsonify(odometer)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')