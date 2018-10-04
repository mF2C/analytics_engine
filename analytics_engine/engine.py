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

__author__ = 'Giuliana Carullo, Eugene Ryan'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"

import argparse
from analytics_engine import common as common
from analytics_engine.heuristics.beans.workload import Workload
from analytics_engine.heuristics.pipes.annotated_telemetry_pipe import AnnotatedTelemetryPipe
from analytics_engine.heuristics.pipes.mf2c.avg_heuristic import AvgHeuristicPipe
from analytics_engine.heuristics.pipes.mf2c.optimal_pipe import OptimalPipe
from analytics_engine.heuristics.pipes.mf2c.refine_recipe_pipe import RefineRecipePipe
from analytics_engine.heuristics.sinks.mf2c.rest_api_sink import RestiAPI
from analytics_engine.utilities import misc as utils
from analytics_engine.utilities.misc import Validation
import time

LOG = common.LOG

# Configuration File Sections
CFS_GENERAL = 'General'
CFS_DYNAMIC_PARAMS = 'Dynamic-params'

PIPES = ['avg_analysis', 'telemetry',
         'optimal', 'refine_recipe']

class Engine:

    def __init__(self, pipe, workload_name, ts_from, ts_to, config, config_type, analysis_id):
        # required initialization
        # Init Common
        self._setup_framework_base_directory()
        self.pipe = pipe
        if pipe == 'optimal':
            ts_from = 0
            ts_to = 0
            workload_name = pipe+"_"+str(int(time.time()))
        self.workload = Workload(workload_name, ts_from, ts_to, config, config_type)
        self.analysis_id = analysis_id

    def run(self):

        pipe_exec = None
        res = None
        if self.pipe == 'avg_analysis':
            pipe_exec = AvgHeuristicPipe()
        elif self.pipe == 'telemetry':
            pipe_exec = AnnotatedTelemetryPipe()
        elif self.pipe == 'optimal':
            pipe_exec = OptimalPipe()
        elif self.pipe == 'refine_recipe':
            pipe_exec = RefineRecipePipe()
            pipe_exec.set_analysis_id(self.analysis_id)

        elif self.pipe == 'rest':
            LOG.info('running in online mode')
            RestiAPI().run()

        else:
            LOG.error('Please specify at least 1 task to be performed '
                      '"{} --help" to see available options'.format(
                     common.SERVICE_NAME))
            exit()
        if self.pipe != 'rest':
            LOG.info('Analyzing Workload: {}'.format(self.workload.get_workload_name()))
            res = pipe_exec.run(self.workload)
        return res

    def _setup_framework_base_directory(self):
        from analytics_engine.utilities import misc as utils
        common.BASE_DIR = utils.Validation.directory_exist_and_format(
            common.BASE_DIR)

    def _setup_framework_configuration_file(self):
        """
        Validate configuration file and setup internal parameters accordingly
        """

        # Check configuration file and sections
        sections = [CFS_GENERAL, CFS_DYNAMIC_PARAMS]
        if common.CONF_FILE_LOCATION:
            Validation.file_exist(common.CONF_FILE_LOCATION)
            common.CONF_FILE = \
                utils.ConfigurationFile(sections, common.CONF_FILE_LOCATION)

        # Load dynamic parameters within common
        for common_attrib in common.CONF_FILE.get_variable_list(CFS_DYNAMIC_PARAMS):
            setattr(
                common, common_attrib.upper(),
                common.CONF_FILE.get_variable(
                    CFS_DYNAMIC_PARAMS, common_attrib))

    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(
            description='Analytics Engine')
        parser.add_argument('--run', type=str, required=True, default='none',
                            help='name of the task to be performed')
        parser.add_argument('--workload_name', type=str, required=False, default='none',
                            help='name of workload to export')
        parser.add_argument('--ts_from', type=int, required=False, default=0,
                            help='start timestamp')
        parser.add_argument('--ts_to', type=int, required=False, default=0,
                            help='end timestamp')
        parser.add_argument('--config', type=str, required=False, default='none',
                            help='path to local config file')
        parser.add_argument('--config_type', type=str, required=False, default=None,
                            help='type of the config file')
        parser.add_argument('--analysis_id', type=str, required=False, default=None,
                            help='type of the config file')

        return parser.parse_args()


def run_engine(pipe, workload_name, start_ts, end_ts, config, config_type, analysis_id):
    engine = Engine(pipe, workload_name, start_ts, end_ts, config, config_type, analysis_id)
    engine.run()

def main():
    """
    Initialize and run the analytics engine
    """
    args = Engine.parse_args()
    run_engine(args.run, args.workload_name, args.ts_from, args.ts_to, args.config, args.config_type, args.analysis_id)


if __name__ == '__main__':
    args = Engine.parse_args()

    # sample usage: --workload_name noisy_neighbor_1 --ts_from 1509214219 --ts_to 1509218632
    # --workload_name avg_test --ts_from 1522144953 --ts_to 1522144965
    run_engine(args.run, args.workload_name, args.ts_from, args.ts_to, args.config, args.config_type, args.analysis_id)
