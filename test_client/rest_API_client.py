import requests
import time
import json
service_json = {
    "name": "clearwater_ims",
    "id": "464d4a27-4f83-473f-bbe4-95c4d3b5f06b",
    "description": "clearwater_ims",
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

