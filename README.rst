Work Associated with the X-SAPR System at the Southern Great Plains
===================================================================

Code is still in the works.

CMAC
----

CMAC: Corrected Precipitation Radar Moments in Antenna Coordinates

Using fuzzy logic, scipy, and more to identify gates as rain, melting,
snow, no clutter, and second trip. Many fields such as reflectivity and
coorelation coefficient are used, but also SNR and sounding data is used.

More information can be found at https://www.arm.gov/data/data-sources/cmac-69

Majority of the processing code was written by Scott Collis and the
convolution code found within the processing code was written by Robert
Jackson.
