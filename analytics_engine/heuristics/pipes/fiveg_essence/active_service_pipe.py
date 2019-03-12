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
from analytics_engine.heuristics.filters.fiveg_essence.active_service_filter import ActiveServiceFilter
import time

LOG = common.LOG


class ActiveServicePipe(Pipe):
    __pipe_name__ = 'active_service_pipe'
    """
    Gets a list of all active services.
    
    :param none
    :return:
    """

    def run(self, workload=None):
        print "Starting ActiveServicePipe Pipe: {}".format(time.time())
        filter = ActiveServiceFilter()
        workload = filter.run(workload)
        print "Returning Active service data in ActiveServicePipe Pipe: {}".format(time.time())
        return workload
