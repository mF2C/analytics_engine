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

from analytics_engine.heuristics.beans.infograph import InfoGraphNodeType as NODE_TYPE

NODE_METRICS = {
    NODE_TYPE.PHYSICAL_DISK: [  # disk
        "node_disk_io_now", "node_disk_io_time_seconds_total",
        # to che check
        # "irate(node_disk_io_time_seconds_total[2S])",
        "node_disk_io_time_weighted_seconds_total", "node_disk_read_bytes_total",
        "node_disk_read_time_seconds_total", "node_disk_reads_completed_total",
        "node_disk_reads_merged_total", "node_disk_write_time_seconds_total",
        "node_disk_writes_completed_total", "node_disk_writes_merged_total",
        "node_disk_written_bytes_total"
    ],
    NODE_TYPE.PHYSICAL_PU: [
        "node_cpu_frequency_hertz", "node_cpu_frequency_max_hertz", "node_cpu_frequency_min_hertz",
        "node_cpu_guest_seconds_total", "node_cpu_package_throttles_total",
        "node_cpu_seconds_total"
    ],
    NODE_TYPE.PHYSICAL_NIC: [
        "node_arp_entries",
        "node_network_receive_bytes_total", "node_network_receive_compressed_total",
        "node_network_receive_drop_total", "node_network_receive_errs_total",
        "node_network_receive_fifo_total", "node_network_receive_frame_total",
        "node_network_receive_multicast_total", "node_network_receive_packets_total",
        "node_network_transmit_bytes_total", "node_network_transmit_carrier_total",
        "node_network_transmit_colls_total", "node_network_transmit_compressed_total",
        "node_network_transmit_drop_total", "node_network_transmit_errs_total",
        "node_network_transmit_fifo_total", "node_network_transmit_packets_total"
    ],
    NODE_TYPE.PHYSICAL_MACHINE: [ "node_arp_entries", "node_buddyinfo_blocks",
        "node_cpu_core_throttles_total", "node_disk_io_now",
        "node_disk_io_time_seconds_total","node_disk_io_time_weighted_seconds_total",
        "node_disk_read_bytes_total","node_disk_read_time_seconds_total",
        "node_disk_reads_completed_total","node_disk_reads_merged_total",
        "node_disk_write_time_seconds_total","node_disk_writes_completed_total",
        "node_disk_writes_merged_total","node_disk_written_bytes_total",
        "node_context_switches_total",
        "node_entropy_available_bits", "node_exporter_build_info",
        "node_filefd_allocated", "node_filefd_maximum",
        "node_filesystem_avail_bytes","node_filesystem_device_error",
        "node_filesystem_files","node_filesystem_files_free",
        "node_filesystem_free_bytes","node_filesystem_readonly",
        "node_filesystem_size_bytes",
        "node_procs_running", "net_conntrack_dialer_conn_attempted_total",
        "net_conntrack_dialer_conn_closed_total",
        "net_conntrack_dialer_conn_established_total", "net_conntrack_dialer_conn_failed_total",
                                                       "net_conntrack_listener_conn_accepted_total",
        "net_conntrack_listener_conn_closed_total", "node_boot_time_seconds",
        "node_forks_total", "node_hwmon_chip_names", "node_hwmon_sensor_label",
        "node_hwmon_temp_celsius", "node_hwmon_temp_crit_alarm_celsius",
        "node_hwmon_temp_crit_celsius", "node_hwmon_temp_max_celsius",
        "node_hwmon_power_average_interval_max_seconds", "node_hwmon_power_average_interval_min_seconds",
        "node_hwmon_power_average_interval_seconds", "node_hwmon_power_average_watt",
        "node_hwmon_power_is_battery_watt", "node_interrupts_total", "node_intr_total",
        "node_load1", "node_load15", "node_load5",
        "node_logind_sessions",
        "node_memory_numa_Active", "node_memory_numa_Active_anon", "node_memory_numa_Active_file",
        "node_memory_numa_AnonHugePages", "node_memory_numa_AnonPages", "node_memory_numa_Bounce",
        "node_memory_numa_Dirty", "node_memory_numa_FilePages", "node_memory_numa_HugePages_Free",
        "node_memory_numa_HugePages_Surp", "node_memory_numa_HugePages_Total", "node_memory_numa_Inactive",
        "node_memory_numa_Inactive_anon", "node_memory_numa_Inactive_file", "node_memory_numa_KernelStack",
        "node_memory_numa_Mapped", "node_memory_numa_MemFree", "node_memory_numa_MemTotal",
        "node_memory_numa_MemUsed", "node_memory_numa_Mlocked", "node_memory_numa_NFS_Unstable",
        "node_memory_numa_PageTables", "node_memory_numa_SReclaimable", "node_memory_numa_SUnreclaim",
        "node_memory_numa_Shmem", "node_memory_numa_Slab", "node_memory_numa_Unevictable",
        "node_memory_numa_Writeback", "node_memory_numa_WritebackTmp", "node_memory_numa_interleave_hit_total",
        "node_memory_numa_local_node_total", "node_memory_numa_numa_foreign_total", "node_memory_numa_numa_hit_total",
        "node_memory_numa_numa_miss_total", "node_memory_numa_other_node_total",

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

        "node_network_receive_bytes_total","node_network_receive_compressed_total",
        "node_network_receive_drop_total","node_network_receive_errs_total",
        "node_network_receive_fifo_total","node_network_receive_frame_total",
        "node_network_receive_multicast_total","node_network_receive_packets_total",
        "node_network_transmit_bytes_total","node_network_transmit_carrier_total",
        "node_network_transmit_colls_total","node_network_transmit_compressed_total",
        "node_network_transmit_drop_total","node_network_transmit_errs_total",
        "node_network_transmit_fifo_total","node_network_transmit_packets_total",

        "node_ntp_leap", "node_ntp_offset_seconds", "node_ntp_reference_timestamp_seconds",
        "node_ntp_root_delay_seconds", "node_ntp_root_dispersion_seconds", "node_ntp_rtt_seconds",
        "node_ntp_sanity", "node_ntp_stratum",

        # memory
        "node_memory_Active_anon_bytes",
        "node_memory_Active_bytes", "node_memory_Active_file_bytes",
        "node_memory_AnonHugePages_bytes", "node_memory_AnonPages_bytes",
        "node_memory_Bounce_bytes", "node_memory_Buffers_bytes", "node_memory_Cached_bytes",
        "node_memory_CmaFree_bytes", "node_memory_CmaTotal_bytes", "node_memory_CommitLimit_bytes",
        "node_memory_Committed_AS_bytes", "node_memory_DirectMap1G_bytes",
        "node_memory_DirectMap2M_bytes", "node_memory_DirectMap4k_bytes",
        "node_memory_Dirty_bytes", "node_memory_HardwareCorrupted_bytes",
        "node_memory_HugePages_Free", "node_memory_HugePages_Rsvd", "node_memory_HugePages_Surp",
        "node_memory_HugePages_Total", "node_memory_Hugepagesize_bytes",
        "node_memory_Inactive_anon_bytes", "node_memory_Inactive_bytes",
        "node_memory_Inactive_file_bytes", "node_memory_KernelStack_bytes",
        "node_memory_Mapped_bytes", "node_memory_MemAvailable_bytes", "node_memory_MemFree_bytes",
        "node_memory_MemTotal_bytes", "node_memory_Mlocked_bytes",
        "node_memory_NFS_Unstable_bytes", "node_memory_PageTables_bytes",
        "node_memory_SReclaimable_bytes", "node_memory_SUnreclaim_bytes",
        "node_memory_ShmemHugePages_bytes", "node_memory_ShmemPmdMapped_bytes",
        "node_memory_Shmem_bytes", "node_memory_Slab_bytes", "node_memory_SwapCached_bytes",
        "node_memory_SwapFree_bytes", "node_memory_SwapTotal_bytes",
        "node_memory_Unevictable_bytes", "node_memory_VmallocChunk_bytes",
        "node_memory_VmallocTotal_bytes", "node_memory_VmallocUsed_bytes",
        "node_memory_WritebackTmp_bytes", "node_memory_Writeback_bytes",

        "node_nf_conntrack_entries", "node_nf_conntrack_entries_limit", "node_procs_blocked",

        "node_qdisc_bytes_total", "node_qdisc_drops_total", "node_qdisc_overlimits_total",
        "node_qdisc_packets_total", "node_qdisc_requeues_total",
        "node_scrape_collector_duration_seconds",
        "node_scrape_collector_success", "node_sockstat_FRAG_inuse", "node_sockstat_FRAG_memory",
        "node_sockstat_RAW_inuse", "node_sockstat_TCP_alloc", "node_sockstat_TCP_inuse",
        "node_sockstat_TCP_mem", "node_sockstat_TCP_mem_bytes", "node_sockstat_TCP_orphan",
        "node_sockstat_TCP_tw", "node_sockstat_UDPLITE_inuse", "node_sockstat_UDP_inuse",
        "node_sockstat_UDP_mem", "node_sockstat_UDP_mem_bytes", "node_sockstat_sockets_used",
        "node_tcp_connection_states",
        "node_textfile_scrape_error", "node_time_seconds", "node_timex_estimated_error_seconds",
        "node_timex_frequency_adjustment_ratio", "node_timex_loop_time_constant",
        "node_timex_maxerror_seconds", "node_timex_offset_seconds",
        "node_timex_pps_calibration_total", "node_timex_pps_error_total",
        "node_timex_pps_frequency_hertz", "node_timex_pps_jitter_seconds",
        "node_timex_pps_jitter_total", "node_timex_pps_shift_seconds",
        "node_timex_pps_stability_exceeded_total", "node_timex_pps_stability_hertz",
        "node_timex_status", "node_timex_sync_status", "node_timex_tai_offset_seconds",
        "node_timex_tick_seconds", "node_uname_info", "node_vmstat_pgfault",
        "node_vmstat_pgmajfault", "node_vmstat_pgpgin", "node_vmstat_pgpgout", "node_vmstat_pswpin",
        "node_vmstat_pswpout", "process_cpu_seconds_total", "process_max_fds",
        "process_open_fds", "process_resident_memory_bytes", "process_start_time_seconds",
        "process_virtual_memory_bytes"
    ],
    # NODE_TYPE.VIRTUAL_MACHINE: ["node_procs_running"],  # "node_filesystem_files"]
    # NODE_TYPE.VIRTUAL_NIC: ["net_conntrack_dialer_conn_attempted_total"] # same metrics

    NODE_TYPE.VIRTUAL_MACHINE: [
        "libvirt_block_stats_errors_number",
        "libvirt_block_stats_read_bytes",
        "libvirt_block_stats_read_requests_issued",
        "libvirt_block_stats_write_bytes",
        "libvirt_block_stats_write_requests_issued",
        "libvirt_cpu_stats_cpu_time_nanosecs",
        "libvirt_cpu_stats_system_time_nanosecs",
        "libvirt_cpu_stats_user_time_nanosecs",
        "libvirt_interface_read_bytes",
        "libvirt_interface_read_drops",
        "libvirt_interface_read_errors",
        "libvirt_interface_read_packets",
        "libvirt_interface_write_bytes",
        "libvirt_interface_write_drops",
        "libvirt_interface_write_errors",
        "libvirt_interface_write_packets",
        "libvirt_mem_stats_actual",
        "libvirt_mem_stats_available",
        "libvirt_mem_stats_last_update",
        "libvirt_mem_stats_major_fault",
        "libvirt_mem_stats_minor_fault",
        "libvirt_mem_stats_rss",
        "libvirt_mem_stats_swap_in",
        "libvirt_mem_stats_swap_out",
        "libvirt_mem_stats_used",
        "libvirt_mem_stats_usable"
    ]
}

NODE_TO_METRIC_TAGS = {
    NODE_TYPE.PHYSICAL_DISK: ["instance", "device"],
    NODE_TYPE.PHYSICAL_PU: ["instance", "cpu"],
    NODE_TYPE.PHYSICAL_NIC: ["instance", "device"],
    NODE_TYPE.VIRTUAL_MACHINE: ["domain"]
}
