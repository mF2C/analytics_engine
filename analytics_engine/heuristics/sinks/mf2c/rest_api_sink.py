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

import os
import threading
import analytics_engine.common as common

LOG = common.LOG
LOCAL_RES_DIR = os.path.join(common.INSTALL_BASE_DIR, "exported_data")

"""
REST Application for the landscape.
"""

import json
import flask
from flask import request
from flask import Response
from analytics_engine.heuristics.beans.workload import Workload
from analytics_engine.heuristics.pipes.optimal_pipe import OptimalPipe
from analytics_engine.heuristics.filters.optimal_filter import OptimalFilter
from analytics_engine.heuristics.pipes.mf2c.refine_recipe_pipe import RefineRecipePipe
from analytics_engine.heuristics.pipes.mf2c.analyse_pipe import AnalysePipe
from analytics_engine.heuristics.pipes.fiveg_essence.analyse_service_hist_pipe import AnalyseServiceHistPipe
from analytics_engine.heuristics.beans.mf2c.recipe import Recipe
from analytics_engine.heuristics.sinks.mf2c.influx_sink import InfluxSink

import analytics_engine.common as common
import time

LOG = common.LOG

app = flask.Flask(__name__)

MIME = "application/json"


@app.route("/mf2c/optimal", methods=['GET', 'POST'])
def get_optimal():
    """
    Returns results from avg heuristic
    """
    LOG.info("Retrieving Optimal with url : %s", request.url)
    recipe = request.get_json()
    LOG.info(recipe)
    LOG.info(str(recipe['name']))
    current_time = int(time.time())
    workload_name = 'optimal_'+str(current_time)
    #if 'ts_from' in recipe:
    #    LOG.debug(recipe['ts_from'])
    #    LOG.debug(recipe['ts_to'])
    #    workload = Workload(str(recipe['name']), ts_from= recipe['ts_from'], ts_to= recipe['ts_to'])
    # eng = Engine()
    # eng.run('optimal', recipe['name'], recipe['ts_from'], recipe['ts_to'])
    #else:
    #   workload = Workload(str(recipe['name']))
    workload = Workload(workload_name)
    # storing initial recipe
    # TODO: validate recipe format
    recipe_bean = Recipe()
    recipe_bean.from_json(recipe)
    workload.add_recipe(int("{}{}".format(int(round(time.time())), '000000000')), recipe_bean)
    pipe_exec = OptimalPipe()
    node_type = 'machine'
    workload = pipe_exec.run(workload, node_type)
    results = workload.get_metadata(OptimalFilter.__filter_name__)
    #return Response(results.to_json(), mimetype=MIME)
    #return Response(results.to_dict('results'), mimetype=MIME)
    json_results = json.dumps(results.to_dict('results'))
    return Response(json_results, mimetype=MIME)


@app.route("/mf2c/analyse", methods=['GET', 'POST'])
def analyse():
    params = request.get_json()
    service_id = params.get('service_id')
    name = params.get('name')
    if service_id:
        LOG.info("Triggering analysis based on input service_id: {}".format(service_id))
    elif name:
        LOG.info("Triggering analysis based on input service name: {}".format(name))
    id = str(service_id) if service_id else str(name)
    influx_sink = InfluxSink()
    workload = influx_sink.show((id, None))
    recipes = {}
    if workload:
        recipes = workload.get_recipes()
    reuse = False
    for recipe_id in recipes:
        recipe = recipes[recipe_id]
        if recipe._ts_from == int(params.get('ts_from')) and recipe._ts_to == int(params.get('ts_to')):
            reuse = True
            break
    if not workload or not reuse:
        # TODO: recipe should come from CIMI
        recipe = request.get_json()
        recipe_bean = Recipe()
        recipe_bean.from_json(recipe)
        workload = Workload(id, int(params['ts_from']), int(params['ts_to']))
        workload.add_recipe(int("{}{}".format(int(round(time.time())), '000000000')), recipe_bean)
    else:
        LOG.info("Reusing existing analysis")
    pipe_exec = AnalysePipe()
    workload = pipe_exec.run(workload)
    recipe = workload.get_latest_recipe()
    analysis_description = {
        "service_id": recipe.get_service_id(),
        "name": workload.get_service_name(),
        "analysis_id": workload.get_latest_recipe_time()
    }
    return Response(json.dumps(analysis_description), mimetype=MIME)


@app.route("/mf2c/refine", methods=['GET', 'POST'])
def refine_recipe():
    """
    Returns a refined recipe.
    Accept a json with service_id and analyse_id
    """
    LOG.info("Retrieving Refined Recipe with url : %s", request.url)
    params = request.get_json()
    LOG.info(params)
    LOG.info(str(params['service_id']))
    # eng = Engine()
    # eng.run('optimal', recipe['name'], recipe['ts_from'], recipe['ts_to'])
    workload = Workload(str(params['name']), None, None)
    pipe_exec = RefineRecipePipe()
    analysis_id = params.get('analysis_id')
    if analysis_id:
        pipe_exec.set_analysis_id(str(analysis_id))

    recipe = pipe_exec.run(workload)
    if recipe:
        return Response(json.dumps(recipe.to_json()), mimetype=MIME)
    return Response(json.dumps({}), mimetype=MIME)

#5g essence specific
@app.route("/5ge/optimal_vms", methods=['GET', 'POST'])
def get_optimal_vms():
    """
    Returns results from avg heuristic
    """
    LOG.info("Retrieving Optimal_VMs with url : %s", request.url)
    recipe = request.get_json()
    LOG.info(recipe)
    LOG.info(str(recipe['name']))
    current_time = int(time.time())
    workload = Workload(str(recipe['name']), ts_from=(current_time-10), ts_to=current_time)
    # storing initial recipe
    # TODO: validate recipe format
    recipe_bean = Recipe()
    recipe_bean.from_json(recipe)
    workload.add_recipe(int("{}{}".format(int(round(time.time())), '000000000')), recipe_bean)
    pipe_exec = OptimalPipe()
    node_type = 'vm'
    workload = pipe_exec.run(workload, node_type)
    results = workload.get_metadata(OptimalFilter.__filter_name__)
    #return Response(results.to_json(), mimetype=MIME)
    #return Response(results.to_dict('results'), mimetype=MIME)
    json_results = json.dumps(results.to_dict('results'))
    return Response(json_results, mimetype=MIME)

#5g essence specific
@app.route("/5ge/analyze_service", methods=['GET', 'POST'])
def analyze_service():
    """
    Returns results from avg heuristic
    """
    LOG.info("Analyzing service instances with url : %s", request.url)
    recipe = request.get_json()
    service_type = 'stack'
    if recipe.get('exec_type') == 'docker':
        service_type = 'service'
    LOG.info(recipe)
    LOG.info(str(recipe['name']))
    workload = Workload(str(recipe['name']))
    # storing initial recipe
    # TODO: validate recipe format
    recipe_bean = Recipe()
    recipe_bean.from_json(recipe)
    workload.add_recipe(int("{}{}".format(int(round(time.time())), '000000000')), recipe_bean)
    pipe_exec = AnalyseServiceHistPipe()
    workload = pipe_exec.run(workload, service_type)

    analysis_description = {
        "service_id": recipe['name'],
        "analysis_id": workload.get_latest_recipe_time()
    }
    return Response(json.dumps(analysis_description), mimetype=MIME)

@app.route('/')
def hello():
    return "Welcome to the Analytics Engine"


class RestiAPI(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self.start()

    def start(self):
        app.run(host="0.0.0.0", port=46020)


if __name__ == '__main__':
    app.run()
