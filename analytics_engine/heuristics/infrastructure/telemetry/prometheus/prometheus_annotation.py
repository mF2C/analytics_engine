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

__author__ = 'eugene_ryan'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"

import traceback
import sys
#from IPy import IP
import pandas
import requests
from analytics_engine import common
from analytics_engine.infrastructure_manager.config_helper import ConfigHelper
from analytics_engine.heuristics.beans.infograph import InfoGraphNode
from analytics_engine.heuristics.beans.infograph import InfoGraphNodeLayer
from analytics_engine.heuristics.beans.infograph import InfoGraphNodeLayer as GRAPH_LAYER
from analytics_engine.heuristics.beans.infograph import InfoGraphNodeType as NODE_TYPE
from analytics_engine.heuristics.infrastructure.telemetry.graph_telemetry import GraphTelemetry
from metric_conf import NODE_TO_METRIC_TAGS
from metric_conf import NODE_METRICS

PROMETHEUS_TS_LIMIT = 11000

LOG = common.LOG

class PrometheusAnnotation(GraphTelemetry):

    def __init__(self):
        PROMETHEUS_HOST = ConfigHelper.get("PROMETHEUS", "PROMETHEUS_HOST")
        PROMETHEUS_PORT = ConfigHelper.get("PROMETHEUS", "PROMETHEUS_PORT")
        PrometheusAnnotation._validateIPAddress(PROMETHEUS_HOST)
        PrometheusAnnotation._validatePortNumber(PROMETHEUS_PORT)
        self.tsdb_ip = PROMETHEUS_HOST
        self.tsdb_port = PROMETHEUS_PORT
        self.metrics = {}

    def get_data(self, node):
        """
        Return telemetry data for the specified node
        :param node: InfoGraph node
        :return: pandas.DataFrame
        """
        queries = InfoGraphNode.get_queries(node)
        ret_val = pandas.DataFrame()
        try:
           ret_val = self._get_data(queries)
        except Exception as ex:
            LOG.debug("Exception in user code: \n{} {} {}".format(
                '-' * 60), traceback.print_exc(file=sys.stdout), '-' * 60)
        #ret_val.set_index(keys='timestamp')
        return ret_val

    def get_queries(self, graph, node, ts_from, ts_to):
        """
        :param graph:
        :param node:
        :param ts_from:
        :param ts_to:
        :return:
        """
        node_name = InfoGraphNode.get_name(node)
        node_layer = InfoGraphNode.get_layer(node)
        queries = list()
        # No point to ask for Service Resources
        if node_layer == InfoGraphNodeLayer.SERVICE:
            return queries

        for metric in self._get_metrics(node):
            try:
                query = self._build_query(metric, node, ts_from, ts_to)
            except Exception as e:
                LOG.error('Exception for metric: {}'.format(metric))
            queries.append({"{}_{}".format(metric, node_name): query})

        return queries

    def _build_query(self, metric, node, ts_from, ts_to):
        """
        Return queries to use for telemetry for the specific node.
        :param metric: the metric on which to build this query
        :param node: the node
        :param ts_from: timestamp from
        :param ts_to: timestamp to
        :return: an individual query URL string
        """
        resolution = ts_to - ts_from
        if resolution > PROMETHEUS_TS_LIMIT:
            ts_from = ts_to - PROMETHEUS_TS_LIMIT

        query_head = "http://{}:{}/api/v1/query_range?query=".format(
            self.tsdb_ip, self.tsdb_port)
        query_times = "&start={}&end={}&step=1s".format(ts_from, ts_to)

        query_selectors = self._get_query_selectors(metric, node)
        query_selector = '{}{{{}}}'.format(metric, query_selectors)

        query = "{}{}{}".format(query_head, query_selector, query_times)
        return query


    def _get_data(self, queries):
        """
        Returns data available for metrics for resources that match the
        criteria.

        :param metric_names: Metrics names as array.
        :param filters: Filter as dictionary.
        :param start_time: A start time.
        :param end_time: A end time.
        :returns: pandas.DataFrame with data and performance related data
        """
        metrics_data = dict()
        # data structure initialization
        for query in queries:
            LOG.debug("QUERY: {}".format(query))
            for resource in query.keys():
                metrics_data[resource] = list()

        for query in queries:
            for resource in query.keys():
                full_request = query[resource]
                retries = 0
                while retries < 3: # Cimarron.RETRIES: # ++++
                    try:
                        # LOG.info("Query - {}".format(full_request))
                        req = requests.get(full_request,
                                           timeout=30) # Cimarron.TIMEOUT) # ++++
                        if req.status_code == 200:
                            # LOG.info("Query output size - {}".format(req.content.__sizeof__()))
                            metrics_data[resource].append(req.json())
                        break
                    except requests.exceptions.RequestException as exc:
                        LOG.error(exc)
                        retries += 1
                        LOG.error("Failed to get metric - {}".
                                  format(resource))
                        LOG.error("Will try again. Attempt number:  {}".
                                  format(retries))
        res = pandas.DataFrame()
        res['timestamp'] = pandas.Series()
        res.set_index('timestamp')
        dfs = []
        mnames = {}
        for resource, results in metrics_data.iteritems():
            for result in results: # metrics_data[resource]
                if result['status'] == 'success':
                    if result['data']['resultType'] == 'matrix':
                        result_metrics = result['data']['result']
                        for result_metric in result_metrics:

                            metric_name = result_metric['metric']['__name__']
                            del result_metric['metric']['__name__']
                            for k, v in result_metric['metric'].iteritems():
                                metric_name = metric_name + ';' + k + ':' + v

                            if mnames.get(metric_name):
                                print metric_name
                                print result_metric['metric']
                                continue
                            else:
                                mnames[metric_name] = 'Exists'
                            values = result_metric['values']
                            LOG.debug("adding {}, size {} to dataframe".format(metric_name, len(values)) )

                            df = pandas.DataFrame(values, columns=["timestamp", metric_name])

                            #df = pandas.DataFrame(columns=('timestamp', metric_name))
                            #df.set_index('timestamp')
                            #timestamp = list()
                            #metric = list()
                            #for [ts, val] in values:
                            #    timestamp.append(ts)
                            #    metric.append(val)
                            #df = pandas.DataFrame({'timestamp': timestamp,
                            #                       metric_name: metric})
                            dfs.append(df)
                            #if res.empty:
                            #    res = df.copy()
                            #else:
                            #    res = pandas.merge(res, df, how='outer', on='timestamp')
        dfs = [df.set_index('timestamp') for df in dfs]
        if len(dfs) > 0:
            res = dfs[0]
        if len(dfs) > 1:
            res = dfs[0].join(dfs[1:], how='outer')
        res.sort_values(by='timestamp', ascending=True)
        return res

    def _get_metrics(self, node):
        """
        Retrieves the metrics for a node based on its type.  This is done by
        checking if the node is in the NODE_METRICS dictionary and then pulling
        out a list of metric heads for that node type.  If the metric head
        matches the metric retrieved from the host then we attach it.
        """
        metrics = []
        node_type = InfoGraphNode.get_type(node)
        LOG.debug('looking for node type = {}, node = {}'.format(node_type, node[0]))

