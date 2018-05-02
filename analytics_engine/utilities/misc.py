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

__author__ = 'Vincenzo Riccobene, Giuliana Carullo'
__copyright__ = "Copyright (c) 2017, Intel Research and Development Ireland Ltd."
__license__ = "Apache 2.0"
__maintainer__ = "Giuliana Carullo"
__email__ = "giuliana.carullo@intel.com"
__status__ = "Development"

import os
import re
import json
import fileinput
import ConfigParser
import argparse
# import analytics_engine.conf_file_sections as cf


class Validation(object):
    @staticmethod
    def str2bool(v):
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')

    @staticmethod
    def string(param, message):
        if not isinstance(param, str):
            raise ValueError(message)
        return True

    @staticmethod
    def integer(param, message=None):
        if not message:
            message = "{} is not an integer".format(param)
        try:
            int(param)
        except:
            raise ValueError(message)
        if not isinstance(param, int):
            raise ValueError(message)
        return True

    @staticmethod
    def boolean(boolean, message):
        if isinstance(boolean, bool):
            return boolean
        if isinstance(boolean, str):
            if boolean == 'True':
                return True
            if boolean == 'False':
                return False
        raise ValueError(message)

    @staticmethod
    def dictionary(param, message):
        if not isinstance(param, dict):
            raise ValueError(message)
        return True

    @staticmethod
    def file_exist(file_name, message=None):
        if not message:
            message = "File {} does not exist".format(file_name)
        if not os.path.isfile(file_name):
            raise ValueError(message + ' ' + file_name)
        return True

    @staticmethod
    def directory_exist_and_format(
            directory, message=None):
        if not message:
            message = 'Directory {} does not exist'.format(directory)
        if not os.path.isdir(directory):
            raise ValueError(message)
        if not directory.endswith('/'):
            return directory + '/'
        return directory

    # @staticmethod
    # def config_file_parameter(section, parameter, message):
    #     params = common.CONF_FILE.get_variable_list(section)
    #     if parameter not in params:
    #         raise ValueError(message)
    #     return True

    # @staticmethod
    # def config_file_section(section, message):
    #     if section not in cf.get_sections():
    #         raise ValueError(message)
    #     return True



    @staticmethod
    def tcpPortNumber(connection_port):
        port = int(connection_port)
        if port < 0 or port > 99999:
            raise ValueError(
                "Port number {} is not valid".format(connection_port))
        return True

    # @staticmethod
    # def validate_os_credentials(credentials):
    #     if not isinstance(credentials, dict):
    #         raise ValueError(
    #             'The provided openstack_credentials '
    #             'variable must be in dictionary format')
    #
    #     credential_keys = ['ip_controller', 'heat_url', 'user', 'password',
    #                        'auth_uri', 'project']
    #     missing = [
    #         credential_key
    #         for credential_key in credential_keys
    #         if credential_key not in credentials.keys()
    #     ]
    #     if len(missing) == 0:
    #         return True
    #     msg = 'OpenStack Credentials Error! ' \
    #           'The following parameters are missing: {}'.\
    #         format(", ".join(missing))
    #     raise ValueError(msg)


# ------------------------------------------------------
# Configuration file access
# ------------------------------------------------------

class ConfigurationFile:
    """
    Used to extract data from the configuration file
    """

    def __init__(self, sections, config_file='conf.cfg'):
        """
        Reads configuration file sections

        :param sections: list of strings representing the sections to be
                         loaded
        :param config_file: name of the configuration file (string)
        :return: None
        """
        Validation.string(
            config_file, "The configuration file name must be a string")
        # config_file = BASE_DIR + config_file
        Validation.file_exist(
            config_file, 'The provided configuration file does not exist')
        self.config = ConfigParser.ConfigParser()
        self.config.read(config_file)
        for section in sections:
            setattr(
                self, section, ConfigurationFile.
                _config_section_map(section, self.config))

    @staticmethod
    def _config_section_map(section, config_file):
        """
        Returns a dictionary with the configuration values for the specific
        section

        :param section: section to be loaded (string)
        :param config_file: name of the configuration file (string)
        :return: dict
        """
        dict1 = dict()
        options = config_file.options(section)
        for option in options:
            dict1[option] = config_file.get(section, option)
        return dict1

    def get_variable(self, section, variable_name):
        """
        Returns the value correspondent to a variable

        :param section: section to be loaded (string)
        :param variable_name: name of the variable (string)
        :return: string
        """
        message = "The variable name must be a string"
        Validation.string(variable_name, message)
        if variable_name in self.get_variable_list(section):
            sect = getattr(self, section)
            return sect[variable_name]
        else:
            exc_msg = 'Parameter {} is not in the {} section of the ' \
                      'conf file'.format(variable_name, section)
            raise ValueError(exc_msg)

    def get_variable_list(self, section):
        """
        Returns the list of the available variables in a section
        :param section: section to be loaded (string)
        :return: list
        """
        try:
            return getattr(self, section)
        except:
            msg = 'Section {}  not found in the configuration file'.\
                format(section)
            raise ValueError(msg)


