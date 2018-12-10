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
# from analytics.info_core import InfoGraph
from analytics_engine.heuristics.filters.telemetry_annotation import TelemetryAnnotation as TA
from analytics_engine.heuristics.filters.parallelized_telemetry_annotation import TelemetryAnnotation as PTA
from analytics_engine.heuristics.infrastructure.topology.lib_analytics import SubgraphUtilities
from base import Filter

LOG = common.LOG

PARALLEL = True
class SubgraphFilteredTelemetryFilter(Filter):

    __filter_name__ = 'subgraph_filtered_telemetry_filter'

    def run(self, workload):
        """
        Filter out the nodes of the graph which do not contain any telemetry


         Add the output of the calculation to the metadata as output

        :param workload: Contains workload related info and results.

        :return: subgraph
        """
        graph = workload.get_latest_graph()
        if not graph:
            raise KeyError()
        # subgraph = SubgraphUtilities.graph_telemetry_annotation(
        #     graph, workload.get_ts_from(), workload.get_ts_to())


        #Filter out nodes with no telemetry data
        try:
            # graph = TelemetryAnnotation.filter_graph(subgraph)
            subgraph = TA.filter_graph(graph)
            workload.save_results(self.__filter_name__, subgraph)
        except KeyError as e:
            LOG.error("SubgraphAnnotatedFilter either has not been "
                          "executed or did not return any output.")
            LOG.error(e)

        return graph


