#!/usr/bin/env python3

##############################################################################
# (c) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT
# which you should have received as part of this distribution
##############################################################################

'''
This file contains a function that sets the default flags for the Cray
compilers and linkers in the ToolRepository.

This function gets called from the default site-specific config file
'''

import argparse
from typing import cast

from fab.api import (BuildConfig, Category, Compiler, ContainFlags, Linker,
                     ToolRepository)

from nf_config import NfConfig


def setup_script_cray(build_config: BuildConfig,
                      args: argparse.Namespace) -> None:
    # pylint: disable=unused-argument
    '''
    Defines the default flags for ftn.

    :param build_config: the Fab build config instance from which
    required parameters can be taken.
    :type build_config: :py:class:`fab.BuildConfig`
    :param argparse.Namespace args: all command line options
    '''

    tr = ToolRepository()
    ftn = tr.get_tool(Category.FORTRAN_COMPILER, "crayftn-ftn")
    ftn = cast(Compiler, ftn)

    if not ftn.is_available:
        return

    # The base flags
    # ==============
    flags = ["-e", "m"]

    # Handle accelerator options:
    if args.openacc or args.openmp:
        host = args.host.lower()
    else:
        # Neither openacc nor openmp specified
        host = ""

    if args.openacc:
        if host == "gpu":
            flags.extend(["-h acc"])
        else:
            # CPU
            flags.extend(["-h acc"])
    elif args.openmp:
        if host == "gpu":
            flags.extend([])

    ftn.add_flags(flags, "base")
    ftn.add_flags(ContainFlags("/model_core/", ["-e", "R"]), "base")
    ftn.add_flags(ContainFlags("/io/", ["-e", "R"]), "base")

    # The following files have special flags in some modes. ContainFlags
    # uses a substring test. Add '/' to make sure we match the full filename.
    psrc = ["/conversions.f90", "/pressuresource.f90", "/fftsolver.f90",
            "/fftnorth.f90", "/fftpack.f90", "/iterativesolver.f90",
            "/iterativesolver_single_prec.f90"]

    # Debug
    # =====
    ftn.add_flags(["-g",
                   "-Ktrap=divz,inv,ovf",    # floating point checking
                   "-R", "bcdps",  # bounds, array shape, collapse,
                                   # pointer, string checking
                   "-O0"],         # No optimisation
                  "debug")

    # Safe
    # ====
    ftn.add_flags(["-O2", "-Ovector1", "-hfp0", "-hflex_mp=strict"], "safe")
    # Special flags:
    for pattern in psrc:
        ftn.add_flags(ContainFlags(pattern, ["-g", "-Ktrap=divz,inv,ovf",
                                             "-R", "bcdps", "-O0"]), "safe")

    # High
    # ====
    ftn.add_flags(["-O3"], "high")
    # Special flags:
    for pattern in psrc:
        ftn.add_flags(ContainFlags(pattern, ["-O1"]), "high")

    # Set up the linker
    # =================
    linker = tr.get_tool(Category.LINKER, f"linker-{ftn.name}")
    linker = cast(Linker, linker)

    # As default, use nf-config to set NetCDF linker flags. If it's not
    # available (or not working properly), the site-specific setup must
    # add netcdf definitions.
    nf_config = NfConfig()
    if nf_config.is_available:
        linker.add_lib_flags("netcdf", nf_config.get_linker_flags())
