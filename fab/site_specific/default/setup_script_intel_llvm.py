#!/usr/bin/env python3

##############################################################################
# (c) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT
# which you should have received as part of this distribution
##############################################################################

'''This file contains a function that sets the default flags for all
Intel llvm based compilers in the ToolRepository (ifx, ifc). For now,
it's basically a copy of setip_script_intel_classic.

This function gets called from the default site-specific config file
'''

import argparse
from typing import cast

from fab.api import (BuildConfig, Category, Compiler, ContainFlags, Linker,
                     ToolRepository)

from nf_config import NfConfig


def setup_script_intel_llvm(build_config: BuildConfig,
                            args: argparse.Namespace) -> None:
    # pylint: disable=unused-argument, too-many-locals
    '''Defines the default flags for all Intel classic compilers.

    :para build_config: the build config from which required parameters
        can be taken.
    :param args: all command line options
    '''

    tr = ToolRepository()
    ifx = tr.get_tool(Category.FORTRAN_COMPILER, "ifx")
    ifx = cast(Compiler, ifx)

    if not ifx.is_available:
        # This can happen if ifx is not in path (in spack environments).
        # To support this common use case, see if mpif90-ifx is available,
        # and initialise this otherwise.
        ifx = tr.get_tool(Category.FORTRAN_COMPILER, "mpif90-ifx")
        ifx = cast(Compiler, ifx)
        if not ifx.is_available:
            # Since some flags depends on version, the code below requires
            # that the intel compiler actually works.
            return

    icx = tr.get_tool(Category.C_COMPILER, "icx")
    icx = cast(Compiler, icx)
    if not icx.is_available:
        icx = tr.get_tool(Category.C_COMPILER, "mpicc-icx")
        icx = cast(Compiler, icx)

    # The base flags
    # ==============
    # The following flags will be applied to all modes:
    ifx.add_flags(["-g", "-traceback", "-fp-model",  "precise"], "base")
    ifx.add_flags(ContainFlags("/model_core/", "-recursive"), "base")
    ifx.add_flags(ContainFlags("/io/", "-recursive"), "base")

    icx.add_flags(["-g", "-traceback", "-std=gnu99"], "base")

    # The following files have special flags in some modes. ContainFlags
    # uses a substring test. Add '/' to make sure we match the full filename.
    psrc = ["/conversions.f90", "/pressuresource.f90", "/fftsolver.f90",
            "/fftnorth.f90", "/fftpack.f90", "/iterativesolver.f90",
            "/iterativesolver_single_prec.f90"]

    # Debug
    # =====
    ifx.add_flags(["-O2", "-check bounds,uninit", "-no-vec"], "debug")

    # Disable all checks for the files in psrc:
    for pattern in psrc:
        ifx.add_flags(ContainFlags(pattern, ["-nocheck"]), "safe")

    # Safe
    # ====
    # No safe-mode defined for intel??

    # High
    # ====
    # AH - does not run with -O3, so standard setting is -O2 with no checking
    ifx.add_flags(["-O2", "-no-vec"], "high")

    # Set up the linker
    # =================
    linker = tr.get_tool(Category.LINKER, f"linker-{ifx.name}")
    linker = cast(Linker, linker)

    # As default, use nf-config to set NetCDF linker flags. If it's not
    # available (or not working properly), the site-specific setup must
    # add netcdf definitions.
    nf_config = NfConfig()
    if nf_config.is_available:
        linker.add_lib_flags("netcdf", nf_config.get_linker_flags())
