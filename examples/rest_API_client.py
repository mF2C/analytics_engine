# Copyright (c) 2017, Intel Research and Development Ireland Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__author__ = 'Giuliana Carullo'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"

import requests
import json


json_recipe = {
    "name": 'avg_test',
    "description": 'test workload',

    "resourceURI": '/avg-test',
    "exec": 'avg_test',
    "exec_type": 'docker',
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

# "ts_to":'1522144965',
# "ts_from":'1522144953',

json_internal = {
    "service_id": 'avg_test',
    "ts_to": '1522144965',
    "ts_from": '1522144953',
    "analysis_id": '',
}

headers = {'Content-type': 'application/json', 'Accept': 'text/json'}
# data=json.dumps(payload)
url = 'http://localhost:46020/mf2c/optimal'
res = requests.post(url, json=json_recipe, headers=headers)
if res.ok:
    print 'Optimal Done'
    json_data = json.loads(res.text)
    print json_data



headers = {'Content-type': 'application/json', 'Accept': 'text/json'}
url = 'http://localhost:46020/mf2c/analyse'
res = requests.post(url, json=json_internal, headers=headers)
if res.ok:
    print 'Analysis Done'
    print ('Received: {}'.format(res.text))
    json_data = json.loads(res.text)
    json_internal = json_data
    print json_data

url = 'http://localhost:46020/mf2c/refine'
res = requests.post(url, json=json_internal, headers=headers)
if res.ok:
    print 'Refine recipe Done'
    print ('Received: {}'.format(res.text))
    json_data = json.loads(res.text)
    print json_data
