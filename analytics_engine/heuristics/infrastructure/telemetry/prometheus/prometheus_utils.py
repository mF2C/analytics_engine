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

__author__ = 'Sridhar Voorakkara'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"

import pandas
from analytics_engine.heuristics.beans.infograph import InfoGraphNode
from analytics_engine import common

LOG = common.LOG

class PrometheusUtils(object):

    @staticmethod
    def annotate_machine_pu_util(internal_graph, node):
        source = InfoGraphNode.get_machine_name_of_pu(node)
        machine = InfoGraphNode.get_node(internal_graph, source)
        machine_util = InfoGraphNode.get_compute_utilization(machine)
        InfoGraphNode.set_compute_utilization(machine, pandas.Dataframe())

    @staticmethod
    def annotate_machine_disk_util(internal_graph, node):
        source = InfoGraphNode.get_attributes(node)['allocation']
        machine = InfoGraphNode.get_node(internal_graph, source)
        machine_util = InfoGraphNode.get_disk_utilization(machine)
        InfoGraphNode.set_disk_utilization(machine, pandas.Dataframe())

    @staticmethod
    def annotate_machine_network_util(internal_graph, node):
        source = InfoGraphNode.get_attributes(node)['allocation']
        machine = InfoGraphNode.get_node(internal_graph, source)
        machine_util = InfoGraphNode.get_network_utilization(machine)
        InfoGraphNode.set_network_utilization(machine, pandas.Dataframe())

    @staticmethod
    def utilization(internal_graph, node, telemetry):
        # machine usage
        telemetry_data = telemetry.get_data(node)
        return

    @staticmethod
    def saturation(internal_graph, node, telemetry):
        telemetry_data = telemetry.get_data(node)
        return


