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

LOG = common.LOG


class RefineRecipe(object):

    @staticmethod
    def _adjust(recipe, tag, value):
        if tag == "memory" :#and value > 10:
            recipe.refine(tag, value)
        if tag == "disk" :#and value > 5:
            recipe.refine(tag, value)
        if tag == "network":# and value > 1:
            recipe.refine(tag, value)

    @staticmethod
    def refine(recipe, conf):
        """
        Given a configuration returns the recipe based on internal analysis
        :param recipe: recipe to be refined
        :param conf: best infrastructure configuration.
        :return: a refined recipe
        """
        conf_dict = conf.to_dict()
        # node_name = str(conf_dict['node_name'])
        compute = conf_dict['compute utilization'][0]
        memory = conf_dict['memory utilization'][0]
        network = conf_dict['network utilization'][0]
        storage = conf_dict['disk utilization'][0]
        if recipe:
            #RefineRecipe._adjust(recipe, "cpu", compute)
            RefineRecipe._adjust(recipe, "memory", memory)
            RefineRecipe._adjust(recipe, "network", network)
            RefineRecipe._adjust(recipe, "disk", storage)
        return recipe