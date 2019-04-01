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

from analytics_engine import common
from analytics_engine.heuristics.beans.infograph import InfoGraphNode, InfoGraphUtilities
from analytics_engine.heuristics.filters import telemetry_annotation as ta
from analytics_engine.heuristics.filters import parallelized_telemetry_annotation as pta
from analytics_engine.infrastructure_manager import graphs
from analytics_engine.infrastructure_manager.config_helper import ConfigHelper
import threading
import multiprocessing

# ApexLake dependencies
from analytics_engine.infrastructure_manager import landscape
import time
LOG = common.LOG

TELEMETRY_TYPE_SNAP = "snap"
# MILLISECONDS = 60000
# MINUTES_TF = 0.1

MILLISECONDS = 10
MINUTES_TF = 1

PARALLEL = False

class SubGraphExtraction(object):

    def __init__(self, landscape_ip=None, landscape_port=None):
        if not landscape_ip:
            landscape_ip = ConfigHelper.get("LANDSCAPE", "host")
            landscape_port = ConfigHelper.get("LANDSCAPE", "port")
        landscape.set_landscape_server(host=landscape_ip, port=landscape_port)

    def get_compute_node_view(self,
                              compute_node_hostnames,
                              ts_from=None,
                              ts_to=None,
                              name_filtering_support=False):
        """
        Returns a view for the compute node.
        """
        res = None
        if isinstance(compute_node_hostnames, str):
            res = self._get_compute_node_subgraph(
                compute_node_hostnames, ts_from, ts_to)

        elif isinstance(compute_node_hostnames, list):
            res = self._get_network_subgraph(ts_from, ts_to)
            for hostname in compute_node_hostnames:
                if isinstance(hostname, str):
                    graph = self._get_compute_node_subgraph(
                        hostname, ts_from, ts_to)
                    if len(graph.nodes()) > 0:
                        graphs.merge_graph(res, graph)

        if name_filtering_support:
            for node in res.nodes(data=True):
                name = InfoGraphNode.get_name(node)
                InfoGraphNode.set_attribute(node, 'node_name', name)
        return res

    def get_workload_view_graph(self,
                                stack_names,
                                ts_from=None,
                                ts_to=None,
                                name_filtering_support=False):
        """
        Returns a graph which only includes the resources related to the
         execution of the stack names indicated in the input parameter
        """
        res = None

        if isinstance(stack_names, str):
            res = self._get_workload_subgraph(
                stack_names, ts_from, ts_to)

        # TODO - URGENT: Check this with the new Lanscape
        elif isinstance(stack_names, list):
            temp_res = list()
            for stack_name in stack_names:
                graph = self._get_workload_subgraph(
                    str(stack_name), ts_from, ts_to)
                if len(graph.nodes()) > 0:
                    temp_res.append(graph)
            for graph in temp_res:
                if not res and len(graph.nodes()) > 0:
                    res = graph
                elif len(graph.nodes()) > 0:
                    # TODO - URGENT: Fix this. Put Merge within the analytics
                    res = graphs.merge_graph(res, graph)
        # TODO - URGENT: Check this with the new Lanscape
        machine_count = 0
        for node in res.nodes(data=True):
            if InfoGraphNode.node_is_machine(node):
                machine_count += 1

        if name_filtering_support:
            for node in res.nodes(data=True):
                name = InfoGraphNode.get_name(node)
                InfoGraphNode.set_attribute(node, 'node_name', name)

        return res

    def get_hist_service_nodes(self, service_type, name):
        '''

        :param service_type: 'stack' or 'service'
        :param name: name of service or stack
        :return: graph
        '''
        prop_name = "stack_name"
        if service_type == 'service':
            prop_name = 'service_name'
        properties = [(prop_name, name)]
        res = landscape.get_service_instance_hist_nodes(properties)
        return res

    def get_active_service_nodes(self):
        '''

        :param service_type: 'stack' or 'service'
        :param name: name of service or stack
        :return: graph
        '''
        prop_name = "layer"
        prop_value = "service"
        ts_from = int(time.time())-5
        timeframe = 5
        properties = [(prop_name, prop_value)]
        res = landscape.get_node_by_properties(properties, ts_from, timeframe)
        return res

    def get_node_subgraph(self, node_id, ts_from=None, ts_to=None):
        try:
            time_window = ts_to - ts_from
        except:
            time_window = 600
        landscape_res = landscape.get_subgraph(
            node_id, ts_from, time_window)

        for node in landscape_res.nodes(data=True):
            attrs = InfoGraphNode.get_attributes(node)
            attrs = InfoGraphUtilities.str_to_dict(attrs)
            InfoGraphNode.set_attributes(node, attrs)

        return landscape_res

    def _get_workload_subgraph(self, stack_name, ts_from=None, ts_to=None):
        res = None
        try:
            # Get the node ID for the stack_name and query the landscape

            properties = [("stack_name", stack_name)]
            try:
                time_window = ts_to - ts_from
            except:
                time_window = 600
            landscape_res = landscape.get_node_by_properties(
                properties, ts_from, time_window)

            if not landscape_res:
                LOG.info("No graph for a stack returned from analytics")
                # try a service name
                properties = [("service_name", stack_name)]
                landscape_res = landscape.get_node_by_properties(
                    properties, ts_from, time_window)
                if not landscape_res:
                    LOG.info("No graph for a service returned from analytics")
                    return None

            res = landscape.get_subgraph(landscape_res.nodes()[0], ts_from, time_window)
        except Exception as e:
            LOG.debug('Something went seriously wrong.')
            LOG.error(e)

        for node in res.nodes(data=True):
            attrs = InfoGraphNode.get_attributes(node)
            attrs = InfoGraphUtilities.str_to_dict(attrs)
            InfoGraphNode.set_attributes(node, attrs)
        return res

    def _get_network_subgraph(self, ts_from=None, ts_to=None):
        # TODO - URGENT: Wait for the network information to be in the graph and test this again
        properties = [("type", "switch"), ]
        try:
            time_window = ts_to - ts_from
        except:
            time_window = 600
        landscape_res = landscape.get_node_by_properties(
            properties, ts_from, time_window)

        subgs = list()
        for lr in landscape_res:
            subgs.append(landscape.get_subgraph(
                lr.nodes()[0], ts_from, time_window))
            for subg in subgs:
                for node in subg.nodes(data=True):
                    attrs = InfoGraphNode.get_attributes(node)
                    attrs = InfoGraphUtilities.str_to_dict(attrs)
                    InfoGraphNode.set_attributes(node, attrs)
        return subgs

    def _get_compute_node_subgraph(self, compute_node, ts_from=None, ts_to=None):

        res = self.db.\
            get_subgraph('type', 'machine', timestamp=ts_to)

        for node in res.nodes(data=True):
            attrs = InfoGraphNode.get_attributes(node)
            attrs = InfoGraphUtilities.str_to_dict(attrs)
            InfoGraphNode.set_attributes(node, attrs)
        return res


