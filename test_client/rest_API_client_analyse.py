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
service_json = {#'service_id': '7fd553a3-b707-49b5-be65-250716e7d4fb',
                "name": "helloworld"
                ,"ts_from":start_time
                ,"ts_to":end_time
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

