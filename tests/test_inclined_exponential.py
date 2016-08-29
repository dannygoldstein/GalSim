# Copyright (c) 2012-2016 by the GalSim developers team on GitHub
# https://github.com/GalSim-developers
#
# This file is part of GalSim: The modular galaxy image simulation toolkit.
# https://github.com/GalSim-developers/GalSim
#
# GalSim is free software: redistribution and use in source and binary forms,
# with or without modification, are permitted provided that the following
# conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions, and the disclaimer given in the accompanying LICENSE
#    file.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions, and the disclaimer given in the documentation
#    and/or other materials provided with the distribution.
#

from __future__ import print_function
import numpy as np
import os
import sys

from galsim_test_helpers import *

try:
    import galsim
except ImportError:
    path, filename = os.path.split(__file__)
    sys.path.append(os.path.abspath(os.path.join(path, "..")))
    import galsim

# set up any necessary info for tests
# Note that changes here should match changes to test image files
image_dir = './inclined_exponential_images'

# Values here are strings, so the filenames will be sure to work (without truncating zeros)
fluxes = ("1.0", "10.0", "0.1", "1.0", "1.0", "1.0")
image_inc_angles = ("0.0", "1.3", "0.2", "0.01", "0.1", "0.78")
image_scale_radii = ("3.0", "3.0", "3.0", "3.0", "2.0", "2.0")
image_scale_heights = ("0.3", "0.5", "0.5", "0.5", "1.0", "0.5")
image_pos_angles = ("0.0", "0.0", "0.0", "0.0", "-0.2", "-0.2")
image_nx = 64
image_ny = 64
oversampling = 1.0

