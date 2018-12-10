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

import analytics_engine.common as common
import pandas

LOG = common.LOG


class Workload(object):
    """
    Internal representation for a workload.
    It stores both input data for the given workload, as well as metadata.
    """

    # TODO : add debug option
    # TODO: set ts_to default to max
    def __init__(self, workload_name, ts_from=0, ts_to=0,
                 workload_config=None, workload_config_type=None,
                 discard=True):
        """

        :param workload_name: (string) name of the workload
        :param ts_from: start of the workload
        :param ts_to: end of the workload
        :param discard: (bool) optional value, if true stores only the last computation results.
        """
        self._workload_name = workload_name
        self._workload_config = workload_config
        self._workload_config_type = workload_config_type
        self._recipe = {}
        self._ts_from = ts_from
        self._ts_to = ts_to
        self._discard = discard
        self._graph = None
        self._results={}
        self._latest_filter_name = ""
        self._latest_recipe_time = None
        self._metadata = {}

    def get_workload_name(self):
        """
        Returns the name of the workload
        :return: workload name
        """
        return self._workload_name

    def get_service_name(self):
        """
        Returns the name of the workload
        :return: workload name
        """
        recipe = self.get_latest_recipe()
        return recipe._name

    def get_ts_from(self):
        """
        Returns the start time of the workload
        :return: workload start
        """
        return self._ts_from

    def get_ts_to(self):
        """
        Returns the end time of the workload
        :return:  workload end
        """
        return self._ts_to

    def get_configuration(self):
        """Returns the configuration being used"""
        return self._workload_config

    def get_configuration_type(self):
        """Returns the configuration type"""
        return self._workload_config_type

    def save_results(self, filter_name, result):
        """
        Decorates the workload with relative metadata
        :param filter_name: name of the filter applied
        :param result: result from filter computation (metadata)
        :return:
        """
        if self._discard:
            self._results={}

        self._results[filter_name] = result
        self._latest_filter_name = filter_name

    def get_results(self):
        """
        Return all the results
        :return: metadata attached to the workload
        """
        return self._results

    def get_latest_graph(self):
        """
        Return the latest results only
        :return: metadata
        """
        if self._results:
            return self._results[self._latest_filter_name]
        return None

    def append_metadata(self, filter_name, result):
        """
        Decorates the workload with additional metadata
        :param filter_name: name of the filter applied
        :param result: result from filter computation (metadata)
        :return:
        """
        if isinstance(result, dict):
            self._metadata[filter_name] = pandas.DataFrame.from_dict(result,  orient='index')
        # self._metadata[filter_name] = result
        if isinstance(result, tuple):
            self._metadata[filter_name] = pandas.DataFrame(list(result))
        if isinstance(result, list):
            self._metadata[filter_name] = pandas.DataFrame(result)
        if isinstance(result, pandas.DataFrame):
            self._metadata[filter_name] = result

    def get_result(self, filter_name):
        if self._results and filter_name in self._results.keys():
            return self._results[filter_name]

        if self._results and filter_name in self._metadata.keys():
            return self._metadata[filter_name]
        return None

    def get_metadata(self, filter='all'):
        """
        Returns metadata attached to the workload.
        :param filter: (str)optional, default: all,
                        which means all metadata is returned
                        Filter name can be specified to get
                        only relative specific results.
        :return: metadata - dict(pandas) or pandas
        """
        if filter == 'all':
            return self._metadata
        return self._metadata[filter]

    def add_recipe(self, time, recipe):
        """
        Add a recipe (deployment configuration) to the workload.
        A recipe is
        :param time: the unique time in which the analysis has been perfomed
                     on the workload.
        :param recipe (json): the deployment recipe
        :return:
        """
        if time in self._recipe:
            LOG.error('A recipe already exists for this date')
        else:
            LOG.info('Adding a new recipe at time {}'.format(time))
            self._recipe[time] = recipe
            self._latest_recipe_time = time

    def get_recipes(self):
        """
        Returns all the recipes associated with the workload
        :return (dict): recipes
        """
        return self._recipe

    def get_latest_recipe(self):
        if self._recipe:
            return self._recipe[self._latest_recipe_time]
        else:
            LOG.error('No recipe found')
            return None

    def get_latest_recipe_time(self):
        return self._latest_recipe_time

    def set_discard(self, discard):
        self._discard = discard

