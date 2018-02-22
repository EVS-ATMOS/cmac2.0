CMAC 2.0
========

CMAC: Corrected Precipitation Radar Moments in Antenna Coordinates

Using fuzzy logic, scipy, and more to identify gates as rain, melting,
snow, no clutter, and second trip. Many fields such as reflectivity,
coorelation coefficient and signal to noise ration are used, but sounding
temperature from sonde data is also used.

There are many new products added to the radar fields, such as specific
attenuation, rain rate A, corrected specific differential phase, attenuation
corrected reflectivity, and more.

More information can be found at https://www.arm.gov/capabilities/vaps/xsapr-cmac-142

Install
-------

CMAC 2.0 and the required environment can be installed by using the
instructions below::

        git clone https://github.com/EVS-ATMOS/cmac2.0.git
        cd cmac2.0
        conda env create -f environment-3.6.yml
        source activate cmac_env
        export COIN_INSTALL_DIR= /Users/yourusername/youranacondadir/envs/cmac_env
        pip install git+https://github.com/jjhelmus/CyLP.git@py3

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
