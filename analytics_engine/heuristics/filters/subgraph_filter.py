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


from analytics_engine import common
from analytics_engine.heuristics.infrastructure.topology.lib_analytics import SubgraphUtilities, SubGraphExtraction, LandscapeUtils
from analytics_engine.heuristics.beans.infograph import InfoGraphNode
from base import Filter

LOG = common.LOG


class SubgraphFilter(Filter):

    __filter_name__ = 'subgraph_filter'

    """
    Returns a graph that constitutes the Landscape of the given
    workload.

    """

    def run(self, workload):

        # Extract data from Info Core
        subgraph = None
        try:
            LOG.debug("Workload: {}".format(workload.get_workload_name()))
            workload_config = workload.get_configuration()
            if workload_config.get('device_id'):
                prop_name = workload_config.get('project', '') + '_device_id'
                device_id = workload_config['device_id']
                properties = [(prop_name, device_id)]
                ls_utils = LandscapeUtils()
                res = ls_utils.get_node_by_properties(properties, inactive=False)
                nodes = [(node[0], InfoGraphNode.get_attributes(node).get('from'),
                          InfoGraphNode.get_attributes(node).get('to')) for node in res.nodes(data=True)]
                if len(nodes) == 0:
                    return
                nodes.sort(reverse=True, key=self.node_sort)
                node_id = nodes[0][0]
                sge = SubGraphExtraction()
                subgraph = sge.get_node_subgraph(node_id, workload.get_ts_from(), workload.get_ts_to())
            else:
                subgraph = SubgraphUtilities.extract_workload_subgraphs(
                            workload.get_service_name(), workload.get_ts_from(), workload.get_ts_to())
        except Exception as e:
                LOG.error(e)
                LOG.error("No topology data has been found for the selected "
                              "workload.")
                import traceback
                traceback.print_exc()
                exit()
        workload.save_results(self.__filter_name__, subgraph)
        return subgraph

    def node_sort(self, elem):
        return elem[1]