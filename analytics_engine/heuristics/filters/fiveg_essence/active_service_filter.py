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


class ActiveServiceFilter(Filter):

    __filter_name__ = 'active_service_filter'

    """
    Returns a graph that constitutes the Landscape of the given
    workload.

    """

    def run(self, workload):

        # Extract data from Info Core
        nodes = list()
        try:
            landscape_ip = ConfigHelper.get("LANDSCAPE", "host")
            landscape_port = ConfigHelper.get("LANDSCAPE", "port")
            landscape.set_landscape_server(host=landscape_ip, port=landscape_port)
            sge = SubGraphExtraction(landscape_ip, landscape_port)
            res = sge.get_active_service_nodes()
            workload.save_results(self.__filter_name__, res)
        except Exception as ex:
            print "Exception fetching active service nodes. Error : {}".format(ex.message)
        return workload
