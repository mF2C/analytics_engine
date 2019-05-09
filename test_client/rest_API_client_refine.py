import requests
import json
headers = {'Content-type': 'application/json', 'Accept': 'text/json'}
# data=json.dumps(payload)
json_recipe = {'name': 'test', "id": "464d4a27-4f83-473f-bbe4-95c4d3b5f06b", 'analysis_id': '1551872706000000000'}
url = 'http://localhost:46020/mf2c/refine'
res = requests.post(url, json=json_recipe, headers=headers)
if res.ok:
    print 'Analysis Done'
    json_data = json.loads(res.text)
    print json_data
else:
    print res.status_code
    print res.content

