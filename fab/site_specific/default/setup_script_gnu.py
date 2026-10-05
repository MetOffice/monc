#!/usr/bin/env python3

##############################################################################
# (c) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT
# which you should have received as part of this distribution
##############################################################################

'''This file contains a function that sets the default flags for all
GNU based compilers in the ToolRepository.

This function gets called from the default site-specific config file
'''

import argparse
from typing import cast

from fab.api import (BuildConfig, Category, Compiler, ContainFlags, Linker,
                     ToolRepository)

from nf_config import NfConfig


def setup_script_gnu(build_config: BuildConfig,
                     args: argparse.Namespace) -> None:
    # pylint: disable=unused-argument
    '''Defines the default flags for all GNU compilers.

    :para build_config: the build config from which required parameters
        can be taken.
    :param args: all command line options
    '''

    tr = ToolRepository()
    gfortran = tr.get_tool(Category.FORTRAN_COMPILER, "gfortran")

    if not gfortran.is_available:
        gfortran = tr.get_tool(Category.FORTRAN_COMPILER, "mpif90-gfortran")
        if not gfortran.is_available:
            return
    gfortran = cast(Compiler, gfortran)

    gcc = tr.get_tool(Category.C_COMPILER, "gcc")
    if not gcc.is_available:
        gcc = tr.get_tool(Category.C_COMPILER, "mpif90-gcc")
        if not gcc.is_available:
            return
    gcc = cast(Compiler, gcc)

    # The base flags
    # ==============
    default_flags = ['-g']
    gfortran.add_flags(default_flags, 'base')
    if gfortran.get_version() >= (10, 0):
        gfortran.add_flags("-fallow-argument-mismatch", "base")
    gfortran.add_flags(ContainFlags("/model_core/", "-frecursive"), "base")
    gfortran.add_flags(ContainFlags("/io/", "-frecursive"), "base")

    # The following files have special flags in some modes. ContainFlags
    # uses a substring test. Add '/' to make sure we match the full filename.
    psrc = ["/conversions.f90", "/pressuresource.f90", "/fftsolver.f90",
            "/fftnorth.f90", "/fftpack.f90", "/iterativesolver.f90",
            "/iterativesolver_single_prec.f90"]

    # Debug
    # =====
    gfortran.add_flags(['-O0', '-Wall', '-fcheck=all',
                        '-ffpe-trap=zero,invalid,overflow',
                        '-fallow-invalid-boz'], "debug")
    gcc.add_flags(["-fcommon"], "debug")

    # Safe
    # ====
    gfortran.add_flags(['-O2', '-fbounds-check', '-fallow-invalid-boz',
                        '-fallow-invalid-boz'], "safe")
    gcc.add_flags(["-fcommon"], "safe")

    for pattern in psrc:
        gfortran.add_flags(ContainFlags(pattern,
                                        ["-O1",
                                         "-ffpe-trap=zero,invalid,overflow"]),
                           "safe")

    # High
    # ====
    gfortran.add_flags(['-O3', '-pg'], "high")
    for fname in psrc:
        gfortran.add_flags(ContainFlags(fname, ["-O1", "-pg"]), "debug")

    # Set up the linker
    # =================
    linker = tr.get_tool(Category.LINKER, f"linker-{gfortran.name}")
    linker = cast(Linker, linker)

    # As default, use nf-config to set NetCDF linker flags. If it's not
    # available (or not working properly), the site-specific setup must
    # add netcdf definitions.
    nf_config = NfConfig()
    if nf_config.is_available:
        linker.add_lib_flags("netcdf", nf_config.get_linker_flags())
