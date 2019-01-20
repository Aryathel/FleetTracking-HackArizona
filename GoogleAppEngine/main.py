import logging
import json
import threading
import pyrebase
import requests
from flask import Flask
from flask import request
from flask import Response

app = Flask(__name__)

CONFIG = json.loads(open("Config.json", "r").read())

connectionConfig = {
    "apiKey": CONFIG['API_KEY'],
    "authDomain": CONFIG['AUTH_DOMAIN'],
    "databaseURL": CONFIG['DB_URL'],
    "storageBucket": CONFIG['STORAGE_BUCKET'],
    "serviceAccount": CONFIG['SERVICE_ACCOUNT'],
}

api_url = CONFIG['API_URL']

firebase = pyrebase.initialize_app(connectionConfig)
db = firebase.database()

@app.route("/check_a_vehicle", methods = ['GET', 'POST', 'DELETE'])
def check_vehicle():
    req = request.get_json(force=True)
    type_params = req.get('queryResult').get('parameters').get('VehicleData')
    id_param = req.get('queryResult').get('parameters').get('number')
    
    r = requests.get(api_url, timeout = 10)
    machineData = json.loads(r.text)

    res_msg = ""

    for machine in machineData:
        if int(machine['id']) == int(id_param):
            res_msg = ""
            for item in type_params:
                longitude = ""
                latitude = ""
                speed = ""
                direction = ""
                altitude =""
                Type = ""
                
                if item == "Everything":
                    longitude = machine['lastPosition']['longitude'] + 8
                    latitude = machine['lastPosition']['latitude']
                    speed = machine['lastPosition']['speed']
                    heading = machine['lastPosition']['heading']
                    if heading < 0:
                        heading += 360
                    if heading <= (0+22.5) or heading > 337.25:
                        direction = "North"
                    elif heading > (22.5) and heading <= (22.5+45):
                        direction = "Northeast"
                    elif heading > (22.5+45) and heading <= (22.5+90):
                        direction = "East"
                    elif heading > (22.5+90) and heading <= (22.5+135):
                        direction = "Southeast"
                    elif heading > (22.5 + 135) and heading <= (22.5 + 180):
                        direction = "South"
                    elif heading > (22.5+180) and heading <= (22.5+225):
                        direction = "Southwest"
                    elif heading > (22.5+225) and heading <= (22.5+270):
                        direction = "West"
                    elif heading > (2.5+270) and heading <= (22.5+305):
                        direction = "Northwest"
                    altitude = machine['lastPosition']['elevation']
                    Type = machine['equipmentType']['name']
                    center_lat = -4.321336
                    center_long = -75.081992
                    towardsOtherQuadrant = False
                    if latitude > center_lat:
                        if longitude > center_long:
                            quadrant = "1"
                            if direction in ['West', 'Southwest', 'South']:
                                towardsOtherQuadrant = True
                                if direction == "West":
                                    towards_quadrant = "2"
                                elif direction == "Southwest":
                                    towards_quadrant = "3"
                                elif direction == "South":
                                    towards_quadrant = "4"
                            else:
                                pass
                        else:
                            quadrant = "2"
                            if direction in ['East', 'Southeast', 'South']:
                                towardsOtherQuadrant = True
                                if direction == "East":
                                    towards_quadrant = "1"
                                elif direction == "Southeast":
                                    towards_quadrant = "4"
                                elif direction == "South":
                                    towards_quadrant = "3"
                            else:
                                pass
                    else:
                        if longitude > center_long:
                            quadrant = "4"
                            if direction in ['North', 'Northwest', 'West']:
                                towardsOtherQuadrant = True
                                if direction == "North":
                                    towards_quadrant = "1"
                                elif direction == "Northwest":
                                    towards_quadrant = "2"
                                elif direction == "West":
                                    towards_quadrant = "3"
                            else:
                                pass
                        else:
                            quadrant = "3"
                            if direction in ['North', 'Northeast', 'East']:
                                towardsOtherQuadrant = True
                                if direction == "North":
                                    towards_quadrant = "2"
                                elif direction == "Northeast":
                                    towards_quadrant = "1"
                                elif direction == "East":
                                    towards_quadrant = "4"
                            else:
                                pass
                    if speed > 0:
                        if towardsOtherQuadrant == True:
                            res_msg = "Vehicle {0} is a {1}. The position of vehicle {0} is {2} degrees North and {3} degrees East, at an altitude of {4} feet. The vehicle is in Quadrant {8} travelling {5} at {6} miles per hour, towards Quadrant {7}.".format(machine['id'], Type, latitude, longitude, altitude, direction, speed, towards_quadrant, quadrant)
                        else:
                            res_msg = "Vehicle {0} is a {1}. The position of vehicle {0} is {2} degrees North and {3} degrees East, at an altitude of {4} feet. The vehicle is in Quadrant {7}, travelling {5} at {6} miles per hour.".format(machine['id'], Type, latitude, longitude, altitude, direction, speed, quadrant)
                    else:
                        res_msg = "Vehicle {0} is a {1}. The position of vehicle {0} is {2} degrees North and {3} degrees East, at an altitude of {4} feet. The vehicle is facing {5} in Quadrant {7}, and it is not moving.".format(machine['id'], Type, latitude, longitude, altitude, direction, speed, quadrant)

                elif item == "Location":
                    longitude = machine['lastPosition']['longitude'] + 8
                    latitude = machine['lastPosition']['latitude']

                    if res_msg == "":
                        res_msg = res_msg + "The position of vehicle %s is %s degrees North and %s degrees East." % (machine['id'], latitude, longitude)
                    else:
                        res_msg = res_msg + "\nThe position of vehicle %s is %s degrees North and %s degrees East." % (machine['id'], latitude, longitude)

                elif item == "Speed":
                    speed = machine['lastPosition']['speed']

                    if res_msg == "":
                        res_msg = res_msg + "The speed of vehicle %s is %s miles per hour." % (machine['id'], speed)
                    else:
                        res_msg = res_msg + "\nThe speed of vehicle %s is %s miler per hour." % (machine['id'], speed)

                elif item == "Heading":
                    longitude = machine['lastPosition']['longitude'] + 8
                    latitude = machine['lastPosition']['latitude']
                    center_lat = -4.321336
                    center_long = -75.081992
                    towardsOtherQuadrant = False

                    heading = machine['lastPosition']['heading']
                    if heading < 0:
                        heading += 360
                    if heading <= (0+22.5) and heading > 337.25:
                        direction = "North"
                    elif heading > (22.5) and heading <= (22.5+45):
                        direction = "Northeast"
                    elif heading > (22.5+45) and heading <= (22.5+90):
                        direction = "East"
                    elif heading > (22.5+90) and heading <= (22.5+135):
                        direction = "Southeast"
                    elif heading > (22.5 + 135) and heading <= (22.5 + 180):
                        direction = "South"
                    elif heading > (22.5+180) and heading <= (22.5+225):
                        direction = "Southwest"
                    elif heading > (22.5+225) and heading <= (22.5+270):
                        direction = "West"
                    elif heading > (2.5+270) and heading <= (22.5+305):
                        direction = "Northwest"

                    if latitude > center_lat:
                        if longitude > center_long:
                            quadrant = "1"
                            if direction in ['West', 'Southwest', 'South']:
                                towardsOtherQuadrant = True
                                if direction == "West":
                                    towards_quadrant = "2"
                                elif direction == "Southwest":
                                    towards_quadrant = "3"
                                elif direction == "South":
                                    towards_quadrant = "4"
                            else:
                                pass
                        else:
                            quadrant = "2"
                            if direction in ['East', 'Southeast', 'South']:
                                towardsOtherQuadrant = True
                                if direction == "East":
                                    towards_quadrant = "1"
                                elif direction == "Southeast":
                                    towards_quadrant = "4"
                                elif direction == "South":
                                    towards_quadrant = "3"
                            else:
                                pass
                    else:
                        if longitude > center_long:
                            quadrant = "4"
                            if direction in ['North', 'Northwest', 'West']:
                                towardsOtherQuadrant = True
                                if direction == "North":
                                    towards_quadrant = "1"
                                elif direction == "Northwest":
                                    towards_quadrant = "2"
                                elif direction == "West":
                                    towards_quadrant = "3"
                            else:
                                pass
                        else:
                            quadrant = "3"
                            if direction in ['North', 'Northeast', 'East']:
                                towardsOtherQuadrant = True
                                if direction == "North":
                                    towards_quadrant = "2"
                                elif direction == "Northeast":
                                    towards_quadrant = "1"
                                elif direction == "East":
                                    towards_quadrant = "4"
                            else:
                                pass

                    speed = machine['lastPosition']['speed']
                    if speed > 0:
                        if towardsOtherQuadrant == True:
                            if res_msg == "":
                                res_msg = res_msg + "Vehicle %s is in Quadrant %s, heading %s towards Quadrant %s." % (machine['id'], quadrant, direction, towards_quadrant)
                            else:
                                res_msg = res_msg + "\nVehicle %s is in Quadrant %s, heading %s towards Quadrant %s." % (machine['id'], quadrant, direction, towards_quadrant)
                        else:
                            if res_msg == "":
                                res_msg = res_msg + "Vehicle %s is in Quadrant %s facing %s." % (machine['id'], quadrant, direction)
                            else:
                                res_msg = res_msg + "\nVehicle %s is in Quadrant %s facing %s." % (machine['id'], quadrant, direction)
                    else:
                        if towardsOtherQuadrant == True:
                            if res_msg == "":
                                res_msg = res_msg + "Vehicle %s is in Quadrant %s, facing %s towards Quadrant %s." % (machine['id'], quadrant, direction, towards_quadrant)
                            else:
                                res_msg = res_msg + "\nVehicle %s is in Quadrant %s, facing %s towards Quadrant %s." % (machine['id'], quadrant, direction, towards_quadrant)
                        else:
                            if res_msg == "":
                                res_msg = res_msg + "Vehicle %s is in Quadrant %s facing %s." % (machine['id'], quadrant, direction)
                            else:
                                res_msg = res_msg + "\nVehicle %s is in Quadrant %s facing %s." % (machine['id'], quadrant, direction)
                

                elif item == "Altitude":
                    altitude = machine['lastPosition']['elevation']
                    
                    if res_msg == "":
                        res_msg = res_msg + "The elevation of vehicle %s is %s feet." % (machine['id'], altitude)
                    else:
                        res_msg = res_msg + "\nThe elevation of vehicle %s is %s feet." % (machine['id'], altitude)
                    
                elif item == "Type":
                    Type = machine['equipmentType']['name']
                
                    if res_msg == "":
                        res_msg = res_msg + "Vehicle %s is a %s." % (machine['id'], Type)
                    else:
                        res_msg = res_msg + "\nVehicle %s is a %s." % (machine['id'], Type)

            break
        
        else:
            res_msg = "I'm sorry, I could not find a vehicle with that ID. Please try again."

    return(json.dumps({"payload": {"google": {"expectUserResponse": True,"richResponse": {"items": [{"simpleResponse": {"textToSpeech": res_msg, "displayText": "Here is your response, my good sir."}}]}}}}))

@app.route("/get_historical_data/")
def get_data():
    try:
        id = request.args.get("id")
    except:
        pass
    if id != None:
        vehicleHistory = db.child('MachineHistory').child(id).get()

        data = dict(vehicleHistory.val())

        latLngList = []
        for key in data.keys():
            latLngList.append({"lat": data[key]['latitude'], "lng": data[key]['longitude']})

        resp = Response(json.dumps(latLngList))
        resp.headers['Access-Control-Allow-Origin'] = "*"

        return resp
    else:
        return "{}"
