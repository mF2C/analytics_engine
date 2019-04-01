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

    def run(self, workload, optimal_node_type='machine'):
        """
        Ranks machines by CPU utilization.

        :param workload: Contains workload related info and results.

        :return: heuristic results
        """
        workload_config = workload.get_configuration()
        graph = workload.get_latest_graph()
        if not graph:
            raise KeyError('No graph to be processed.')

        scores = LandscapeScore.utilization_scores(graph)
        scores_sat = LandscapeScore.saturation_scores(graph)
        heuristic_results = pd.DataFrame(columns=['node_name', 'type', 'ipaddress', 
                                                  'compute utilization', 'compute saturation',
                                                  'memory utilization', 'memory saturation',
                                                  'network utilization', 'network saturation',
                                                  'disk utilization', 'disk saturation',
                                                  ])
        heuristic_results_nt = heuristic_results.copy()
        device_id_col_name = None
        project = None
        if workload_config.get('project'):
            project = workload_config['project']
            device_id_col_name = workload_config['project']+'_device_id'
            heuristic_results[device_id_col_name] = None

        telemetry_filter = workload_config.get('telemetry_filter')
        for node in graph.nodes(data=True):
            node_name = InfoGraphNode.get_name(node)
            node_type = InfoGraphNode.get_type(node)
            list_node_name = node_name
            if node_type == optimal_node_type:
                if InfoGraphNode.node_is_vm(node):
                    vm_name = InfoGraphNode.get_properties(node).get('vm_name')
                    if vm_name:
                        list_node_name = vm_name
                data = {'node_name': list_node_name,
                                                    'type': node_type,
                                                    'ipaddress': InfoGraphNode.get_attributes(node).get('ipaddress'),
                                                    'compute utilization': scores[node_name]['compute'],
                                                    'compute saturation': scores_sat[node_name]['compute'],
                                                    'memory utilization': scores[node_name]['memory'],
                                                    'memory saturation': scores_sat[node_name]['memory'],
                                                    'network utilization': scores[node_name]['network'],
                                                    'network saturation': scores_sat[node_name]['network'],
                                                    'disk utilization': scores[node_name]['disk'],
                                                    'disk saturation': scores_sat[node_name]['disk']}
                if device_id_col_name:
                    dev_id = InfoGraphNode.get_properties(node).get(device_id_col_name)
                    if project == 'mf2c':
                        dev_id = dev_id.replace('_', '-')
                    data[device_id_col_name] = dev_id
                if InfoGraphNode.get_properties(node).get("telemetry_data") is not None:
                    heuristic_results = heuristic_results.append(data,
                                                        ignore_index=True)
                elif not telemetry_filter:
                    heuristic_results_nt = heuristic_results.append(data,
                                                        ignore_index=True)

            if not workload.get_workload_name().startswith('optimal_'):
                if InfoGraphNode.get_type(node) == "docker_container" and optimal_node_type == 'machine':
                    node_name = InfoGraphNode.get_docker_id(node)
                    heuristic_results = heuristic_results.append({'node_name': node_name,
                                                    'type': node_type,
                                                    'ipaddress': None,
                                                    'compute utilization': scores[node_name]['compute'],
                                                    'compute saturation': None,
                                                    'memory utilization': scores[node_name]['memory'],
                                                    'memory saturation': None,
                                                    'network utilization': scores[node_name]['network'],
                                                    'network saturation': None,
                                                    'disk utilization': scores[node_name]['disk'],
                                                    'disk saturation': None},
                                                    ignore_index=True)
        sort_fields = ['compute utilization']
        sort_order = workload_config.get('sort_order')
        if sort_order:
            sort_fields = []
            for val in sort_order:
                if val == 'cpu':
                    sort_fields.append('compute utilization')
                if val == 'memory':
                    sort_fields.append('memory utilization')
                if val == 'network':
                    sort_fields.append('network utilization')
                if val == 'disk':
                    sort_fields.append('disk utilization')
        heuristic_results_nt = heuristic_results_nt.replace([0], [None])
        heuristic_results = heuristic_results.sort_values(by=sort_fields, ascending=True)
        heuristic_results = heuristic_results.append(heuristic_results_nt, ignore_index=True)
        workload.append_metadata(self.__filter_name__, heuristic_results)
        LOG.info('AVG: {}'.format(heuristic_results))
        return heuristic_results




