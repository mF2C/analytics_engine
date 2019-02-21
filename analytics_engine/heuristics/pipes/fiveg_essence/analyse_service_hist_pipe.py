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
from analytics_engine.heuristics.pipes.base import Pipe
from analytics_engine.heuristics.filters.fiveg_essence.service_hist_subgraph_filter import ServiceHistorySubgraphFilter
from analytics_engine.heuristics.filters.fiveg_essence.analyse_service_hist_filter import AnalyseServiceHistoryFilter
from analytics_engine.infrastructure_manager.config_helper import ConfigHelper
from analytics_engine.heuristics.sinks.file_sink import FileSink
from analytics_engine.heuristics.infrastructure.topology.lib_analytics import SubgraphUtilities
import time

LOG = common.LOG


class AnalyseServiceHistPipe(Pipe):
    __pipe_name__ = 'analyse_pipe'
    """
    Given the service id queries the current landscape,
    performs the analysis and returns analysis id.
    
    :param workload
    :return:
    """

    def run(self, workload, service_type):
        print "Starting AnalyseServiceHistPipe Pipe: {}".format(time.time())
        if not workload:
            raise IOError('A workload needs to be specified')
        # get the service subgraph(s)
        telemetry_system = ConfigHelper.get("DEFAULT", "telemetry")
        service_analyse = ServiceHistorySubgraphFilter()
        service_subgraphs = service_analyse.run(workload, service_type, telemetry_system=telemetry_system)
        print "Telemetry annotation completed in AnalyseServiceHistPipe Pipe: {}".format(time.time())
        ash = AnalyseServiceHistoryFilter()
        ash.run(workload)
        print "Subgraph analysis completed in AnalyseServiceHistPipe Pipe: {}".format(time.time())
        if not telemetry_system:
            telemetry_system = 'snap'
        # influx_sink = InfluxSink()
        # influx_sink.save(workload)
        fs = FileSink()
        fs.save(workload, topology=False)
        # temp code
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
        print "Data saved in AnalyseServiceHistPipe Pipe: {}".format(time.time())
        return workload
