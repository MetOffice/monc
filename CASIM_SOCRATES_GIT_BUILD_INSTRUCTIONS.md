# Building MONC with CASIM and SOCRATES from Git Sources

This guide explains how to build MONC using CASIM and SOCRATES from their official GitHub repositories, rather than the frozen FCM sources.

## Prerequisites

- MONC repository checked out locally
- Git installed
- FCM build system installed and configured
- Appropriate compiler modules/environment loaded

## Build Steps

### Step 1: Fetch CASIM and SOCRATES Git Repositories

Run the fetch script from the MONC root directory:

```bash
./misc/fetch_casim_socrates.sh
```

This script will:
- Clone CASIM and SOCRATES Git repositories into `../git_deps/` (by default)
- Checkout the specified Git refs (default: CASIM `vn1.3`, SOCRATES `cf83d4c`)
- Create an environment file at `../git_deps/.casim_socrates.env` with paths to both repositories

**To use custom paths or refs, see [Advanced Options](#advanced-options) below.**

### Step 2: Source the Environment File

Before running the FCM build, source the environment file created by the fetch script:

```bash
source ../git_deps/.casim_socrates.env
```

This exports the following environment variables:
- `CASIM_GIT_DIR` — path to CASIM repository
- `SOCRATES_GIT_DIR` — path to SOCRATES repository
- `MONC_GIT_DEPS_DIR` — parent directory of dependencies

### Step 3: Build MONC with FCM

Run the FCM build using the CASIM/SOCRATES Git configuration:

```bash
fcm make -f fcm-make/casim_socrates_GIT_TEST.cfg
```

You can pass additional FCM options as needed:

```bash
# Clean build
fcm make -f fcm-make/casim_socrates_GIT_TEST.cfg --new

# Build with verbose output
fcm make -f fcm-make/casim_socrates_GIT_TEST.cfg -v

# Build with specific jobs (parallel build)
fcm make -f fcm-make/casim_socrates_GIT_TEST.cfg -j 8
```

## Complete Workflow Example

```bash
# From MONC root directory:

# 1. Fetch repositories
./misc/fetch_casim_socrates.sh

# 2. Source environment
source ../git_deps/.casim_socrates.env

# 3. Build with FCM (clean build, 8 parallel jobs)
fcm make -f fcm-make/casim_socrates_GIT_TEST.cfg --new -j 8
```

## Advanced Options

### Using Custom Repository Locations

By default, repositories are cloned to `../git_deps/casim` and `../git_deps/socrates` relative to the MONC root. To use different locations:

```bash
./misc/fetch_casim_socrates.sh \
  --deps-dir /path/to/custom/deps/directory
```

Or specify individual directories:

```bash
./misc/fetch_casim_socrates.sh \
  --casim-dir /path/to/casim \
  --socrates-dir /path/to/socrates
```

### Checking Out Different Versions

By default, the script checks out:
- CASIM: Git tag `vn1.3` (corresponding to SVN trunk@10614)
- SOCRATES: Git commit `cf83d4c` (corresponding to SVN trunk@989)

To use different Git refs (tags, branches, or commit hashes):

```bash
./misc/fetch_casim_socrates.sh \
  --casim-ref <tag-or-commit> \
  --socrates-ref <tag-or-commit>
```

Example:
```bash
./misc/fetch_casim_socrates.sh \
  --casim-ref main \
  --socrates-ref HEAD
```

After running the fetch script with new refs, re-source the environment file:

```bash
source ../git_deps/.casim_socrates.env
```

Then proceed with the FCM build.

## Troubleshooting

### "CASIM_GIT_DIR not found" or similar errors

Make sure you've sourced the environment file:

```bash
source ../git_deps/.casim_socrates.env
```

### Stale repository state

To update CASIM and SOCRATES to the latest refs:

```bash
./misc/fetch_casim_socrates.sh
source ../git_deps/.casim_socrates.env
fcm make -f fcm-make/casim_socrates_GIT_TEST.cfg --new
```

### Build failures with CASIM or SOCRATES

Check that the correct Git refs were checked out:

```bash
git -C $CASIM_GIT_DIR describe --tags --always
git -C $SOCRATES_GIT_DIR describe --tags --always
```

If you need different versions, use the `--casim-ref` or `--socrates-ref` options when running the fetch script.

## For Multiple Users or Machines

Each user can run:

```bash
./misc/fetch_casim_socrates.sh
```

This will clone repositories to their own `../git_deps/` directory and create a `.casim_socrates.env` file with paths relative to their machine. No shared paths or configuration needed.
