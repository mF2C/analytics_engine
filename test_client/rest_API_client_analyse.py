import requests
import json

headers = {'Content-type': 'application/json', 'Accept': 'text/json'}
# data=json.dumps(payload)
service_json = {
    "name": "test",
    "description": "test service",
    "id": "464d4a27-4f83-473f-bbe4-95c4d3b5f06b",
    "ts_from": '1551803300',
    "ts_to": '1551803400'
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

