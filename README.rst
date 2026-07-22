CMAC
====

CMAC: Corrected Precipitation Radar Moments in Antenna Coordinates

CMAC (Corrected Moments in Antenna Coordinates) is a set of
algorithms and code that does corrections to Radar data, but also adds fields
to the original data. Using fuzzy logic CMAC also calculates gate IDs such as
rain, snow and second-trip. Some other examples of the corrections done are
velocity dealiasing and attenuation-corrected reflectivity. Example of fields
added are rain_rate_A, velocity_texture and filtered_corrected_differential_phase. 

More information can be found at https://arm.gov/data/science-data-products/vaps/cmac
 
The `Atmospheric Community Toolkit <https://arm-doe.github.io/ACT>`_ is installed in this binder
and can be used to download data for CMAC from ARM Data Discovery. For an example on how
to download ARM datastreams from Data Discovery, click `here <https://arm-doe.github.io/ACT/API/generated/act.discovery.download_data.html#act.discovery.download_data>`_.

All ARM files are in the format that is needed by CMAC for processing.

Install
-------

CMAC and the required environment can be installed by using the
instructions below::

        git clone https://github.com/ARM-Development/cmac.git
        cd cmac
        conda env create -f environment.yml
        conda activate cmac_env

If you wish to use the LP phase processing code instead of the CSU code, you will
need to set an environment variable to point to the location of the COIN-OR
libraries. This can be done by using the following command in the terminal::

        export COIN_INSTALL_DIR=/Users/yourusername/youranacondadir/envs/cmac_env

If you are using the Bringi KDP retrieval, method then this is not needed.
The Bringi method is the default method for KDP retrieval in CMAC. If you want to use the LP method, then you will need to set the environment variable as described above and then set the kdp_method argument in the config file to 'lp'.

You will need to install Anaconda Compilers for the installation of CyLP.
These compilers can be found here and differ between OS:
https://docs.conda.io/projects/conda-build/en/latest/resources/compiler-tools.html

After the compilers are installed, you should be able to install CyLP with::

        pip install git+https://github.com/coin-or/CyLP.git

Scripts such as cmac_animation and cmac_dask require additional dependencies::

        source activate cmac_env
        conda install -c menpo ffmpeg=version
        conda install dask ipyparallel

Note: For ffmpeg, depending on the user's operating system, the version will
need to be replaced with corresponding version number found here:

https://anaconda.org/menpo/ffmpeg

Using CMAC
----------

Once downloaded, CMAC can be used in the terminal. The required positional
arguments are ``radar_file``, ``sonde_file`` and ``radar_config`` (the name
of a radar configuration, e.g. ``bnf_csapr2_ppi``, that exists in
``cmac.default_config`` or in a YAML file passed via ``--config-file``).

An example::

        cmac /home/user/cmac2.0/data/radar_file.nc \
             /home/user/cmac2.0/data/sonde_file.cdf \
             bnf_csapr2_ppi

The script also accepts the following optional arguments:

``-c``, ``--config-file`` ``PATH``
    Optional YAML config file whose values override the built-in defaults
    for the given ``radar_config``.

``-cf``, ``--clutter-file`` ``PATH``
    Clutter file to use for addition of the clutter gate id.

``-o``, ``--out-radar-directory`` ``PATH``
    Output directory for the CMAC radar file. Defaults to the user home
    directory.

``-id``, ``--image-directory`` ``PATH``
    Directory to save CMAC radar quicklook images. Defaults to the user
    home directory.

``-ma``, ``--meta-append`` ``SOURCE``
    Source of metadata for the output file. ``config`` (default) uses the
    per-radar metadata from ``cmac.default_config`` / the YAML override.
    Pass a path to a JSON file to use custom metadata, or ``default`` to
    use the generic global defaults.

``--verbose`` / ``--no-verbose``
    Display debugging output. Defaults to off.

For backwards compatibility, the underscore forms of each long option
(e.g. ``--config_file``, ``--clutter_file``, ``--out_radar_directory``,
``--image_directory``, ``--meta_append``) are also accepted.

There is currently a ``default_config.py`` file with dictionaries for
radars. Additional radars can be added there, or supplied through a YAML
file passed via ``--config-file`` and selected with the ``radar_config``
positional argument. See ``documents/cmac_config_reference.md`` for a full
description of every section and key in that YAML file.

Documentation
-------------

- `notebooks/getting_started_with_cmac.ipynb <notebooks/getting_started_with_cmac.ipynb>`_ —
  a walkthrough of downloading a radar file and sounding, running ``cmac()``,
  and generating quicklooks from a Jupyter notebook.
- `documents/cmac_config_reference.md <documents/cmac_config_reference.md>`_ —
  a reference for every section and key of the YAML config file accepted via
  ``config_file`` / ``--config-file``.

Lead Developers
---------------

 - Scott Collis
 - Robert Jackson
 - Zach Sherman
 - Max Grover

Credits
-------
The Bringi KDP retrieval method is taken from CSU-RadarTools, which is a collection of radar processing tools developed by Colorado State University. 
The CSU-RadarTools can be found at https://github.com/CSU-Radarmet/CSU_RadarTools.
