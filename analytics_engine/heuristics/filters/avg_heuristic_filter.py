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
from base import Filter

LOG = common.LOG


class AvgHeuristicFilter(Filter):

    __filter_name__ = 'avg_heuristic_filter'

    def run(self, workload):
        """
        Computes avg utilization statistics.

        :param workload: Contains workload related info and results.

        :return: heuristic results
        """
        graph = workload.get_latest_graph()
        if not graph:
            raise KeyError('No graph to be processed.')

        scores = LandscapeScore.utilization_scores(graph)
        statistics = self.workload(scores)
        scores_sat = LandscapeScore.saturation_scores(graph)
        statistics_sat = self.workload(scores_sat)
        heuristic_results = {}
        heuristic_results['avg_util'] = scores
        heuristic_results['avg_saturation'] = scores_sat
        heuristic_results['statistics'] = statistics
        heuristic_results['statistics_sat'] = statistics_sat
        workload.append_metadata(self.__filter_name__, heuristic_results)
        LOG.info('Avg util per node: {}'.format(heuristic_results['avg_util']))
        LOG.info('Avg saturation per node: {}'.format(heuristic_results['avg_saturation']))
        LOG.info('Statistics util: {}'.format(heuristic_results['statistics']))
        LOG.info('Statistics sat: {}'.format(heuristic_results['statistics_sat']))
        return heuristic_results

    @staticmethod
    def workload(nodes):
        """
        This is a type of fingerprint from the infrastructure perspective
        """
        avg_compute = 0
        avg_disk=0
        avg_network = 0
        avg_memory = 0
        count = 0
        stats = dict()
        for entry in nodes.itervalues():
            count = count + 1
            avg_compute = avg_compute + entry['compute']
            avg_disk = avg_disk + entry['disk']
            avg_network = avg_network + entry['network']
            avg_memory = avg_memory + entry['memory']
        stats['disk'] = avg_disk/count
        stats['compute'] = avg_compute/count
        stats['memory'] = avg_memory/count
        stats['network'] = avg_network/count
        return stats
