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

from analytics_engine.heuristics.sinks.base import Sink
from analytics_engine import common as common
from analytics_engine.infrastructure_manager.config_helper import ConfigHelper
from influxdb import InfluxDBClient
from networkx.readwrite import json_graph
from analytics_engine.heuristics.beans.workload import Workload
import analytics_engine.infrastructure_manager.infograph as infograph
from analytics_engine.heuristics.beans.mf2c.recipe import Recipe
import json

LOG = common.LOG


class InfluxSink(Sink):

    """Stores workload into an influxDB"""

    def __init__(self):
        self._read_conf()
        if self.INFLUX:
            self._connect()

    def _read_conf(self):
        """
        Reads influx configuration.
        :return:
        """
        self.INFLUX = ConfigHelper.get("INFLUXDB", "INFLUX")
        if self.INFLUX:

            if self.INFLUX:
                self.INFLUX_IP = ConfigHelper.get("INFLUXDB", "INFLUX_IP")
                self.INFLUX_PORT = ConfigHelper.get("INFLUXDB", "INFLUX_PORT")
                self.INFLUX_USER = ConfigHelper.get("INFLUXDB", "INFLUX_USER")
                self.INFLUX_PASSWD = ConfigHelper.get("INFLUXDB", "INFLUX_PASSWD")

                try:
                    development = ConfigHelper.get("Dynamic-params", "development")

                except:
                    development = False

                # Init database
                db_name = "development" if development else "production"
                self.INFLUX_DATABASE = "{}_{}".format(
                    common.SERVICE_NAME, db_name)

                if hasattr(common, "TEST") and getattr(common, "TEST"):
                    self.INFLUX_DATABASE = "{}_{}".format(
                        common.SERVICE_NAME, "test")
        else:
            LOG.info('Influx is not configured properly.')

    def _connect(self):
        """

        Connects with the specified Influx DB
        :return:
        """
        self.client = InfluxDBClient(self.INFLUX_IP, self.INFLUX_PORT, self.INFLUX_USER, self.INFLUX_PASSWD)
        dbs = self.client.get_list_database()
        if self.INFLUX_DATABASE not in dbs:
            LOG.info('creating DB: {}'.format(self.INFLUX_DATABASE))
            self.client.create_database(self.INFLUX_DATABASE)
        self.client.switch_database(self.INFLUX_DATABASE)

    @staticmethod
    def _workload_to_json(workload):
        """
        Returns the workload data formatted as json accordingly to
        InfluxDB structure.
        TODO: needs to be generalized to work with all filters
        :param workload: (Workload) the workload to be transformed
        :return: json representation of the workload for InfluxDB
        """
        subgraph_topology = workload.get_result('subgraph_filter')
        # internal management to make Influx happy with None values
        time = 0
        if workload.get_latest_recipe_time():
            time = workload.get_latest_recipe_time()
        try:
            subgraph_topology= json.dumps(json_graph.node_link_data(subgraph_topology))
        except:
            subgraph_topology = "{}"
        json_body = [
            {
                "measurement": 'workloads',
                "time": time,
                "fields": {
                    "subgraph": subgraph_topology,
                    "deployment conf": str(workload.get_configuration()),
                    "configuration type": str(workload.get_configuration_type()),
                    "ts_from": str(workload.get_ts_from()),
                    "ts_to": str(workload.get_ts_to()),
                    "recipe": json.dumps(workload.get_latest_recipe().to_json()),
                    "recipe_time": int(workload.get_latest_recipe_time())

                },
                "tags": {
                    "service_id": str(workload.get_workload_name()),
                    "analysis_id": int(workload.get_latest_recipe_time())


                 }
            }
        ]
        return json_body

    def save(self, workload):
        """
        Saves the workload on InfluxDB
        :param workload: (Workload) the workload to be saved
        :return:
        """
        if self.INFLUX:
            # At the moment this just stores results from comparison
            data = self._workload_to_json(workload)
            LOG.info("Writing workload data: {}".format(data))
            self.client.write_points(data)
        else:
            LOG.error('Modify the configuration file in order to use influx for storage')

    def show(self, params):
        """
        Retrieves wl data from influx. Rebuilds the workload
        based on service_id and analysis_id.
        Currently it queries for a single workload retrieval.
        Can be extended to retrieve all history data relative to a workload.
        :param params: (service_id, analysis_id)
        :return:
        """
        service_id = params[0]
        analysis_id = params[1]
        query = ""

        if service_id and analysis_id:
            query = 'SELECT * FROM "workloads" WHERE service_id = \'{}\'' \
                    'AND analysis_id = \'{}\';'.format(service_id, analysis_id)

        elif service_id:
            query = 'SELECT * FROM "workloads" WHERE service_id = \'{}\' ' \
                    'ORDER BY time DESC limit 1;'.format(service_id)
        else:
            LOG.error('service_id and analysis ID needs to be specified.')
            return None
        LOG.info("QUERY: {}".format(query))
        results = self.client.query(query)
        # TODO: losing part of the history
        workload = None
        for item in results.items():  # just 1 item
            data_points = item[1]
            data = next(data_points)
            workload_name = str(data["service_id"])
            ts_from = int(data["ts_from"])
            ts_to = int(data["ts_to"])
            workload_config = data["deployment conf"]  # the recipe
            workload_config_type = data["configuration type"]

            workload = Workload(workload_name=workload_name,
                                ts_from=ts_from, ts_to=ts_to,
                                workload_config=workload_config,
                                workload_config_type=workload_config_type)
            subgraph = data["subgraph"]
            if subgraph != "{}":
                nx_subgraph = json_graph.node_link_graph(json.loads(subgraph))
                workload.save_results('subgraph_filter',
                                      infograph.get_info_graph(landscape=nx_subgraph))  # json to inforgraph needed
            recipe_time = int(data["recipe_time"])
            if recipe_time:
                recipe_json = data["recipe"]
                recipe = Recipe()
                recipe.from_json(recipe_json)
                workload.add_recipe(recipe_time, recipe)
            break
        return workload