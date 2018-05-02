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
from analytics_engine.heuristics.filters.mf2c.analyse_and_refine_recipe_filter import AnalyseAndRefineRecipeFilter
from analytics_engine.heuristics.pipes.annotated_telemetry_pipe import AnnotatedTelemetryPipe
from analytics_engine.heuristics.sinks.file_sink import FileSink
from analytics_engine.heuristics.sinks.mf2c.influx_sink import InfluxSink


LOG = common.LOG


class AnalysePipe(AnnotatedTelemetryPipe):
    __pipe_name__ = 'analyse_pipe'
    """
    Given the service id queries the current landscape,
    performs the analysis and returns analysis id.
    
    :param workload
    :return:
    """

    def run(self, workload):
        if not workload:
            raise IOError('A workload needs to be specified')
        # retrieving other informations. Recipe needed
        # TODO: mainstain consistency with the old a new landscape when saving
        super(AnalysePipe, self).run(workload)
        avg_analyse = AnalyseAndRefineRecipeFilter()
        workload = avg_analyse.run(workload)
        influx_sink = InfluxSink()
        influx_sink.save(workload)
        fs = FileSink()
        fs.save(workload)
        return workload
