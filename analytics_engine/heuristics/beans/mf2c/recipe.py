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

    def __init__(self, name=None, id=None, description=None, exec_field=None, exec_type=None, exec_ports=[],
                 agent_type="normal", num_agents=1, cpu_arch="x64-64", os="linux", ts_to=None, ts_from=None,
                 req_resource=[], opt_resource=[]):
        self._name = name
        self._id = id
        self._description = description
        self._exec = exec_field
        self._exec_type = exec_type
        self._exec_ports = exec_ports
        self._ts_to = ts_to
        self._ts_from = ts_from
        self._agent_type = agent_type
        self._num_agents = num_agents
        self._cpu_arch = cpu_arch
        self._os = os
        self._req_resource = req_resource
        self._opt_resource = opt_resource
        self._cpu_recommended = None
        self._memory_recommended = None
        self._disk_recommended = None
        self._storage_min = None
        self._network_recommended = None

    def refine(self, tag, value):
        if tag == "cpu":
            self._cpu_recommended = value
        elif tag == "memory":
            self._memory_recommended = value
        elif tag == "network":
            self._network_recommended = value
        elif tag == "disk":
            self._disk_recommended = value
        else:
            LOG.error('Not valid tag for the recipe')

    def to_json(self):
        json_recipe = {
                    u"name": self._name,
                    u"id": self._id,
                    u"description": self._description,
                    u"ts_to": self._ts_to,
                    u"ts_from": self._ts_from,
                    u"exec": self._exec,
                    u"exec_type": self._exec_type,
                    u"exec_ports": self._exec_ports,
                    u"agent_type": self._agent_type,
                    u"num_agents": self._num_agents,
                    u"cpu_arch": self._cpu_arch,
                    u"os": self._os,
                    u"req_resource": self._req_resource,
                    u"opt_resource": self._opt_resource,
                    u"cpu_recommended": self._cpu_recommended,
                    u"memory_recommended": self._memory_recommended,
                    u"disk_recommended": self._disk_recommended,
                    u"storage_min": self._storage_min,
                    u"network_recommended": self._network_recommended
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
            self._name = json_data.get('name').encode("ascii") if json_data.get('name') else None
        self._id = json_data.get('id')
        self._description = json_data.get('description')
        self._exec = json_data.get('exec')
        self._exec_type = json_data.get('exec_type')
        self._exec_ports = json_data.get('exec_ports')
        self._agent_type = json_data.get('agent_type')
        self._num_agents = json_data.get('num_agents')
        self._cpu_arch = json_data.get('cpu_arch')
        self._os = json_data.get('os')
        self._req_resource = json_data.get('req_resource')
        self._opt_resource = json_data.get('opt_resource')
        self._cpu_arch = json_data.get("cpu_arch")
        self._cpu_recommended = json_data.get("cpu_recommended")
        self._memory_recommended = json_data.get("memory_recommended")
        self._disk_recommended = json_data.get("disk_recommended")
        self._storage_min = json_data.get("storage_min")
        self._network_recommended = json_data.get("network_recommended")
        if 'ts_from' in json_data:
            self._ts_to = int(json_data.get('ts_to'))
            self._ts_from = int(json_data.get('ts_from'))
        else:
            self._ts_to = 0
            self._ts_from = 0

    def set_service_id(self, id):
        self._id = id

    def get_service_id(self):
        if hasattr(self, "_id"):
            return self._id
        else:
            return None