#        if node_type != 'cache' and node_type != 'pcidev':
#            dummy = 1

        if node_type in NODE_METRICS:
            metrics = NODE_METRICS[node_type]
        LOG.debug("METRICS: {}".format(metrics))
        return metrics

    def _get_query_selectors(self, metric, node):
        node_type = InfoGraphNode.get_type(node)
        tags = self._tags(metric, node)
        selectors = []
        for tag, tag_value in tags.iteritems():
            if tag == "instance": #and node_type == NODE_TYPE.PHYSICAL_MACHINE:  # hostname needs a regexp
                selector = 'instance=~"{}:.*"'.format(tag_value)
            else:
                selector = '{}="{}"'.format(tag, tag_value)
            selectors.append(selector)
        s = ','.join(selectors)
        return s

    def _tags(self, metric, node):
        tags = {}
        attrs = InfoGraphNode.get_attributes(node)
        tag_keys = self._tag_keys(metric, node)
        for tag_key in tag_keys:
            tag_value = self._tag_value(tag_key, node, metric)
            tags[tag_key] = tag_value
        return tags

    def _tag_keys(self, metric, node):
        tag_keys = []

        # always put in instance
        tag_keys +=  ["instance"]

        node_type = InfoGraphNode.get_type(node)
        if node_type in NODE_TO_METRIC_TAGS:
            tag_keys = NODE_TO_METRIC_TAGS[node_type]

        return tag_keys

    def _tag_value(self, tag_key, node, metric):
        # TODO: fully qualify this with metric name, if metric is this and tag
        tag_value = None
        if tag_key == "instance":
            tag_value  = self._source(node)
        elif tag_key == "source":
            tag_value = self._source(node)

        if tag_value is None:
            node_type = InfoGraphNode.get_type(node)
            if node_type == NODE_TYPE.PHYSICAL_DISK:
                tag_value = self._disk(node)
            elif node_type == NODE_TYPE.PHYSICAL_PU:
                tag_value = self._pu(node, metric)
            elif node_type == NODE_TYPE.PHYSICAL_NIC:
                attrs = InfoGraphNode.get_attributes(node)
                tag_value = self._nic(node)

            elif node_type == NODE_TYPE.VIRTUAL_MACHINE:
                tag_value = self._vm(node)

        return tag_value

    def _source(self, node):
        attrs = InfoGraphNode.get_attributes(node)
        if InfoGraphNode.get_layer(node) == GRAPH_LAYER.PHYSICAL:
            if 'allocation' in attrs:
                return attrs['allocation']
        if InfoGraphNode.get_type(node) == NODE_TYPE.VIRTUAL_MACHINE:
            if 'vm_name' in attrs:
                return attrs['vm_name']
            elif 'name' in attrs:
                return attrs['name']
        if InfoGraphNode.get_type(node) == NODE_TYPE.INSTANCE_DISK:
            # The machine is the source as this is a libvirt disk.
            disk_name = InfoGraphNode.get_name(node)
            vm = self.landscape.get_neighbour_by_type(
                disk_name, NODE_TYPE.VIRTUAL_MACHINE)
            machine = self.landscape.get_neighbour_by_type(
                vm, NODE_TYPE.PHYSICAL_MACHINE)
            return machine
        if InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_MACHINE:
            if 'name' in attrs:
                return attrs['name']
        return None


    def _disk(self, node):
        disk = None
        if (InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_DISK or
                InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_MACHINE):
            attrs = InfoGraphNode.get_attributes(node)
            if 'osdev_storage-name' in attrs:
                disk = attrs["osdev_storage-name"]
        elif InfoGraphNode.get_type(node) == NODE_TYPE.INSTANCE_DISK:
            disk = InfoGraphNode.get_name(node).split("_")[1]
        return disk

    def _pu(self, node, metric):
        pu = None
        if (InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_PU or
                    InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_MACHINE):
            attrs = InfoGraphNode.get_attributes(node)
            if 'os_index' in attrs:
                pu = attrs["os_index"]
        # metric prefix 'cpu' on to the front of the cpu number.
        if pu and ('intel/proc/schedstat/cpu/' in metric or 'intel/psutil/cpu/' in metric):
            pu = "cpu{}".format(pu)
        return pu

    def _nic(self, node):
        nic = None
        if InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_NIC:
            attrs = InfoGraphNode.get_attributes(node)
            if 'osdev_network-name' in attrs:
                nic = attrs["osdev_network-name"]
        # if InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_MACHINE:
        #     LOG.info('NODEEEEE: {}'.format(node))
        return nic

    def _vm(self, node):
        if InfoGraphNode.get_type(node) == NODE_TYPE.VIRTUAL_MACHINE:
            attrs = InfoGraphNode.get_attributes(node)
        return attrs['libvirt_instance']

    def _stack(self, node):
        if InfoGraphNode.get_type(node) == NODE_TYPE.VIRTUAL_MACHINE:
            # Taking service node to which the VM is connected
            predecessors = self.landscape.predecessors(
                InfoGraphNode.get_name(node))
            for predecessor in predecessors:
                predecessor_node = self.landscape.node[predecessor]
                if predecessor_node['type'] == NODE_TYPE.SERVICE_COMPUTE:
                    if 'stack_name' in predecessor_node:
                        return predecessor_node["stack_name"]
        return None



    @staticmethod
    def _validateIPAddress(tsdb_ip):
        #IP(tsdb_ip)
        return True

    @staticmethod
    def _validatePortNumber(tsdb_port):
        port = int(tsdb_port)
        if port < 0 or port > 99999:
            raise ValueError("Port number {} is not valid".format(tsdb_port))
        return True
