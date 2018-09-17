import requests
import json
headers = {'Content-type': 'application/json', 'Accept': 'text/json'}
# data=json.dumps(payload)
json_recipe = {'service_id': 'helloworld', 'analysis_id': '1534252200000000000'}
url = 'http://localhost:46020/mf2c/refine'
res = requests.post(url, json=json_recipe, headers=headers)
if res.ok:
    print 'Analysis Done'
    json_data = json.loads(res.text)
    print json_data
else:
    print res.status_code
    print res.content

