import requests
import time
import json
service_json = {
    "name": "clearwater_ims",
    "device_id": "092b7908-69ee-46ee-b2c7-2d9ae23ee2xx", #optional. No device filtering applied if this value is not provided. Invalid device will return 404 error.
    'sort_order': ['memory', 'cpu'], #optional, default - [cpu]
    'telemetry_filter': False, #optional, default - False
    "description": "clearwater_ims",
    "project": "mf2c", #optional. Required if device_id is provided for filtering
    "exec": "mf2c/compss-test:it2",
    "exec_type": "vm",
    "exec_ports": [8080],
    "agent_type": "normal",
    "num_agents": 2,
    "cpu_arch": "x86-64",
    "os": "linux",
    "memory_min": 1000,
    "storage_min": 100,
    "disk": 100,
    "req_resource": ["Location"],
    "opt_resource": ["SenseHat"]
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

