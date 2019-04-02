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
from analytics_engine.heuristics.filters.subgraph_filter import SubgraphFilter
from analytics_engine.heuristics.filters.graph_filter import GraphFilter
from analytics_engine.heuristics.filters.subgraph_annotated_filter import SubgraphAnnotatedFilter
from analytics_engine.heuristics.filters.subgraph_filtered_telemetry_filter import SubgraphFilteredTelemetryFilter
from analytics_engine.infrastructure_manager.config_helper import ConfigHelper
from analytics_engine.heuristics.sinks.file_sink import FileSink
from analytics_engine.heuristics.pipes.base import Pipe
LOG = common.LOG


class AnnotatedTelemetryPipe(Pipe):

    __pipe_name__ = 'Annotated TelemetryPipe'
    """
    Returns a workload annotated with telemetry information.
    :param workload
    :return: workload decorated with the annotated graph (landscape and telemetry).
    """
    def run(self, workload):
        telemetry_system = ConfigHelper.get("DEFAULT","telemetry")
        if not telemetry_system:
            telemetry_system = 'snap'
        if not workload:
            raise IOError('A workload needs to be specified')
        # testing purposes
        workload.set_discard(False)
        workload_config = workload.get_configuration()
        # Generalizing it to make it return entire graph
        # if ts_to and ts_from are not set up
        if workload.get_ts_from() != 0 or workload_config.get('device_id'):
            sub_filter = SubgraphFilter()
            sub_filter.run(workload)
            if workload.get_latest_graph() is None:
                LOG.error("No topology data has been found for the selected workload.")
                return workload
        else:
            graph_filter = GraphFilter()
            graph_filter.run(workload)
        sub_filter_ann = SubgraphAnnotatedFilter()
        sub_filter_ann.run(workload, telemetry_system)
        # sub_filter_ann_filtered = SubgraphFilteredTelemetryFilter()
        # sub_filter_ann_filtered.run(workload)
        fs = FileSink()
        fs.save(workload)
        return workload

