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

__author__ = 'Giuliana Carullo, Kevin Mullery'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"

# previously into snap_graph_telemetry Who's the original author?)
from analytics_engine import common

LOG = common.LOG

class SnapQuery(object):
    """
    This class hosts the definition of the query object for snap
    """

    def __init__(self, snap, metric, tags, ts_from, ts_to):
        self.snap = snap
        self.metric = metric
        self.tags = tags
        self.ts_from = ts_from
        self.ts_to = ts_to

    def run(self):
        LOG.debug('Get Metric "{}" from "{}" to "{}" where {}'.format(
            self.metric, self.ts_from, self.ts_to, self.tags))
        if self.metric.startswith('intel/libvirt/'):
            LOG.info('Get Metric "{}" from "{}" to "{}" where {}'.format(
                self.metric, self.ts_from, self.ts_to, self.tags))
        return self.snap.get_metric(self.metric, self.ts_from, self.ts_to, self.tags)