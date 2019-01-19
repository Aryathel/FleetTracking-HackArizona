import json
import requests
import time
import pyrebase
import websocket
import threading
import datetime

machineIDS = []

CONFIG = json.loads(open("Config.json", "r").read())

connectionConfig = {
    "apiKey": CONFIG['API_KEY'],
    "authDomain": CONFIG['AUTH_DOMAIN'],
    "databaseURL": CONFIG['DB_URL'],
    "storageBucket": CONFIG['STORAGE_BUCKET'],
    "serviceAccount": CONFIG['SERVICE_ACCOUNT'],
}

firebase = pyrebase.initialize_app(connectionConfig)
db = firebase.database()

websocketURL = CONFIG['WEBSOCKET_URL']
api_url = CONFIG['API_URL']

def onSocketUpdate(socket, message):
    vehicleUpdateData = json.loads(message)
    updateJSON = []
    for i in range(0, len(vehicleUpdateData['payload'])):
        vehicleUpdateData['payload'][i]['lastPosition']['longitude'] = vehicleUpdateData['payload'][i]['lastPosition']['longitude'] + 8
        updateJSON.append({"id": vehicleUpdateData['payload'][i]['equipmentUnitId'],"update": {"lastPosition": {"longitude": vehicleUpdateData['payload'][i]['lastPosition']['longitude'], "latitude": vehicleUpdateData['payload'][i]['lastPosition']['latitude'], "elevation": vehicleUpdateData['payload'][i]['lastPosition']['elevation'], "speed": vehicleUpdateData['payload'][i]['lastPosition']['speed'], "heading": vehicleUpdateData['payload'][i]['lastPosition']['heading'], "timestamp": vehicleUpdateData['payload'][i]['lastPosition']['timestamp']}}})

    for update in updateJSON:
        db.child("Machines").child(update['id']).child('lastPosition').set(update['update']['lastPosition'])

def onSocketError(sockket, error):
    print(error)

def onSocketClose(socket):
    print("###### SOCKET CLOSING ######")

def onSocketOpen(socket):
    websocketSubscribeMessage = "ws://mine-view/subscribe?{'equipmentUnitIds':%s, 'boundingBox':{'minLatitude': -5, 'minLongitude': -84, 'maxLatitude': -3, 'maxLongitude': -82}}" % (machineIDS)
    socket.send(websocketSubscribeMessage)

def trackVehicleHistory():
    print("### STARTING TO STORE HISTORICAL DATA ###")
    while True:
        time.sleep(15)
        r = requests.get(api_url, timeout = 10)
        machineData = json.loads(r.text)
        print(machineData)

        for machine in machineData:
            machine['lastPosition']['longitude'] = machine['lastPosition']['longitude'] + 8
            machineIDS.append(machine['id'])
            timestamp = machine['lastPosition']['timestamp'].split(".")[0]
            db.child("MachineHistory").child(machine['id']).child(round(datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S").timestamp())).set(machine['lastPosition'])

"""
async def mainLoop(url):

    async with websockets.connect(url) as socket:
        await socket.send(websocketSubscribeMessage)
        while True:
            vehicleData = json.loads(await socket.recv())
            for i in range(0, len(vehicleData['payload'])):
                vehicleData['payload'][i]['lastPosition']['longitude'] = vehicleData['payload'][i]['lastPosition']['longitude'] + 8
"""

if __name__ == "__main__":
    r = requests.get(api_url, timeout = 10)
    machineData = json.loads(r.text)
    print(str(machineData[0]) + "\n" + str(machineData[1]))

    for machine in machineData:
        machine['lastPosition']['longitude'] = machine['lastPosition']['longitude'] + 8
        machineIDS.append(machine['id'])
        db.child("Machines").child(machine['id']).set(machine)

    threading.Thread(target = trackVehicleHistory).start()

    websocket.enableTrace(True)
    socket = websocket.WebSocketApp(websocketURL, on_message = onSocketUpdate, on_error = onSocketError, on_close = onSocketClose)
    socket.on_open = onSocketOpen
    socket.run_forever()
