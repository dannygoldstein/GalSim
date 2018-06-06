# Copyright (c) 2012-2018 by the GalSim developers team on GitHub
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
"""@file gsparams.py
This file defines the GSParams class.
"""

from . import _galsim
from .errors import convert_cpp_errors

class GSParams(object):
    """GSParams stores a set of numbers that govern how GSObjects make various speed/accuracy
    tradeoff decisions.

    All GSObjects can take an optional parameter named `gsparams`, which would be an instance of
    this class.  e.g.

        >>> gsp = galsim.GSParams(folding_threshold=1.e-3)
        >>> gal = galsim.Sersic(n=3.4, half_light_radius=3.2, flux=200, gsparams=gsp)

    Note that `gsparams` needs to be provided when the object is initialized, rather than when the
    object is drawn (as would perhaps be slightly more intuitive), because most of the relevant
    approximations happen during the initialization of the object, rather than during the actual
    rendering.

    Initialization
    --------------

    All parameters have reasonable default values.  You only need to specify the ones you want
    to change.

    @param minimum_fft_size     The minimum size of any FFT that may need to be performed.
                                [default: 128]
    @param maximum_fft_size     The maximum allowed size of an image for performing an FFT.  This
                                is more about memory use than accuracy.  We have this maximum
                                value to help prevent the user from accidentally trying to perform
                                an extremely large FFT that crashes the program. Instead, GalSim
                                will raise an exception indicating that the image is too large,
                                which is often a sign of an error in the user's code. However, if
                                you have the memory to handle it, you can raise this limit to
                                allow the calculation to happen. [default: 8192]
    @param folding_threshold    This sets a maximum amount of real space folding that is allowed,
                                an effect caused by the periodic nature of FFTs.  FFTs implicitly
                                use periodic boundary conditions, and a profile specified on a
                                finite grid in Fourier space corresponds to a real space image
                                that will have some overlap with the neighboring copies of the real
                                space profile.  As the step size in k increases, the spacing
                                between neighboring aliases in real space decreases, increasing the
                                amount of folded, overlapping flux.  `folding_threshold` is used to
                                set an appropriate step size in k to allow at most this fraction of
                                the flux to be folded.
                                This parameter is also relevant when you let GalSim decide how
                                large an image to use for your object.  The image is made to be
                                large enough that at most a fraction `folding_threshold` of the
                                total flux is allowed to fall off the edge of the image.
                                [default: 5.e-3]
    @param stepk_minimum_hlr    In addition to the above constraint for aliasing, also set stepk
                                such that pi/stepk is at least `stepk_minimum_hlr` times the
                                profile's half-light radius (for profiles that have a well-defined
                                half-light radius). [default: 5]
    @param maxk_threshold       This sets the maximum amplitude of the high frequency modes in
                                Fourier space that are excluded by truncating the FFT at some
                                maximum k value. Lowering this parameter can help minimize the
                                effect of "ringing" if you see that in your images.
                                [default: 1.e-3]
    @param kvalue_accuracy      This sets the accuracy of values in Fourier space. Whenever there
                                is some kind of approximation to be made in the calculation of a
                                Fourier space value, the error in the approximation is constrained
                                to be no more than this value times the total flux.
                                [default: 1.e-5]
    @param xvalue_accuracy      This sets the accuracy of values in real space. Whenever there is
                                some kind of approximation to be made in the calculation of a
                                real space value, the error in the approximation is constrained
                                to be no more than this value times the total flux.
                                [default: 1.e-5]
    @param table_spacing        Several profiles use lookup tables for either the Hankel transform
                                (Sersic, Moffat) or the real space radial function (Kolmogorov).
                                We try to estimate a good spacing between values in the lookup
                                tables based on either `xvalue_accuracy` or `kvalue_accuracy` as
                                appropriate. However, you may change the spacing with this
                                parameter. Using `table_spacing < 1` will use a spacing value that
                                is that much smaller than the default, which should produce more
                                accurate interpolations. [default: 1]
    @param realspace_relerr     This sets the relative error tolerance for real-space integration.
                                [default: 1.e-4]
    @param realspace_abserr     This sets the absolute error tolerance for real-space integration.
                                [default: 1.e-6]
                                The estimated integration error for the flux value in each pixel
                                when using the real-space rendering method (either explicitly with
                                `method='real_space'` or if it is triggered automatically with
                                `method='auto'`) is constrained to be no larger than either
                                `realspace_relerr` times the pixel flux or `realspace_abserr`
                                times the object's total flux.
    @param integration_relerr   The relative error tolerance for integrations other than real-space
                                rendering. [default: 1.e-6]
    @param integration_abserr   The absolute error tolerance for integrations other than real-space
                                rendering. [default: 1.e-8]
    @param shoot_accuracy       This sets the relative accuracy on the total flux when photon
                                shooting.  The photon shooting algorithm at times needs to make
                                approximations, such as how high in radius it needs to sample the
                                radial profile. When such approximations need to be made, it makes
                                sure that the resulting fractional error in the flux will be at
                                most this much. [default: 1.e-5]
    @param allowed_flux_variation      The maximum range of allowed (abs value of) photon fluxes
                                within an interval before the rejection sampling algorithm is
                                invoked for photon shooting. [default: 0.81]
    @param range_division_for_extrema  The number of parts into which to split a range to bracket
                                extrema when photon shooting. [default: 32]
    @param small_fraction_of_flux      When photon shooting, intervals with less than this fraction
                                of probability are considered ok to use with the dominant-sampling
                                algorithm. [default: 1.e-4]
    """
    def __init__(self, minimum_fft_size=128, maximum_fft_size=8192,
                 folding_threshold=5.e-3, stepk_minimum_hlr=5, maxk_threshold=1.e-3,
                 kvalue_accuracy=1.e-5, xvalue_accuracy=1.e-5, table_spacing=1,
                 realspace_relerr=1.e-4, realspace_abserr=1.e-6,
                 integration_relerr=1.e-6, integration_abserr=1.e-8,
                 shoot_accuracy=1.e-5, allowed_flux_variation=0.81,
                 range_division_for_extrema=32, small_fraction_of_flux=1.e-4):
        self._minimum_fft_size = minimum_fft_size
        self._maximum_fft_size = maximum_fft_size
        self._folding_threshold = folding_threshold
        self._stepk_minimum_hlr = stepk_minimum_hlr
        self._maxk_threshold = maxk_threshold
        self._kvalue_accuracy = kvalue_accuracy
        self._xvalue_accuracy = xvalue_accuracy
        self._table_spacing = table_spacing
        self._realspace_relerr = realspace_relerr
        self._realspace_abserr = realspace_abserr
        self._integration_relerr = integration_relerr
        self._integration_abserr = integration_abserr
        self._shoot_accuracy = shoot_accuracy
        self._allowed_flux_variation = allowed_flux_variation
        self._range_division_for_extrema = range_division_for_extrema
        self._small_fraction_of_flux = small_fraction_of_flux

        # This is the thing that is needed for any c++ calls.
        with convert_cpp_errors():
            self._gsp = _galsim.GSParams(*self._getinitargs())

    # Make all the attributes read-only
    @property
    def minimum_fft_size(self): return self._minimum_fft_size
    @property
    def maximum_fft_size(self): return self._maximum_fft_size
    @property
    def folding_threshold(self): return self._folding_threshold
    @property
    def stepk_minimum_hlr(self): return self._stepk_minimum_hlr
    @property
    def maxk_threshold(self): return self._maxk_threshold
    @property
    def kvalue_accuracy(self): return self._kvalue_accuracy
    @property
    def xvalue_accuracy(self): return self._xvalue_accuracy
    @property
    def table_spacing(self): return self._table_spacing
    @property
    def realspace_relerr(self): return self._realspace_relerr
    @property
    def realspace_abserr(self): return self._realspace_abserr
    @property
    def integration_relerr(self): return self._integration_relerr
    @property
    def integration_abserr(self): return self._integration_abserr
    @property
    def shoot_accuracy(self): return self._shoot_accuracy
    @property
    def allowed_flux_variation(self): return self._allowed_flux_variation
    @property
    def range_division_for_extrema(self): return self._range_division_for_extrema
    @property
    def small_fraction_of_flux(self): return self._small_fraction_of_flux

    @staticmethod
    def check(gsparams, default=None):
        """Checks that gsparams is either a valid GSParams instance or None.

        In the former case, it returns gsparams, in the latter it returns default
        (GSParams.default if no other default specified).
        """
        if gsparams is None:
            return default if default is not None else GSParams.default
        elif not isinstance(gsparams, GSParams):
            raise TypeError("Invalid GSParams: %s"%gsparams)
        else:
            return gsparams

    # Define once the order of args in __init__, since we use it a few times.
    def _getinitargs(self):
        return (self.minimum_fft_size, self.maximum_fft_size,
                self.folding_threshold, self.stepk_minimum_hlr, self.maxk_threshold,
                self.kvalue_accuracy, self.xvalue_accuracy, self.table_spacing,
                self.realspace_relerr, self.realspace_abserr,
                self.integration_relerr, self.integration_abserr,
                self.shoot_accuracy, self.allowed_flux_variation,
                self.range_division_for_extrema, self.small_fraction_of_flux)

    def __getstate__(self): return self._getinitargs()
    def __setstate__(self, state): self.__init__(*state)

    def __repr__(self):
        return 'galsim.GSParams(%r,%r,%r,%r,%r,%r,%r,%r,%r,%r,%r,%r,%r,%r,%r,%r)'% \
                self._getinitargs()

    def __eq__(self, other):
        return isinstance(other, GSParams) and self._getinitargs() == other._getinitargs()
    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(repr(self))

# We use the default a lot, so make it a class attribute.
GSParams.default = GSParams()
