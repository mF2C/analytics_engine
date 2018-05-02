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

__authors__ = 'Giuliana Carullo, Vincenzo Riccobene'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"


from analytics_engine.heuristics.beans.infograph import InfoGraphNode, InfoGraphNodeType, \
    InfoGraphNodeCategory, InfoGraphNodeLayer
import pandas
import math


class Fingerprint(object):

    # Deprecated
    @staticmethod
    def _node_is_nic_on_management_net(node, graph, mng_net_name):
        node_name = InfoGraphNode.get_name(node)
        node_type = InfoGraphNode.get_type(node)
        if node_type == InfoGraphNodeType.VIRTUAL_NIC or \
           node_type == InfoGraphNodeType.VIRTUAL_NIC_2:
            neighs = graph.neighbors(node_name)
            for n in neighs:
                neighbor = InfoGraphNode.\
                    get_node(graph, n)
                if InfoGraphNode.get_type(neighbor) == \
                        InfoGraphNodeType.VIRTUAL_NETWORK:
                    network_name = \
                        InfoGraphNode.get_attributes(
                            neighbor)['name']
                    if network_name == mng_net_name:
                        return True
        return False

    @staticmethod
    def workload_capacity_usage(annotated_subgraph):
        """
        This is a type of fingerprint
        """
        # TODO: Validate graph

        categories = list()
        categories.append(InfoGraphNodeCategory.COMPUTE)
        categories.append(InfoGraphNodeCategory.NETWORK)
        # TODO: Add a Volume to the workloads to get HD usage
        categories.append(InfoGraphNodeCategory.STORAGE)
        # TODO: Get telemetry for Memory
        categories.append(InfoGraphNodeCategory.MEMORY)

        fingerprint = dict()
        counter = dict()
        for category in categories:
            fingerprint[category] = 0
            counter[category] = 0

        # calculation of the fingerprint on top of the virtual resources
        local_subgraph = annotated_subgraph.copy()
        local_subgraph.filter_nodes('layer', "physical")
        local_subgraph.filter_nodes('layer', "service")

        for node in local_subgraph.nodes(data=True):
            # if Fingerprint._node_is_nic_on_management_net(
            #         node, annotated_subgraph, mng_net_name):
            #     continue
            category = InfoGraphNode.get_category(node)
            utilization = InfoGraphNode.get_utilization(node)
            if 'utilization' in utilization.columns.values:
                mean = utilization['utilization'].mean()
                fingerprint[category] += mean
                counter[category] += 1

        # This is just an average
        # TODO: Improve the average
        for category in categories:
            if counter[category] > 0:
                fingerprint[category] = \
                    fingerprint[category] / counter[category]
        return fingerprint

    @staticmethod
    def machine_capacity_usage(annotated_subgraph):
        """
        This is a type of fingerprint from the infrastructure perspective
        """
        # TODO: Validate graph
        categories = list()
        categories.append(InfoGraphNodeCategory.COMPUTE)
        categories.append(InfoGraphNodeCategory.NETWORK)
        # TODO: Add a Volume to the workloads to get HD usage
        categories.append(InfoGraphNodeCategory.STORAGE)
        # TODO: Get telemetry for Memory
        categories.append(InfoGraphNodeCategory.MEMORY)

        fingerprint = dict()
        counter = dict()
        for category in categories:
            fingerprint[category] = 0
            counter[category] = 0

        # calculation of the fingerprint on top of the virtual resources
        local_subgraph = annotated_subgraph.copy()
        local_subgraph.filter_nodes('layer', "virtual")
        local_subgraph.filter_nodes('layer', "service")
        local_subgraph.filter_nodes('type', 'machine')

        for node in local_subgraph.nodes(data=True):
            # if Fingerprint._node_is_nic_on_management_net(
            #         node, annotated_subgraph, mng_net_name):
            #     continue
            name = InfoGraphNode.get_name(node)
            category = InfoGraphNode.get_category(node)
            utilization = InfoGraphNode.get_utilization(node)
            if 'utilization' in utilization.columns.values:
                # LOG.info("NODE: {} - CATEGORY: {}".format(name, category))
                mean = utilization['utilization'].mean()
                fingerprint[category] += mean
                counter[category] += 1

        # This is just an average
        # TODO: Improve the average
        for category in categories:
            if counter[category] > 0:
                fingerprint[category] = \
                    fingerprint[category] / counter[category]
        return fingerprint

    @staticmethod
    def compute_node(annotated_subgraph, hostname=None):
        """
        This is a type of fingerprint from the infrastructure perspective
        """
        # TODO: Validate graph
        data = dict()
        statistics = dict()
        compute = InfoGraphNodeCategory.COMPUTE
        data[compute] = pandas.DataFrame()
        statistics[compute] = {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'var': 0, 'std_dev': 0}
        network = InfoGraphNodeCategory.NETWORK
        data[network] = pandas.DataFrame()
        statistics[network] = {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'var': 0, 'std_dev': 0}
        storage = InfoGraphNodeCategory.STORAGE
        data[storage] = pandas.DataFrame()
        statistics[storage] = {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'var': 0, 'std_dev': 0}
        memory = InfoGraphNodeCategory.MEMORY
        data[memory] = pandas.DataFrame()
        statistics[memory] = {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'var': 0, 'std_dev': 0}

        # Calculation of the fingerprint on top of the virtual resources
        local_subgraph = annotated_subgraph.copy()

        for node in local_subgraph.nodes(data=True):
            layer = InfoGraphNode.get_layer(node)
            is_machine = InfoGraphNode.node_is_machine(node)
            if is_machine:
                continue
            if layer == InfoGraphNodeLayer.VIRTUAL:
                continue
            if layer == InfoGraphNodeLayer.SERVICE:
                continue
            # If hostname has been specified, need to take into account only
            # nodes that are related to the specific host
            attrs = InfoGraphNode.get_attributes(node)
            allocation = attrs['allocation'] if 'allocation' in attrs \
                else None
            if hostname and not hostname == allocation:
                continue

            category = InfoGraphNode.get_category(node)
            utilization = InfoGraphNode.get_utilization(node)
            try:
                utilization = utilization.drop('timestamp', 1)
            except ValueError:
                utilization = InfoGraphNode.get_utilization(node)
            data[category] = pandas.concat([data[category], utilization])

        for category in statistics:
            if not data[category].empty:
                mean = data[category]['utilization'].mean()
                median = (data[category]['utilization']).median()
                min = data[category]['utilization'].min()
                maximum = data[category]['utilization'].max()
                var = data[category]['utilization'].var()
                std_dev = math.sqrt(var)
            else:
                mean = 0
                median = 0
                min = 0
                maximum = 0
                var = 0
                std_dev = 0
            statistics[category] = \
                {'mean': mean,
                 'median': median,
                 'min': min,
                 'max': maximum,
                 'var': var,
                 'std_dev': std_dev}

        return [data, statistics]

    @staticmethod
    def compute_node_resources(annotated_subgraph, hostname=None):
        """
        This is a type of fingerprint from the infrastructure perspective
        """
        # TODO: Validate graph
        data = dict()
        statistics = dict()

        # Calculation of the fingerprint on top of the virtual resources
        local_subgraph = annotated_subgraph.copy()

        for node in local_subgraph.nodes(data=True):
            layer = InfoGraphNode.get_layer(node)
            if layer == InfoGraphNodeLayer.VIRTUAL:
                continue
            if layer == InfoGraphNodeLayer.SERVICE:
                continue
            type = InfoGraphNode.get_type(node)
            if type == 'core':
                continue

            # If hostname has been specified, need to take into account only
            # nodes that are related to the specific host
            attrs = InfoGraphNode.get_attributes(node)
            allocation = attrs['allocation'] if 'allocation' in attrs \
                else None
            if hostname and not hostname == allocation:
                continue

            name = InfoGraphNode.get_name(node)
            statistics[name] = {'mean': 0,
                                'median': 0,
                                'min': 0,
                                'max': 0,
                                'var': 0,
                                'std_dev': 0}
            utilization = InfoGraphNode.get_utilization(node)
            try:
                utilization = utilization.drop('timestamp', 1)
            except ValueError:
                utilization = InfoGraphNode.get_utilization(node)
            data[name] = utilization

            if not data[name].empty:
                mean = data[name]['utilization'].mean()
                median = (data[name]['utilization']).median()
                min = data[name]['utilization'].min()
                maximum = data[name]['utilization'].max()
                var = data[name]['utilization'].var()
                std_dev = math.sqrt(var)
            else:
                mean = 0
                median = 0
                min = 0
                maximum = 0
                var = 0
                std_dev = 0
            statistics[name] = \
                {'mean': mean,
                 'median': median,
                 'min': min,
                 'max': maximum,
                 'var': var,
                 'std_dev': std_dev}

        return [data, statistics]

    @staticmethod
    def workload(nodes):
        """
        This is a type of fingerprint from the infrastructure perspective
        """
        # TODO: Validate graph
        data = dict()
        statistics = dict()
        compute = InfoGraphNodeCategory.COMPUTE
        data[compute] = pandas.DataFrame()
        statistics[compute] = {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'var': 0, 'std_dev': 0}
        network = InfoGraphNodeCategory.NETWORK
        data[network] = pandas.DataFrame()
        statistics[network] = {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'var': 0, 'std_dev': 0}
        storage = InfoGraphNodeCategory.STORAGE
        data[storage] = pandas.DataFrame()
        statistics[storage] = {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'var': 0, 'std_dev': 0}
        memory = InfoGraphNodeCategory.MEMORY
        data[memory] = pandas.DataFrame()
        statistics[memory] = {'mean': 0, 'median': 0, 'min': 0, 'max': 0, 'var': 0, 'std_dev': 0}

        # Calculation of the fingerprint on top of the virtual resources
        for node in nodes:
            layer = InfoGraphNode.get_layer(node)
            is_machine = InfoGraphNode.node_is_machine(node)
            if is_machine:
                continue
            if layer == InfoGraphNodeLayer.PHYSICAL:
                continue
            if layer == InfoGraphNodeLayer.SERVICE:
                continue

        for category in statistics:
            mean = data[category]['utilization'].mean()
            median = 0
            min = 0
            maximum = 0
            var = 0
            std_dev = 0
            statistics[category] = \
                {'mean': mean,
                 'median': median,
                 'min': min,
                 'max': maximum,
                 'var': var,
                 'std_dev': std_dev}

        return [data, statistics]