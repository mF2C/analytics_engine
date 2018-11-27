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

import requests
from analytics_engine.infrastructure_manager.config_helper import ConfigHelper as config
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from analytics_engine import common

LOG = common.LOG
CIMI_URL = config.get("CIMI", "url")
SERVICE_PATH = "/service"
HEADERS = {'slipstream-authn-info': 'internal ADMIN', 'Content-Type': 'application/json'}
SSL_VERIFY = False

if CIMI_URL.lower().find('https') > 0:
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def get_services_by_name(name):
    uri = CIMI_URL+SERVICE_PATH
    if name and len(name) > 0:
        uri = uri+'?{}'.format(_filter_url([{'name': name}]))
    services = _get(uri).get('services')
    return services


def get_service(service_id):
    uri = CIMI_URL+SERVICE_PATH+'/{}'.format(service_id)
    service = _get(uri)
    return service


def update_service(service_id, service_def):
    uri = CIMI_URL + SERVICE_PATH + '/{}'.format(service_id)
    updt = _put(uri, service_def)
    return updt


def _get(path):
    req = requests.get(path, headers=HEADERS, verify=SSL_VERIFY)
    if req.status_code == 200:
        return req.json()


def _put(path, content, params=None):
    req = requests.put(path, content, headers=HEADERS,  verify=SSL_VERIFY)
    if req.status_code == 200:
        return True
    else:
        return False


def _filter_url(params):
    """
    Builds the filter part of the uri to the service and then returns fotmatted string.
    :param params: key value pairs of filter criteria.
    :return: string.
    """
    uri = ""
    if params:
        uri = "$filter="
        for param_name, param in params.iteritems():
            if param is None:  # Skip parameters that are none.
                continue
            uri += "{}={}&".format(param_name, param)
        uri = uri[:len(uri)]  # Remove ? or & from the  end of query string
    return uri


def _sort_url(params):
    uri = ""
    if params:
        uri = "$orderby="
        for param_name, param, sort_type in params.iteritems():
            if param is None:  # Skip parameters that are none.
                continue
            uri += "{}={}:{}&".format(param_name, param, sort_type)
        uri = uri[:len(uri)]  # Remove ? or & from the  end of query string
    return uri
