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

"""
Info core integration.
"""
import time
import json
import networkx as nx
from config_helper import ConfigHelper
import telemetry
import analytics_engine.common as common

LOG = common.LOG

PROPS = ['name', 'layer', 'category', 'type', 'attributes']
EOT = 1924905600.0


def get_info_graph(info_graph=None, landscape=None):
    """
    Factory function which returns an info graph class either using the
    arguments provided or from a configuration file.
    :param info_graph: The name of the info graph to use.
    :param landscape: A graph of the landscape.
    :return: Returns info graph based on the infograph type supplied either
    directly or from the INI file.
    """
    if not info_graph:
        info_graph = ConfigHelper.get("DEFAULT", "iaas")

    if info_graph == "openstack":
        return OpenStackInfoGraph(landscape)
    else:
        msg = "No infograph subclass for type {}".format(info_graph)
        raise AttributeError(msg)


class InfoGraph(nx.DiGraph):
    """
    Graph object representing a (sub)graph of the landscape.
    """

    def __init__(self):
        """
        Initializes the InfoGraph.
        """
        super(InfoGraph, self).__init__()
        #self.telemetry = telemetry.get_telemetry()

    def add_landscape(self, graph):
        """
        replace all nodes and edges in the graph.
        :param graph: The graph containing the nodes and edges that are placed
        in the infograph.
        """
        self.clear()
        self.add_nodes_from(graph.nodes(data=True))
        self.add_edges_from(graph.edges())

    def get_nodes_by_type(self, qtype):
        """
        Get a set of nodes by a give type.

        :param qtype: The type you are looking for
        :return: List of nodes
        """
        res = []
        for node in self.nodes():
            if qtype == self.node[node].get('type'):
                res.append(node)
        return res

    def get_machine_cores(self, machine):
        cores = []
        for node in self.nodes(data=True):
            if node[1]["type"] == "core":
                if node[1]["attributes"]["allocation"] == machine:
                    cores.append(node[0])
        return cores

    def get_neighbour_by_type(self, node_id, ntype):
        """
        Return the first neighbour which is of a certain type.

        :param node_id: Id for a node
        :param ntype: Type the neighbour node should have
        :return: The neighbour.
        """
        for relation in nx.all_neighbors(self, node_id):
            if self.node[relation].get('type') == ntype:
                return relation

    def get_neighbours_by_type(self, node_id, ntype):
        """
        Return all neighbours of a certain type.

        :param node_id: Id for a node
        :param ntype: Type the neighbour node should have
        :return: The neighbours.
        """
        neighbours = []
        for relation in nx.all_neighbors(self, node_id):
            if self.node[relation].get('type') == ntype:
                neighbours.append(relation)
        return neighbours

    def get_neighbours_by_layer(self, node_id, nlayer):
        """
        Return all neighbours within a specific layer.

        :param node_id: Id for a node
        :param ntype: Layer the neighbour node should have
        :return: The neighbours.
        """
        neighbours = []
        for relation in nx.all_neighbors(self, node_id):
            if self.node[relation].get('layer', None) == nlayer:
                neighbours.append(relation)
        return neighbours

    def get_physical_mac(self, physical_node):
        """
        Given a physical component node, return the MAC address.
        :param physical_node: Name of the physical node
        :return: MAC address for the physical node
        """
        if self.node[physical_node].get("layer") != "physical":
            return None

        # Every node on the physical layer is prefaced with the machine name
        # (e.g. 'iriln073_socket_0')
        machine_name = physical_node.split("_")[0]
        # TODO: Only returns em1 mac adress as this is all merlin has at
        # this time. correct when merlin is updated.
        interface_name = "{}_eno1_0".format(machine_name)
        try:
            interface_attrs = self.node[interface_name].get("attributes")
        except KeyError:
            interface_name = "{}_em1_0".format(machine_name)
            interface_attrs = self.node[interface_name].get("attributes")

        mac = interface_attrs.get("address", "")
        return mac

    def get_inter_layer_rels(self, node_id, directed=True):
        """
        Get all nodes relating to this node from layers below.

        :param node_id: The node id.
        :param directed: Take direction into account or not (Default yes)
        :return: List of nodes
        """
        res = []
        tmp = self.copy()
        if not directed:
            tmp = tmp.to_undirected()

        for relation in tmp.neighbors(node_id):
            if self.node[relation]['layer'] != self.node[node_id]['layer']:
                res.append(relation)
        return res

    def get_intra_layer_rels(self, node_id, directed=True):
        """
        Get all nodes relating to this node from within the same layer.

        :param node_id: The node id.
        :param directed: Take direction into account or not (Default yes)
        :return: List of nodes
        """
        res = []
        tmp = self.copy()
        if not directed:
            tmp = tmp.to_undirected()

        for relation in tmp.neighbors(node_id):
            if self.node[relation]['layer'] == self.node[node_id]['layer']:
                res.append(relation)
        return res

    def filter_nodes(self, key, val):
        """
        Removes all of the nodes with the key value pair. When a node is
        removed the node's neighbours are connected together so that all
        connections are maintained.
        """
        if key is not None and val is not None:
            nodes_to_filter = self.select_nodes(key, val)
            for node in nodes_to_filter:
                self._filter_node(node)

    def select_nodes(self, key, val):
        """
        Return list of nodes with the given key/value.The value is optional.
        If only the key is specified then all nodes with that key are returned.
        If both key and value are specified then the key value pair must exist
        in a node for it to be added to the list.

        If the key value cannot be found in the node's properties then the node
        attributes are searched.
        :param key: The key to be searched for.
        :param val: The key value. If selected then the value and key must
        match before the node is added to the returned list.(Optional)
        """
        nodes = []
        for node, attr in self.nodes(data=True):
            if key in PROPS:
                if val:
                    if key in attr and attr[key] == val:
                        nodes.append(node)
                else:
                    if key in attr:
                        nodes.append(node)
            else:
                attributes = json.loads(attr['attributes'])
                if val:
                    if key in attributes and attributes[key] == val:
                        nodes.append(node)
                else:
                    if key in attributes:
                        nodes.append(node)
        return nodes

    def _filter_node(self, node):
        """
        Removes a node but maintains the connections between the neighbouring
        nodes.
        """
        self._connect_neighbours(node)
        self.remove_node(node)

    def _connect_neighbours(self, node):
        """
        Connect all of a node's neighbours together so that the node can be
        removed without losing the node connections.

        This is done by connecting all incoming connections of a nodeto the
        outgoing connections of the same node.
        """
        for in_edge in self.in_edges([node]):
            for out_edge in self.out_edges([node]):
                self.add_edge(in_edge[0], out_edge[1])

    def get_nominal_capacity(self, node):
        """
        Calculates and returns the nominal capacity of a node
        :param node: node of the landscape (node of a networkx graph)
        :return: float [-1,1]
        """
        if self.node[node]["layer"] != "physical":
            return None
        node_type = self.node[node]["type"]
        host = self.node[node]["attributes"]["allocation"]
        # If the input is a string it is the name of the landscape node
        if node_type == "machine":
            return self.telemetry.get_nominal_capacity("compute", host)
        elif node_type == 'osdev_network':
            nic_id = "{}".format(self.node[node]["attributes"]["name"])
            tags = {"dev_id": nic_id}
            return self.telemetry.get_nominal_capacity("network", host, tags)
        elif node_type == 'osdev_storage':
            disk_id = "/dev/{}".format(self.node[node]["attributes"]["name"])
            tags = {"dev_id": disk_id}
            return self.telemetry.get_nominal_capacity("disk", host, tags)
        return None

    def get_ram_nominal(self, node):
        if self.node[node]["layer"] != "physical":
            return None
        host = self.node[node]["attributes"]["allocation"]
        return self.telemetry.get_nominal_capacity("memory", host)

    def get_ram_used(self, node):
        if self.node[node]["layer"] != "physical":
            return None
        host = self.node[node]["attributes"]["allocation"]
        return self.telemetry.get_sold_capacity("memory", host)

    def get_oversubscription_ratio(self, node):
        node_type = self.node[node]["type"]

        if node_type == "machine":
            # cpu over-subscription ratio
            return 15
        elif node_type == "osdev_network":
            # Network over-subscription ratio
            return 1.5
        elif node_type == "osdev_storage":
            # Storage over-subscription ratio
            return 1.5
        return None

    def get_potential_capacity(self, node):
        """
        Returns the node potential capacity
        :param node: node of the landscape (node of a networkx graph)
        :param node_nominal_capacity: nominal capacity of the node
        :return: float
        """
        node_nominal_capacity = self.get_nominal_capacity(node)
        if not node_nominal_capacity:
            return None
        if node_nominal_capacity <= 0:
            return node_nominal_capacity

        oversubscription_ratio = self.get_oversubscription_ratio(node)
        if node_nominal_capacity and oversubscription_ratio:
            return float(node_nominal_capacity * oversubscription_ratio)
        return None

    def get_resource_coefficient(self, node):
        node_type = self.node[node]["type"]

        if node_type == "machine":
            return float(len(self.get_machine_cores(node)))
        elif node_type == "osdev_network":
            # All these fake figures, it's terrible, terrible.
            return 1000.0
        elif node_type == "osdev_storage":
            # Who knows
            return 1.0
        return None

    def get_network_bandwidth(self, vm):
        # If the network bandwidth is not indicated, it means
        # that there is no SLA on the network.
        return 0

    def get_sold_capacity(self, node):
        """
        Return the sold capacity of a node
        :param node: node of the landscape (node of a networkx graph)
        :return: float
        """
        node_type = self.node[node]["type"]
        # Get the network sold capacity from the landscape
        if node_type == 'osdev_network':
            net_bandwidth_request = 0.0
            machine = self.node[node]['attributes']['allocation']
            vms = self.get_neighbours_by_type(machine, "vm")
            for vm in vms:
                net_bandwidth_request += self.get_network_bandwidth(vm)
            return net_bandwidth_request

        # Get the storage sold capacity from the landscape
        if node_type == 'osdev_storage':
            storage_size_request = 0.0
            machine = self.node[node]['attributes']['allocation']
            volumes = self.get_neighbours_by_type(machine, "volume")
            for volume in volumes:
                storage_size_request += self.node[volume]['attributes']['size']
            return storage_size_request

        # Get the compute sold capacity from the landscape
        if node_type == 'machine':
            compute_core_request = 0.0
            vms = self.get_neighbours_by_type(node, "vm")
            for vm in vms:
                compute_core_request += self.node[vm]['attributes']['vcpu']
            return compute_core_request
        return None

    @staticmethod
    def get_capacity_factor(guard_threshold, nominal_capacity,
                            sold_capacity, potential_capacity):
        """
        Calculates and returns the capacity factor starting from the input
        parameters

        :param guard_threshold: tuning parameter for the capacity factor
        :param nominal_capacity:nominal capacity of the node
        :param sold_capacity: sold capacity of the node
        :param potential_capacity: potential capacity of the node
        :return: int [0, 1]
        """
        if nominal_capacity <= 0 \
                or sold_capacity < 0 \
                or potential_capacity < 0:
            return None
        if sold_capacity == 0:
            return 1
        if sold_capacity < nominal_capacity:
            return 1
        if sold_capacity > potential_capacity:
            return 0
        ratio = (float(nominal_capacity) / sold_capacity)
        if sold_capacity <= guard_threshold:
            return 1
        else:
            return ratio

    def get_capacity(self, node_id):
        return self.node[node_id].get("capacity", -1)

    def get_resource_capacities(self):
        resource_capacities = dict()
        for node in self.node:
            resource_capacity = self.get_resource_capacity(node)
            if resource_capacity:
                node_type = self.node[node]["type"]
                if node_type not in resource_capacities:
                    resource_capacities[node_type] = dict()
                resource_capacities[node_type][node] = resource_capacity

        return resource_capacities

    def save_capacities(self, bad_util, bad_sat):
        for node in self.node:
            self.node[node]['util_attrs'] = {}

            if node == 'iriln074':
                pass
            try:
                resource_cp = self.get_resource_capacity(node)
            except Exception as e:
                resource_cp = {}
            try:
                processing_cp = self.get_processing_capacity(node, bad_util,
                                                             bad_sat)
            except Exception as e:
                processing_cp = {}

            if 'compute' in resource_cp and 'compute' in processing_cp:
                res_cp = resource_cp['compute']
                prc_cp = processing_cp['compute']
                self.node[node]['util_attrs']['compute_resource_cp'] = res_cp
                self.node[node]['util_attrs']['compute_processing_cp'] = prc_cp
            if 'network' in resource_cp and 'network' in processing_cp:
                res_cp = resource_cp['network']
                prc_cp = processing_cp['network']
                self.node[node]['util_attrs']['network_resource_cp'] = res_cp
                self.node[node]['util_attrs']['network_processing_cp'] = prc_cp
            if 'storage' in resource_cp and 'storage' in processing_cp:
                res_cp = resource_cp['storage']
                prc_cp = processing_cp['storage']
                self.node[node]['util_attrs']['storage_resource_cp'] = res_cp
                self.node[node]['util_attrs']['storage_processing_cp'] = prc_cp

    def get_latencies(self):
        lat_list = []
        for node_name in self.node:
            n_type = self.node[node_name]['type']
            if n_type == 'machine':
                lat_list += self.telemetry.get_e2e_latency(node_name, '60s')
        return lat_list

    def get_resource_capacity(self, node):
        node_type = self.node[node]["type"]
        resource_cp = dict()

        if node_type == 'machine':
            nominal_cap = self.get_nominal_capacity(node)
            self.node[node]['util_attrs']['n_cpu'] = nominal_cap
            potential_cap = self.get_potential_capacity(node)
            self.node[node]['util_attrs']['p_cpu'] = potential_cap
            sold_cap = self.get_sold_capacity(node)
            self.node[node]['util_attrs']['s_cpu'] = sold_cap
            cap_factor_cpu = self.get_capacity_factor(nominal_cap, nominal_cap,
                                                      sold_cap, potential_cap)

            nominal_ram = self.get_ram_nominal(node)
            self.node[node]['util_attrs']['n_ram'] = nominal_ram
            self.node[node]['util_attrs']['p_ram'] = nominal_ram
            # nominal capacity for ram is equal to potential capacity
            sold_ram = self.get_ram_used(node)
            self.node[node]['util_attrs']['s_ram'] = sold_ram
            cap_factor_ram = self.get_capacity_factor(nominal_ram, nominal_ram,
                                                      sold_ram, nominal_ram)

            cap_factor = cap_factor_cpu * cap_factor_ram

            resource_cp['compute'] = ((potential_cap - sold_cap) /
                                      potential_cap) * cap_factor

        if node_type == 'osdev_network':
            nominal_cap = self.get_nominal_capacity(node)
            self.node[node]['util_attrs']['n_network'] = nominal_cap
            potential_cap = self.get_potential_capacity(node)
            self.node[node]['util_attrs']['p_network'] = potential_cap
            sold_cap = self.get_sold_capacity(node)
            self.node[node]['util_attrs']['s_network'] = sold_cap
            cap_factor = self.get_capacity_factor(nominal_cap, nominal_cap,
                                                  sold_cap, potential_cap)
            resource_cp['network'] = ((potential_cap - sold_cap) /
                                      potential_cap) * cap_factor

        if node_type == 'osdev_storage':
            nominal_cap = self.get_nominal_capacity(node)
            self.node[node]['util_attrs']['n_storage'] = nominal_cap
            potential_cap = self.get_potential_capacity(node)
            self.node[node]['util_attrs']['p_storage'] = potential_cap
            sold_cap = self.get_sold_capacity(node)
            self.node[node]['util_attrs']['s_storage'] = sold_cap
            cap_factor = self.get_capacity_factor(nominal_cap, nominal_cap,
                                                  sold_cap, potential_cap)
            resource_cp['storage'] = ((potential_cap - sold_cap) /
                                      potential_cap) * cap_factor

        return resource_cp

    def get_resource_capacity_with_request(self, node_name, r_attr):
        """
        calculates revised capacities left over when a request is applied to a
        node.
        :param node_name: identifier for the node to be mapped on
        :param r_attr: attributes of the request node to be mapped
        :return: dict()
        """
        n_attr = self.node[node_name]
        node_type = n_attr["type"]
        resource_cp = dict()
        # Get the network capacity
        if node_type == 'osdev_network':
            nominal_cap = n_attr['util_attrs']['n_network']
            potential_cap = n_attr['util_attrs']['p_network']
            sold_cap = (n_attr['util_attrs']['s_network'] +
                        r_attr['attributes']['bnwd'])
            cap_factor = self.get_capacity_factor(nominal_cap, nominal_cap,
                                                  sold_cap, potential_cap)
            resource_cp['network_resource_cp'] = (((potential_cap - sold_cap) /
                                                   potential_cap) * cap_factor)

        # Get the compute capacity factor
        if node_type == 'machine':
            nominal_cap = n_attr['util_attrs']['n_cpu']
            potential_cap = n_attr['util_attrs']['p_cpu']
            sold_cap = n_attr['util_attrs']['s_cpu'] + r_attr['attributes'][
                'vcpus']
            cap_factor_cores = self.get_capacity_factor(nominal_cap,
                                                        nominal_cap, sold_cap,
                                                        potential_cap)

            nominal_ram = n_attr['util_attrs']['n_ram']
            sold_ram = (n_attr['util_attrs']['s_ram'] +
                        r_attr['attributes']['ram'])
            cap_factor_ram = self.get_capacity_factor(nominal_ram, nominal_ram,
                                                      sold_ram, nominal_ram)
            cap_factor = cap_factor_cores * cap_factor_ram

            resource_cp['compute_resource_cp'] = (((potential_cap - sold_cap) /
                                                   potential_cap) * cap_factor)

            nominal_cap = n_attr['util_attrs']['n_storage']
            potential_cap = n_attr['util_attrs']['p_storage']
            sold_cap = (n_attr['util_attrs']['s_storage'] +
                        r_attr['attributes']['disk'])
            cap_factor = self.get_capacity_factor(nominal_cap, nominal_cap,
                                                  sold_cap, potential_cap)

            resource_cp['storage_resource_cp'] = (((potential_cap - sold_cap) /
                                                   potential_cap) * cap_factor)

        return resource_cp

    def get_processing_capacity(self, node_name, bad_util, bad_sat):
        node_type = self.node[node_name]["type"]
        processing_cp = dict()
        utilization = None
        saturation = None

        if node_type == 'machine':
            key_type_base = 'compute_'
            host = node_name
            utilization = self.telemetry.get_mean_utilisation("compute",
                                                              "10m", host)

            saturation = self.telemetry.get_percentage_saturated("compute",
                                                                 host, "10m",
                                                                 1)
            if utilization > bad_util or saturation > bad_sat:
                processing_cp['compute'] = -1
            elif utilization <= 1:
                processing_cp['compute'] = 1
            else:
                processing_cp['compute'] = 1/utilization

        if node_type == 'osdev_network':
            key_type_base = 'network_'
            # todo: hardcoded.
            host = self.node[node_name]["attributes"]["allocation"]
            # tags = {"dev_id": "ens3f1"}

            device_id = node_name.split('_')[-2]
            tags = {"dev_id": device_id}
            utilization = self.telemetry.get_mean_utilisation("network", "10m",
                                                              host, tags=tags)

            sat_data_nic = self.telemetry.get_percentage_saturated("disk",
                                                                   host,
                                                                   "10m",
                                                                   tags=tags,
                                                                   threshold=1)
            tag = {"dev_id": "eno1"}
            sat_mgmt_nic = self.telemetry.get_percentage_saturated("disk",
                                                                   host,
                                                                   "10m",
                                                                   tags=tag,
                                                                   threshold=1)

            saturation = max(sat_data_nic, sat_mgmt_nic, 0)

            if utilization > bad_util or sat_data_nic >= bad_sat or\
               sat_mgmt_nic > bad_sat:
                processing_cp['network'] = -1
            elif utilization <= 1:
                processing_cp['network'] = 1
            else:
                processing_cp['network'] = 1/utilization

        if node_type == 'osdev_storage':
            key_type_base = 'storage_'
            host = self.node[node_name]["attributes"]["allocation"]
            tags = {"dev": self.node[node_name]["attributes"]["name"]}

            utilization = self.telemetry.get_mean_utilisation("disk", "10m",
                                                              host, tags=tags)

            saturation = self.telemetry.get_percentage_saturated("disk", host,
                                                                 "10m",
                                                                 tags=tags,
                                                                 threshold=1)
            if utilization > bad_util or saturation > bad_sat:
                processing_cp['storage'] = -1
            elif utilization <= 1:
                processing_cp['storage'] = 1
            else:
                processing_cp['storage'] = 1/utilization

        self.node[node_name]['util_attrs'][
            '{}{}'.format(key_type_base, 'saturation')] = saturation or 0
        self.node[node_name]['util_attrs'][
            '{}{}'.format(key_type_base, 'utilization')] = utilization or 0

        return processing_cp


