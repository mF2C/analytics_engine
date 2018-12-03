import requests
import json
headers = {'Content-type': 'application/json', 'Accept': 'text/json'}
# data=json.dumps(payload)
json_recipe = {'name': 'helloworld', 'analysis_id': '1543771140000000000', 'service_id': '7fd553a3-b707-49b5-be65-250716e7d4fb'}
url = 'http://localhost:46020/mf2c/refine'
res = requests.post(url, json=json_recipe, headers=headers)
if res.ok:
    print 'Analysis Done'
    json_data = json.loads(res.text)
    print json_data
else:
    print res.status_code
    print res.content

