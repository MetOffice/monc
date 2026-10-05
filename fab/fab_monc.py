#!/usr/bin/env python3
##############################################################################
# (c) Crown copyright Met Office. All rights reserved.
# For further details please refer to the file COPYRIGHT
# which you should have received as part of this distribution
##############################################################################

'''
This module contains a Fab-based build script for the Unified Model.
'''

import argparse
import logging
from pathlib import Path
from typing import cast, Iterable, List, Optional, Union

from fab.fab_base.fab_base import FabBase
from fab.api import (AddFlags, Category, Compiler, Exclude, find_source_files,
                     grab_files, Include, root_inc_files)


class FabMonc(FabBase):
    '''
    A class to build MONC using Fab as base class.

    :param str name: name of the build.
    '''

    def __init__(self, name):
        super().__init__(name)
        # We need to overwrite the name of the main program, it
        # defaults to `monc`.
        self.set_root_symbols("monc_driver")
        # Store the root directory of MONC:
        self._root = Path(__file__).resolve().parents[1]

    def define_command_line_options(
            self,
            parser: Optional[argparse.ArgumentParser] = None
            ) -> argparse.ArgumentParser:
        '''
        Adds the additionally required command line options for the UM.

        :param Optional[argparse.ArgumentParser] parser: a pre-defined
        argument parser. If not, a new instance will be created.

        :returns: the argument parser with the UM specific options added.
        '''

        parser = super().define_command_line_options(parser)
        parser = cast(argparse.ArgumentParser, parser)

        monc_config = parser.add_argument_group("MONC configuration options")
        monc_config.add_argument(
            "--petsc", action="store_true", default=False,
            help="Enable the usage of PETSc.")
        monc_config.add_argument(
            "--casim", action="store_true", default=False,
            help="Enable the usage of CASIM.")
        monc_config.add_argument(
            "--casim-profile-dgs", action="store_true",
            default=False, help="Enable the usage of CASIM profile dgs.")
        monc_config.add_argument(
            "--socrates", action="store_true", default=False,
            help="Enable the usage of SOCRATES.")

        return parser

    def grab_files_step(self) -> None:
        '''
        Extracts all the required source files from the repositories.
        It then sets the include path (since include files are not
        copied into the build tree).

        :raises RuntimeError: the expected `rose-meta/um-atmos` file
            does not exist, indicating an invalid directory structure.
        '''
        for directory in ["components", "io", "misc", "model_core",
                          "testcases",
                          "monc_driver.F90"]:
            grab_files(self.config, self._root / directory,
                       dst_label=directory)

    def find_source_files_step(
            self,
            path_filters: Optional[Iterable[Union[Exclude, Include]]] = None
            ):
        '''
        Finds all the UM sources files to analyse. If the tests are
        being compiled, only search the tests directory.
        '''
        path_filters = [Exclude("model_core/test")]
        if self.args.petsc:
            # Exclude the stub if we are using PETSc
            path_filters.append(Exclude("petsc_solver_stub.F90"))
        else:
            # No PETSc, ignore the solver (and use the stub)
            path_filters.append(Exclude("petsc_solver.F90"))

        if self.args.casim:
            path_filters.append(Exclude("casim_stub.F90"))
        else:
            path_filters.append(Exclude("casim.F90"))

        if self.args.casim_profile_dgs:
            path_filters.append(Exclude("casim_profile_dgs_stub.F90"))
        else:
            path_filters.append(Exclude("casim_profile_dgs.F90"))

        if self.args.socrates:
            path_filters.append(Exclude("socrates_couple_stub.F90"))
        else:
            path_filters.append(Exclude("socrates_couple.F90"))

        find_source_files(self.config,
                          path_filters=path_filters)
        root_inc_files(self.config, [".h", ".static"])

    def define_preprocessor_flags_step(self) -> None:
        '''
        Defines the preprocessor flags.
        '''
        super().define_preprocessor_flags_step()

        flags = ['-DU_ACTIVE', '-DV_ACTIVE', '-DW_ACTIVE',
                 '-DENFORCE_THREAD_SAFETY', '-D__DARWIN',
                 '-D_XOPEN_SOURCE=700',
                 '-I$output',
                 ]
        if self.args.profile == "debug":
            flags.append("-DDEBUG_MODE")

        self.add_preprocessor_flags(flags)

    def compile_fortran_step(
            self,
            common_flags: Optional[List[str]] = None,
            path_flags: Optional[List[AddFlags]] = None
            ) -> None:

        fc = self.config.tool_box.get_tool(Category.FORTRAN_COMPILER)
        fc = cast(Compiler, fc)
        new_flags = []
        if common_flags:
            new_flags.extend(common_flags)

        super().compile_fortran_step(common_flags=new_flags,
                                     path_flags=path_flags)

    def get_linker_flags(self) -> List[str]:
        return ["netcdf"]


# ==========================================================================
if __name__ == "__main__":

    # Enable full fab logging for now:
    logger = logging.getLogger('fab')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    fab_monc = FabMonc("monc")
    fab_monc.build()
