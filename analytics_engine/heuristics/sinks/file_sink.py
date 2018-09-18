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

import json
import os
from analytics_engine.heuristics.filters.telemetry_annotation import TelemetryAnnotation
from networkx.readwrite import json_graph
import analytics_engine.common as common
from base import Sink

LOG = common.LOG
LOCAL_RES_DIR = os.path.join(common.INSTALL_BASE_DIR, "exported_data")


class FileSink(Sink):

    def __init__(self):
        self._metadata = None
        pass

    def save(self, workload, metrics=True, topology=True, avg=True):
        """
        Saves results on file, as well as metadata from the execution of
        different
        :param workload: the workload to be saved
        :param metrics: true if metrics needs to be stored
        :param topology: true if topology needs to be stored
        :param avg: true if avg computation needs to be stored
        """
        # TODO: improve the design of parameters
        exp_dir = os.path.join(LOCAL_RES_DIR, str(workload.get_workload_name()))
        if not os.path.exists(LOCAL_RES_DIR):
            os.mkdir(LOCAL_RES_DIR)

        if not os.path.exists(exp_dir):
            os.mkdir(exp_dir)

        subgraph = workload.get_latest_graph()
        # Export the telemetry for the whole graph on a CSV File
        filename = os.path.join(
            exp_dir,
            "{}_metrics.csv".format(workload.get_workload_name()))
        TelemetryAnnotation.export_graph_metrics(
            subgraph,
            destination_file_name=filename,
            mode='csv', metrics='all')

        # Export topology
        filename = os.path.join(
            exp_dir,
            "{}_topology.json".format(workload.get_workload_name()))

        # TODO: fix this workaround
        subgraph_topology = workload.get_result('subgraph_filter')
        if not subgraph_topology:
            subgraph_topology = workload.get_result('graph_filter')

        with open(filename, 'w') as outfile:
            topology = json_graph.node_link_data(subgraph_topology)
            outfile.write(json.dumps(topology))

        metadata = workload.get_metadata()
        if metadata:
            for filter_name in metadata:
                filename = os.path.join(
                    exp_dir,
                    "{}_{}.csv".format(workload.get_workload_name(), filter_name))
                metadata[filter_name].transpose()
                metadata[filter_name].to_csv(filename, sep='\t')

        def show(self, source_type):
            LOG.error('File sink does not implement show method')

    @staticmethod
    def check(source_name):
        exp_dir = os.path.join(LOCAL_RES_DIR, str(source_name))
        if not os.path.exists(LOCAL_RES_DIR):
            return False

        if not os.path.exists(exp_dir):
            return False
        return True