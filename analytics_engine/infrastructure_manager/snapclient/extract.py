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
DB extract class:
Instantiate class by passing required query parameters e.g. start/end dates, etc.

"""

__author__ = 'Gordon Wallace'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"


import datetime
import re
import sys
from influxdb import InfluxDBClient
import pandas as pd
import analytics_engine.common as common
from snap.utilities import derivative
LOG = common.LOG


class Extract:

    def __init__(self, **kwargs):
        """
        Extract parameters can be set below:
        Dates: Set desired start and end dates (specific time can also be applied if required).

        Days relative: if using a n days extract (relative to now), set days_relative to int n.

        Tags: Set desired tag key and value in tags dict, setting key to None for any tag will force
        extract to ignore tag.

        Measurement Name: Set data measurement/series name as key.

        Derivative: Set derivative metric as required, set interval as sample time and set
        time unit s, h, d.
        :param kwargs:
        """

        self.measurement_name = kwargs.get('measurement_name', None)
        self.start_date = kwargs.get('start_date', None)
        self.end_date = kwargs.get('end_date', None)
        self.relative_duration = kwargs.get('relative_duration', None)
        self.tags = kwargs.get('tags', None)
        self.grouping = kwargs.get('grouping', None)
        self.db_client = kwargs.get('db_client', None)
        self.derivative_metric = kwargs.get('derivative_metric', None)
        self.derivative_interval = kwargs.get('derivative_interval', None)
        self.derivative_time_unit = kwargs.get('derivative_time_unit', None)
        self.mean_metric = kwargs.get('mean_metric', None)
        self.panda_dataframe = kwargs.get('panda_dataframe', False)

        self._setup_client()

    def _setup_client(self):
        """
        Checks that supplied db_client obj is not null, if null a TypeError is thrown, else
        funtion checks if client is Influx client if true sets instance variable database_client
        to supplied client obj. If a dict with client details supplied a new Influx client
        obj creation will be attempted, if successful instance var database_client set to
        new client obj.
        :return:
        """
        if self.db_client is None:
            raise TypeError("Database client error: Please supply client information (db_client = clientObj)")
        else:
            if not self._is_influx_client():
                try:
                    hostname = self.db_client['hostname']
                    port = self.db_client['port']
                    username = self.db_client['username']
                    password = self.db_client['password']
                    db_name = self.db_client['database']

                    self.database_client = InfluxDBClient(hostname, port, username, password, db_name)
                except:
                    raise ValueError("Database client error: Supplied client parameters are incorrect")
            else:
                self.database_client = self.db_client

    def retrieve_relative(self):
        result = self.db_client.query(self._build_query(self._build_relative_query()))
        return self._get_values(result)

    def retrieve_date_range(self):
        result = self.db_client.query(self._build_query(self._build_date_range_query()))
        return self._get_values(result)

    def retrieve_tags(self):
        result = self.db_client.query(self._build_query(self._build_tag_query()))
        return self._get_values(result)

    def retrieve_derivative(self):
        result = self.db_client.query(self._build_derivative_query())
        return self._get_values(result)

    def retrieve_last_datapoint(self):
        result = self.db_client.query(self._build_last_query())
        return self._get_values(result)

    def retrieve_last_with_tags(self):
        """
        Retrieves not just the value and time but also the tags.
        :return: returns not just the value and time but also the tags.
        """
        query = self._last_w_tags(self._build_query(None, 'lwt'))
        result = self.db_client.query(query)
        return self._get_values(result)

    def retrieve_mean(self):
        result = self.db_client.query(self._build_mean_query())
        return self._get_values(result)

    def retrieve_mean_raw(self):
        return self.db_client.query(self._build_mean_query())

    def retrieve_measurements(self):
        """
        Retrieves a list of the available measurements on the db.  Typically a
        source is provided as a tag, e.g {'source':'node1'}.  This will then 
        retrieve just the measurements associated with that node. 
        :return: list of available measurements. 
        """
        result = self.db_client.query(self._build_measurements_query())
        results = self._get_values(result)
        return [measurement["name"] for measurement in results]

    def _last_w_tags(self, query_head):
        if query_head.strip().endswith("WHERE"):
            query_head = query_head.strip()[:-5]
        return "{} ORDER BY time DESC LIMIT 1".format(query_head)

    def _build_relative_query(self):
        if self._validate_relative_duration():
            return "time > now() - {}".format(self.relative_duration)

    def _build_days_query(self):  # no longer used.
        """
        Builds a relative time based query using the supplied days_relative value.
        Exception raised if value non int type, else required relative query returned.
        :return:
        """
        try:
            number_days = abs(int(self.relative_duration))  # Get supplied days_relative value and convert to int
        except ValueError:
            print("Could not convert data to integer")
            sys.exit(1)
        except TypeError:
            print("Value must be positive integer")
            sys.exit(1)

        return 'time > now() - ' + str(number_days) + 'd'

    def _build_date_range_query(self):
        query = ""
        if self.start_date is not None and self.end_date is not None:
            if not (int(self.start_date)) < (int(self.end_date)):
                raise ValueError("Date order error, please check start and end dates are correct")
            else:
                # range_query = 'time <= ' + "'" + start + "'" + ' AND time >= ' + "'" + end + "'"
                query = 'time >= {}s AND time <= {}s'.format(int(self.start_date),
                                                             int(self.end_date))
        return query

    def _build_tag_query(self):
        # return the final tag query logic
        query_type = ' AND '  # change this to force query type (AND OR), default AND
        logic_and = ' AND '
        logic_or = ' OR '
        tags = "("
        for k, v in self.tags.items():
            if v != "None":
                if query_type == logic_and:
                    tags += "(" + k + " = " + "'" + v + "')" + logic_and
                elif query_type == logic_or:
                    tags += "(" + k + " = " + "'" + v + "')" + logic_or
        query = tags[:-5] + ")"  # set substring :-4 if OR logic used

        return query

    def _build_base_query(self):
        return 'SELECT * FROM "{}" '.format(self.measurement_name)

    def _build_query(self, query_range, lwt=''):
        """
        Builds the base query. Method checks for tags and a
        range e.g. start/end times. Any tags are concatenated to query
        otherwise base query returned.
        :param query_range:
        :return:
        """
        if query_range is None:
            query_range = ""
        metric = self.measurement_name
        clauses = ""
        # check for tags
        if self.tags:
            if len(query_range) > 0:  # checking if any query range supplied
                clauses += self._build_tag_query() + ' AND '
            else:
                clauses += self._build_tag_query()

        query = 'SELECT mean(value) as value FROM "{}" WHERE {}'.format(metric, clauses + query_range)

        if lwt == "lwt":
            query = 'SELECT * FROM "{}" WHERE {}'.format(metric, clauses + query_range)
        if self.grouping:
            query = "{0} GROUP BY {1} fill(linear)".format(query, ", ".join(self.grouping))
        return query

    def _build_derivative_query(self):
        """Main method generates full derivative query"""
        # Can concatenate: WHERE <stuff> onto query if required at this point.
        key = self.derivative_metric
        interval = self.derivative_interval
        unit = self.derivative_time_unit
        date_range = ""
        if self.start_date is not None and self.end_date is not None:
            date_range += ' WHERE time >= {}s AND time <= {}s'.format(int(self.start_date),
                                                                      int(self.end_date))
        if derivative(key):
            metric = self.measurement_name
            start = self._derivative_query_key_time(key, interval, unit)
            return start + metric + date_range
        else:
            raise TypeError("Non-derivative parameter given: " + key)

    def _derivative_query_key_time(self, key, interval, unit):
        """Helper method generates the front section of derivative query"""
        # Unit can be u - microseconds, s - seconds, m - minutes, h - hours, d - days or w - weeks
        # Option to add actual sample time i.e. 1s or 10s can easily be implemented.
        # default sample time is one.
        return 'SELECT DERIVATIVE(' + key + ', ' + str(interval) + unit + ') From '

    def _build_measurements_query(self):
        clauses = ""
        if self.tags:
            clauses += self._build_tag_query()

        if self._build_date_range_query():
            clauses += " AND "
            clauses += self._build_date_range_query()

        query = 'SHOW MEASUREMENTS'

        if clauses:
            query += " WHERE {}".format(clauses)

        return query

    def _build_last_query(self):
        clauses = ""
        if self.tags:
            clauses += self._build_tag_query()

        if self._build_date_range_query():
            clauses += " AND "
            clauses += self._build_date_range_query()

        query = 'SELECT LAST(*) FROM "{}"'.format(self.measurement_name)

        if clauses:
            query += " WHERE {}".format(clauses)

        return query

    def _build_mean_query(self):
        clauses = ""
        if self.tags:
            clauses += self._build_tag_query()
            if self.relative_duration:
                clauses += " AND "

        if self.relative_duration:
            clauses += self._build_relative_query()

        if self.grouping:
            clauses += " GROUP BY {0} fill(linear)".format(", ".join(self.grouping))

        query = 'SELECT MEAN({}) FROM "{}"'.format(self.mean_metric, self.measurement_name)

        if clauses:
            query += " WHERE {}".format(clauses)

        return query

    def _check_date_format(self, date_str):
        """
        Takes a date_str as argument and validates correct format. If incorrect format detected
        function halts and raises exception error else if format valid date_str is returned.
        :param date_str:
        :return:
        """
        date_time_format_error = "Incorrect date format, should be YYYY-MM-DD"
        date_format_error = "Incorrect date format, should be YYYY-MM-DD#hh:mm:ss (ensure to include #)"
        type_error = "Date must be str format"
        try:
            if date_str.count('#') == 1:  # test for # seperator (ensure only one instance of # inserted).
                temp_date = date_str.replace('#', '-')  # temp remove # to test date/time format ok.
                try:
                    datetime.datetime.strptime(temp_date, '%Y-%m-%d-%H:%M:%S')
                except ValueError:
                    raise ValueError(date_format_error)
            elif date_str.count('#') > 1:  # user has incorrectly set date time # seperator
                raise ValueError(date_format_error)
            else:  # no has seperator detected user set date only
                try:
                    datetime.datetime.strptime(date_str, '%Y-%m-%d')
                except ValueError:
                    raise ValueError(date_time_format_error)
        except TypeError:
            raise TypeError(type_error)

        return date_str

    def _check_dates(self, start, end):
        """
        takes a start and end date, returns true if start date before end date otherwise
        false retuned.
        :param start:
        :param end:
        :return:
        """
        dates_good = False
        if start > end:
            dates_good = True
        return dates_good

    def _parse_date(self, date_str):
        """
        Takes a date/date_time stamp as parameter and converts to necessary Influx DB time stamp
        format.
        Final processed date time stamp is returned.
        :param date_str:
        :return:
        """
        if '#' in date_str:
            date_time = date_str.replace('#', 'T')
            date_time += 'Z'
        else:
            date_time = date_str

        return date_time

    def _is_influx_client(self):
        return type(self.db_client) is InfluxDBClient

    def _get_values(self, query_result):
        if self.panda_dataframe:
            df = pd.DataFrame(list(query_result.get_points()))
            return df
        else:
            if len(query_result) > 0:
                result =  list(query_result)[0]
            else:
                result = list(query_result)
            return result

    def _validate_relative_duration(self):
        """
        Validates supplied relative_duration of correct format.
        Rteruns True if format good otherwise valueError thrown.
        :return: 
        """
        error = "Relative duration format incorrect."
        if self.relative_duration:
            # regex pattern to ensure integer and alphabetical single character supplied
            match = re.match(r"([0-9]+)(?:\d*[usmhdw]){1}\d*$"
                             , self.relative_duration
                             , re.I)
            if match:
                return True
            else:
                raise ValueError(error)
