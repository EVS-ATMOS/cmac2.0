CMAC 2.0
========

CMAC: Corrected Precipitation Radar Moments in Antenna Coordinates

Using fuzzy logic, scipy, and more to identify gates as rain, melting,
snow, no clutter, and second trip. Many fields such as reflectivity and
coorelation coefficient are used, but also SNR and sounding data is used.

More information can be found at https://www.arm.gov/data/data-sources/cmac-69

The processing code was written by Scott Collis and the convolution code
found within pyart, used in the velocity texture function, was written by
Robert Jackson.

Install
-------

To install CMAC 2.0::

        git clone https://github.com/EVS-ATMOS/cmac2.0.git
        cd cmac2.0
        python setup.py install

Using CMAC 2.0
--------------

One download, CMAC 2.0 can be used in the terminal. The required arguments
are radar_file and sonde_file. There are optional arguments such as
radar_filepath, but also plot arguments such as image_directory, sweep,
max_latitude, min_latitude, max_longitude, and min_longitude.

An example::

        xsapr_cmac '/home/user/cmac2.0/data/radar_file.nc' '/home/user/cmac2.0/data/sonde_file.cdf'

Optional arguments can be called by using::

        -ro -id -sw -maxlat -minlat -maxlon -minlon
