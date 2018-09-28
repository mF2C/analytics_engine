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

__author__ = 'Giuliana Carullo, Vincenzo Riccobene'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"

import re
import ast
import json
import copy
import yaml
import pandas
from analytics_engine import common

LOG = common.LOG


class InfoGraphNodeLayer():
    PHYSICAL = 'physical'
    VIRTUAL = 'virtual'
    SERVICE = 'service'


class InfoGraphNodeType():
    PHYSICAL_SWITCH = 'switch'
    PHYSICAL_MACHINE = 'machine'
    PHYSICAL_NIC = 'osdev_network'

    # TODO - URGENT: Select the right one between the following options.
    # The right one depends on the snap collector for the disk, according to the info necessary
    PHYSICAL_DISK = 'osdev_storage' #or 'disk'
    PHYSICAL_PU = 'pu'
    PHYSICAL_CORE = 'core'  # or "pu"

    # Skipping all the followings:
    # misc
    # memorymodule
    # bridge
    # cache
    # package
    # numanode
    # osdev_compute
    # subnet

    VIRTUAL_MACHINE = 'vm'
    VIRTUAL_NIC = 'vnic'
    VIRTUAL_NETWORK = 'network'
    VIRTUAL_DISK = 'volume'
    INSTANCE_DISK = 'disk'
    VIRTUAL_SWITCH = 'switch'

    SERVICE_COMPUTE = 'stack'
    DOCKER_CONTAINER = 'docker_container'
    # SERVICE_NETWORK = 'OS::Neutron::Port'
    # # SERVICE_VOLUME = 'OS::Cinder::Volume'
    # SERVICE_VOLUME = 'OS::Cinder::VolumeAttachment'


class InfoGraphNodeCategory():
    NETWORK = 'network'
    COMPUTE = 'compute'
    STORAGE = 'storage'
    MEMORY = 'memory'


class InfoGraphNodeProperty():
    LAYER = 'layer'
    TYPE = 'type'
    CATEGORY = 'category'
    # ATTRIBUTES = 'attributes'
    QUERIES = 'queries'
    TELEMETRY_DATA = 'telemetry_data'
    UTILIZATION = 'utilization'
    UTILIZATION_COMPUTE = 'utilization_compute'
    UTILIZATION_MEMORY = 'utilization_memory'
    UTILIZATION_DISK = 'utilization_disk'
    UTILIZATION_NETWORK = 'utilization_network'
    SATURATION_COMPUTE = 'saturation_compute'
    SATURATION_MEMORY = 'saturation_memory'
    SATURATION_DISK = 'saturation_disk'
    SATURATION_NETWORK = 'saturation_network'