class OpenStackInfoGraph(InfoGraph):
    """
    OpenStack specific InfoGraph which is mapped to telemetry data.
    """

    def __init__(self, graph=None):
        super(OpenStackInfoGraph, self).__init__()

        # Add a graph
        if graph is not None:
            self.add_nodes_from(graph.nodes(data=True))
            self.add_edges_from(graph.edges(data=True))
        self._set_thresholds()
        self.telemetry_data = None

    def get_service_node(self, vm_id):
        """
        Given a VM id return the service layer node which defined it.

        :param vm_id: The VM id.
        :return: The name in the Graph.
        """
        # TODO: check necessity!
        for relation in self.predecessors(vm_id):
            if self.node[relation].get('type') == 'OS::Nova::Server':
                return relation.split(':')[0]

    def get_mac_for_port(self, port_name):
        """
        Return the actual MAC address for a OS::Neutron::Port in the
        service layer.

        :param port_name: Name in the template
        :return: MAC as string.
        """
        # TODO: check necessity!
        for port in self.get_nodes_by_type('OS::Neutron::Port'):
            if port.find(port_name) != -1:
                for vport in self.neighbors(port):
                    if self.node[vport].get('type') == 'compute:None':
                        tmp = self.node[vport]['attributes']
                        return tmp['mac']

    def get_mac_for_vm(self, vm_id):
        """
        Return the Mac address for a Virtual machine.

        :param vm_id: Name of the VM.
        :return: MAC as string.
        """
        # TODO: check necessity!
        port = self.get_neighbour_by_type(vm_id, 'vnic')
        return self.node[port]['attributes']['mac']

    def get_stack_id(self):
        """
        Get first stack id for this graph.

        Note: works only on subgraphs - otherwise returns first stack id.

        :return: The stack id.
        """
        for node in self.nodes():
            if 'stack_id' in self.node[node]['attributes']:
                tmp = self.node[node]['attributes']
                return tmp['stack_id']

    def get_defined_stacks(self):
        """
        Get defined stack ids and names for this graph.

        :return: Dict of stack ids & names.
        """
        res = {}
        for node in self.nodes():
            if 'stack_id' in self.node[node]['attributes']:
                tmp = self.node[node]['attributes']
                res[tmp['stack_id']] = tmp['stack_name']
        return res

    def _set_thresholds(self):
        """
        Sets the thresholds used to calculate saturation.
        """
        thresholds = {'storage_saturation': 0,
                      'network_saturation': 0,
                      'compute_saturation': 0,
                      'mem_saturation': 0
                      }
        self.thresholds = thresholds

    def _get_raw_telemetry_data(self, nsecs=600):
        """
        Gets the full suite of apexlake metrics. This should include everything
        that is required for the info_core
        """
        # Grab metric data from telemetry.
        self.telemetry_data = dict()
        telem = telemetry.get_telemetry()
        time_stamp_to = int(time.time())
        time_stamp_from = int(time.time()) - nsecs

        tags = {'type': '*', 'host': '*', 'MAC': '*'}
        raw_telemetry_data = telem.get_metric('al_metrics', tags,
                                              time_stamp_from, time_stamp_to)
        # Calculate Util/Sat values and package
        for metric in raw_telemetry_data:
            mac = metric["meta"]['tags']['MAC']
            if mac not in self.telemetry_data:
                self.telemetry_data[mac] = dict()

            # Get USE type
            use_type = ""
            metric_type = metric["meta"]['tags']['type']
            if "_" in metric_type:
                use_type = metric_type.split('_')[1]

            # Calculate value base on USE type
            metric = metric["data"]
            if use_type == "utilization":
                value = self._calculate_utilisation(metric)
            elif use_type == "saturation":
                sat_threshold = self.thresholds[metric_type]
                value = self._calculate_saturation(metric, sat_threshold)
            else:
                value = self._average_data(metric)

            # Store Value
            self.telemetry_data[mac][metric_type] = value

    def get_utilisation(self, node_name):
        """
        Return the utilisation value for a node.

        :param node_name: A node name.
        """
        return self._get_telemetry_data(node_name, 'utilization')

    def get_saturation(self, node_name):
        """
        Return the utilisation value for a node.

        :param node_name: A node name.
        """
        return self._get_telemetry_data(node_name, 'saturation')

    @staticmethod
    def _calculate_saturation(data, threshold):
        """
        Calculates the saturation value for a given data set. Saturation is
        determined as the percent of sample values above the given threshold.
        :param data: The time-series data set. format per record in dataset is
        of the form (timestamp, value).
        :param threshold: The threshold used to determine whether a value is
        saturated
        :return: The proportion of saturated data samples.
        """
        # Safegaurd against empty datasets
        if data == [] or data is None:
            return None

        saturated_samples = 0.0
        for _, value in data:
            if value > threshold:
                saturated_samples += 1
        saturation = (saturated_samples / len(data)) * 100
        return int(round(saturation))

    def _calculate_utilisation(self, data):
        """
        Calculates the utilisation value for a given dataset.  Just averages
        the values.
        :param data: The dataset
        :return: The utilisation value
        """
        return self._average_data(data)

    @staticmethod
    def _average_data(data):
        """
        Averages a list of telemetry data. The data is a list of tuples in the
        format, (timestamp, data_value)
        :param data: List of telemetry data.
        :return: Average of the data.
        """
        if data == [] or data is None:
            return None

        data_values = [value for _, value in data]
        mean = sum(data_values) / len(data_values)
        return mean

    def _get_telemetry_data(self, node_name, metric_ext):
        """
        Retrieve data from telemetry system.
        """
        if not self.telemetry_data or not hasattr(self, 'telemetry_data'):
            self._get_raw_telemetry_data()
        typo = self.node[node_name]['type']
        # compute - VCPU
        if typo == 'vm':
            mac = self.get_mac_for_vm(node_name).replace(':', '')
            try:
                tmp = self.telemetry_data[mac]
                return tmp['compute_' + metric_ext]
            except KeyError:
                LOG.warn('Missing data %s for: %s.', metric_ext, node_name)
                return -1.0
        # compute:None - SDN port
        elif typo == "vnic":
            mac = self.node[node_name]['attributes']['mac'].replace(':', '')
            try:
                tmp = self.telemetry_data[mac]
                return tmp['network_' + metric_ext]
            except KeyError:
                LOG.warn('Missing data %s for: %s.', metric_ext, node_name)
                return -1.0
        # storage - cinder block storage
        elif typo == 'volume':
            tmp = self.get_neighbour_by_type(node_name, 'vm')
            if not tmp:
                return None
            mac = self.get_mac_for_vm(tmp).replace(':', '')
            try:
                tmp = self.telemetry_data[mac]
                return tmp['storage_' + metric_ext]
            except KeyError:
                LOG.warn('Missing data %s for: %s.', metric_ext, node_name)
                return -1.0
        elif typo == "machine":
            # telemetry data for a physical machine
            return self._get_machine_util_sat(node_name, metric_ext)
        elif typo == "osdev_network":
            # em0, em1 ... etc
            return self._get_network_interface_util_sat(node_name, metric_ext)
        elif typo == "osdev_storage":
            # sda, sdb .. etc
            return self._get_storage_drive_util_sat(node_name, metric_ext)
        else:
            return None

    def _get_storage_drive_util_sat(self, drive_name, metric_type):
        """
        Get the utilisation/saturation value for a storage drive on a physical
        machine.
        :param drive_name: The name of the drive give by the OS
        :param metric_type: Metric required. Utilisation/Saturation.
        :return: Utilisation or Saturation metric for the drive.
        """
        mac_address = self.get_physical_mac(drive_name).replace(':', '')
        telemetry_data = self.telemetry_data.get(mac_address, None)

        if telemetry_data:
            metric_name = "{}_{}".format("storage", metric_type)
            metric = telemetry_data.get(metric_name, -1.0)
        else:
            LOG.warn('Missing data %s for: %s.', metric_type, drive_name)
            metric = -1.0
        return metric

    def _get_network_interface_util_sat(self, interface_name, metric_type):
        """
        Get the utilisation/saturation value for a network interface on a
        physical machine.
        :param interface_name: Name of the network interface
        :param metric_type: Metric required. Utilisation/Saturation.
        :return: Utilisation or Saturation metric for the network interface.
        """
        mac_address = self.get_physical_mac(interface_name).replace(':', '')
        telemetry_data = self.telemetry_data.get(mac_address, None)

        if telemetry_data:
            metric_name = "{}_{}".format("network", metric_type)
            metric = telemetry_data.get(metric_name, -1.0)
        else:
            LOG.warn('Missing data %s for: %s.', metric_type, interface_name)
            metric = -1.0
        return metric

    def _get_machine_util_sat(self, machine_name, metric_type):
        """
        Gets the utilisation or saturation values for a physical machine.

        :param machine_name: Physical machine name
        :param metric_type: Type of metric to return, utilisation/saturation.
        :return: Compute Utilisation or Saturation metric for the Machine.
        """

        mac_address = self.get_physical_mac(machine_name).replace(':', '')
        machine_telemetry_data = self.telemetry_data.get(mac_address, None)
        if machine_telemetry_data:
            metric_name = "{}_{}".format("compute", metric_type)
            metric = machine_telemetry_data.get(metric_name, -1.0)
        else:
            LOG.warn('Missing data %s for: %s.', metric_type, machine_name)
            metric = -1.0
        return metric

