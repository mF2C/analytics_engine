import requests
import time
import json
service_json = {
    "name": "test",
    "device_id": "092b7908-69ee-46ee-b2c7-2d9ae23ee298", #optional. No device filtering applied if this value is not provided. Invalid device will return 404 error.
    'sort_order': ['memory', 'cpu'], #optional, default - [cpu]
    'telemetry_filter': False, #optional, default - False
    "description": "test",
    "project": "mf2c" #optional. Required if device_id is provided for filtering
}

headers = {'Content-type': 'application/json', 'Accept': 'text/json'}
# data=json.dumps(payload)
url = 'http://localhost:46020/mf2c/optimal'
print time.time()
res = requests.post(url, json=service_json, headers=headers)
if res.ok:
    print time.time()
    print 'Optimal hosts'
    json_data = json.loads(res.text)
    print json_data
else:
    print 'Error ' + str(res.status_code) + ":" + res.content