class InfoGraphNode(object):

    @staticmethod
    def adjust_node_str_to_dict(node):
        """
        If the node properties are in string format, this method returns
        a node where properties are in a dictionary format

        :param node: Node of InfoGraph
        :return: Node of InfoGraph
        """
        node = [node[0], InfoGraphUtilities.str_to_dict(node[1])]
        if 'attributes' in node[1]:
            node[1]['attributes'] = \
                InfoGraphUtilities.str_to_dict(node[1]['attributes'])
        return node

    @staticmethod
    def get_node(graph, node_name):
        if not isinstance(node_name, str) and \
                not isinstance(node_name, unicode):
            raise ValueError("Parameter node_name is not a string. param: {}".
                             format(node_name))
        node_props = graph.node[node_name]
        node = [node_name, node_props]
        return node

    @staticmethod
    def get_name(node):
        return node[0]

    @staticmethod
    def get_properties(node):
        if len(node) == 2:
            return InfoGraphUtilities.str_to_dict(node[1])
        return None

    @staticmethod
    def get_type(node):
        if len(node) == 2 and InfoGraphNodeProperty.TYPE in node[1]:
            return str(node[1][InfoGraphNodeProperty.TYPE])
        return None

    @staticmethod
    def get_layer(node):
        if len(node) == 2 and InfoGraphNodeProperty.LAYER in node[1]:
            return node[1][InfoGraphNodeProperty.LAYER]
        return None

    @staticmethod
    def get_category(node):
        if len(node) == 2 and InfoGraphNodeProperty.CATEGORY in node[1]:
            return node[1][InfoGraphNodeProperty.CATEGORY]
        return None

    @staticmethod
    def get_attributes(node):
        if len(node) == 2:
            attrs = copy.deepcopy(node[1])
            attrs.pop("category")
            attrs.pop("layer")
            res = InfoGraphUtilities.str_to_dict(attrs)
            return res
        return None

    @staticmethod
    def set_queries(node, queries):
        """
        Store the telemetry queries into the node properties.

        :param node:
        :param queries: (list of str) Queries to get all metrics related to
                        the node.
        :return: None
        """
        if not len(node) == 2:
            raise ValueError("Node format is not correct. NODE: {}".
                             format(node))
        node[1][InfoGraphNodeProperty.QUERIES] = queries

    @staticmethod
    def get_queries(node):
        if len(node) == 2 and InfoGraphNodeProperty.QUERIES in node[1]:
            return node[1][InfoGraphNodeProperty.QUERIES]
        return None

    @staticmethod
    def get_utilization(node):
        # if len(node) == 2 and InfoGraphNodeProperty.UTILIZATION in node[1]:
        #     return node[1][InfoGraphNodeProperty.UTILIZATION]
        # return pandas.DataFrame()
        node_utilization_compute = InfoGraphNode.get_compute_utilization(node)
        node_utilization_memory = InfoGraphNode.get_memory_utilization(node)
        node_utilization_disk = InfoGraphNode.get_disk_utilization(node)
        node_utilization_network = InfoGraphNode.get_network_utilization(node)
        util = node_utilization_compute.append(node_utilization_memory).append(node_utilization_disk).append(
                node_utilization_network)
        return util


    @staticmethod
    def get_compute_utilization(node):
        if len(node) == 2 and InfoGraphNodeProperty.UTILIZATION_COMPUTE in node[1]:
            return node[1][InfoGraphNodeProperty.UTILIZATION_COMPUTE]
        return pandas.DataFrame()

    @staticmethod
    def get_memory_utilization(node):
        if len(node) == 2 and InfoGraphNodeProperty.UTILIZATION_MEMORY in node[1]:
            return node[1][InfoGraphNodeProperty.UTILIZATION_MEMORY]
        return pandas.DataFrame()

    @staticmethod
    def get_network_utilization(node):
        if len(node) == 2 and InfoGraphNodeProperty.UTILIZATION_NETWORK in node[1]:
            return node[1][InfoGraphNodeProperty.UTILIZATION_NETWORK]
        return pandas.DataFrame()

    @staticmethod
    def get_disk_utilization(node):
        if len(node) == 2 and InfoGraphNodeProperty.UTILIZATION_DISK in node[1]:
            return node[1][InfoGraphNodeProperty.UTILIZATION_DISK]
        return pandas.DataFrame()

    @staticmethod
    def set_utilization(node, utilization):
        if not len(node) == 2:
            raise ValueError("Node format is not correct.")
        node[1][InfoGraphNodeProperty.UTILIZATION] = utilization.fillna(0)

    @staticmethod
    def set_compute_utilization(node, utilization):
        if not len(node) == 2:
            raise ValueError("Node format is not correct.")
        node[1][InfoGraphNodeProperty.UTILIZATION_COMPUTE] = utilization.fillna(0)

    @staticmethod
    def set_memory_utilization(node, utilization):
        if not len(node) == 2:
            raise ValueError("Node format is not correct.")
        node[1][InfoGraphNodeProperty.UTILIZATION_MEMORY] = utilization.fillna(0)

    @staticmethod
    def set_disk_utilization(node, utilization):
        if not len(node) == 2:
            raise ValueError("Node format is not correct.")
        node[1][InfoGraphNodeProperty.UTILIZATION_DISK] = utilization.fillna(0)

    @staticmethod
    def set_network_utilization(node, utilization):
        if not len(node) == 2:
            raise ValueError("Node format is not correct.")
        node[1][InfoGraphNodeProperty.UTILIZATION_NETWORK] = utilization.fillna(0)

    ####### saturation ########
    @staticmethod
    def set_compute_saturation(node, saturation):
        if not len(node) == 2:
            raise ValueError("Node format is not correct.")
        node[1][InfoGraphNodeProperty.SATURATION_COMPUTE] = saturation

    @staticmethod
    def set_memory_saturation(node, saturation):
        if not len(node) == 2:
            raise ValueError("Node format is not correct.")
        node[1][InfoGraphNodeProperty.SATURATION_MEMORY] = saturation

    @staticmethod
    def set_disk_saturation(node, saturation):
        if not len(node) == 2:
            raise ValueError("Node format is not correct.")
        node[1][InfoGraphNodeProperty.SATURATION_DISK] = saturation

    @staticmethod
    def set_network_saturation(node, saturation):
        if not len(node) == 2:
            raise ValueError("Node format is not correct.")
        node[1][InfoGraphNodeProperty.SATURATION_NETWORK] = saturation

    @staticmethod
    def get_disk_saturation(node):
        if len(node) == 2 and InfoGraphNodeProperty.SATURATION_DISK in node[1]:
            return node[1][InfoGraphNodeProperty.SATURATION_DISK]
        return pandas.DataFrame()

    @staticmethod
    def get_compute_saturation(node):
        if len(node) == 2 and InfoGraphNodeProperty.SATURATION_COMPUTE in node[1]:
            return node[1][InfoGraphNodeProperty.SATURATION_COMPUTE]
        return pandas.DataFrame()

    @staticmethod
    def get_memory_saturation(node):
        if len(node) == 2 and InfoGraphNodeProperty.SATURATION_MEMORY in node[1]:
            return node[1][InfoGraphNodeProperty.SATURATION_MEMORY]
        return pandas.DataFrame()

    @staticmethod
    def get_network_saturation(node):
        if len(node) == 2 and InfoGraphNodeProperty.SATURATION_NETWORK in node[1]:
            return node[1][InfoGraphNodeProperty.SATURATION_NETWORK]
        return pandas.DataFrame()

    @staticmethod
    def get_saturation(node):
        node_saturation_compute = InfoGraphNode.get_compute_saturation(node)
        node_saturation_memory = InfoGraphNode.get_memory_saturation(node)
        node_saturation_disk = InfoGraphNode.get_disk_saturation(node)
        node_saturation_network = InfoGraphNode.get_network_saturation(node)
        sat = node_saturation_compute.append(node_saturation_memory).append(node_saturation_disk).append(
            node_saturation_network)
        return sat

    @staticmethod
    def set_attribute(node, key, value):
        if not len(node) == 2:
            raise ValueError("Node format is not correct.")
        if not isinstance(InfoGraphNode.get_attributes(node), dict):
            raise ValueError("Node has no attributes.")
        node[1]['attributes'][key] = value

    @staticmethod
    def set_attributes(node, attributes):
        if not len(node) == 2:
            raise ValueError("Node format is not correct.")

        # if 'attributes' not in node[1]:
        node[1]['attributes'] = dict()
        for key in attributes:
            node[1]['attributes'][key] = attributes[key]

    @staticmethod
    def set_telemetry_data(node, data):
        if not len(node) == 2:
            raise ValueError("Node format is not correct.")
        node[1][InfoGraphNodeProperty.TELEMETRY_DATA] = data

    @staticmethod
    def get_telemetry_data(node):
        if len(node) == 2 and InfoGraphNodeProperty.TELEMETRY_DATA in node[1]:
            return node[1][InfoGraphNodeProperty.TELEMETRY_DATA]
        return pandas.DataFrame()

    @staticmethod
    def get_core_index(node):
        # TODO - Refer to the PU instead of cores
        node_name = InfoGraphNode.get_name(node)
        if not InfoGraphNode.get_type(node) == InfoGraphNodeType.PHYSICAL_CORE:
            raise ValueError("Node {} is not a core. \nNode: {}",
                             node_name, InfoGraphNode.get_properties(node))
        match_obj = re.search("(.*)_core_(.*)", node_name)
        try:
            core = match_obj.group(2)
        except:
            return None
        return core

    @staticmethod
    def node_is_machine(node):
        node_type = InfoGraphNode.get_type(node)
        node_layer = InfoGraphNode.get_layer(node)
        if node_type == InfoGraphNodeType.PHYSICAL_MACHINE and \
                        node_layer == InfoGraphNodeLayer.PHYSICAL:
            return True
        return False

    @staticmethod
    def node_is_disk(node):
        node_type = InfoGraphNode.get_type(node)
        node_layer = InfoGraphNode.get_layer(node)
        if node_type == InfoGraphNodeType.PHYSICAL_DISK and \
                        node_layer == InfoGraphNodeLayer.PHYSICAL:
            return True
        return False

    @staticmethod
    def node_is_nic(node):
        node_type = InfoGraphNode.get_type(node)
        node_layer = InfoGraphNode.get_layer(node)
        if node_type == InfoGraphNodeType.PHYSICAL_NIC and \
                        node_layer == InfoGraphNodeLayer.PHYSICAL:
            return True
        return False

    @staticmethod
    def node_is_vm(node):
        node_type = InfoGraphNode.get_type(node)
        node_layer = InfoGraphNode.get_layer(node)
        if node_type == InfoGraphNodeType.VIRTUAL_MACHINE and \
                        node_layer == InfoGraphNodeLayer.VIRTUAL:
            return True
        return False

    @staticmethod
    def node_is_vnic(node):
        node_type = InfoGraphNode.get_type(node)
        node_layer = InfoGraphNode.get_layer(node)
        if node_type == InfoGraphNodeType.VIRTUAL_NIC and \
                        node_layer == InfoGraphNodeLayer.VIRTUAL:
            return True
        return False

    @staticmethod
    def node_is_virtual_disk(node):
        node_type = InfoGraphNode.get_type(node)
        node_layer = InfoGraphNode.get_layer(node)
        if node_type == InfoGraphNodeType.VIRTUAL_DISK and \
                node_layer == InfoGraphNodeLayer.VIRTUAL:
            return True
        return False

    @staticmethod
    def node_is_physical_switch(node):
        node_type = InfoGraphNode.get_type(node)
        # LOG.info(node_type)
        node_layer = InfoGraphNode.get_layer(node)
        if node_type == InfoGraphNodeType.PHYSICAL_SWITCH and \
           node_layer == InfoGraphNodeLayer.PHYSICAL:
            return True
        return False

    @staticmethod
    def get_vnic_ip_address(node):
        node_properties = InfoGraphNode.get_attributes(node)
        if 'ip' in node_properties.keys():
            return node_properties['ip']
        else:
            return ''

    @staticmethod
    def get_stack_name(graph, node):
        """
        If the node is a virtual machine, returns the stack name correspondent

        :param graph: InfoGraph
        :param node: node of InfoGraph representing a vm
        :return: (str)
        """
        res = ['', '']
        ungraph = graph.to_undirected()

        node_layer = InfoGraphNode.get_layer(node)
        heat_template = None
        if node_layer == InfoGraphNodeLayer.SERVICE:
            res[0] = InfoGraphNode.get_attributes(node)['stack_name']

        elif node_layer == InfoGraphNodeLayer.VIRTUAL:
            node_name = InfoGraphNode.get_name(node)
            neighbors = ungraph.neighbors(node_name)
            for neigh_name in neighbors:
                neighbor = InfoGraphNode.get_node(ungraph, neigh_name)
                if not InfoGraphNode.get_layer(neighbor) == \
                        InfoGraphNodeLayer.SERVICE:
                    continue
                res[0] = graph.node[neigh_name]['stack_name']
                template = yaml.load(graph.node[neigh_name]['template'])

                # TODO - URGENT: Check this with Kevin (in the graph, vm_name has value N/A)
                vm_name = InfoGraphNode.get_attributes(node)['vm_name']
                # LOG.info(template['resources'][vm_name].keys())
                res[1] = template['Properties']['name']

        elif node_layer == InfoGraphNodeLayer.PHYSICAL:
            LOG.critical("The physical nodes do not have any specific Stack "
                         "name associated to them. Please check the call to "
                         "the methoc get_stack_name - node: {}"
                         "".format(InfoGraphNode.get_name(node)))
        return res

    @staticmethod
    def physical_nic_is_sriov(node):
        # TODO - Giuseppe: Add parameter to the SRIOV NICs in the landscaper
        node_name = InfoGraphNode.get_name(node)
        match_obj = re.search("(.*)_\d_\d", node_name)
        if match_obj:
            return True
        else:
            return False

    @staticmethod
    def get_machine_name_of_pu(node):
        if InfoGraphNode.get_type(node) == InfoGraphNodeType.PHYSICAL_PU:
            return InfoGraphNode.get_name(node).split('_')[0]
        return None

    @staticmethod
    def get_nic_speed_mbps(node):
        if InfoGraphNode.node_is_machine(node):
            nic_speed_str = InfoGraphNode.get_attributes(node).get("nicspeedmbps")
            if nic_speed_str:
                return int(nic_speed_str)
            else:
                return 100  #default to 100mbps


    @staticmethod
    def get_docker_id(node):
        if InfoGraphNode.get_type(node) == InfoGraphNodeType.DOCKER_CONTAINER:
            #return "7985896f2336"
            attrs = InfoGraphNode.get_attributes(node)
            while attrs.get('attributes', None):
                attrs = attrs['attributes']
            if 'Hostname' in attrs:
                return attrs['Hostname']