def get_file_first_line(file_name):
    """
    Returns the first line of a file

    :param file_name: name of the file to be read (str)
    :return: str
    """
    message = "The name of the file must be a string"
    Validation.string(file_name, message)
    message = 'The file {} does not exist'.format(file_name)
    Validation.file_exist(file_name, message)
    res = open(file_name, 'r')
    return res.readline()


def replace_in_file(file, text_to_search, text_to_replace):
    """
    Replaces a string within a file

    :param file: name of the file (str)
    :param text_to_search: text to be replaced
    :param text_to_replace: new text that will replace the previous
    :return: None
    """
    message = 'The text to be replaced in the file must be a string'
    Validation.string(text_to_search, message)
    message = 'The text to replace in the file must be a string'
    Validation.string(text_to_replace, message)
    message = "The name of the file must be a string"
    Validation.string(file, message)
    message = "The file does not exist"
    Validation.file_exist(file, message)
    for line in fileinput.input(file, inplace=True):
        print(line.replace(text_to_search, text_to_replace).rstrip())


def remove_files(directory, pattern):
    """
    Remove files from a given directory which satisfy a given pattern

    :param directory: (str) dirname
    :param pattern: (str) pattern to be satisfied
    :return:
    """
    for f in os.listdir(directory):
        if re.search(pattern, f):
            os.remove(os.path.join(directory, f))


def split_file_name(file_absolute_name):
    """
    Splits a file name into: [directory, name, extension]

    :param full_name_template:
    :return:
    """
    split_template = file_absolute_name.split('/')
    [name, extension] = split_template[-1].split('.')
    directory = "/".join(split_template[0: len(split_template) - 1])
    return [directory, name, extension]


def get_file_content(filename):
    """
    Return content of a file in a string

    :param filename: full name of the file
    :return: content of the file as str
    """
    with open(filename, 'r') as content_file:
        content = content_file.read()
        return content


def write_to_json_file(obj, filename):
    """
    Write on file filename the object in JSON format

    :param obj: object to be written on the JSON file
    :param filename: filename to be used to store the obj
    :return: success (bool)
    """

    f = open(filename, "w")
    try:
        json.dump(obj, f)
        success = True
    except:
        success = False
    finally:
        f.close()
    return success


def read_from_json_file(filename):
    """
    Read from file filename the object in JSON format

    :param obj: object to be written on the JSON file
    :param filename: filename to be used to store the obj
    :return: success (bool)
    """
    f = open(filename, "rb")
    try:
        obj = json.load(f)
    except Exception as e:
        print (e)
        obj = None
    finally:
        f.close()
    return obj


# ------------------------------------------------------
# JSON management
# ------------------------------------------------------
def from_str_to_json(string):
    """
    Convert a string into a JSON (dict)
    :param string: string to convert into JSON format
    :return: dict
    """
    decoder = json.JSONDecoder()
    obj = decoder.decode(string)
    return obj


def from_str_to_dict(string):
    import ast
    return ast.literal_eval(string)


def from_json_to_string(json_obj):
    """
    Convert a JSON object (dict) into a string
    :param json_obj: JSON object to be converted
    :return: string
    """
    encoder = json.JSONEncoder()
    string = encoder.encode(json_obj)
    return string


# ------------------------------------------------------
# Shell interaction
# ------------------------------------------------------
def run_command(command):
    return os.system(command)


# def push_data_influxdb(data):
#     ip = INFLUXDB_IP
#     port = INFLUXDB_PORT
#     db_name = INFLUXDB_DB_NAME
#     command = "curl -i -XPOST 'http://{}:{}/write?db={}' " \
#               "--data-binary {}".format(ip, port, db_name, data)
#     run_command(command)


# ------------------------------------------------------
# Data Structure
# ------------------------------------------------------
def convert_unicode_dict_to_string(dictionary):
    import collections

    if isinstance(dictionary, basestring):
        return str(dictionary)
    elif isinstance(dictionary, collections.Mapping):
        return dict(map(convert_unicode_dict_to_string, dictionary.iteritems()))
    elif isinstance(dictionary, collections.Iterable):
        return type(dictionary)(map(convert_unicode_dict_to_string, dictionary))
    else:
        return dictionary


def simplify_nested_dict(dictionary, name, separator='_'):
    """
    Takes a nested dictionary and transforms it into a flat one.

    :param dictionary: (dict) dictionary to transform
    :return: (dict) result dictionary
    """
    res = dict()
    for key in dictionary:
        if isinstance(dictionary[key], dict):
            res.update(simplify_nested_dict(
                dictionary[key],
                "{}{}{}".format(name, separator, key),
                separator))
        else:
            res['{}{}{}'.format(name, separator, key)] = dictionary[key]
    return res


