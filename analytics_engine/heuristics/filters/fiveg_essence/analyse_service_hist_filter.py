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

from analytics_engine import common
import pandas as pd
from analytics_engine.heuristics.filters.base import Filter
from analytics_engine.infrastructure_manager import graphs
from analytics_engine.heuristics.beans.infograph import InfoGraphNode
import analytics_engine.heuristics.infrastructure.telemetry.utils as tm_utils
import time

LOG = common.LOG

class AnalyseServiceHistoryFilter(Filter):

    __filter_name__ = 'analyse_service_history_filter'

    """
    Returns a graph that constitutes the Landscape of the given
    workload.

    """

    def run(self, workload):

        tmp_path = "/media/iolie/WORK/data/"

        # Extract data from Info Core
        service_subgraphs = workload.get_latest_graph()
        telemetry = {}
        cols = []
        if not service_subgraphs or len(service_subgraphs) == 0:
            return
        # first add telemetry data of all nodes to a dictionary
        print "Data merger started " + str(time.time())
        for subgraph in service_subgraphs:
            for node in subgraph.nodes(data=True):
                node_id = node[0]
                node_tm = InfoGraphNode.get_telemetry_data(node)
                if InfoGraphNode.node_is_vm(node):
                    if not node_tm.empty:
                        node_tm.columns = tm_utils.clean_vm_telemetry_colnames(node_tm.columns)
                        vm_name = InfoGraphNode.get_attributes(node).get("vm_name")
                        if vm_name:
                            node_id = vm_name
                if not node_tm.empty:
                    tm = telemetry.get(node_id)
                    if not isinstance(tm, pd.DataFrame):
                    #if not tm:
                        telemetry[node_id] = node_tm
                        #telemetry[node_id] = [node_tm]
                        #node_tm.to_csv(tmp_path+node_id, index=False)
                    else:
                        telemetry[node_id] = pd.concat([tm, node_tm])
                        #telemetry[node_id].append(node_tm)
                        #node_tm.to_csv(tmp_path + node_id, mode='a', header=False, index=False)
                InfoGraphNode.set_telemetry_data(node, pd.DataFrame())
        print "Data merger finished " + str(time.time())
        print telemetry.keys()
        print len(telemetry)
        # merge subgraphs
        graph = None
        counter = 0
        for subgraph in service_subgraphs:
            counter = counter + 1
            if not graph and len(subgraph.nodes()) > 0:
                graph = subgraph
            elif len(subgraph.nodes()) > 0:
                graphs.merge_graph(graph, subgraph)
            #print "Merged {} subgraphs out of {} subgraphs in all".format(counter, len(service_subgraphs))
        # merge telemetry data

        #for key in telemetry.keys():
        #    val = telemetry[key]
            # print key + ' {}'.format(len(val))
        #    if len(val) > 1:
        #        telemetry[key] = pd.concat(val)
        #    elif len(val) == 1:
        #        telemetry[key] = val[0]
            # print node_id + ', ' + str(time.time())
            # print "Merged telemetry data of {} nodes out of {} nodes in all".format(counter, len(telemetry.keys()))

        # set telemetry data on merged graph
        for node in graph.nodes(data=True):
            node_id = node[0]
            if InfoGraphNode.node_is_vm(node):
                vm_name = InfoGraphNode.get_attributes(node).get("vm_name")
                if vm_name:
                    node_id = vm_name
            tm = telemetry.get(node_id)
            #try:
            #    tm = pd.read_csv(tmp_path + node_id)
            #except:
            #    tm = pd.DataFrame()
            if isinstance(tm, pd.DataFrame):
                if not tm.empty:
                    InfoGraphNode.set_telemetry_data(node, tm)
                    del telemetry[node_id]  # delete telemetry data so that only one copy exists in the graph
            else:
                InfoGraphNode.set_telemetry_data(node, None)
            # print "Set telemetry data of node {}".format(node_id)
        print "Set telemetry data of merged graph"
        workload.save_results(self.__filter_name__, graph)
        return graph