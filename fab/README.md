# Fab Build Scripts for MONC

This directory contains the files for building MONC with Fab.

You need Fab version 2.3.0 (or later).

## Building
The build script is a Python script that relies on Fab.
MONC can be compiled by providing the required
command line options to the script.

Please read the Fab documentation (esp the 
[introduction to the Fab base class](https://metoffice.github.io/fab/fab_base/index.html)
for details. See also the next section ('setup') if you need site-specific
modifications.

The actual build is defined by command line parameters to the
``fab_monc.py`` script. Use the ``-h`` option to list all available
options. Many options are inherited from the Fab base class, only
MONC specific options are defined in ``fab_monc.py`` and are grouped
at the end of the help output::

    MONC configuration options:
      --petsc               Enable the usage of PETSc. (default: False)
      --casim               Enable the usage of CASIM. (default: False)
      --casim-profile-dgs   Enable the usage of CASIM profile dgs. (default: False)
      --socrates            Enable the usage of SOCRATES. (default: False)

In the ``site_specific`` directory are various site-specific
setups. The main one is called ``default``, and it contains setting
for any compiler currently supported by Fab. But each site can
modify the settings. Have a look at the existing configurations
already contained in MONC, and check the
[Fab documentation](https://metoffice.github.io/fab/fab_base/config.html)
for a full explanation of the available options. 

Specific for MONC, I have added a `NfConfig.py` class, which wraps
the detection of NetCDF using the `nf-config` tools. This is a copy
of the file used in LFRic_core. A site can overwrite the settings
if e.g. `nf-config` is not available or not working properly.

An example build can be done as follows::

    ./fab_monc.py   --site nci --platform gadi --suite gnu  --profile debug

The compilers are selected by specifying a suite (Fab supports out of
the box ``gnu``, ``intel-classic``, ``intel-llvm``, ``nvidia`` and
``cray``), and it will use the corresponding Fortran and C compiler.
If MPI is enabled (which is the default), Fab will search for
corresponding ``mpif90`` and ``mpicc`` compiler wrapper, and verify
that they are indeed of the right suite. If you need to use say
a different C compiler (e.g. use ``gcc`` in an otherwise Intel build),
use the ``-cc`` command line option.

Any Fab script also supports the ``--available-compilers`` flag, which
just lists all compilers that Fab knows about that are available on the
system. Example output (of a system that has ``gfortran`` and ``mpif90``
as a wrapper for gfortran)::

    ----- Available compiler and linkers -----
    Gcc - gcc: gcc
    Mpicc - mpicc-gcc: mpicc
    Gfortran - gfortran: gfortran
    Mpif90 - mpif90-gfortran: mpif90
    Linker - linker-gcc: gcc
    Linker - linker-gfortran: gfortran
    Linker - linker-mpif90-gfortran: mpif90
    Linker - linker-mpicc-gcc: mpicc

The Fab workspace defaults to ``./fab-workspace``, but this can be
changed using the ``--fab-workspace`` command line option.

If the build finished successfully, the binary will be in the
directory ``fab-workspace/monc-debug-gfortran/``, it is
called ``monc_driver``. The actual directory name will depend on the
options specified of course.

## Setting up site-specific options
If you need site-specific options (e.g. you want to change the
default compiler flags used for your compiler), create
a directory with the name of your site and platform under
``site-specific``. Please check the existing
[Fab documentation](https://metoffice.github.io/fab/fab_base/config.html)
for examples on setting up options, or the existing
site-specific setups under ``fab/site-specific``.
