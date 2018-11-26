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
Graph Database Base class and factory.
"""
import time
import requests
from networkx.readwrite import json_graph
from config_helper import ConfigHelper as config
import infograph
import json
import os
import analytics_engine.common as common

LOG = common.LOG
# HOST = '10.1.24.14'
# PORT = 9001
config.get("LANDSCAPE", "host")
config.get("LANDSCAPE", "port")

def get_graph():
    """
    Retrieves the entire landscape graph.
    :return: Landscape as a networkx graph.
    """
    landscape = _get("/graph")
    landscape.raise_for_status()  # Raise an exception if we get an error.

    nx_graph = json_graph.node_link_graph(landscape.json())
    return infograph.get_info_graph(landscape=nx_graph)


def get_subgraph(node_id, timestamp=None, timeframe=0):
    """
    Grab the subgraph starting from the specified node.
    :param node_id: THe id of the node which will be used to extract the sub.
    :return: A networkx graph of the subgraph. None if the ID is not found.
    """
    if HOST == 'localhost_file':
        exp_id = None
        # testing
        node_id = '1iozone'
        directory = os.path.join(common.INSTALL_BASE_DIR, "input_data")
        landscape = os.path.join(directory, node_id)
        for x in os.walk(landscape):
            exp_id = x[1][0]
            break
        topology_folder = os.path.join(landscape, exp_id)
        topology_json = os.path.join(topology_folder, "{}_topology.json".format(exp_id))
        LOG.info(topology_json)
        with open(topology_json) as json_data:
            subgraph = json.load(json_data)
            nx_subgraph = json_graph.node_link_graph(subgraph)
            LOG.info(nx_subgraph)
    else:
        timestamp = timestamp or time.time()
        path = "/subgraph/{}".format(node_id)
        subgraph = _get(path, {"timestamp": timestamp, "timeframe": timeframe})

        if subgraph.status_code == 400:
            LOG.error(error_message(subgraph))
            return None
        subgraph.raise_for_status()

        nx_subgraph = json_graph.node_link_graph(subgraph.json())
    return infograph.get_info_graph(landscape=nx_subgraph)


def get_node_by_uuid(node_id):
    """
    Returns the node identified by the id.  The id is the name property of the
    node.
    :param node_id: The name of the node to be retrieved.
    :return: Returns the node inside a networkx Graph object.
    """
    path = "/node/{}".format(node_id)
    node_graph_resp = _get(path)

    if node_graph_resp.status_code == 400:
        LOG.error(error_message(node_graph_resp))
        return None
    node_graph_resp.raise_for_status()
    nx_node_graph = json_graph.node_link_graph(node_graph_resp.json())
    return infograph.get_info_graph(landscape=nx_node_graph)


def get_node_by_properties(properties, start=None, timeframe=0):
    """
    Return a graph of nodes which match the given properties.
    :param properties: A list of tuples with the key, value and operator.If
    no operator is specified then the operator is '='. Oh and I am not
    checking the order of these things, so get it right.
    Example: [(k, v, o), (k, v)]
    :return: A matching nodes in a networkx graph.
    """
    if HOST == 'localhost_file':
        exp_id = None
        # testing
        node_id = '1iozone'
        directory = os.path.join(common.INSTALL_BASE_DIR, "input_data")
        landscape = os.path.join(directory, node_id)
        for x in os.walk(landscape):
            exp_id = x[1][0]
            break
        topology_folder= os.path.join(landscape, exp_id)
        topology_json = os.path.join(topology_folder, "{}_topology.json".format(exp_id))
        LOG.info(topology_json)
        with open(topology_json) as json_data:
            subgraph = json.load(json_data)
            nx_prop_graph = json_graph.node_link_graph(subgraph)
            LOG.info(nx_prop_graph)
    else:
        start = start or time.time()
        response = _get("/nodes", params={"properties": properties,
                                          "timestamp": start,
                                          "timeframe": timeframe})
        response.raise_for_status()
        nx_prop_graph = json_graph.node_link_graph(response.json())
    return infograph.get_info_graph(landscape=nx_prop_graph)


def get_service_instance_hist_nodes(properties):
    response = _get("/service_instances", params={"properties": properties})
    response.raise_for_status()
    nx_prop_graph = json_graph.node_link_graph(response.json())
    return infograph.get_info_graph(landscape=nx_prop_graph)

def get_service_instance_hist_subgraphs(properties):
    response = _get("/service_instances", params={"properties": properties})
    response.raise_for_status()
    nx_prop_graph = json_graph.node_link_graph(response.json())
    return infograph.get_info_graph(landscape=nx_prop_graph)

def _get(path, params=None):
    """
    Builds the uri to the service and then retrieves from the host.
    :param path: The path of the service. Host and port are already known.
    :return: A response object of the request.
    """
    uri = "http://{}:{}{}".format(HOST, PORT, path)

    if params:
        uri += "?"
        for param_name, param in params.iteritems():
            if param is None:  # Skip parameters that are none.
                continue
            uri += "{}={}&".format(param_name, param)
        uri = uri[:len(uri)]  # Remove ? or & from the  end of query string
        LOG.debug(uri)
    return requests.get(uri)


def error_message(response):
    """
    Strip out the error message from a HTTP Error response.
    """
    error_body = response.text.strip()
    start = error_body.index("<p>") + 3
    end = len(error_body) - 4
    return error_body[start:end]


def set_landscape_server(host, port=9000):
    """
    Changes the landscape connection, specified using host and port.
    :param host: host address.
    :param port: port number
    """
    global HOST, PORT

    HOST = host
    PORT = port


def reset_landscape_server():
    """
    Resets the landscaper server connection back to the one specified in the
    config file.
    """
    global HOST, PORT

    HOST = config.get("LANDSCAPE", "host")
    PORT = config.get("LANDSCAPE", "port")
