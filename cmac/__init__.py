"""
====
CMAC
====

CMAC functions for determining gate ids, detect second trip returns and
more.

    cmac
    quicklooks
    snr_and_sounding
    get_texture
    cum_score_fuzzy_logic
    do_my_fuzz
    return_csu_kdp
    retrieve_qvp
    tall_clutter

"""

from .cmac_radar import cmac, area_coverage
from .cmac_quicklooks import quicklooks
from .cmac_processing import snr_and_sounding, do_my_fuzz
from .cmac_processing import get_texture, cum_score_fuzzy_logic
from .cmac_processing import return_csu_kdp, retrieve_qvp
from .config import get_cmac_values, get_field_names
from .config import get_metadata, get_plot_values
from .data_catalouging import get_sounding_times, get_sounding_file_name
from .radar_clutter import tall_clutter

__all__ = [s for s in dir() if not s.startswith('_')]
