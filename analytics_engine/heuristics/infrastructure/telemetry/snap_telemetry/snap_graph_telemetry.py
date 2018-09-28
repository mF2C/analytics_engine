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

import time
from datetime import datetime

import dateutil.parser as d_parser
import pandas as pd

from analytics_engine import common
import analytics_engine.infrastructure_manager.telemetry as telemetry
from analytics_engine.heuristics.beans.infograph import InfoGraphNode
from analytics_engine.heuristics.beans.infograph import InfoGraphNodeLayer as GRAPH_LAYER
from analytics_engine.heuristics.beans.infograph import InfoGraphNodeType as NODE_TYPE
from analytics_engine.heuristics.infrastructure.telemetry.graph_telemetry import GraphTelemetry
from metric_conf import METRIC_TAGS
from metric_conf import NODE_METRICS
from snap_query import SnapQuery

LOG = common.LOG


class SnapAnnotation(GraphTelemetry):

    def __init__(self, metric_timeout=120):
        self.snap = telemetry.get_telemetry("snap")
        self.metrics = {}
        self.metric_timeout = metric_timeout
        self.landscape = None
        self.vms = []

    def get_utilization_data(self, node):
        pass

    def get_data(self, node):
        """
        Return telemetry data for the specified node

        :param node: InfoGraph node
        :return: pandas.DataFrame
        """
        data = self._get_data(node)
        return data

    def get_queries(self, landscape, node, ts_from, ts_to):
        """
        Return queries to use for telemetry for the specific node.

        :param landscape:
        :param node:
        :param ts_from:
        :param ts_to:
        :return:
        """

        queries = []
        self.landscape = landscape
        node_layer = InfoGraphNode.get_layer(node)
        # Service Layer metrics are not required
        #if node_layer == GRAPH_LAYER.SERVICE:
        #    return []
        for metric in self._get_metrics(node):
            try:
                query = self._build_query(metric, node, ts_from, ts_to)
                queries.append(query)
            except Exception as e:
                LOG.error('Exception for metric: {}'.format(metric))


        return queries

    def _build_query(self, metric, node, ts_from, ts_to):
        tags = self._tags(metric, node)
        # query = SnapQuery(self.snap, metric, tags, ts_from, ts_to)
        query = dict()
        query['metric'] = metric
        query['tags'] = tags
        query['ts_from'] = ts_from
        query['ts_to'] = ts_to
        return query

    def _get_data(self, node):
        # TODO: Create here the object SnapQuery from the string
        results = {}
        for query_vars in InfoGraphNode.get_queries(node):
            query = SnapQuery(self.snap,
                              query_vars['metric'],
                              query_vars['tags'],
                              query_vars['ts_from'],
                              query_vars['ts_to'])
            res = query.run()
            results[query.metric] = res
        results_dataframe = self._to_dataframe(results)
        return results_dataframe

    def _to_dataframe(self, results):
        dataframes = []
        largest_index = 0
        largest = 0
        i = 0

        for metric, result in results.iteritems():
            times = []
            vals = []
            i += 1
            if len(result) > largest:
                largest_index = i
                largest = len(result)
            for ts, val in result:
                dt = d_parser.parse(ts[:-1].split(".")[0])
                unix_time = datetime(1970, 1, 1)
                if dt.tzinfo is not None:
                    unix_time.replace(tzinfo=dt.tzinfo)
                epoch = (dt - unix_time).total_seconds()
                timestamp = int(round(epoch))
                times.append(timestamp)
                vals.append(val)

            result_df = pd.DataFrame()
            result_df['timestamp'] = pd.Series(times)
            result_df[metric] = pd.Series(vals)
            dataframes.append(result_df)

        if len(dataframes) > 0:
            df_res = pd.DataFrame()
            df_res['timestamp'] = dataframes[0]['timestamp']
            for df in dataframes:
                try:
                    df = df.drop_duplicates(subset='timestamp')
                    df_res = pd.merge(df_res, df, on='timestamp', how='outer')
                except Exception as e:
                    LOG.error(e)
                    exit()
            # df_res = df_res.set_index('timestamp')
            df_res['timestamp'] = df_res['timestamp'].astype(str)
            return df_res
            # return pd.concat(dataframes, axis=1,
            #                  join_axes=[dataframes[largest_index].index])
        return pd.DataFrame()

    def _tags(self, metric, node):
        tags = {}
        tag_keys = self._tag_keys(metric, node)
        for tag_key in tag_keys:
            tag_value = self._tag_value(tag_key, node, metric)
            tags[tag_key] = tag_value
        return tags

    def _tag_keys(self, metric, node):
        tag_keys = []

        # metric keys specific to node type
        node_type = InfoGraphNode.get_type(node)
        if node_type == NODE_TYPE.VIRTUAL_MACHINE:
            tag_keys.append("stack_name")

            # TODO: Check if this comment causes any problem
            # tag_keys.append("vm_name")
        elif node_type == NODE_TYPE.VIRTUAL_NIC:
            tag_keys.append("ip")

        # standard metric keys
        for metric_head, keys in METRIC_TAGS:
            if metric_head in metric:
                tag_keys += keys
                return tag_keys
        return None

    def _tag_value(self, tag_key, node, metric):
        # TODO: fully qualify this with metric name, if metric is this and tag
        tag_value = None
        if tag_key == "source":
            tag_value = self._source(node)
        elif tag_key in set(["device_id", "disk", "device_name"]):
            tag_value = self._disk(node)
        elif tag_key in set(["cpu_id", "cpuID", "core_id"]):
            tag_value = self._pu(node, metric)
        elif tag_key in set(["nic_id", "interface", "network_interface", "interface_name"]):
            tag_value = self._nic(node)
        elif tag_key == "nova_uuid":
            tag_value = self._nova_uuid(node)
        elif tag_key == "stack_name":
            tag_value = self._stack(node)
        elif tag_key == "dev_id":
            if "intel/use/network" in metric:
                tag_value = self._nic(node)
            elif "intel/use/disk" in metric:
                tag_value = self._disk(node)
        elif tag_key == "docker_id":
            tag_value = InfoGraphNode.get_docker_id(node)
        return tag_value

    def _source(self, node):
        attrs = InfoGraphNode.get_attributes(node)
        if InfoGraphNode.get_layer(node) == GRAPH_LAYER.PHYSICAL:
            if 'allocation' in attrs:
                return attrs['allocation']
            # fix due to the landscape
            else:
                while attrs.get('attributes', None):
                    attrs = attrs['attributes']
                if 'allocation' in attrs:
                    return attrs['allocation']
        if InfoGraphNode.get_type(node) == NODE_TYPE.VIRTUAL_MACHINE:
            if 'vm_name' in attrs:
                return attrs['vm_name']
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
        if InfoGraphNode.get_type(node) == NODE_TYPE.DOCKER_CONTAINER:
            docker_node = self.landscape.get_neighbour_by_type(InfoGraphNode.get_name(node),'docker_node')
            machine = self.landscape.get_neighbour_by_type(docker_node,'machine')
            return machine
        return None

    def _disk(self, node):
        disk = None
        if (InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_DISK or
                InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_MACHINE):
            attrs = InfoGraphNode.get_attributes(node)
            if 'osdev_storage-name' in attrs:
                disk = attrs["osdev_storage-name"]
            elif 'name' in attrs:
                disk = attrs["name"]
        elif InfoGraphNode.get_type(node) == NODE_TYPE.INSTANCE_DISK:
            disk = InfoGraphNode.get_name(node).split("_")[1]
        return disk

    def _pu(self, node, metric):
        pu = None
        if (InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_PU or
                    InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_MACHINE):
            attrs = InfoGraphNode.get_attributes(node)
            # fix attributes from landscaper - fixing
            # permanently on the fly if needed

            while attrs.get('attributes', None):
                attrs = attrs['attributes']

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
            elif 'name' in attrs:
                nic = attrs["name"]
        # if InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_MACHINE:
        #     LOG.info('NODEEEEE: {}'.format(node))
        return nic

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

    def _nova_uuid(self, node):
        if InfoGraphNode.get_type(node) == NODE_TYPE.INSTANCE_DISK:
            disk_name = InfoGraphNode.get_name(node)
            vm = self.landscape.get_neighbour_by_type(disk_name, "vm")
            return vm
        if InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_MACHINE:
            vm = self.vms.pop()
            return vm
        return None

    def _cached_metrics(self, identifier, query_tags):
        """
        Retrieves cached metrics.  Snap is queried using the tags and saved
        in an object variable, identified by the identifier. Metrics are then
        retrieved from this variable, rather than making a query each time. If 
        the last time the metrics were queried exceeds a timeout, then a new
        query is cached.
        """
        # If the metric attribute is empty for a given source then fill it.
        if identifier not in self.metrics:
            metrics = self.snap.show_metrics(query_tags)
            self.metrics[identifier] = (time.time(), metrics)
        else:
            # If the timer has elapsed for a given source since then refill it.
            last_query_timestamp = self.metrics[identifier][0]
            current_time = time.time()
            if (current_time - last_query_timestamp) > self.metric_timeout:
                metrics = self.snap.show_metrics(query_tags)
                self.metrics[identifier] = (time.time(), metrics)

        return self.metrics[identifier][1]  # just the types not the timestamp

    def _get_metrics(self, node):
        """
        Retrieves the metrics for a node based on its type.  This is done by
        checking if the node is in the NODE_METRICS dictionary and then pulling
        out a list of metric heads for that node type.  If the metric head 
        matches the metric retrieved from the host then we attach it.
        """
        metrics = []
        node_type = InfoGraphNode.get_type(node)

        if node_type in NODE_METRICS:
            source_metrics = self._source_metrics(node)
            for metric in source_metrics:
                for metric_start in NODE_METRICS[node_type]:
                    if metric.startswith(metric_start) \
                            and not self._exception(node, metric):
                        if metric.startswith("intel/net/"):
                            nic_id = self._nic(node)
                            if nic_id in metric:
                                metrics.append(metric)
                        if metric.startswith('intel/libvirt/'):
                            self._get_nova_uuids(node)
                            for x in range(0, len(self.vms)):
                                #LOG.info('Adding {}'.format(metric))
                                metrics.append(metric)
                        else:
                            metrics.append(metric)
        return metrics

    def _get_nova_uuids(self, node):
        if InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_MACHINE:
            phy_name = InfoGraphNode.get_name(node)
            self.vms = self.landscape.get_neighbours_by_type(phy_name, "vm")
            #LOG.info('Collecting nova uuids: {}'.format(self.vms))

    def _source_metrics(self, node):
        """
        Retrieves metrics associated with a source/host.  The source is 
        identified by the node and then all metrics types are collected for 
        that source.  If the node is physical then the metric types are 
        retrieved using just the machine name as the source, if the node is 
        virtual then the source (the vm hostname) and the stack name are 
        required. 
        """

        metric_types = []
        node_layer = InfoGraphNode.get_layer(node)
        node_type = InfoGraphNode.get_type(node)
        if node_layer == GRAPH_LAYER.PHYSICAL \
                or node_type == NODE_TYPE.INSTANCE_DISK:
            try:
                source = self._source(node)
                identifier = source
                query_tags = {"source": source}
                metric_types = self._cached_metrics(identifier, query_tags)
            except Exception as ex:
                LOG.error('Malformed graph: {}'.format(InfoGraphNode.get_name(node)))
                LOG.error(ex)


        elif node_layer == GRAPH_LAYER.VIRTUAL:
            source = self._source(node)
            stack = self._stack(node)

            #LOG.info("SOURCE: {}".format(source))
            #LOG.info("STACK: {}".format(stack))

            if stack is not None:

                identifier = "{}-{}".format(source, stack)
                # query_tags = {"source": source, "stack": stack}

                query_tags = {"stack_name": stack}
                metric_types = self._cached_metrics(identifier, query_tags)
        elif node_type == NODE_TYPE.DOCKER_CONTAINER:
            source = self._source(node)
            docker_id = InfoGraphNode.get_docker_id(node)
            if docker_id is not None and source is not None:
                identifier = "{}-{}".format(source, docker_id)
                query_tags = {"docker_id": docker_id, "source": source}
                metric_types = self._cached_metrics(identifier, query_tags)

        return metric_types

    def _exception(self, node, metric):
        # This metric should be attached to the machine and not nic.
        if InfoGraphNode.get_type(node) == NODE_TYPE.PHYSICAL_NIC \
                and metric.startswith("intel/psutil/net/all"):
            return True
        return False


