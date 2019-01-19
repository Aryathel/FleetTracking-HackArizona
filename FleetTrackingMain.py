import json
import requests
import time
import asyncio

async def mainLoop():
    while True:
        r = requests.get("http://52.160.46.169//api/EquipmentManagement/v1.0/EquipmentUnit", timeout = 10)
        machineData = json.loads(r.text)
        print(machineData)
        await asyncio.sleep(30)

loop = asyncio.get_event_loop()
loop.run_until_complete(mainLoop())
print("Hi")
