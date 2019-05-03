import requests
import time
import json
service_json = {
    "name": "test",
    "description": "test",
    "id": "464d4a27-4f83-473f-bbe4-95c4d3b5f06b"
}

headers = {'Content-type': 'application/json', 'Accept': 'text/json'}
# data=json.dumps(payload)
url = 'http://localhost:46020/5ge/optimal_vms'
print time.time()
res = requests.post(url, json=service_json, headers=headers)
if res.ok:
    print time.time()
    print 'Optimal hosts'
    json_data = json.loads(res.text)
    print json_data

