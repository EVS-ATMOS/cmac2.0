#!/usr/bin/env python
""" CMAC Corrected Precipitation Radar Moments in Antenna Coordinates

Using fuzzy logic, scipy, and more to identify gates as rain, melting,
snow, no clutter, and second trip. Many fields such as reflectivity and
coorelation coefficient are used, but also SNR and sounding data is used.
More information can be found at https://www.arm.gov/data/data-sources/cmac-69

"""


import glob

from numpy.distutils.core import setup
from numpy.distutils.misc_util import Configuration


DOCLINES = __doc__.split("\n")

NAME = 'cmac'
MAINTAINER = 'Scott Collis, Zach Sherman and Robert Jackson'
DESCRIPTION = DOCLINES[0]
# INSTALL_REQUIRES = ['pyart', 'scipy', scikit-fuzzy, CSU_radartools]
LONG_DESCRIPTION = "\n".join(DOCLINES[2:])
LICENSE = 'BSD'
PLATFORMS = "Linux"
MAJOR = 0
MINOR = 1
MICRO = 0
# SCRIPTS = glob.glob('scripts/*')
TEST_SUITE = 'nose.collector'
TESTS_REQUIRE = ['nose']
VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

def configuration(parent_package='', top_path=None):
    """ Configuration of the cmac package. """
    config = Configuration(None, parent_package, top_path)
    config.set_options(ignore_setup_xxx_py=True,
                       assume_default_configuration=True,
                       delegate_options_to_subpackages=True,
                       quiet=True)

    config.add_subpackage('cmac')
    return config


def setup_package():
    """ Setup of cmac package. """
    setup(
        name=NAME,
        maintainer=MAINTAINER,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        version=VERSION,
        license=LICENSE,
        platforms=PLATFORMS,
        configuration=configuration,
        include_package_data=True,
        # install_requires=INSTALL_REQUIRES,
        test_suite=TEST_SUITE,
        tests_require=TESTS_REQUIRE,
        # scripts=SCRIPTS,
    )

if __name__ == '__main__':
    setup_package()
