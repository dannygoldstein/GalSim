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

# Define the class hierarchy for errors and warnings emitted by GalSim that aren't
# obviously one of the standard python errors.

from builtins import super

class GalSimError(RuntimeError):
    """The base class for GalSim-specific run-time errors.
    """

class GalSimRangeError(GalSimError, ValueError):
    """A GalSim-specific exception class indicating that some user-input value is
    outside of the allowed range of values.

    Attrubutes:

        value = the invalid value
        min = the minimum allowed value (may be None)
        max = the maximum allowed value (may be None)
    """
    def __init__(self, message, value, min, max=None):
        super().__init__(message + " Value {0!s} not in range [{1!s}, {2!s}].".format(
                         value, min, max))
        self.value = value
        self.min = min
        self.max = max


class GalSimWarning(UserWarning):
    """The base class for GalSim-emitted warnings.
    """
    pass
