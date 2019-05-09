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

import pandas
import analytics_engine.common as common
from analytics_engine.heuristics.beans.infograph import InfoGraphNode, InfoGraphNodeType

# from lib_analytics

LOG = common.LOG


class LandscapeScore(object):

    @staticmethod
    def utilization_scores(graph):
        """
        Returns a dictionary with the scores of
        all the nodes of the graph.

        :param graph: InfoGraph
        :return: dict[node_name] = score
        """
        res = dict()
        for node in graph.nodes(data=True):
            node_name = InfoGraphNode.get_name(node)
            res[node_name] = dict()
            util = InfoGraphNode.get_utilization(node)
            import analytics_engine.common as common
            LOG = common.LOG

            res[node_name]['compute'] = 0
            res[node_name]['disk'] = 0
            res[node_name]['network'] = 0
            res[node_name]['memory'] = 0
            if (isinstance(util, pandas.DataFrame) and
                    util.empty) or \
                    (not isinstance(util, pandas.DataFrame) and
                             util==None):
                continue

            # intel/use/
            if 'intel/use/compute/utilization' in util:
                res[node_name]['compute'] = (util.get('intel/use/compute/utilization').mean()) / 100.0
            elif 'intel/procfs/cpu/utilization_percentage' in util:
                    res[node_name]['compute'] = (util.get('intel/procfs/cpu/utilization_percentage').mean()) / 100.0
            if 'intel/use/memory/utilization' in util:
                res[node_name]['memory'] = (util.get('intel/use/memory/utilization').mean()) / 100.0
            elif 'intel/procfs/memory/utilization_percentage' in util:
                res[node_name]['memory'] = (util.get('intel/procfs/memory/utilization_percentage').mean()) / 100.0
            if 'intel/use/disk/utilization' in util:
                res[node_name]['disk'] = (util.get('intel/use/disk/utilization').mean()) / 100.0
            elif 'intel/procfs/disk/utilization_percentage' in util:
                res[node_name]['disk'] = (util.get('intel/procfs/disk/utilization_percentage').mean()) / 100.0
            if 'intel/use/network/utilization' in util:
                res[node_name]['network'] = (util.get('intel/use/network/utilization').mean()) / 100.0
            elif 'intel/psutil/net/utilization_percentage' in util:
                res[node_name]['network'] = (util.get('intel/psutil/net/utilization_percentage').mean()) / 100.0

            # special handling of cpu, disk & network utilization if node is a machine
            if InfoGraphNode.node_is_machine(node):
                # mean from all cpu columns
                cpu_util = InfoGraphNode.get_compute_utilization(node)
                cpu_util['total'] = [sum(row) / len(row) for index, row in cpu_util.iterrows()]
                res[node_name]['compute'] = cpu_util['total'].mean() / 100
                # mean from all disk columns
                disk_util = InfoGraphNode.get_disk_utilization(node)
                if disk_util.empty:
                    res[node_name]['disk'] = 0.0
                else:
                    disk_util['total'] = [sum(row) / len(row) for index, row in disk_util.iterrows()]
                    res[node_name]['disk'] = disk_util['total'].mean() / 100
                # mean from all nic columns
                net_util = InfoGraphNode.get_network_utilization(node)
                if net_util.empty:
                    res[node_name]['network'] = 0.0
                else:
                    net_util['total'] = [sum(row) / len(row) for index, row in net_util.iterrows()]
                    res[node_name]['network'] = net_util['total'].mean() / 100
                # custom metric

            if InfoGraphNode.get_type(node)==InfoGraphNodeType.DOCKER_CONTAINER:
                node_name = InfoGraphNode.get_docker_id(node)
                res[node_name] = {}
                if 'intel/docker/stats/cgroups/cpu_stats/cpu_usage/percentage' in util.columns:
                    res[node_name]['compute'] = util['intel/docker/stats/cgroups/cpu_stats/cpu_usage/percentage'].mean() / 100
                else:
                    res[node_name]['compute'] = 0
                if 'intel/docker/stats/cgroups/memory_stats/usage/percentage' in util.columns:
                    res[node_name]['memory'] = util['intel/docker/stats/cgroups/memory_stats/usage/percentage'].mean() / 100
                else:
                    res[node_name]['memory'] = 0
                if 'intel/docker/stats/network/utilization_percentage' in util.columns:
                    res[node_name]['network'] = util['intel/docker/stats/network/utilization_percentage'].mean() / 100
                else:
                    res[node_name]['network'] = 0
                if 'intel/docker/stats/cgroups/blkio_stats/io_time_recursive/percentage' in util.columns:
                    res[node_name]['disk'] = util['intel/docker/stats/cgroups/blkio_stats/io_time_recursive/percentage'].mean() / 100
                else:
                    res[node_name]['disk'] = 0
        return res

    @staticmethod
    def saturation_scores(graph):
        """
        Returns a dictionary with the scores of
        all the nodes of the graph.

        :param graph: InfoGraph
        :return: dict[node_name] = score
        """
        res = dict()
        for node in graph.nodes(data=True):
            node_name = InfoGraphNode.get_name(node)
            res[node_name] = dict()
            sat = InfoGraphNode.get_saturation(node)
            import analytics_engine.common as common
            LOG = common.LOG

            res[node_name]['compute'] = 0
            res[node_name]['disk'] = 0
            res[node_name]['network'] = 0
            res[node_name]['memory'] = 0
            if (isinstance(sat, pandas.DataFrame) and
                    sat.empty) or \
                    (not isinstance(sat, pandas.DataFrame) and
                             sat == None):
                continue

            if 'intel/use/compute/saturation' in sat:
                res[node_name]['compute'] = (sat.get('intel/use/compute/saturation').mean()) / 100.0
            if 'intel/use/memory/saturation' in sat:
                res[node_name]['memory'] = (sat.get('intel/use/memory/saturation').mean()) / 100.0
            if 'intel/use/disk/saturation' in sat:
                res[node_name]['disk'] = (sat.get('intel/use/disk/saturation').mean()) / 100.0
            if 'intel/use/network/saturation' in sat:
                res[node_name]['network'] = (sat.get('intel/use/network/saturation').mean()) / 100.0
        return res

    @staticmethod
    def _calc_score(utilization=1, saturation=0, capacity=1):
        """
        Returns the score related to the utilization
        """
        if utilization > 1 or utilization < 0:
            raise ValueError("Utilization must be in the range 0-1")
        if saturation > 1 or saturation < 0:
            raise ValueError("Saturation must be in the range 0-1")
        if capacity > 1 or capacity < 0:
            raise ValueError("Capacity must be in the range 0-1")

        score = (1 - saturation) * float(capacity) / (1 + float(utilization))
        return score



