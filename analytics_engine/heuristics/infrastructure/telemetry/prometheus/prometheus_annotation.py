__author__ = 'eugene_ryan'

import traceback
import sys
#from IPy import IP
import pandas
import requests
from analytics_engine import common
from analytics_engine.heuristics.beans.infograph import InfoGraphNode
from analytics_engine.heuristics.beans.infograph import InfoGraphNodeLayer
from analytics_engine.heuristics.beans.infograph import InfoGraphNodeLayer as GRAPH_LAYER
from analytics_engine.heuristics.beans.infograph import InfoGraphNodeType as NODE_TYPE
from analytics_engine.heuristics.infrastructure.telemetry.graph_telemetry import GraphTelemetry

LOG = common.LOG

class PrometheusAnnotation(GraphTelemetry):
    NODE_METRICS = {
        NODE_TYPE.PHYSICAL_DISK: [        # disk
            "node_disk_io_now","node_disk_io_time_seconds_total",
            "node_disk_io_time_weighted_seconds_total","node_disk_read_bytes_total",
            "node_disk_read_time_seconds_total","node_disk_reads_completed_total",
            "node_disk_reads_merged_total","node_disk_write_time_seconds_total",
            "node_disk_writes_completed_total","node_disk_writes_merged_total",
            "node_disk_written_bytes_total",
            "node_filesystem_avail_bytes",
            "node_filesystem_device_error","node_filesystem_files","node_filesystem_files_free",
            "node_filesystem_free_bytes","node_filesystem_readonly","node_filesystem_size_bytes"
        ],
        NODE_TYPE.PHYSICAL_PU: [
            "node_cpu_core_throttles_total",
            "node_cpu_frequency_hertz","node_cpu_frequency_max_hertz","node_cpu_frequency_min_hertz",
            "node_cpu_guest_seconds_total","node_cpu_package_throttles_total",
            "node_cpu_seconds_total"
        ],
        NODE_TYPE.PHYSICAL_NIC: [
            "node_arp_entries",
            "node_network_receive_bytes_total","node_network_receive_compressed_total",
            "node_network_receive_drop_total","node_network_receive_errs_total",
            "node_network_receive_fifo_total","node_network_receive_frame_total",
            "node_network_receive_multicast_total","node_network_receive_packets_total",
            "node_network_transmit_bytes_total","node_network_transmit_carrier_total",
            "node_network_transmit_colls_total","node_network_transmit_compressed_total",
            "node_network_transmit_drop_total","node_network_transmit_errs_total",
            "node_network_transmit_fifo_total","node_network_transmit_packets_total"
        ],
        NODE_TYPE.PHYSICAL_MACHINE: [
            "node_context_switches_total",

            "node_entropy_available_bits",
            "node_filefd_allocated", "node_filefd_maximum",
            "node_procs_running", "net_conntrack_dialer_conn_attempted_total",
            "net_conntrack_dialer_conn_closed_total",
            "net_conntrack_dialer_conn_established_total","net_conntrack_dialer_conn_failed_total"
            "net_conntrack_listener_conn_accepted_total",
            "net_conntrack_listener_conn_closed_total","node_boot_time_seconds",
            "node_forks_total","node_hwmon_chip_names","node_hwmon_sensor_label",
            "node_hwmon_temp_celsius","node_hwmon_temp_crit_alarm_celsius",
            "node_hwmon_temp_crit_celsius","node_hwmon_temp_max_celsius","node_intr_total",
            "node_load1","node_load15","node_load5",

            # no specific nic info
            "node_netstat_Icmp6_InErrors", "node_netstat_Icmp6_InMsgs", "node_netstat_Icmp6_OutMsgs",
            "node_netstat_Icmp_InErrors", "node_netstat_Icmp_InMsgs", "node_netstat_Icmp_OutMsgs",
            "node_netstat_Ip6_InOctets", "node_netstat_Ip6_OutOctets",
            "node_netstat_IpExt_InOctets", "node_netstat_IpExt_OutOctets",
            "node_netstat_Ip_Forwarding", "node_netstat_TcpExt_ListenDrops",
            "node_netstat_TcpExt_ListenOverflows", "node_netstat_TcpExt_SyncookiesFailed",
            "node_netstat_TcpExt_SyncookiesRecv", "node_netstat_TcpExt_SyncookiesSent",
            "node_netstat_Tcp_ActiveOpens", "node_netstat_Tcp_CurrEstab", "node_netstat_Tcp_InErrs",
            "node_netstat_Tcp_PassiveOpens", "node_netstat_Tcp_RetransSegs",
            "node_netstat_Udp6_InDatagrams", "node_netstat_Udp6_InErrors", "node_netstat_Udp6_NoPorts",
            "node_netstat_Udp6_OutDatagrams", "node_netstat_UdpLite6_InErrors",
            "node_netstat_UdpLite_InErrors", "node_netstat_Udp_InDatagrams",
            "node_netstat_Udp_InErrors", "node_netstat_Udp_NoPorts", "node_netstat_Udp_OutDatagrams",

            # memory
            "node_memory_Active_anon_bytes",
            "node_memory_Active_bytes","node_memory_Active_file_bytes",
            "node_memory_AnonHugePages_bytes","node_memory_AnonPages_bytes",
            "node_memory_Bounce_bytes","node_memory_Buffers_bytes","node_memory_Cached_bytes",
            "node_memory_CmaFree_bytes","node_memory_CmaTotal_bytes","node_memory_CommitLimit_bytes",
            "node_memory_Committed_AS_bytes","node_memory_DirectMap1G_bytes",
            "node_memory_DirectMap2M_bytes","node_memory_DirectMap4k_bytes",
            "node_memory_Dirty_bytes","node_memory_HardwareCorrupted_bytes",
            "node_memory_HugePages_Free","node_memory_HugePages_Rsvd","node_memory_HugePages_Surp",
            "node_memory_HugePages_Total","node_memory_Hugepagesize_bytes",
            "node_memory_Inactive_anon_bytes","node_memory_Inactive_bytes",
            "node_memory_Inactive_file_bytes","node_memory_KernelStack_bytes",
            "node_memory_Mapped_bytes","node_memory_MemAvailable_bytes","node_memory_MemFree_bytes",
            "node_memory_MemTotal_bytes","node_memory_Mlocked_bytes",
            "node_memory_NFS_Unstable_bytes","node_memory_PageTables_bytes",
            "node_memory_SReclaimable_bytes","node_memory_SUnreclaim_bytes",
            "node_memory_ShmemHugePages_bytes","node_memory_ShmemPmdMapped_bytes",
            "node_memory_Shmem_bytes","node_memory_Slab_bytes","node_memory_SwapCached_bytes",
            "node_memory_SwapFree_bytes","node_memory_SwapTotal_bytes",
            "node_memory_Unevictable_bytes","node_memory_VmallocChunk_bytes",
            "node_memory_VmallocTotal_bytes","node_memory_VmallocUsed_bytes",
            "node_memory_WritebackTmp_bytes","node_memory_Writeback_bytes",

            "node_nf_conntrack_entries","node_nf_conntrack_entries_limit","node_procs_blocked",
            "node_procs_running","node_scrape_collector_duration_seconds",
            "node_scrape_collector_success","node_sockstat_FRAG_inuse","node_sockstat_FRAG_memory",
            "node_sockstat_RAW_inuse","node_sockstat_TCP_alloc","node_sockstat_TCP_inuse",
            "node_sockstat_TCP_mem","node_sockstat_TCP_mem_bytes","node_sockstat_TCP_orphan",
            "node_sockstat_TCP_tw","node_sockstat_UDPLITE_inuse","node_sockstat_UDP_inuse",
            "node_sockstat_UDP_mem","node_sockstat_UDP_mem_bytes","node_sockstat_sockets_used",
            "node_textfile_scrape_error","node_time_seconds","node_timex_estimated_error_seconds",
            "node_timex_frequency_adjustment_ratio","node_timex_loop_time_constant",
            "node_timex_maxerror_seconds","node_timex_offset_seconds",
            "node_timex_pps_calibration_total","node_timex_pps_error_total",
            "node_timex_pps_frequency_hertz","node_timex_pps_jitter_seconds",
            "node_timex_pps_jitter_total","node_timex_pps_shift_seconds",
            "node_timex_pps_stability_exceeded_total","node_timex_pps_stability_hertz",
            "node_timex_status","node_timex_sync_status","node_timex_tai_offset_seconds",
            "node_timex_tick_seconds","node_uname_info","node_vmstat_pgfault",
            "node_vmstat_pgmajfault","node_vmstat_pgpgin","node_vmstat_pgpgout","node_vmstat_pswpin",
            "node_vmstat_pswpout","process_cpu_seconds_total","process_max_fds",
            "process_open_fds","process_resident_memory_bytes","process_start_time_seconds","process_virtual_memory_bytes"
        ],
        #NODE_TYPE.VIRTUAL_MACHINE: ["node_procs_running"],  # "node_filesystem_files"]
        #NODE_TYPE.VIRTUAL_NIC: ["net_conntrack_dialer_conn_attempted_total"] # same metrics

        NODE_TYPE.VIRTUAL_MACHINE: [
            "collectd_libvirt_if_errors_1",
            "collectd_libvirt_if_packets_1",
            "collectd_libvirt_if_errors_0",
            "collectd_libvirt_memory",
            "collectd_libvirt_if_octets_0",
            "collectd_libvirt_if_packets_0",
            "collectd_libvirt_virt_vcpu",
            "collectd_libvirt_disk_octets_1",
            "collectd_libvirt_if_dropped_1",
            "collectd_libvirt_disk_ops_0",
            "collectd_libvirt_if_dropped_0",
            "collectd_libvirt_disk_octets_0",
            "collectd_disk_octets_1",
            "collectd_libvirt_if_octets_1",
            "collectd_libvirt_disk_ops_1",
            "collectd_libvirt_virt_cpu_total",
        ]

    }

    NODE_TO_METRIC_TAGS = {
        NODE_TYPE.PHYSICAL_DISK: ["instance", "device"],
        NODE_TYPE.PHYSICAL_PU: ["instance", "core"],
        NODE_TYPE.PHYSICAL_NIC: ["instance", "device"],
        NODE_TYPE.VIRTUAL_MACHINE: ["exported_instance"],
    }

    def __init__(self, tsdb_ip, tsdb_port):
        PrometheusAnnotation._validateIPAddress(common.PROMETHEUS_HOST)
        PrometheusAnnotation._validatePortNumber(common.PROMETHEUS_PORT)
        self.tsdb_ip = common.PROMETHEUS_HOST
        self.tsdb_port = common.PROMETHEUS_PORT
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
        except:
            LOG.debug("Exception in user code: \n{} {} {}".format(
                '-' * 60), traceback.print_exc(file=sys.stdout), '-' * 60)
        ret_val.set_index(keys='timestamp')
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
                        req = requests.get(full_request,
                                           timeout=3) # Cimarron.TIMEOUT) # ++++
                        if req.status_code == 200:
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
        res.sort(columns='timestamp', ascending=True)

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

                            values = result_metric['values']
                            LOG.debug("adding {}, size {} to dataframe".format(metric_name, len(values)) )

                            df = pandas.DataFrame(columns=('timestamp', metric_name))
                            df.set_index('timestamp')
                            timestamp = list()
                            metric = list()
                            for [ts, val] in values:
                                timestamp.append(ts)
                                metric.append(val)
                            df = pandas.DataFrame({'timestamp': timestamp,
                                                   metric_name: metric})
                            res = pandas.merge(res, df, how='outer', on='timestamp')
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

        if node_type in PrometheusAnnotation.NODE_METRICS:
            metrics = PrometheusAnnotation.NODE_METRICS[node_type]
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
        if node_type in PrometheusAnnotation.NODE_TO_METRIC_TAGS:
            tag_keys = PrometheusAnnotation.NODE_TO_METRIC_TAGS[node_type]

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
