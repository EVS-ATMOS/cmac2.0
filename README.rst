CMAC 2.0
========

CMAC: Corrected Precipitation Radar Moments in Antenna Coordinates

CMAC 2.0 (Corrected Moments in Antenna Coordinates version 2) is a set of
algorithms and code that does corrections to Radar data, but also adds fields
to the original data. Using fuzzy logic CMAC also calculates gate IDs such as
rain, snow and second-trip. Some other examples of the corrections done are
velocity dealiasing and attenuation-corrected reflectivity. Example of fields
added are rain_rate_A, velocity_texture and filtered_corrected_differential_phase. 

More information can be found at https://www.arm.gov/capabilities/vaps/xsapr-cmac-142

Interactive notebooks on the cloud
----------------------------------
.. image:: https://binder.pangeo.io/badge_logo.svg
 :target: https://binder.pangeo.io/v2/gh/EVS-ATMOS/cmac2.0/master
 
 
The `Atmospheric Community Toolkit <https://arm-doe.github.io/ACT>`_ is installed in this binder
and can be used to download data for CMAC2.0 from ARM Data Discovery. For an example on how
to download ARM datastreams from Data Discovery, click `here <https://arm-doe.github.io/ACT/API/generated/act.discovery.download_data.html#act.discovery.download_data>`_.


All ARM files are in the format that is needed by CMAC2.0 for processing.

Install
-------

CMAC 2.0 and the required environment can be installed by using the
instructions below::

        git clone https://github.com/EVS-ATMOS/cmac2.0.git
        cd cmac2.0
        conda env create -f environment-3.6.yml
        source activate cmac_env
        export COIN_INSTALL_DIR=/Users/yourusername/youranacondadir/envs/cmac_env

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

Using CMAC 2.0
--------------

Once downloaded, CMAC 2.0 can be used in the terminal. The required arguments
are radar_file, sonde_file, clutter_file and config_dict. There are optional
arguments such as out_radar, image_directory and sweep for the quicklooks.

An example::

        cmac /home/user/cmac2.0/data/radar_file.nc /home/user/cmac2.0/data/sonde
        _file.cdf /home/user/cmac2.0/data/clutter_file.nc config_xsapr_i5

Optional arguments can be called by using::

        -o -id -sw

There is currently a config.py file with dictionaries for radars. Down the road,
radars such as C-SAPR can be added to config.py which then can be called with
the config_dict argument.

Lead Developers
---------------

 - Scott Collis
 - Robert Jackson
 - Zach Sherman