class InfoGraphUtilities():

    @staticmethod
    def add_stack_names(graph):
        for node in graph.nodes(data=True):
            layer = InfoGraphNode.get_layer(node)
            if layer == InfoGraphNodeLayer.VIRTUAL:
                [stack, vm] = InfoGraphNode.get_stack_name(graph, node)
                res_name = "{}-{}".format(stack, vm)
                InfoGraphNode.set_attribute(node, 'resource_name', res_name)

    @staticmethod
    def get_physical_nodes(graph):
        """
        Returns physical nodes grouped by hostname.
        :param graph: (InfoGraph) graph
        :return:
        """
        res = dict()
        for node in graph.nodes(data=True):
            node_layer = InfoGraphNode.get_layer(node)
            if not node_layer == InfoGraphNodeLayer.PHYSICAL:
                continue
            allocation = InfoGraphNode.get_attributes(node)['allocation']
            if allocation not in res:
                res[allocation] = list()
            if InfoGraphNode.node_is_machine(node):
                res[allocation].append(node)
            elif InfoGraphNode.node_is_disk(node):
                res[allocation].append(node)
            elif InfoGraphNode.node_is_nic(node):
                res[allocation].append(node)
        return res

    @staticmethod
    def filter_by_layer(graph, layer):
        """
        Returns virtual nodes
        :param graph:
        :param layer: (str) the result will include only nodes beloging to
                            this layer
        :return: (list of InfoGraphNodes)
        """
        res = list()
        for node in graph.nodes(data=True):
            node_layer = InfoGraphNode.get_layer(node)
            if not node_layer == layer:
                continue
            res.append(node)
        return res

    @staticmethod
    def get_vnic_on_phnic(graph, node):
        """
        If node is a physical SRIOV NIC, it returns the virtual NIC
        with it.

        :param graph: (InfoGraph)
        :param node: (Infograph Node) physical NIC
        :return: InfoGraph node or None
        """
        node_name = InfoGraphNode.get_name(node)
        node_layer = InfoGraphNode.get_layer(node)
        ungraph = graph.to_undirected()
        neighbors = ungraph.neighbors(node_name)
        for neigh in neighbors:
            neighbor = InfoGraphNode.get_node(ungraph, neigh)
            neighbor_layer = InfoGraphNode.get_layer(neighbor)
            if neighbor_layer == InfoGraphNodeLayer.VIRTUAL:
                return neighbor
        return None

    @staticmethod
    def str_to_dict(string):
        """
        Returns a dictionary from the string

        :param string: (str) String to be converted
        :return: (dict)
        """
        res = None
        if isinstance(string, str):
            res = ast.literal_eval(str(string))
        elif isinstance(string, unicode):
            res = ast.literal_eval(str(string))
        elif isinstance(string, dict):
            res = string
        return res

    @staticmethod
    def graph_attrs_from_dict_to_str(dictionary):
        return json.dumps(dictionary)

    @staticmethod
    def get_neighbors(graph, node_name, layer=None, type=None):
        """
        Return the neighbors of a node in the graph.
        THe neighbors could be filtered by the layer or the type.

        :param graph: (InfoGraph) Graph to search into
        :param node_name: (str) Name of the node to look the neighbors for
        :param layer: (str) Layer of the neighbors (optional)
        :param type: (str) Type of the neighbors
        :return: (list) List of neighbors
        """
        if not layer and not type:
            return graph.neighbors(node_name)

        res = list()
        neighbors = graph.neighbors(node_name)
        for neigh_name in neighbors:
            node = InfoGraphNode.get_node(graph, neigh_name)
            if layer and not layer == InfoGraphNode.get_layer(node):
                continue
            if type and not type == InfoGraphNode.get_type(node):
                continue
            res.append(node)
        return res

    @staticmethod
    def get_vitual_resources(graph, hostnames):
        """
        Returns virtual nodes grouped by compute nodes

        :param graph: (InfoGraph)
        :param hostnames: (list(str))
        :return: (dict)
        """
        res = dict()

        # Creates a copy of the graph which is undirected
        undirected_graph = graph.to_undirected()

        # Group by hostname
        for hostname in hostnames:
            res[hostname] = list()

            # Individuate the node representing the physical machine in the graph
            machine_node_name = "{}_machine_0".format(hostname)
            # node = InfoGraphNode.get_node(machine_node_name)
            # hostname = InfoGraphNode.get_attributes(node)['allocation']

            try:
                InfoGraphNode.get_node(undirected_graph, machine_node_name)
            except KeyError:
                continue

            # Get all virtual machines deployed on the compute node
            virtual_machines = InfoGraphUtilities.get_neighbors(
                undirected_graph, machine_node_name,
                layer=InfoGraphNodeLayer.VIRTUAL)

            for vm in virtual_machines:
                res[hostname].append(vm)
                vm_name = InfoGraphNode.get_name(vm)
                virtual_resources = InfoGraphUtilities.get_neighbors(
                    undirected_graph, vm_name,
                    layer=InfoGraphNodeLayer.VIRTUAL)
                for virtual_resource in virtual_resources:
                    res[hostname].append(virtual_resource)
        return res

