import json
import requests
import time
import pyrebase
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

api_url = CONFIG['API_URL']

def trackVehicleHistory():
    print("### STARTING TO STORE HISTORICAL DATA ###")
    while True:
        try:
            r = requests.get(api_url, timeout = 10)
            machineData = json.loads(r.text)
            print(machineData)

            for machine in machineData:
                machine['lastPosition']['longitude'] = machine['lastPosition']['longitude'] + 8
                timestamp = machine['lastPosition']['timestamp'].split(".")[0]
                db.child("MachineHistory").child(machine['id']).child(round(datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S").timestamp())).set(machine['lastPosition'])
                db.child("Machines").child(machine['id']).set(machine)
        except:
            pass
        time.sleep(15)

if __name__ == "__main__":
    r = requests.get(api_url, timeout = 10)
    machineData = json.loads(r.text)
    print(str(machineData[0]) + "\n" + str(machineData[1]))

    for machine in machineData:
        machine['lastPosition']['longitude'] = machine['lastPosition']['longitude'] + 8
        machineIDS.append(machine['id'])
        db.child("Machines").child(machine['id']).set(machine)

    threading.Thread(target = trackVehicleHistory).start()