@timer
def test_regression():
    """Test that the inclined exponential profile matches the results from Lance Miller's code."""
    
    for inc_angle, scale_radius, scale_height, pos_angle in zip(image_inc_angles,image_scale_radii,
                                                                image_scale_heights,image_pos_angles):
        image_filename = "galaxy_"+inc_angle+"_"+scale_radius+"_"+scale_height+"_"+pos_angle+".fits"
        image = galsim.fits.read(image_filename, image_dir)
        
        # Get float values for the details
        inc_angle=float(inc_angle)
        scale_radius=float(scale_radius)/oversampling
        scale_height=float(scale_height)/oversampling
        pos_angle=float(pos_angle)
        
        # Now make a test image
        test_profile = galsim.InclinedExponential(inc_angle*galsim.radians,scale_radius,scale_height,
                                                  gsparams=galsim.GSParams(maximum_fft_size=5000))
        
        # Rotate it by the position angle
        test_profile = test_profile.rotate(pos_angle*galsim.radians)
        
        # Draw it onto an image
        test_image = galsim.Image(image_nx,image_ny,scale=1.0)
        test_profile.drawImage(test_image,offset=(0.5,0.5)) # Offset to match Lance's
        
        # Compare to the example - Due to the different fourier transforms used, some offset is expected,
        # so we just compare in the core to two decimal places
        
        image_core = image.array[image_ny//2-2:image_ny//2+3, image_nx//2-2:image_nx//2+3]
        test_image_core = test_image.array[image_ny//2-2:image_ny//2+3, image_nx//2-2:image_nx//2+3]
        
        ratio_core = image_core / test_image_core
        
        # galsim.fits.write(test_image,"test_"+image_filename,image_dir)
        
        np.testing.assert_array_almost_equal(ratio_core, np.mean(ratio_core)*np.ones_like(ratio_core), decimal = 2,
                                             err_msg = "Error in comparison of inclined exponential profile to samples.",
                                             verbose=True)

@timer
def test_sanity():
    """ Performs various sanity checks on a set of InclinedExponential profiles. """
    
    for flux, inc_angle, scale_radius, scale_height, pos_angle in zip(fluxes,
                                                                      image_inc_angles,
                                                                      image_scale_radii,
                                                                      image_scale_heights,
                                                                      image_pos_angles):
        
        # Get float values for the details
        flux = float(flux)
        inc_angle=float(inc_angle)
        scale_radius=float(scale_radius)/oversampling
        scale_height=float(scale_height)/oversampling
        pos_angle=float(pos_angle)
        
        # Now make a test image
        test_profile = galsim.InclinedExponential(inc_angle*galsim.radians,scale_radius,scale_height,flux,
                                                  gsparams=galsim.GSParams(maximum_fft_size=5000))
        
        # Rotate it by the position angle
        test_profile = test_profile.rotate(pos_angle*galsim.radians)
        
        # Check that the k value for (0,0) is the flux
        np.testing.assert_almost_equal(test_profile.kValue(kx=0.,ky=0.),flux)
        
        # Check that the drawn flux for a large image is indeed the flux
        test_image = galsim.Image(5*image_nx,5*image_ny,scale=1.0)
        test_profile.drawImage(test_image)
        test_flux = test_image.array.sum()
        np.testing.assert_almost_equal(test_flux,flux,decimal=3)
        
        # Check that the centroid is (0,0)
        centroid = test_profile.centroid()
        np.testing.assert_equal(centroid.x, 0.)
        np.testing.assert_equal(centroid.y, 0.)
        
@timer
def test_k_limits():
    """ Check that the maxk and stepk give reasonable results for a few different profiles. """
    
    for inc_angle, scale_radius, scale_height in zip(image_inc_angles,image_scale_radii,
                                                     image_scale_heights):
        # Get float values for the details
        inc_angle=float(inc_angle)
        scale_radius=float(scale_radius)/oversampling
        scale_height=float(scale_height)/oversampling
        
        gsparams = galsim.GSParams(maximum_fft_size=5000)
    
        # Now make a test image
        test_profile = galsim.InclinedExponential(inc_angle*galsim.radians,scale_radius,scale_height,
                                                  gsparams=gsparams)
        
        # Check that the k value at maxK() is below maxk_threshold in both the x and y dimensions
        kx = test_profile.maxK()
        ky = test_profile.maxK()
        
        kx_value=test_profile.kValue(kx=kx,ky=0.)
        np.testing.assert_(np.abs(kx_value)<gsparams.maxk_threshold)
        
        ky_value=test_profile.kValue(kx=0.,ky=ky)
        np.testing.assert_(np.abs(ky_value)<gsparams.maxk_threshold)
        
        # Check that less than folding_threshold fraction of light falls outside r = pi/stepK()
        rmax = np.pi/test_profile.stepK()
        
        test_image = galsim.Image(int(10*rmax),int(10*rmax),scale=1.0)
        test_profile.drawImage(test_image)
        
        image_center = test_image.center()
        
        # Get an array of indices within the limits
        image_shape = np.shape(test_image.array)
        x, y = np.indices(image_shape, dtype=float)
        
        x -= image_center.x
        y -= image_center.y
        
        r = np.sqrt(np.square(x)+np.square(y))
        
        good = r<rmax
        
        # Get flux within the limits
        contained_flux = np.ravel(test_image.array)[np.ravel(good)].sum()
        
        # Check that we're not missing too much flux
        total_flux = 1.
        np.testing.assert_((total_flux-contained_flux)/(total_flux)<gsparams.folding_threshold)

@timer
def test_ne():
    """ Check that equality/inequality works as expected."""
    gsp = galsim.GSParams(folding_threshold=1.1e-3)
 
    gals = [galsim.InclinedExponential(0.1*galsim.radians, 3.0, 0.3),
            galsim.InclinedExponential(0.1*galsim.radians, 3.0, 0.4),
            galsim.InclinedExponential(0.2*galsim.radians, 3.0, 0.3),
            galsim.InclinedExponential(0.1*galsim.radians, 3.1, 0.3),
            galsim.InclinedExponential(0.1*galsim.radians, 3.0, 0.3, flux=0.5),
            galsim.InclinedExponential(0.1*galsim.radians, 3.0, 0.3, gsparams=gsp)]
    all_obj_diff(gals)


if __name__ == "__main__":
    test_regression()
    test_sanity()
    test_k_limits()
    test_ne()
