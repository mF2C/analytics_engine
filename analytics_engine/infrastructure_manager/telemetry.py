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

"""
Telemetry base class and factory.
"""
from abc import abstractmethod
from abc import ABCMeta
import threading
import shutil
import json
import time
import sys
import os
import requests
import pandas as pd
from config_helper import ConfigHelper
from snap import Snap
import analytics_engine.common as common

LOG = common.LOG


def get_telemetry(telemetry=None, host=None, port=None):
    """
    Factory function which returns a telemetry class either using the arguments
    provided or from a configuration file.
    :param telemetry: The string name of the telemetry class to return.
    :param host: IP of the telemetry server.
    :param port: Port for the telemetry server
    :return: A telemetry class derived from the Telemetry abstract class.
    """
    if not telemetry:
        telemetry = ConfigHelper.get("DEFAULT", "telemetry")

    if telemetry == "snap":
        LOG.debug('snap telemetry')
        host = ConfigHelper.get('SNAP', 'host')
        port = ConfigHelper.get('SNAP', 'port')
        user = ConfigHelper.get('SNAP', 'user')
        password = ConfigHelper.get('SNAP', 'password')
        dbname = ConfigHelper.get('SNAP', 'dbname')
        return Snap(host, port, user, password, dbname)
    elif telemetry == "prometheus":
        LOG.debug('prometheus telemetry')
        host = ConfigHelper.get('PROMETHEUS', 'PROMETHEUS_HOST')
        port = ConfigHelper.get('PROMETHEUS', 'PROMETHEUS_PORT')
        return (host, port)
    else:
        msg = "No telemetry class for the type: {}".format(telemetry)
        raise AttributeError(msg)


