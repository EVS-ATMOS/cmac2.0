"""

.. currentmodule:: cmac

X-SAPR CMAC function for determing gate ids, detect second trip returns and
more.

Functions
=========

.. autosummary::
    :toctree: generated/

    cmac
    std_convoluted_radar
    snr_and_sounding
    get_texture
    cum_score_fuzzy_logic
    fix_rain_above_bb
    do_my_fuzz
    extract_unmasked_data
    csu_to_field
    return_csu_kdp
    retrieve_qvp

"""

# Note: .processing_code has imports for all functions. This, however,
# will change on the decision of which functions are private or not. 
from .cmac import cmac
from .processing_code import std_convoluted_radar, snr_and_sounding
from .processing_code import get_texture, cum_score_fuzzy_logic
from .processing_code import fix_rain_above_bb, do_my_fuzz
from .processing_code import extract_unmasked_data, csu_to_field
from .processing_code import return_csu_kdp, retrieve_qvp

# __all__ = [s for s in dir() if not s.startswith('_')]
