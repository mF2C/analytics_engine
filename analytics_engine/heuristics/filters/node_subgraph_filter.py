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
from analytics_engine.heuristics.infrastructure.topology.lib_analytics import SubGraphExtraction
from analytics_engine.infrastructure_manager.config_helper import ConfigHelper
import analytics_engine.infrastructure_manager.landscape as landscape
from base import Filter

LOG = common.LOG


class NodeSubgraphFilter(Filter):

    __filter_name__ = 'node subgraph_filter'

    """
    Returns a graph that constitutes the Landscape of the given
    node.

    """

    def run(self, workload):

        # Extract data from Info Core
        subgraph = None
        try:
            LOG.debug("Workload: {}".format(workload.get_workload_name()))
            landscape_ip = ConfigHelper.get("LANDSCAPE", "host")
            landscape_port = ConfigHelper.get("LANDSCAPE", "port")
            landscape.set_landscape_server(host=landscape_ip, port=landscape_port)
            sge = SubGraphExtraction(landscape_ip, landscape_port)
            subgraph = sge.get_node_subgraph(
                        workload.get_workload_name(), workload.get_ts_from(), workload.get_ts_to())
        except Exception as e:
                LOG.error(e)
                LOG.error("No topology data has been found for the selected "
                              "node.")
                import traceback
                traceback.print_exc()
                exit()
        workload.save_results(self.__filter_name__, subgraph)
        return subgraph
