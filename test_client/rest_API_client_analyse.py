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
                "ts_from":'1551088710',
                "ts_to":'1551088720',
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

# service_json = {'category': {'battery level': False, 'jammer': False, 'ir_motion': False, 'air_pressure': False, 'door sensor': False, 'pump sensor': False, 'temperature': False, 'disk': 'low', 'network': 'low', 'accelerometer': False, 'humidity': False, 'location': False, 'memory': 'low', 'inclinometer': False, 'cpu': 'low'},
#                 'ts_from': '1550755977', 'name': 'clearwater_ims', 'resourceURI': '/clearwater_ims', 'exec_type': 'docker', 'service_id': 'clearwater_ims', 'exec': 'helloworld', 'ts_to': '1550756040', 'description': 'clearwater_ims'}


url = 'http://localhost:46020/mf2c/analyse'
res = requests.post(url, json=service_json, headers=headers)
if res.ok:
    print 'Analysis Done'
    json_data = json.loads(res.text)
    print json_data
else:
    print res.status_code
    print res.content

