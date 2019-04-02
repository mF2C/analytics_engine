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

from analytics_engine.heuristics.beans.infograph import InfoGraphNodeType as NODE_TYPE

# refactored from snap_graph_telemetry
NODE_METRICS = {NODE_TYPE.PHYSICAL_DISK: ["intel/iostat/device/",
                                          "intel/procfs/disk/"],
                NODE_TYPE.PHYSICAL_PU: ["intel/proc/schedstat/cpu/",
                                        "intel/procfs/cpu/"],
                NODE_TYPE.PHYSICAL_NIC: ["intel/net",
                                         "intel/psutil/net/",
                                         "intel/procfs/iface/",
                                         "intel/use/network/"],
                NODE_TYPE.PHYSICAL_MACHINE: ["intel/iostat/avg-cpu/",
                                             "intel/psutil/net/all/",
                                             "intel/psutil/vm/",
                                             "intel/procfs/load/",
                                             "intel/procfs/meminfo/",
                                             # "intel/procfs/processes/",
                                             "intel/procfs/swap/all/",
                                             "intel/procfs/swap/io/",
                                             "intel/psutil/cpu/cpu-total/",
                                             "intel/psutil/load/",
                                             "intel/libvirt/",
                                             "intel/libvirtuse/cpu/utilization",
                                             "intel/use/compute/",
                                             "intel/rdt/",
                                             "intel/use/memory"],
                NODE_TYPE.VIRTUAL_MACHINE: ["intel/iostat/avg-cpu/",
                                            "intel/psutil/net/all/",
                                            "intel/psutil/vm/",
                                            "intel/procfs/load/",
                                            "intel/procfs/meminfo/",
                                            "intel/procfs/processes/",
                                            "intel/procfs/swap/all/",
                                            "intel/procfs/swap/io/",
                                            "intel/psutil/cpu/cpu-total/",
                                            "intel/psutil/load/",
                                            "intel/use/compute/",
                                            "intel/use/memory"],
                NODE_TYPE.INSTANCE_DISK: ["intel/libvirt/disk/"],
                NODE_TYPE.DOCKER_CONTAINER: ["intel/docker/stats/cgroups/cpu_stats/cpu_usage/total",
                                             "intel/docker/stats/cgroups/memory_stats/usage/usage",
                                             "intel/docker/stats/network/tx_bytes",
                                             "intel/docker/stats/network/rx_bytes",
                                             "intel/docker/stats/cgroups/blkio_stats/io_time_recursive/value"]}

METRIC_TAGS = [("intel/iostat/device/", ["device_id", "source"]),
               ("intel/iostat/avg-cpu/", ["source"]),
               ("intel/net/", ["source"]),
               ("intel/proc/schedstat/cpu/", ["source", "cpu_id"]),
               ("intel/procfs/cpu/", ["source", "cpuID"]),
               ("intel/procfs/disk/", ["source", "disk"]),
               ("intel/procfs/filesystem/", ["source", "filesystem"]),
               ("intel/procfs/iface/", ["source", "hardware_addr"]),
               ("intel/procfs/load/", ["source"]),
               ("intel/procfs/meminfo/", ["source"]),
               ("intel/procfs/processes/", ["source"]),
               ("intel/procfs/swap/all/", ["source"]),
               ("intel/procfs/swap/io/", ["source"]),
               # ("intel/procfs/swap/device/", ["source", "device"]),  # TODO:  Check if only for LVM.
               ("intel/psutil/cpu/cpu-total/", ["source"]),
               ("intel/psutil/cpu/", ["source", "cpu_id"]),
               ("intel/psutil/load/", ["source"]),
               ("intel/psutil/net/all/", ["source"]),
               ("intel/psutil/net/", ["source", "interface_name"]),
               ("intel/rdt/capabilities/", ["source"]), # only source tag!!!
               ("intel/rdt/llc_occupancy", ["source", "core_id"]),
               ("intel/rdt/memory_bandwidth", ["source", "core_id"]),
               ("odl/switch/", ["source"]),
               ("intel/use/compute/", ["source"]),
               ("intel/use/network/", ["source", "dev_id"]),
               ("intel/use/disk/", ["source", "dev_id"]),
               ("intel/use/memory/", ["source"]),
               ("intel/libvirtuse/cpu/utilization", ["source", "nova_uuid"]),
               ("intel/libvirt/disk/", ["source", "nova_uuid", "device_name"]),
               ("intel/libvirt/cpu/", ["source", "nova_uuid", "cpu_id"]),
               ("intel/libvirt/memory/", ["source", "nova_uuid"]),
               ("intel/psutil/vm/", ["source"]),
               # no support from the landscaper on network_interface, ignoring this ATM
               # just supporting retrieval by source/nova_uuid(network interface)
               # add "network_interface" once supported
               ("intel/libvirt/network/", ["source", "nova_uuid"]),
               ("intel/docker/stats/cgroups/cpu_stats/cpu_usage/total", ["docker_id", "source"]),
               ("intel/docker/stats/cgroups/memory_stats/usage/usage", ["docker_id", "source"]),
               ("intel/docker/stats/network/tx_bytes", ["docker_id", "source"]),
               ("intel/docker/stats/network/rx_bytes", ["docker_id", "source"]),
               ("intel/docker/stats/cgroups/blkio_stats/io_time_recursive/value", ["docker_id", "source"])
               ]