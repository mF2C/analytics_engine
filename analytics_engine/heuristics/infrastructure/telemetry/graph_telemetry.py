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

__author__ = 'Giuliana Carullo, Vincenzo Riccobene, Kevin Mullery'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"


class GraphTelemetry(object):
    """
    This class represents the portion of the data related to the specific
    telemetry system.
    """

    def get_queries(self, graph, node, ts_from, ts_to):
        """
        Returns a list of queries to get telemetry data related to the node

        :param node: InfoGraph node
        :param ts_from: (str) epoch representing start time
        :param ts_to: (str) epoch representing stop time
        :return: (str)
        """
        raise NotImplementedError()

    def get_data(self, node):
        """
        Return telemetry data for the specified node.
        The node needs to have already a field containing the query

        :param node: InfoGraph node
        :return: pandas.DataFrame
        """
        raise NotImplementedError()
