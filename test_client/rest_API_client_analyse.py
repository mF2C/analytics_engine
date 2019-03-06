import requests
import json
import time

#end_time = int(time.time())-10
end_time = 1543763810
start_time = end_time - 200
#start_time = 1543225841-100
#end_time = 1543225841
print start_time
print end_time
headers = {'Content-type': 'application/json', 'Accept': 'text/json'}
# data=json.dumps(payload)
service_json = {
    "name": "clearwater_ims",
    "description": "clearwater_ims",
    "id": "464d4a27-4f83-473f-bbe4-95c4d3b5f06b",
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
    "opt_resource": ["SenseHat"],
    "ts_from": '1551803300',
    "ts_to": '1551803400',
}

url = 'http://localhost:46020/mf2c/analyse'
res = requests.post(url, json=service_json, headers=headers)
if res.ok:
    print 'Analysis Done'
    json_data = json.loads(res.text)
    print json_data
else:
    print res.status_code
    print res.content

