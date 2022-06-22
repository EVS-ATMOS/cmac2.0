"""
cmac.config
===========
CMAC 2.0 Configuration.

    get_metadata
    get_field_names
    get_cmac_values
    get_plot_values

"""

from .default_config import (_DEFAULT_METADATA, _DEFAULT_FIELD_NAMES,
                             _DEFAULT_CMAC_VALUES, _DEFAULT_PLOT_VALUES,
                             _DEFAULT_ZS_RELATIONSHIPS)


def get_metadata(radar):
    """
    Return a dictionary of metadata for a given radar. An empty dictionary
    will be returned in no metadata dictionary exists for parameter radar.
    """
    if radar in _DEFAULT_METADATA:
        return _DEFAULT_METADATA[radar].copy()
    else:
        return {}


def get_field_names(radar):
    """
    Return the field name from the configuration file for a given field.
    """
    return _DEFAULT_FIELD_NAMES[radar]


def get_cmac_values(radar):
    """
    Return the values specific to a radar for processing the radar data,
    using CMAC 2.0.
    """
    return _DEFAULT_CMAC_VALUES[radar].copy()


def get_plot_values(radar):
    """
    Return the values specific to a radar for plotting the radar fields.
    """
    return _DEFAULT_PLOT_VALUES[radar].copy()

def get_zs_relationships():
    """
    Return the default set of Z-S relationships to use.
    """
    return _DEFAULT_ZS_RELATIONSHIPS
