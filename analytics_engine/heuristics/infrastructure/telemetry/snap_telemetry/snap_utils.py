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

import pandas
from analytics_engine.heuristics.beans.infograph import InfoGraphNode
from analytics_engine import common

LOG = common.LOG

class SnapUtils(object):

    @staticmethod
    def annotate_machine_pu_util(internal_graph, node):
        source = InfoGraphNode.get_machine_name_of_pu(node)
        machine = InfoGraphNode.get_node(internal_graph, source)
        machine_util = InfoGraphNode.get_compute_utilization(machine)
        if 'intel/use/compute/utilization' not in machine_util.columns:
            sum_util = None
            cpu_metric = 'intel/procfs/cpu/utilization_percentage'
            pu_util_df = InfoGraphNode.get_compute_utilization(node)
            if cpu_metric in pu_util_df.columns:
                pu_util = pu_util_df[cpu_metric]
                pu_util = pu_util.fillna(0)
                machine_util[InfoGraphNode.get_attributes(node)['name']] = pu_util
                InfoGraphNode.set_compute_utilization(machine, machine_util)
            else:
                LOG.info('CPU util not Found use for node {}'.format(InfoGraphNode.get_name(node)))
        else:
            LOG.debug('Found use for node {}'.format(InfoGraphNode.get_name(node)))

    @staticmethod
    def annotate_machine_disk_util(internal_graph, node):
        source = InfoGraphNode.get_attributes(node)['allocation']
        machine = InfoGraphNode.get_node(internal_graph, source)
        machine_util = InfoGraphNode.get_disk_utilization(machine)
        if 'intel/use/disk/utilization' not in machine_util.columns:
            disk_metric = 'intel/procfs/disk/utilization_percentage'
            disk_util_df = InfoGraphNode.get_disk_utilization(node)
            if disk_metric in disk_util_df.columns:
                disk_util = disk_util_df[disk_metric]
                disk_util = disk_util.fillna(0)
                machine_util[InfoGraphNode.get_attributes(node)['name']] = disk_util
                InfoGraphNode.set_disk_utilization(machine, machine_util)
            else:
                LOG.info('Disk util not Found use for node {}'.format(InfoGraphNode.get_name(node)))
        else:
            LOG.debug('Found use disk for node {}'.format(InfoGraphNode.get_name(node)))

    @staticmethod
    def annotate_machine_network_util(internal_graph, node):
        source = InfoGraphNode.get_attributes(node)['allocation']
        machine = InfoGraphNode.get_node(internal_graph, source)
        machine_util = InfoGraphNode.get_network_utilization(machine)
        if 'intel/use/network/utilization' not in machine_util.columns:
            net_metric = 'intel/psutil/net/utilization_percentage'
            net_util_df = InfoGraphNode.get_network_utilization(node)
            if net_metric in net_util_df.columns:
                net_util = net_util_df[net_metric]
                net_util = net_util.fillna(0)
                machine_util[InfoGraphNode.get_attributes(node)['name']] = net_util
                InfoGraphNode.set_network_utilization(machine, machine_util)
            else:
                LOG.info('Net util not Found use for node {}'.format(InfoGraphNode.get_name(node)))
        else:
            LOG.debug('Found use network for node {}'.format(InfoGraphNode.get_name(node)))

    @staticmethod
    def utilization(internal_graph, node, telemetry):
        # machine usage
        telemetry_data = telemetry.get_data(node)
        if 'intel/use/compute/utilization' in telemetry_data:
            InfoGraphNode.set_compute_utilization(node,
                                                  pandas.DataFrame(telemetry_data['intel/use/compute/utilization'],
                                                                   columns=['intel/use/compute/utilization']))
        # pu usage
        if 'intel/procfs/cpu/utilization_percentage' in telemetry_data:
                InfoGraphNode.set_compute_utilization(node,
                                                      pandas.DataFrame(
                                                          telemetry_data['intel/procfs/cpu/utilization_percentage'],
                                                          columns=['intel/procfs/cpu/utilization_percentage']))
        if 'intel/use/memory/utilization' in telemetry_data:
            InfoGraphNode.set_memory_utilization(node, pandas.DataFrame(telemetry_data['intel/use/memory/utilization']))
        if 'intel/use/disk/utilization' in telemetry_data:
            InfoGraphNode.set_disk_utilization(node, pandas.DataFrame(telemetry_data['intel/use/disk/utilization']))
        if 'intel/use/network/utilization' in telemetry_data:
            InfoGraphNode.set_network_utilization(node,
                                                  pandas.DataFrame(telemetry_data['intel/use/network/utilization']))
        # supporting not available /use/ metrics

        if 'intel/procfs/meminfo/mem_total' in telemetry_data and 'intel/procfs/meminfo/mem_used' in telemetry_data:
            # LOG.info('Found memory utilization procfs')
            mem_used = telemetry_data['intel/procfs/meminfo/mem_used'].fillna(0)
            mem_total = telemetry_data['intel/procfs/meminfo/mem_total'].fillna(0)
            mem_util = mem_used * 100 / mem_total
            mem_util.name = 'intel/procfs/memory/utilization_percentage'
            InfoGraphNode.set_memory_utilization(node, pandas.DataFrame(mem_util))
        if 'intel/procfs/disk/io_time' in telemetry_data:
            io_time = telemetry_data['intel/procfs/disk/io_time'].fillna(0)
            disk_util = io_time*100/1000
            disk_util.name = 'intel/procfs/disk/utilization_percentage'
            InfoGraphNode.set_disk_utilization(node, pandas.DataFrame(disk_util))
        if 'intel/psutil/net/bytes_recv' in telemetry_data and 'intel/psutil/net/bytes_sent' in telemetry_data:
            source=telemetry._source(node)
            machine = InfoGraphNode.get_node(internal_graph, source)
            nic_speed = InfoGraphNode.get_nic_speed_mbps(machine) * 1000000
            net_data = telemetry_data.filter(['timestamp', 'intel/psutil/net/bytes_recv','intel/psutil/net/bytes_sent'], axis=1)
            net_data.fillna(0)
            net_data['intel/psutil/net/bytes_total'] = net_data['intel/psutil/net/bytes_recv']+net_data['intel/psutil/net/bytes_sent']
            net_data_interval = net_data.set_index('timestamp').diff()
            net_data_interval['intel/psutil/net/utilization_percentage'] = net_data_interval['intel/psutil/net/bytes_total'] * 100 /nic_speed
            net_data_pct = pandas.DataFrame(net_data_interval['intel/psutil/net/utilization_percentage'])
            InfoGraphNode.set_network_utilization(node, net_data_pct)
        if 'intel/docker/stats/cgroups/cpu_stats/cpu_usage/total' in telemetry_data:
            # Container node
            #cpu util
            cpu_data = telemetry_data.filter(['timestamp', 'intel/docker/stats/cgroups/cpu_stats/cpu_usage/total'], axis=1)
            cpu_data_interval = cpu_data.set_index('timestamp').diff()
            #util data in nanoseconds
            cpu_data_interval['intel/docker/stats/cgroups/cpu_stats/cpu_usage/percentage'] = cpu_data_interval['intel/docker/stats/cgroups/cpu_stats/cpu_usage/total'] / 10000000
            cpu_data_pct = pandas.DataFrame(cpu_data_interval['intel/docker/stats/cgroups/cpu_stats/cpu_usage/percentage'])
            InfoGraphNode.set_compute_utilization(node, cpu_data_pct)
        if "intel/docker/stats/cgroups/memory_stats/usage/usage" in telemetry_data:
            #container mem util
            source=telemetry._source(node)
            machine = InfoGraphNode.get_node(internal_graph, source)
            local_mem = int(InfoGraphNode.get_attributes(machine).get("local_memory"))
            mem_data = telemetry_data.filter(['timestamp', "intel/docker/stats/cgroups/memory_stats/usage/usage"], axis=1)
            mem_data["intel/docker/stats/cgroups/memory_stats/usage/percentage"] = mem_data["intel/docker/stats/cgroups/memory_stats/usage/usage"]/local_mem * 100
            mem_data_pct = pandas.DataFrame(mem_data["intel/docker/stats/cgroups/memory_stats/usage/percentage"])
            InfoGraphNode.set_memory_utilization(node, mem_data_pct)
        if "intel/docker/stats/network/tx_bytes" in telemetry_data:
            #container network util
            source=telemetry._source(node)
            machine = InfoGraphNode.get_node(internal_graph, source)
            nic_speed = InfoGraphNode.get_nic_speed_mbps(machine) * 1000000
            net_data = telemetry_data.filter(['timestamp', "intel/docker/stats/network/tx_bytes","intel/docker/stats/network/rx_bytes"], axis=1)
            net_data.fillna(0)
            net_data['intel/docker/stats/network/bytes_total'] = net_data["intel/docker/stats/network/tx_bytes"]+net_data["intel/docker/stats/network/rx_bytes"]
            net_data_interval = net_data.set_index('timestamp').diff()
            net_data_interval['intel/docker/stats/network/utilization_percentage'] = net_data_interval['intel/docker/stats/network/bytes_total'] * 100 /nic_speed
            net_data_pct = pandas.DataFrame(net_data_interval['intel/docker/stats/network/utilization_percentage'])
            InfoGraphNode.set_network_utilization(node, net_data_pct)
        if "intel/docker/stats/cgroups/blkio_stats/io_time_recursive/value" in telemetry_data:
            #container disk util
            disk_data = telemetry_data.filter(['timestamp', "intel/docker/stats/cgroups/blkio_stats/io_time_recursive/value"], axis=1)
            disk_data_interval = disk_data.set_index('timestamp').diff()
            #util data in milliseconds
            disk_data_interval["intel/docker/stats/cgroups/blkio_stats/io_time_recursive/percentage"] = \
                disk_data_interval["intel/docker/stats/cgroups/blkio_stats/io_time_recursive/value"] / 1000000
            disk_data_pct = pandas.DataFrame(disk_data_interval["intel/docker/stats/cgroups/blkio_stats/io_time_recursive/percentage"])
            InfoGraphNode.set_disk_utilization(node, disk_data_pct)


    @staticmethod
    def saturation(internal_graph, node, telemetry):
        telemetry_data = telemetry.get_data(node)
        if 'intel/use/compute/saturation' in telemetry_data:
            InfoGraphNode.set_compute_saturation(node,
                                                 pandas.DataFrame(telemetry_data['intel/use/compute/saturation']))
        if 'intel/use/memory/saturation' in telemetry_data:
            InfoGraphNode.set_memory_saturation(node, pandas.DataFrame(telemetry_data['intel/use/memory/saturation']))
        if 'intel/use/disk/saturation' in telemetry_data:
            InfoGraphNode.set_disk_saturation(node, pandas.DataFrame(telemetry_data['intel/use/disk/saturation']))
        if 'intel/use/network/saturation' in telemetry_data:
            InfoGraphNode.set_network_saturation(node,
                                                 pandas.DataFrame(telemetry_data['intel/use/network/saturation']))