class Telemetry(object):
    """
    Abstract class for Telemetry.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_apexlake_metrics(self, period=600):
        """
        Grabs the current Apexlake metrics for all nodes being actively
        monitored. The period of time that the metrics are returned depends on
        the 'period' parameter.  This says how many seconds of metrics should
        be retrieved.
        :param seconds: How many seconds of metrics should be retrieved.
        retrieved.
        :return: Returns a dictionary of utilisation and saturation values for
        every node ordered by the node MAC address.  The format of the returned
        dictionary is :
        {"MAC":{"storage_saturation": [("timestamp_1", value),
        ("timestamp_2", value), ...], "network_saturation": [...}}
        """

    @abstractmethod
    def get_metric(self, metric_name, filters, start_time, end_time):
        """
        Returns metric values for the times between start_time and end_time.
        Specifics of where and how to get the metric is specified by the
        filters dictionary.

        :param metric_name: Name of the metric.
        :param filters:  A dictionary of filter terms and values.
        :param start_time: A start time.
        :param end_time: An end time.
        :returns: Dictionary containing metric data.
        """

    @abstractmethod
    def get_metrics(self, metric_names, filters, start_time, end_time):
        """
        Returns metric values for each metric in the metric names list.  The
        time period for the metrics is specified using the start_time and
        end_time parameters. Specifics of where ard how to get the metric is
        specified by the filters dictionary.

        :param metric_names: Array of metric names.
        :param filters: A dictionary of filter terms and values.
        :param start_time: A start time.
        :param end_time: An end time.
        :returns: Dictionary containing metric data.
        """




# TODO: Clarify this method.
def persist_to_disk(a_metrics, s_path, s_id, tag_name, tag_value):
    '''
    Persist metrics to disk
    :param a_metrics:
    :param s_path:
    :param s_id:
    :param tag_name:
    :param tag_value:
    :return:
    '''
    # TODO: ARFF output
    LOG.info("Work In Progress - WIP")
    # sId => hostname/IP etc.
    # Checking path
    # Will be removed -> for creating an index
    if tag_name is not None:
        LOG.info("Tag name - " + tag_name)
    if tag_value is not None:
        LOG.info("Tag value - " + tag_value)
    if not os.path.exists(s_path):
        LOG.error("Path does not exist - " + str(s_path))
        return None
    LOG.info("Id - " + str(s_id))
    LOG.info("Metrics len:  " + str(len(a_metrics)))
    if len(a_metrics) == 0:
        return None
    d_data = {}
    s_metric_separator = "_"
    a_metric_names = []
    for s_item in a_metrics:
        # dps contains the actual time series data
        d_dps = s_item["dps"]
        metric = s_item["metric"]
        metric = metric.replace(".", s_metric_separator)
        s_file_name = metric
        d_tags = s_item["tags"]
        if tag_name is not None:
            metric += s_metric_separator
        for s_time_stamp in d_dps:
            i_time_stamp = int(s_time_stamp)
            if tag_name is not None:
                s_metric_name = metric + d_tags["type"]
            else:
                s_metric_name = metric

            if s_metric_name not in a_metric_names:
                a_metric_names.append(s_metric_name)
            #
            if i_time_stamp in d_data:
                d_data[i_time_stamp][s_metric_name] = d_dps[s_time_stamp]
            else:
                # We create a new row of data
                d_data[i_time_stamp] = {}
                d_data[i_time_stamp][s_metric_name] = d_dps[s_time_stamp]
                # And include the tag
                # This tag is non-numeric

    # We add the tag to the metric names list
    # This tag is non-numeric
    # a_metric_names.append(tag_name)
    # If We have have no data, fail very loudly
    try:
        #
        a_metric_names = sorted(a_metric_names)
        # Add to configuration
        s_header = "timestamp"
        if s_id is None:
            s_id = ""
        else:
            s_id = str(s_id)
            s_id = s_id.strip()
        if len(s_id) != 0:
            s_file_name = s_id + '-' + s_file_name
        LOG.info("Full FileName for  metric - " + s_file_name)

        s_full_path = s_path + os.sep + s_file_name + ".csv"
        LOG.info("Full Path - " + s_full_path)
        csv_file = open(s_full_path, 'w')
        # ARRF option could go here
        for s_metric_name in a_metric_names:
            s_header = s_header + "," + s_metric_name
        csv_file.write(s_header + "\n")
        for i_time_stamp in d_data:
            s_log_line = str(i_time_stamp)
            for s_metric_name in a_metric_names:
                if s_metric_name in d_data[i_time_stamp]:
                    s_log_line = s_log_line + "," + \
                                 str(d_data[i_time_stamp][s_metric_name])
                else:
                    s_log_line += ",0"
            csv_file.write(s_log_line + "\n")
        csv_file.flush()
        csv_file.close()

        # We calculate the summ. stats
        timestamp_col = 0
        data_frame = pd.read_csv(s_full_path,
                                 infer_datetime_format=True,
                                 parse_dates=[timestamp_col],
                                 index_col=timestamp_col)

        summary_stats_metrics = dict()
        columns = list(data_frame.columns.values)
        for column_name in columns:
            summary_stats = dict()
            series = data_frame[column_name].describe()
            # pandas.core.series.Series
            for index_name in series.index:
                # TODO: fix constants
                summary_stats[index_name] = series[index_name]
            summary_stats_metrics[column_name] = summary_stats
        summary_stats_path = os.path.join(s_path,
                                          s_file_name + '-summ.json')
        LOG.info('#####')
        LOG.info('Summary stats')
        LOG.info('Path - ' + summary_stats_path)
        file_handler = open(summary_stats_path, 'w')
        file_handler.write(json.dumps(summary_stats_metrics))
        file_handler.close()
        return s_full_path
    except IOError:
        full_tb = sys.exc_info()
        LOG.error(full_tb)
        LOG.error('line number - ' + str(full_tb[2].tb_lineno))
        LOG.error('Probably there is no data available for these metrics')
        if len(a_metrics) == 0:
            LOG.error("List of metrics is empty: " + str(len(a_metrics)))
        return None


class TimeseriesGraphWorker(threading.Thread):
    """
    Executes parallel queries to cimarron and saves the results as separate
    images.
    """
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, verbose=None):
        threading.Thread.__init__(self, group=group, target=target, name=name,
                                  verbose=verbose)
        self.args = args
        self.kwargs = kwargs
        self.result = None

    def run(self):
        full_request = self.kwargs['full_request']
        metric_name = self.kwargs['metric_name']
        output_dir = self.kwargs['output_dir']
        retries = self.kwargs['RETRIES']
        timeout = self.kwargs['TIMEOUT']

        output_file = None
        query_latency = None
        query_num_bytes = None
        while retries > 0:
            try:
                start_time = time.time()
                req = requests.get(full_request, timeout=timeout, stream=True)
                if req.status_code == 200:
                    image_name = metric_name + '.png'
                    output_file = os.path.join(output_dir, image_name)
                    with open(output_file, 'wb') as file_handler:
                        shutil.copyfileobj(req.raw, file_handler)

                    # Size in bytes
                    # latency  value in milliseconds (*1000.0god g)
                    query_latency = round((time.time() - start_time) * 1000.0,
                                          2)
                    query_num_bytes = len(req.content)
                else:
                    LOG.error("Could not retrieve - " + full_request)
                    # There was some error, we set the output_file to None
                break
            except requests.exceptions.RequestException as exc:
                LOG.error(exc)
                retries -= 1
                LOG.error("Failed to get metric - " + metric_name)
                LOG.error("Trying again. Attempt number: %s", str(retries))
                # There was some error, we set the output_file to None

        self.result = dict()
        self.result['metric_name'] = metric_name
        self.result['full_request'] = full_request
        self.result['output_file'] = output_file
        self.result['query_latency'] = query_latency
        self.result['query_num_bytes'] = query_num_bytes
