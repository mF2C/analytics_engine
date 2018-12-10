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
from analytics_engine.heuristics.sinks.mf2c.influx_sink import InfluxSink
from analytics_engine.heuristics.filters.cimi_filter import CimiFilter

LOG = common.LOG


class RefineRecipePipe(Pipe):
    __pipe_name__ = 'refine_recipe_pipe'

    def __init__(self):
        self._analysis_id = None

    def run(self, workload):
        """
        Returns results from a previous analysis
        :param workload - workload name
        :return: returns the refined recipe
        """
        if not workload:
            raise IOError('A workload needs to be specified')
        if not self._analysis_id:
            raise IOError('An analysis ID needs to be specified before invoking run()')
        service_id = workload.get_workload_name()
        influx_sink = InfluxSink()
        latest_recipe = None
        workload = influx_sink.show(params=(service_id, self._analysis_id))
        if workload:
            latest_recipe = workload.get_latest_recipe()

            # update cimi
            cimi_filter = CimiFilter()
            latest_recipe = cimi_filter.run(latest_recipe)
            cimi_filter.refine(latest_recipe)

            LOG.info('Recipe: {}'.format(latest_recipe))
        else:
            LOG.error('No existing analysis for the specified params.')
        return latest_recipe

    def set_analysis_id(self, analysis_id):
        """
        Preliminary method to be called before invoking
        the run method.
        Sets the analysis_id for which the RefineRecipePipe needs
        to be run upon.
        Method needed to have consistency on the Pipe interface.
        :param analysis_id: analysis ID
        :return:
        """
        self._analysis_id = analysis_id