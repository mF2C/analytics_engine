import requests
import time
import json
json_recipe = {
    "name": 'helloworld',
    "description": 'test workload',
    "ts_from":'1536916504',
    "ts_to":'1536916604',
    "resourceURI": '/helloworld',
    "exec": 'helloworld',
    "exec_type":'docker',
    "category": {
        "cpu": 'low',
        "memory": 'low',
        "disk": 'low',
        "network": 'low',
        "inclinometer": False,
        "temperature": False,
        "jammer": False,
        "location": False,
        "battery level": False,
        "door sensor": False,
        "pump sensor": False,
        "accelerometer": False,
        "humidity": False,
        "air_pressure": False,
        "ir_motion": False
    }

}
headers = {'Content-type': 'application/json', 'Accept': 'text/json'}
# data=json.dumps(payload)
url = 'http://localhost:46020/mf2c/optimal'
print time.time()
res = requests.post(url, json=json_recipe, headers=headers)
if res.ok:
    print time.time()
    print 'Analysis Done'
    json_data = json.loads(res.text)
    print json_data

