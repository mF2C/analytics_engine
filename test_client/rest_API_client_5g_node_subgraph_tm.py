import requests
import time
import json
service_json = {"name": "tnova-computeA"}
headers = {'Content-type': 'application/json', 'Accept': 'text/json'}
# data=json.dumps(payload)
url = 'http://localhost:46021/5ge/node_subgraph_telemetry'
print time.time()
res = requests.post(url, json=service_json, headers=headers)
if res.ok:
    print time.time()
    print 'Optimal hosts'
    json_data = json.loads(res.text)
    print json_data

