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

    def __init__(self, name=None, service_id=None, description=None, resourceURI=None,
                 exec_field = None, exec_type = None, ts_to = None, ts_from = None):
        self._name = name
        self._service_id = service_id
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
            "network": None
        }

    def set_category(self, tag, value):
        if tag in self._category.keys():
            self._category[tag] = value
        else:
            LOG.error('Not valid tag for the recipe')

    def to_json(self):
        json_recipe = {
                    u"name": self._name,
                    u"service_id": self._service_id,
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
                        u"network": self._category['network']
                    }

                }
        return json_recipe

    def from_json(self, json_data):
        LOG.info('JSON: {}'.format(json_data))
        json_data = json.loads(json.dumps(json_data))
        LOG.info(json_data)
        try:
            # self._name = str(json_data['name'])
            self._name = json_data.get('name').encode("ascii")
        except:
            json_data = json.loads(json_data)
            # self._name = str(json_data['name'])
            self._name = json_data.get('name').encode("ascii")
        self._service_id = json_data.get('service_id').encode("ascii")
        self._description = json_data.get('description')
        self._resourceURI = json_data.get('resourceURI')
        self._exec_field = json_data.get('exec')
        self._exec_type = json_data.get('exec_type')
        if 'ts_from' in json_data:
            self._ts_to = int(json_data.get('ts_to'))
            self._ts_from = int(json_data.get('ts_from'))
        else:
            self._ts_to = 0
            self._ts_from = 0
        category = json_data.get('category')
        if category:
            self._category = {
                "cpu": category.get("cpu"),
                "memory": category.get("memory"),
                "disk": category.get("disk"),
                "network": category.get("network")
            }
