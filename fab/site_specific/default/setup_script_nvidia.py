#!/usr/bin/env python3

##############################################################################
# (c) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT
# which you should have received as part of this distribution
##############################################################################

'''This file contains a function that sets the default flags for the NVIDIA
compilers in the ToolRepository.

#TODO:
This flags must be checked, atm they are just copied from LFRic.

This function gets called from the default site-specific config file
'''

import argparse
from typing import cast

from fab.api import BuildConfig, Category, Compiler, Linker, ToolRepository

from nf_config import NfConfig


def setup_script_nvidia(build_config: BuildConfig,
                        args: argparse.Namespace) -> None:
    # pylint: disable=unused-argument
    '''Defines the default flags for nvfortran.

    :param build_config: the build config from which required parameters
        can be taken.
    :param args: all command line options
    '''

    tr = ToolRepository()
    nvfortran = tr.get_tool(Category.FORTRAN_COMPILER, "nvfortran")
    nvfortran = cast(Compiler, nvfortran)

    if not nvfortran.is_available:
        nvfortran = tr.get_tool(Category.FORTRAN_COMPILER, "mpif90-nvfortran")
        nvfortran = cast(Compiler, nvfortran)
        if not nvfortran.is_available:
            return

    # The base flags
    # ==============
    flags = ["-g", "-traceback",
             "-O0",                # No optimisations
             ]

    # Handle accelerator options:
    if args.openacc or args.openmp:
        host = args.host.lower()
    else:
        # Neither openacc nor openmp specified
        host = ""

    lib_flags = []
    if args.openacc:
        if host == "gpu":
            flags.extend(["-acc=gpu", "-gpu=managed"])
            lib_flags.extend(["-aclibs", "-cuda"])
        else:
            # CPU
            flags.extend(["-acc=cpu"])
    elif args.openmp:
        if host == "gpu":
            flags.extend(["-mp=gpu", "-gpu=managed"])
            lib_flags.append("-cuda")

    nvfortran.add_flags(flags, "base")

    # Debug
    # =====
    nvfortran.add_flags(["-O0", "-fp-model=strict"], "debug")

    # Safe
    # ====
    nvfortran.add_flags(["-O2", "-fp-model=strict"], "fast-debug")

    # Production
    # ==========
    nvfortran.add_flags(["-O4"], "high")

    # Set up the linker
    # =================
    linker = tr.get_tool(Category.LINKER, f"linker-{nvfortran.name}")
    linker = cast(Linker, linker)

    linker.add_post_lib_flags(lib_flags)
    # As default, use nf-config to set NetCDF linker flags. If it's not
    # available (or not working properly), the site-specific setup must
    # add netcdf definitions.
    nf_config = NfConfig()
    if nf_config.is_available:
        linker.add_lib_flags("netcdf", nf_config.get_linker_flags())
