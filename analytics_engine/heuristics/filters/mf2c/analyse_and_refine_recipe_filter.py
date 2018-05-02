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


from analytics_engine.heuristics.filters.mf2c.optimal_filter import OptimalFilter
from analytics_engine.data_analytics.mf2c.refine_recipe import RefineRecipe
from analytics_engine import common
import time

LOG = common.LOG


class AnalyseAndRefineRecipeFilter(OptimalFilter):

    __filter_name__ = 'analyse_and_refine_filter'

    def run(self, workload):
        """
        Attaches a refined recipe to the workload.

        :param workload: Contains workload related info and results.

        :return: heuristic results
        """
        heuristic_results = super(AnalyseAndRefineRecipeFilter, self).run(workload)
        # grabbing first row
        first_row = heuristic_results.iloc[0:1, :]
        recipe = workload.get_latest_recipe()
        refined_recipe = RefineRecipe.refine(recipe, first_row)
        workload.add_recipe(int("{}{}".format(int(round(time.time())), '000000000')), refined_recipe)
        workload.append_metadata(self.__filter_name__, refined_recipe)
        LOG.info('Adjusting based on: {}'.format(heuristic_results))
        LOG.info('Refined recipe: {}'.format(refined_recipe))
        heuristic_results = workload
        return heuristic_results