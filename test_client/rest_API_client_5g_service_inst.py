import requests
import time
import json
service_json = {'service_id': 'FGE_stack_1',
                "name": "FGE_stack_1",
                "description": "FGE_stack_1",
                "resourceURI": '/FGE_stack_1',
    "exec": 'helloworld',
    "exec_type":'vm',
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
url = 'http://localhost:46020/5ge/analyze_service'
print time.time()
res = requests.post(url, json=service_json, headers=headers)
if res.ok:
    print time.time()
    print 'Optimal hosts'
    json_data = json.loads(res.text)
    print json_data

