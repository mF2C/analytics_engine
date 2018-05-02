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

"""
Keeps track of all of the paths in the landscaper.
"""
import os
PROJECT_ROOT = os.path.split(os.path.dirname(os.path.abspath(__file__)))[0]
# CONF = os.path.join(PROJECT_ROOT, "plugins.conf")
INFRA_MGR = os.path.join(PROJECT_ROOT, "analytics_engine", "infrastructure_manager")
CONF = os.path.join(INFRA_MGR, "config", "plugins.ini")
