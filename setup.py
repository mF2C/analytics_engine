"""
Analytics Engine
"""
from setuptools import setup, find_packages
from analytics_engine.common import SERVICE_NAME
from analytics_engine.common import INSTALL_BASE_DIR

setup(name=SERVICE_NAME,
      version='0.1.1',
      description=
      'Framework supporting automatic analysis of workloads',
      author='Giuliana Carullo - Intel Research and Development Ireland Ltd',
      author_email='giuliana.carullo@intel.com',
      license='TBD',
      url='www.intel.com',
      zip_safe=False,
      python_requires='>=3.5',
      namespace_packages=['analytics_engine'],
      packages=find_packages(),
      include_package_data=True,
      data_files=[
          (INSTALL_BASE_DIR, ['analytics_engine.conf']),
      ],
      entry_points={
          'console_scripts': [
              '{} = analytics_engine.engine:main'.format(
                  SERVICE_NAME)
          ]
      })

project_contributors = [
    'Giuliana Carullo', 'giuliana.carullo@intel.com',
    'Vincenzo Riccobene', 'vincenzo.m.riccobene@intel.com',
    'Kevin Mullery', 'kevinx.mullery@intel.com'
    'Marcin Spoczynski', 'marcin.spoczynski@intel.com',
    'Gordon Wallace', 'gordon.wallace@intel.com'
    'Eugene Ryan', 'eugenex.ryan@intel.com'
]
