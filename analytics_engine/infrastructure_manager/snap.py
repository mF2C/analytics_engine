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
Snap telemetry module.
"""
from time import time
import influxdb
from snapclient.extract import Extract
import analytics_engine.common as common

LOG = common.LOG


class Snap(object):
    """
    Snap telemetry retrieval class.
    """
    def __init__(self, host, port, username, password, db_name):
        # TODO: Remove Influxdb client.
        self.influxdbclient = influxdb.InfluxDBClient(host, port, username,
                                                      password, db_name)

    def get_metric(self, metric, start=0, end=None, tags=None,
                   all_tags=False):
        """
        Retrieves a list data points for a metric between the start and end
        time specified.
        :param metric: Name of the metric to retrieve.
        :param start: Start time in milliseconds.
        :param end:  End time in milliseconds.
        :param tags: A dictionary of tags, used to refine the query for metric
        data.
        :param all_tags: Flag, if set to true all tags are returned in the
        results, if set to False then just the timestamp & value are returned.
        :return: Metric data.
        """
        end = end or time()
        grouping = {"time(1s)"}
        snap = Extract(db_client=self.influxdbclient, measurement_name=metric,
                       start_date=start, end_date=end, tags=tags,
                       grouping=grouping, output_json=True)
        result = snap.retrieve_date_range()
        if all_tags:
            return list(result)
        return [(m["time"], m["value"]) for m in result]

    def get_last_metric(self, metric, tags=None, with_tags=False):
        """
        Retrieves the last metric value.
        :param metric: Name of the metric to retrieve.
        :param tags: A dictionary of tags, used to refine the query.
        :param with_tags: Flag, if set to true all tags are returned, if not
        then just the last value is returned.
        :return: Last metric.
        """
        snap = Extract(db_client=self.influxdbclient, measurement_name=metric,
                       tags=tags)

        if with_tags:
            result = snap.retrieve_last_with_tags()
            if result:
                return result[0]
        else:
            result = snap.retrieve_last_datapoint()
            if result:
                return result[0]["last_value"]
        return None

    def get_relative_metric(self, metric, duration, tags=None):
        """
        Retrieves a metric using a relative duration, from the current time. If
        the duration is set to '10m', then the last 10 minutes of metrics are
        retrieved. The duration can be set as u for microseconds, s for
        seconds, m for minutes, h for hours, d for days and w for weeks.
        If no suffix is given the value is interpreted as microseconds.
        :param metric: Name of the metric to retrieve.
        :param duration: The relative duration.
        :param tags: A dictionary of tags, used to refine the query.
        :return: List of (time, value) tuples.
        """
        snap = Extract(db_client=self.influxdbclient, measurement_name=metric,
                       tags=tags, relative_duration=duration)
        result = snap.retrieve_relative()
        return [(m["time"], m["value"]) for m in result]

    def get_mean_metric(self, metric, duration, tags=None):
        """
        Retrieves the mean value for a given metric over the duration
        specified. Duration is relative,
        :param metric: Name of the metric to retrieve.
        :param duration: The relative duration.
        :param tags: A dictionary of tags, used to refine the query.
        :return: Mean value.
        """
        snap = Extract(db_client=self.influxdbclient, measurement_name=metric,
                       tags=tags, relative_duration=duration,
                       mean_metric="value")
        result = list(snap.retrieve_mean())
        if result:
            return result[0]["mean"]
        return None

    def get_utilisation(self, util_type, host, start=0, end=None, tags=None):
        """
        Retrieve the utilisation from the 'USE' metrics.
        :param util_type:  The type of USE metric, such as 'network'.
        :param host: The machine/instance to be queried.
        :param start: Start Time of retrieval duration. Seconds from epoch.
        :param end: End of of retrieval duration. Seconds from epoch.
        :param tags: A dictionary of tags, used to refine the query.
        :return: List of (time, value) tuples.
        """
        end = end or time()
        return self._get_util_sat_metric("utilization", util_type, host, tags,
                                         start=start, end=end)

    def get_last_utilisation(self, util_type, host, tags=None):
        """
        Retrieves the last utilisation metric for a give utilisation type.
        :param util_type: The type of USE metric, such as 'network'.
        :param host: The machine/instance to be queried.
        :param tags: A dictionary of tags, used to refine the query.
        :return: Returns the last utilisation metric.
        """
        return self._get_util_sat_metric("utilization", util_type, host, tags)

    def get_relative_utilisation(self, util_type, host, duration, tags=None):
        """
        Retrieve the utilisation from the 'USE' metrics using relative
        duration.
        :param util_type:  The type of USE metric, such as 'network'.
        :param host: The machine/instance to be queried.
        :param duration: The relative duration.
        :param tags: A dictionary of tags, used to refine the query.
        :return: List of (time, value) tuples.
        """
        return self._get_util_sat_metric("utilization", util_type, host, tags,
                                         duration=duration)

    def get_saturation(self, sat_type, host, start=0, end=None, tags=None):
        """
        Retrieve the saturation from the 'USE' metrics.
        :param sat_type:  The type of USE metric, such as 'network'.
        :param host: The machine/instance to be queried.
        :param start: Start Time of retrieval duration. Seconds from epoch.
        :param end: End of of retrieval duration. Seconds from epoch.
        :param tags: A dictionary of tags, used to refine the query.
        :return: List of (time, value) tuples.
        """
        end = end or time()
        return self._get_util_sat_metric("saturation", sat_type, host, tags,
                                         start=start, end=end)

    def get_last_saturation(self, sat_type, host, tags=None):
        """
        Retrieves the last saturation metric for a given saturation type.
        :param sat_type: The type of USE metric, such as 'network'.
        :param host: The machine/instance to be queried.
        :param tags: A dictionary of tags, used to refine the query.
        :return: Returns the last saturation metric.
        """
        return self._get_util_sat_metric("saturation", sat_type, host, tags)

    def get_relative_saturation(self, sat_type, host, duration, tags=None):
        """
        Retrieve the saturation from the 'USE' metrics using relative
        duration.
        :param sat_type: The type of USE metric, such as 'network'.
        :param host: The machine/instance to be queried.
        :param duration: The relative duration.
        :param tags: A dictionary of tags, used to refine the query.
        :return: List of (time, value) tuples.
        """
        return self._get_util_sat_metric("saturation", sat_type, host, tags,
                                         duration=duration)

    def get_mean_utilisation(self, util_type, duration, host, tags=None):
        """
        Retrieve the mean utilisation value for a given utilisation type, such
        as 'network'.
        :param util_type: The type of USE metric, such as 'network'.
        :param duration: The relative duration.
        :param host: The machine/instance to be queried.
        :param tags: A dictionary of tags, used to refine the query.
        :return: Mean utilisation value.
        """
        metric = "intel/use/{}/utilization".format(util_type)
        tags = tags or {}
        tags["source"] = host
        return self.get_mean_metric(metric, duration, tags)

    def get_percentage_saturated(self, sat_type, host, duration, threshold=1,
                                 tags=None):
        """
        Returns how saturated a given saturated type is.
        :param sat_type:  The type of USE metric, such as 'network'.
        :param host: The machine/instance to be queried.
        :param duration: The relative duration.
        :param threshold: Threshold which identify a saturated value.
        :param tags: A dictionary of tags, used to refine the query.
        :return: A saturation percentage.
        """
        metric = "intel/use/{}/saturation".format(sat_type)
        tags = tags or {}
        tags["source"] = host
        mets = self.get_relative_metric(metric, duration, tags)
        total_values = len(mets)

        if total_values > 0:
            sat_values = [val for _, val in mets if val >= threshold]
            return (float(len(sat_values))/float(total_values)) * 100
        return None

    def get_nominal_capacity(self, nom_type, hostname, tags=None):
        """
        Retrieves the nominal capacity for a given nominal capacity type.
        :param nom_type: Nominal capacity type, such as 'compute'.
        :param hostname: The machine/instance to be queried.
        :param tags: A dictionary of tags, used to refine the query.
        :return: Nominal capacity.
        """
        metric = "intel/capacity/{}/nominal".format(nom_type)
        tags = tags or {}
        tags["source"] = hostname
        return self.get_last_metric(metric, tags=tags)

    def get_sold_capacity(self, sold_type, hostname, tags=None):
        """
        Retrieves the sold capacity for a given sold capacity type.
        :param sold_type: Sold capacity type, such as 'compute'.
        :param hostname: The machine/instance to be queried.
        :param tags: A dictionary of tags, used to refine the query.
        :return: Sold capacity.
        """
        metric = "intel/capacity/{}/sold".format(sold_type)
        tags = tags or {}
        tags["source"] = hostname
        return self.get_last_metric(metric, tags=tags)

    def get_network_latency(self, source, destination):
        """
        Retrieve the network latency between two nodes. This uses the
        intel/ping/avg metric.
        :param source: Source IP.
        :param destination: Destination IP
        :return: Network Latency Value.
        """
        metric = "intel/ping/avg"
        tags = {"source": source, "destination": destination}
        return self.get_last_metric(metric, tags=tags)

    def _get_util_sat_metric(self, util_sat, us_type, host, tags, start=None,
                             end=None, duration=None):
        """
        Helper method for the utilisation and saturation public methods.
        """
        metric = "intel/use/{}/{}".format(us_type, util_sat)
        tags = tags or {}
        tags["source"] = host
        if end:
            return self.get_metric(metric, start, end, tags)
        if duration:
            return self.get_relative_metric(metric, duration, tags)
        return self.get_last_metric(metric, tags)

    def get_e2e_latency(self, source, duration='30s'):
        """
        Retrieves mean end to end latency value over the relative duration.
        :param source: Source.
        :param duration: The relative duration.
        :return: Mean end to end latency value.
        """
        metric = "intel/latency"
        tags = {"source": source}
        grouping = ['source_mac', 'destination_mac', 'type']
        return self.get_mean_metric_grouped(metric, duration, tags=tags,
                                            grouping=grouping)

    def get_mean_metric_grouped(self, metric, duration, tags=None,
                                grouping=None):
        """
        Influx does not have a GROUPING method to return tags. This combines
        the mean result with its associated grouped tags.
        :param metric: Name of the metric to retrieve.
        :param duration: The relative duration.
        :param tags: A dictionary of tags, used to refine the query.
        :param grouping: Grouping.
        :return: Grouped mean metrics.
        """
        snap = Extract(db_client=self.influxdbclient,
                       mean_metric='value', measurement_name=metric, tags=tags,
                       relative_duration=duration, grouping=grouping)
        results = snap.retrieve_mean_raw()
        result = []
        for i in results.items():
            for j in i[1]:
                join = i[0][1].copy()
                join.update(j)
                result.append(join)
        return result

    def show_metrics(self, tags):
        """
        Retrieves a list of metrics which are available for querying. Tags
        help to refine the metrics list, by narrowing the search window, such
        as setting the source to one particular machine.
        :param tags: A dictionary of tags, used to refine the query.
        :return: A list of available metrics.
        """
        snap = Extract(db_client=self.influxdbclient, output_json=True,
                       tags=tags)
        return snap.retrieve_measurements()