def convert_dict_keys_to_strings(dictionary):
    """
    Convert all the keys of the dictionary to strings,
    no matter which type they are.

    :param dictionary: dict()
    :return: dict() with converted keys
    """
    res = dict()
    for p in dictionary:
        if isinstance(dictionary[p], dict):
            res[str(p)] = convert_dict_keys_to_strings(dictionary[p])
        else:
            res[str(p)] = dictionary[p]
    return res


def convert_dict_values_to_strings(dictionary):
    """
    Convert leaf parameters of a dictionary to string
    :return:
    """
    res = dict()
    for param in dictionary:
        p = dictionary[param]
        if not isinstance(p, dict):
            res[param] = str(dictionary[param])
        else:
            res[param] = convert_dict_values_to_strings(dictionary[param])
    return res


def compare_dictionaries(d1, d2):
    """
    Compare two dictionaries
    :param d1:
    :param d2:
    :return: (bool) True if equal, False if different
    """
    res = True
    try:
        for key in d1:
            res &= (d1[key] == d2[key])
        for key in d2:
            res &= (d1[key] == d2[key])
    except KeyError:
        return False
    return res


def _string_to_list(string):
    new_string = string.replace(" ", "")
    array_items = new_string.split(",")
    res = list()
    for name in array_items:
        res.append(name)
    return res

# ------------------------------------------------------
# Expose variables to other modules
# ------------------------------------------------------

# def get_base_dir():
#     return BASE_DIR


# def get_template_dir():
#     return TEMPLATE_DIR


# def get_result_dir():
#     return RESULT_DIR


# def get_dpdk_pktgen_vars():
#     if not (PKTGEN == 'dpdk_pktgen'):
#         return dict()
#     ret_val = dict()
#     ret_val[cf.CFSP_DPDK_PKTGEN_DIRECTORY] = PKTGEN_DIR
#     ret_val[cf.CFSP_DPDK_DPDK_DIRECTORY] = PKTGEN_DPDK_DIRECTORY
#     ret_val[cf.CFSP_DPDK_PROGRAM_NAME] = PKTGEN_PROGRAM
#     ret_val[cf.CFSP_DPDK_COREMASK] = PKTGEN_COREMASK
#     ret_val[cf.CFSP_DPDK_MEMORY_CHANNEL] = PKTGEN_MEMCHANNEL
#     ret_val[cf.CFSP_DPDK_BUS_SLOT_NIC_1] = PKTGEN_BUS_SLOT_NIC_1
#     ret_val[cf.CFSP_DPDK_BUS_SLOT_NIC_2] = PKTGEN_BUS_SLOT_NIC_2
#     ret_val[cf.CFSP_DPDK_NAME_IF_1] = PKTGEN_NAME_NIC_1
#     ret_val[cf.CFSP_DPDK_NAME_IF_2] = PKTGEN_NAME_NIC_2
#     return ret_val


# ------------------------------------------------------
# Configuration Variables from Config File
# ------------------------------------------------------
# def get_deploy_vars_from_conf_file():
#     variables = dict()
#     types = dict()
#     constraints = list()
#
#     all_variables = common.CONF_FILE.get_variable_list(cf.CFS_EXPERIMENT_VNF)
#     for var in all_variables:
#         if var == 'constraint':
#             all_constraints = common.CONF_FILE.get_variable(cf.CFS_EXPERIMENT_VNF, var)
#             for c in re.findall(r'\[(.+?)\]', all_constraints):
#                 values = c.split(',')
#                 constraint = dict()
#                 for v in values:
#                     key, val = v.split(':')
#                     key = re.findall(r'\"(.+?)\"', key)[0].lower()
#                     val = re.findall(r'\"(.+?)\"', val)[0]
#                     constraint[key] = val
#                 constraints.append(constraint)
#         else:
#             v = common.CONF_FILE.get_variable(cf.CFS_EXPERIMENT_VNF, var)
#             var_type = re.findall(r'@\w*', v)
#             values = re.findall(r'\"(.+?)\"', v)
#             variables[var] = values
#             try:
#                 types[var] = var_type[0][1:]
#             except IndexError:
#                 pass
#                 #LOG.debug("No type has been specified for variable " + var)
#     return variables, constraints or [{}]


# ------------------------------------------------------
# usecase from Config File
# ------------------------------------------------------
# def get_usecases_from_conf_file():
#     requested_usecases = list()
#     usecases = \
#         common.CONF_FILE.get_variable(
#             cf.CFS_GENERAL, cf.CFSG_USECASES).split(', ')
#     for usecase in usecases:
#         requested_usecases.append(usecase)
#     return requested_usecases


def byteify(input):
    # remove the unicode from a json object.
    # carefull with max recursion depth, see below
    # http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python/13105359#13105359
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input