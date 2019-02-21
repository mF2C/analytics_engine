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
service_json = {'service_id': 'clearwater_ims',
                "name": "clearwater_ims",
                "ts_from":'1550756320',
                "ts_to":'1550756330',
                "description": "test workload",
                "resourceURI": '/cpu_stress',
                "exec": 'helloworld',
                "exec_type": 'docker',
                'category': {"cpu": 'low',
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
                            "ir_motion": False}
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