class SubgraphUtilities(object):
    """
    Contains a set of methods that can be of help within the heuristics to
    load/store data from/to ApexLake Information Core
    """

    @staticmethod
    def extract_workload_subgraphs(workload_names, ts_from, ts_to):
        """
        Returns the subgraph (InfoGraph) for the specified workload names
        related to the specified time window

        :param workload_names: list(str) Names of stacks/workloads to be
                               loaded
        :param ts_from: (int) epoch begin time of the experiment (or of the
                        time window)
        :param ts_to: (int) epoch end time of the experiment (or of the
                        time window)
        :return: (InfoGraph)
        """
        ts_from = int(ts_from)
        ts_to = int(ts_to)

        # Getting configuration for the ApexLake Landscape
        landscape_ip = ConfigHelper.get("LANDSCAPE", "host")
        landscape_port = ConfigHelper.get("LANDSCAPE", "port")

        # Manage the extraction of the subgraph
        subgraph_extraction = SubGraphExtraction(landscape_ip=landscape_ip,
                                                 landscape_port=landscape_port)
        res = subgraph_extraction.get_workload_view_graph(
            workload_names, int(ts_from), int(ts_to),
            name_filtering_support=True)

        return res

    @staticmethod
    def extract_infrastructure_graph(workload_name, ts_from, ts_to):
        """
        Returns the entire landscape at the current time

        :return:
        """
        landscape_ip = ConfigHelper.get("LANDSCAPE", "host")
        landscape_port = ConfigHelper.get("LANDSCAPE", "port")
        subgraph_extraction = SubGraphExtraction(landscape_ip=landscape_ip,
                                                 landscape_port=landscape_port)
        # res = subgraph_extraction.get_workload_view_graph(
        #     workload_name, int(ts_from), int(ts_to),
        #     name_filtering_support=True)
        res = landscape.get_graph()
        #PARALLEL = True
        if PARALLEL:
            i = 0
            threads = []
            cpu_count = multiprocessing.cpu_count()
            all_node = res.nodes(data=True)
            no_node_thread = len(res.nodes()) / cpu_count
            node_pool = []

            for node in all_node:
                if i < no_node_thread:
                    node_pool.append(node)
                    i = i + 1
                else:
                    thread1 = ParallelLandscape(i, "Thread-{}".format(InfoGraphNode.get_name(node)), i,
                                                          node_pool)
                    # thread1 = ParallelTelemetryAnnotation(i, "Thread-{}".format(InfoGraphNode.get_name(node)), i,
                    #                                       node_pool, internal_graph, self.telemetry, ts_to, ts_from)
                    thread1.start()
                    threads.append(thread1)
                    i = 0
                    node_pool = []
            if len(node_pool) != 0:
                thread1 = ParallelLandscape(i, "Thread-{}".format(InfoGraphNode.get_name(node)), i,
                                            node_pool)
                thread1.start()
                threads.append(thread1)

            [t.join() for t in threads]
        else:
            for node in res.nodes(data=True):
                attrs = InfoGraphNode.get_attributes(node)
                attrs = InfoGraphUtilities.str_to_dict(attrs)
                InfoGraphNode.set_attributes(node, attrs)
        return res


    @staticmethod
    def graph_telemetry_annotation(graph, ts_from, ts_to, telemetry_type='snap'):
        """
        Annotates the provided graph with telemetry information

        :param graph: TBD
        :param ts_from: (int) epoch begin time of the experiment (or of the
                        time window)
        :param ts_to: (int) epoch end time of the experiment (or of the
                        time window)
        :return: TBD
        """
        # TODO - P5: Validate Graph

        ts_from = int(ts_from)
        ts_to = int(ts_to)
        ts_now = int(time.time())
        if ts_to > ts_now:
            ts_to = ts_now
        # if we are analysing the infrastructure status we ask for
        # last 10 minutes of metrics.

        if ts_from == 0 and ts_to == 0:
            ts_to = int(time.time())
            ts_from = ts_to - (MILLISECONDS*MINUTES_TF)
        #PARALLEL = True
        if PARALLEL and telemetry_type=='snap':
            annotation = \
                pta.TelemetryAnnotation(
                    telemetry_system=telemetry_type)
        else:
            annotation = \
                ta.TelemetryAnnotation(
                    telemetry_system=telemetry_type)
        res = annotation.get_annotated_graph(
            graph, ts_from, ts_to, utilization=True, saturation=True)
        return res


class LandscapeUtils(object):

    def __init__(self):
        landscape_ip = ConfigHelper.get("LANDSCAPE", "host")
        landscape_port = ConfigHelper.get("LANDSCAPE", "port")
        landscape.set_landscape_server(host=landscape_ip, port=landscape_port)

    def get_node_by_properties(self, properties, inactive=False):
        from_ts = int(time.time())
        if inactive:
            # to_ts = int(attrs['to'])
            tf = from_ts * -1
        else:
            tf = 0
        res = landscape.get_node_by_properties(properties, from_ts, tf)
        return res

class ParallelLandscape(threading.Thread):

    def __init__(self, threadID, name, counter, node):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
        self.node_pool = node

    def run(self):
        for node in self.node_pool:
            attrs = InfoGraphNode.get_attributes(node)
            attrs = InfoGraphUtilities.str_to_dict(attrs)
            InfoGraphNode.set_attributes(node, attrs)







