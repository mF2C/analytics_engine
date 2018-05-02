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

__author__ = 'Giuliana Carullo, Vincenzo Riccobene'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"


import pandas
from analytics_engine.heuristics.beans.infograph import InfoGraphNode


class InfoGraphStatistics():

    @staticmethod
    def get_correlation(node_a, node_b, metric_a, metric_b):
        # TODO: Add node validation
        # InfoGraphNode.validateNode(node_a)
        # InfoGraphNode.validateNode(node_b)

        node_name_a = InfoGraphNode.get_name(node_a)
        node_name_b = InfoGraphNode.get_name(node_b)

        if metric_a == 'utilization':
            telemetry_a = InfoGraphNode.get_utilization(node_a)
        else:
            telemetry_a = InfoGraphNode.get_telemetry_data(node_a)

        if metric_b == 'utilization':
            telemetry_b = InfoGraphNode.get_utilization(node_b)
        else:
            telemetry_b = InfoGraphNode.get_telemetry_data(node_b)

        if metric_a not in telemetry_a.columns.values:
            raise ValueError("Metric {} is not in Telemetry data of Node {}".
                             format(metric_a, node_name_a))
        if metric_b not in telemetry_b.columns.values:
            raise ValueError("Metric {} is not in Telemetry data of Node {}".
                             format(metric_b, node_name_b))
        if telemetry_a.empty and telemetry_b.empty:
            return 0

        res = telemetry_a.corrwith(telemetry_b)

        df_a = telemetry_a.\
            rename(columns={metric_a: "a-{}".format(metric_a)}).astype(float)
        df_b = telemetry_b.\
            rename(columns={metric_b: "b-{}".format(metric_b)}).astype(float)
        correlation = pandas.merge(df_a, df_b,
                                   how='outer', on='timestamp')
        correlation = correlation.dropna()
        res = correlation["a-{}".format(metric_a)].\
            corr(correlation["b-{}".format(metric_b)])
        return res