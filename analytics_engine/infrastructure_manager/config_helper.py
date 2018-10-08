"""
Methods to read the configurations for analytics.
"""
from ConfigParser import SafeConfigParser
import os

class ConfigHelper:
    _CONFIG = None
    _config_file = None

    SERVICE_NAME = 'analytics_engine'
    INSTALL_BASE_DIR = os.path.join(os.path.expanduser('~'), SERVICE_NAME)
    CONF_FILE_LOCATION = os.path.join(INSTALL_BASE_DIR, 'analytics_engine.conf')

    @staticmethod
    def _setup():
        # Set Configs just once, as we only have one config file.
        ConfigHelper._CONFIG = SafeConfigParser()
        ConfigHelper._config_file = ConfigHelper.CONF_FILE_LOCATION

        print("Config {}".format(ConfigHelper._config_file))
        if not os.path.isfile(ConfigHelper._config_file):
            message = "File {} does not exist".format(ConfigHelper._config_file)
            raise ValueError(message + ' ' + ConfigHelper._config_file)
        print("Config {}".format(ConfigHelper._config_file))

        ConfigHelper._CONFIG.read(ConfigHelper._config_file)

    @staticmethod
    def get(section, attribute):
        """
        Returns config value from the INI file based on the section and
        attribute parameters.
        :param config:
        :param section: Section of the ini file. Section is the identifier in
        the ini file surrounded by square brackets, e.g ["DEFAULT"].
        :param attribute: Attribute name  in the ini file, which is under the
        section specified.
        :return: Value of the attribute specified.
        """
        if ConfigHelper._CONFIG is None:
            ConfigHelper._setup()
        elif section == 'DEFAULT':
            return ConfigHelper._CONFIG.defaults().get(attribute)
        return ConfigHelper._CONFIG.get(section, attribute)


