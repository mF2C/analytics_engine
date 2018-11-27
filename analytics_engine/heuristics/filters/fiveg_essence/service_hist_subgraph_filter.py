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
from analytics_engine.heuristics.infrastructure.topology.lib_analytics import SubGraphExtraction, SubgraphUtilities
from analytics_engine.heuristics.filters.base import Filter
from analytics_engine.infrastructure_manager.config_helper import ConfigHelper
from analytics_engine.infrastructure_manager import landscape
from analytics_engine.heuristics.beans.infograph import InfoGraphNode, InfoGraphUtilities
import time
import cProfile

LOG = common.LOG
SUBGRAPH_LIMIT = 25


class ServiceHistorySubgraphFilter(Filter):

    __filter_name__ = 'service_history_subgraph_filter'

    """
    Returns a graph that constitutes the Landscape of the given
    workload.

    """

    def run(self, workload, service_type="stack", telemetry_system='snap'):

        # Extract data from Info Core
        service_subgraphs = list()
        try:
            LOG.debug("Workload: {}".format(workload.get_workload_name()))
            landscape_ip = ConfigHelper.get("LANDSCAPE", "host")
            landscape_port = ConfigHelper.get("LANDSCAPE", "port")
            landscape.set_landscape_server(host=landscape_ip, port=landscape_port)
            sge = SubGraphExtraction(landscape_ip, landscape_port)
            res = sge.get_hist_service_nodes(service_type, workload.get_workload_name())
            nodes = [(node[0], InfoGraphNode.get_attributes(node).get('from'), InfoGraphNode.get_attributes(node).get('to')) for node in res.nodes(data=True)]
            nodes.sort(reverse=True, key=self.node_sort)
            #pr = cProfile.Profile()
            counter = 0
            for node in nodes:
                #pr.enable()
                node_id = node[0]
                from_ts = int(time.time())
                # to_ts = int(attrs['to'])
                tf = from_ts * -1
                subgraph = landscape.get_subgraph(node_id, from_ts, tf)
                if len(subgraph.nodes()) > 0:
                    annotated_subgraph = SubgraphUtilities.graph_telemetry_annotation(subgraph, node[1],
                                                                                      node[2],
                                                                                      telemetry_system)
                    service_subgraphs.append(annotated_subgraph)
                #print "cProfile Stats"+node_id
                #print "=============="
                #pr.print_stats(sort='time')
                #print "=============="
                #pr.disable()
                counter = counter + 1
                if counter == SUBGRAPH_LIMIT:
                    break
        except Exception as e:
                LOG.error(e)
                LOG.error("No topology data has been found for the selected "
                              "workload.")
                import traceback
                traceback.print_exc()
                exit()
        workload.save_results(self.__filter_name__, service_subgraphs)
        return service_subgraphs

    def node_sort(self, elem):
        return elem[1]