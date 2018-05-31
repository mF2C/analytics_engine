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
from analytics_engine.data_analytics.mf2c.landscape_score import LandscapeScore
from analytics_engine.heuristics.beans.infograph import InfoGraphNode
import pandas as pd
from analytics_engine.heuristics.filters.base import Filter

LOG = common.LOG


class OptimalFilter(Filter):

    __filter_name__ = 'optimal_filter'

    def run(self, workload):
        """
        Ranks machines by CPU utilization.

        :param workload: Contains workload related info and results.

        :return: heuristic results
        """
        graph = workload.get_latest_graph()
        if not graph:
            raise KeyError('No graph to be processed.')

        scores = LandscapeScore.utilization_scores(graph)
        scores_sat = LandscapeScore.saturation_scores(graph)
        heuristic_results = pd.DataFrame(columns=['node_name', 'type',
                                                  'compute utilization', 'compute saturation',
                                                  'memory utilization', 'memory saturation',
                                                  'network utilization', 'network saturation',
                                                  'disk utilization', 'disk saturation',
                                                  ])

        for node in graph.nodes(data=True):
            node_name = InfoGraphNode.get_name(node)
            if InfoGraphNode.get_type(node) == "machine":
                heuristic_results = heuristic_results.append({'node_name': node_name,
                                                    'type': InfoGraphNode.get_type(node),
                                                    'compute utilization': scores[node_name]['compute'],
                                                    'compute saturation': scores_sat[node_name]['compute'],
                                                    'memory utilization': scores[node_name]['memory'],
                                                    'memory saturation': scores_sat[node_name]['memory'],
                                                    'network utilization': scores[node_name]['network'],
                                                    'network saturation': scores_sat[node_name]['network'],
                                                    'disk utilization': scores[node_name]['disk'],
                                                    'disk saturation': scores_sat[node_name]['disk']},
                                                    ignore_index=True)
        heuristic_results = heuristic_results.sort_values(by=['compute utilization'], ascending=True)
        workload.append_metadata(self.__filter_name__, heuristic_results)
        LOG.info('AVG: {}'.format(heuristic_results))
        return heuristic_results




