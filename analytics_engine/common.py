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

__author__ = 'Giuliana Carullo, Vincenzo Riccobene'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"

import os
import logging
import warnings
from analytics_engine.infrastructure_manager.config_helper import ConfigHelper
from urllib3.exceptions import InsecureRequestWarning

from pandas.core.common import SettingWithCopyWarning



# Configuration File Sections
CFS_GENERAL = 'General'
CFS_DYNAMIC_PARAMS = 'Dynamic-params'
CFS_INFLUX = 'INFLUXDB'
CFS_PROMETHEUS = 'PROMETHEUS'


# ------------------------------------------------------
# Common variables
# ------------------------------------------------------

SERVICE_NAME = 'analytics_engine'
CONF_FILE = None
ORCHESTRATOR = None
DATA_MANAGER = None
LOG = None
test_res = None

b_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = "/".join(b_dir.split('/')[:-1])
FRAMEWORK_TEMPORARY_DIR = "/tmp/{}".format(SERVICE_NAME)
INSTALL_BASE_DIR = os.path.join(os.path.expanduser('~'), SERVICE_NAME)
R_LIB_DIR = os.path.join(INSTALL_BASE_DIR, "data_analytics_lib/R/")
RESULT_DIR = os.path.join(INSTALL_BASE_DIR, 'results')
SOURCE_CFG_DIR = os.path.join(INSTALL_BASE_DIR, 'source_cfg')
CONF_FILE_LOCATION = \
    os.path.join(INSTALL_BASE_DIR, 'analytics_engine.conf')

def configure_logging():
    """
    Initialization of the logging system for the framework
    :return:
    """
    global LOG
    debug = ConfigHelper.get(CFS_GENERAL, "debug")
    if debug.lower() == "true":
        file_level = logging.DEBUG
    else:
        file_level = logging.INFO

    # Clean logs
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=SettingWithCopyWarning)
    warnings.filterwarnings("ignore", category=InsecureRequestWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    logging.getLogger("httpstream").setLevel(logging.WARNING)
    logging.getLogger("py2neo.cypher").setLevel(logging.WARNING)
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
    logging.getLogger("requests.packages.urllib3."
                      "connectionpool").setLevel(logging.WARNING)

    # Create logging
    log = logging.getLogger(SERVICE_NAME)

    logdir = '/tmp/{0}/var/log/'.format(SERVICE_NAME)
    if not os.path.exists(logdir):
        os.makedirs(logdir)

    stream = open('{0}/{1}_{2}.log'.format(logdir, SERVICE_NAME, os.getpid()),
                  'a')
    fileHandler = logging.StreamHandler(stream)
    fileHandler.setLevel(file_level)
    formatter = logging.Formatter(
        '[%(asctime)s] %(module)s (line: %(lineno)d) '
        '%(levelname)s: %(message)s', "%Y/%m/%d %H:%M:%S")
    fileHandler.setFormatter(formatter)
    log.addHandler(fileHandler)

    cliHandler = logging.StreamHandler()
    cliHandler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '[%(asctime)s] %(message)s', "%Y/%m/%d %H:%M:%S")
    cliHandler.setFormatter(formatter)

    log.addHandler(cliHandler)
    log.setLevel(logging.DEBUG)
    log.propagate = False

    LOG = log

    return log

# Init

try:
    if not LOG:
        LOG = configure_logging()
except:
    pass
