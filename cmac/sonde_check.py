""" Sonde check attempts to read each sonde file with netCDF4, error
files are sent to a new directory. """

import glob
import os
import shutil
import stat

import netCDF4


files = glob.glob('/lustre/or-hydra/cades-arm/proj-shared/sgpsondewnpnC1.b1/*')

for file in files:
    try:
        sonde = netCDF4.Dataset(file)
        sonde.close()
    except OSError:
        print(file + ' is corrupt!')
        path = ('/lustre/or-hydra/cades-arm/proj-shared/'
                + 'sgpsondewnpnC1.b1/corrupt_soundings/')
        if not os.path.exists(path):
            os.makedirs(path)
            os.chmod(
                path,
                stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                stat.S_IRGRP | stat.S_IWGRP | stat.S_IXGRP)
        shutil.move(file, path)
