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

import analytics_engine.common as common
import json

LOG = common.LOG

"""
Models the recipe input for MF2C project.
"""


class Recipe(object):

    def __init__(self, name=None, description=None, resourceURI=None,
                 exec_field = None, exec_type = None, ts_to = None, ts_from = None):
        self._name = name
        self._description = description
        self._resourceURI = resourceURI
        self._exec_field = exec_field
        self._exec_type = exec_type
        self._ts_to = ts_to
        self._ts_from = ts_from
        self._category = {
            "cpu": None,
            "memory": None,
            "disk": None,
            "network": None,
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

    def set_category(self, tag, value):
        if tag in self._category.keys():
            self._category[tag] = value
        else:
            LOG.error('Not valid tag for the recipe')

    def to_json(self):
        json_recipe = {
                    u"name": self._name,
                    u"description": self._description,
                    u"ts_to": self._ts_to,
                    u"ts_from": self._ts_from,
                    u"resourceURI": self._resourceURI,
                    u"exec": self._exec_field,
                    u"exec_type": self._exec_type,
                    u"category": {
                        u"cpu": self._category['cpu'],
                        u"memory": self._category['memory'],
                        u"disk": self._category['disk'],
                        u"network": self._category['network'],
                        u"inclinometer": self._category['inclinometer'],
                        u"temperature": self._category['temperature'],
                        u"jammer": self._category['jammer'],
                        u"location": self._category['location'],
                        u"battery level": self._category['battery level'],
                        u"door sensor": self._category['door sensor'],
                        u"pump sensor": self._category['pump sensor'],
                        u"accelerometer": self._category['accelerometer'],
                        u"humidity": self._category['humidity'],
                        u"air_pressure": self._category['air_pressure'],
                        u"ir_motion": self._category['ir_motion']
                    }

                }
        return json_recipe

    def from_json(self, json_data):
        LOG.info('JSON: {}'.format(json_data))
        json_data = json.loads(json.dumps(json_data))
        LOG.info(json_data)
        try:
            # self._name = str(json_data['name'])
            self._name= json_data['name'].encode("ascii")
        except:
            json_data = json.loads(json_data)
            # self._name = str(json_data['name'])
            self._name = json_data['name'].encode("ascii")
        self._description = json_data['description']
        self._resourceURI = json_data['resourceURI']
        self._exec_field = json_data['exec']
        self._exec_type = json_data['exec_type']
        if 'ts_from' in json_data:
            self._ts_to = int(json_data['ts_to'])
            self._ts_from = int(json_data['ts_from'])
        else:
            self._ts_to = 0
            self._ts_from = 0
        self._category = {
            "cpu": json_data["category"]["cpu"],
            "memory": json_data["category"]["memory"],
            "disk": json_data["category"]["disk"],
            "network": json_data["category"]["network"],
            "inclinometer": json_data["category"]["inclinometer"],
            "temperature": json_data["category"]["temperature"],
            "jammer": json_data["category"]["jammer"],
            "location": json_data["category"]["location"],
            "battery level": json_data["category"]["battery level"],
            "door sensor": json_data["category"]["door sensor"],
            "pump sensor": json_data["category"]["pump sensor"],
            "accelerometer": json_data["category"]["accelerometer"],
            "humidity": json_data["category"]["humidity"],
            "air_pressure": json_data["category"]["air_pressure"],
            "ir_motion": json_data["category"]["ir_motion"]
        }
