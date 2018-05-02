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

# -*- coding: utf-8 -*-
"""This module extracts data from the influxdb database."""

import yaml
import os


def derivative(metric):
    """
    metric string
    @returns true if metric is derrivative false if is not
    """
    with open(os.path.join(os.path.dirname(__file__), 'snap_nonderivative.yaml'), 'r') as stream:
        try:
            nondev_metrics = yaml.load(stream)
            if any(metric in s for s in nondev_metrics):
                return False
            return True

        except yaml.YAMLError as exc:
            print exc
    return True
