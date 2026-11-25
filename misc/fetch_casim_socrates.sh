#!/bin/bash
# -----------------------------------------------------------------------------
# (C) Crown copyright Met Office. All rights reserved.
# The file LICENCE, distributed with this code, contains details of the terms
# under which the code may be used.
# -----------------------------------------------------------------------------
# Some content in this file was generated or refactored with assistance from
# - University of Reading Microsoft Copilot (OpenAI GPT-5.6 SoI); PR #12.

set -euo pipefail # fail loudly:
# -e:          exit on error;
# -u:          undefined variables are errors;
# -o pipefail: pipeline status is nonzero if ANY command in pipeline fails,
#              not just the last command

###############################################################################
# Repository URLs
###############################################################################

CASIM_REPO="https://github.com/MetOffice/casim.git"
SOCRATES_REPO="https://github.com/MetOffice/socrates.git"

###############################################################################
# Find MONC root
###############################################################################

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MONC_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [[ ! -d "${MONC_ROOT}/fcm-make" ]]; then
    echo "ERROR: ${MONC_ROOT} does not appear to be a MONC checkout"
    exit 1
fi

###############################################################################
# Defaults
###############################################################################

DEPS_DIR="${MONC_ROOT}/../git_deps"

CASIM_DIR=""
SOCRATES_DIR=""

CASIM_REF="vn1.3"      # Git tag corresponding to SVN trunk@10614
SOCRATES_REF="cf83d4c" # Git commit corresponding to SVN trunk@989

###############################################################################
# Help
###############################################################################

usage() {
cat << EOF
Usage:

    fetch_casim_socrates.sh [OPTIONS]

Clone/update CASIM and SOCRATES Git repositories for MONC builds.

By default repositories are placed in:

    \$MONC_ROOT/../git_deps/casim
    \$MONC_ROOT/../git_deps/socrates

The default git revisions are:
    CASIM: tag vn1.3 (corresponding to SVN trunk\@10614)
    SOCRATES: commit id cf83d4c (corresponding to SVN trunk\@

Options:

    --deps-dir PATH
        Parent directory for dependency repositories.

        Example:
            --deps-dir /scratch/user/deps

        Creates:
            /scratch/\$USER/deps/casim
            /scratch/\$USER/deps/socrates

    --casim-dir PATH
        Directory where CASIM should be cloned.

    --socrates-dir PATH
        Directory where SOCRATES should be cloned.

    --casim-ref REF
        Tag, branch or commit hash to checkout after fetching.

    --socrates-ref REF
        Tag, branch or commit hash to checkout after fetching.

    -h, --help
        Show this message.

Examples:

    fetch_casim_socrates.sh

    fetch_casim_socrates.sh \\
        --socrates-ref <socrates-commit>

    fetch_casim_socrates.sh \\
        --deps-dir /scratch/\$USER/monc_deps

    fetch_casim_socrates.sh \\
        --casim-ref <casim-commit> \\
        --socrates-ref <socrates-commit>

EOF
}

###############################################################################
# Parse arguments
###############################################################################

while [[ $# -gt 0 ]]; do
    case "$1" in
        --deps-dir)
	    [[ $# -ge 2 ]] || {
		echo "ERROR: --deps-dir requires an argument"
		exit 1
	    }
            DEPS_DIR="$2"
            shift 2
            ;;
        --casim-dir)
	    [[ $# -ge 2 ]] || {
		echo "ERROR: --casim-dir requires an argument"
		exit 1
	    }
            CASIM_DIR="$2"
            shift 2
            ;;
        --socrates-dir)
	    [[ $# -ge 2 ]] || {
		echo "ERROR: --socrates-dir requires an argument"
		exit 1
	    }
            SOCRATES_DIR="$2"
            shift 2
            ;;
        --casim-ref)
	    [[ $# -ge 2 ]] || {
		echo "ERROR: --casim-ref requires an argument"
		exit 1
	    }
            CASIM_REF="$2"
            shift 2
            ;;
        --socrates-ref)
	    [[ $# -ge 2 ]] || {
		echo "ERROR: --socrates-ref requires an argument"
		exit 1
	    }
            SOCRATES_REF="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "ERROR: Unknown option '$1'"
            echo
            usage
            exit 1
            ;;
    esac
done

###############################################################################
# Resolve dependency locations & refs
###############################################################################

CASIM_DIR="${CASIM_DIR:-${DEPS_DIR}/casim}"
SOCRATES_DIR="${SOCRATES_DIR:-${DEPS_DIR}/socrates}"

mkdir -p "$(dirname "${CASIM_DIR}")"
mkdir -p "$(dirname "${SOCRATES_DIR}")"

###############################################################################
# Clone/update CASIM
###############################################################################

if [[ ! -d "${CASIM_DIR}/.git" ]]; then
    echo "Cloning CASIM into ${CASIM_DIR}"
    git clone "${CASIM_REPO}" "${CASIM_DIR}"
else
    echo "Using existing CASIM repository: ${CASIM_DIR}"
fi

git -C "${CASIM_DIR}" fetch --all --tags

if [[ -n "${CASIM_REF}" ]]; then
    echo "Checking out CASIM ref: ${CASIM_REF}"
    git -C "${CASIM_DIR}" checkout "${CASIM_REF}"
fi

###############################################################################
# Clone/update SOCRATES
###############################################################################

if [[ ! -d "${SOCRATES_DIR}/.git" ]]; then
    echo "Cloning SOCRATES into ${SOCRATES_DIR}"
    git clone "${SOCRATES_REPO}" "${SOCRATES_DIR}"
else
    echo "Using existing SOCRATES repository: ${SOCRATES_DIR}"
fi

git -C "${SOCRATES_DIR}" fetch --all --tags

if [[ -n "${SOCRATES_REF}" ]]; then
    echo "Checking out SOCRATES ref: ${SOCRATES_REF}"
    git -C "${SOCRATES_DIR}" checkout "${SOCRATES_REF}"
fi

###############################################################################
# Write environment file for fcm-make
###############################################################################

ENV_FILE="${DEPS_DIR}/.casim_socrates.env"
mkdir -p "$(dirname "${ENV_FILE}")"

cat > "${ENV_FILE}" << ENVEOF
export CASIM_GIT_DIR="${CASIM_DIR}"
export SOCRATES_GIT_DIR="${SOCRATES_DIR}"
export MONC_GIT_DEPS_DIR="${DEPS_DIR}"
ENVEOF

echo
echo "Environment variables written to: ${ENV_FILE}"
echo "Source it before running fcm-make:"
echo "  source ${ENV_FILE}"
echo "  fcm make -f fcm-make/casim_socrates_GIT_TEST.cfg"

###############################################################################
# Summary
###############################################################################

echo
echo "================================================================="
echo "MONC_ROOT    : ${MONC_ROOT}"
echo "CASIM_DIR    : ${CASIM_DIR}"
echo "SOCRATES_DIR : ${SOCRATES_DIR}"
echo

echo "CASIM:"
echo "  Ref: $(git -C "${CASIM_DIR}" describe --tags --always)"
echo "  Hash: $(git -C "${CASIM_DIR}" rev-parse HEAD)"


echo
echo "SOCRATES:"
echo "  Ref: $(git -C "${SOCRATES_DIR}" describe --tags --always)"
echo "  Hash: $(git -C "${SOCRATES_DIR}" rev-parse HEAD)"

echo
echo "Done."
echo "================================================================="
