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
from analytics_engine.heuristics.pipes.base import Pipe
from analytics_engine.heuristics.filters.node_subgraph_filter import NodeSubgraphFilter
from analytics_engine.heuristics.filters.subgraph_annotated_filter import SubgraphAnnotatedFilter
from analytics_engine.heuristics.sinks.file_sink import FileSink
import time

LOG = common.LOG


class NodeSubgraphTelemetryPipe(Pipe):
    __pipe_name__ = 'subgraph_telemetry_pipe'
    """
    Gets a list of all active services.
    
    :param none
    :return:
    """

    def run(self, workload=None):
        print "Starting NodeSubgraphTelemetry Pipe: {}".format(time.time())
        filter = NodeSubgraphFilter()
        subgraph = filter.run(workload)
        filter = SubgraphAnnotatedFilter()
        annotated_subgraph = filter.run(workload)
        print "Returning NodeSubgraph Telemetry data for NodeSubgraphTelemetry Pipe: {}".format(time.time())
        fs = FileSink()
        fs.save(workload, topology=False)
        # temp code for research
        import os
        import pickle
        LOCAL_RES_DIR = os.path.join(common.INSTALL_BASE_DIR, "exported_data")
        exp_dir = os.path.join(LOCAL_RES_DIR, str(workload.get_workload_name()))
        if not os.path.exists(LOCAL_RES_DIR):
            os.mkdir(LOCAL_RES_DIR)

        if not os.path.exists(exp_dir):
            os.mkdir(exp_dir)
        filename = os.path.join(
            exp_dir,
            "{}.pickle".format(workload.get_workload_name()))
        subgraph_topology = workload.get_latest_graph()
        with open(filename, 'w') as outfile:
            pickle.dump(subgraph_topology, outfile)
        ##########################
        return workload
