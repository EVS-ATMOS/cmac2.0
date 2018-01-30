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

CMAC 2.0 and the required environment can be installed on Linux by using the
instructions below::

        git clone https://github.com/EVS-ATMOS/cmac2.0.git
        cd cmac2.0
        conda env create -f environment.yml
        source activate cmac_env
        pip install git+https://github.com/jjhelmus/CyLP.git@py3

Note: Environments for Mac and Windows are being worked on and a simplified
environment for Linux is also in the works.

Using CMAC 2.0
--------------

Once downloaded, CMAC 2.0 can be used in the terminal. The required arguments
are radar_file, sonde_file, clutter_file and facility. There are optional
arguments such as out_radar, image_directory and sweep for the quicklooks.

An example::

        xsapr_cmac /home/user/cmac2.0/data/radar_file.nc /home/user/cmac2.0/data/sonde_file.cdf /home/user/cmac2.0/data/clutter_file.nc I5

Optional arguments can be called by using::

        -o -id -sw

Facility is the location at the ARM SGP site where the three X-SAPR radars are
located, such as facility I4, I5 and I6. There is currently a config.py file
with dictionaries for each radar. Down the road, radars such as C-SAPR can be
added to config.py and facility will most likely change to include more options
or the code will continue to increase in automation.

Lead Developers
---------------

Scott Collis
Robert Jackson
Zach Sherman
