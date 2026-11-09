#!/bin/bash

cd "$MONC_ROOT"

echo "Running from $(pwd)"

set -euo pipefail

ulimit -c unlimited

mkdir -p "$STDOUT_DIR"
mkdir -p "$CP_DIR"

RUN_MONC_CONFIG=0
RUN_MONC_CP=0
outputid=0

#
# Check executable exists.
#

if [ ! -f "$MONC_EXEC" ]
then
    echo "Error - executable $MONC_EXEC does not exist"
    exit 1
fi

#
# Current cycle number.
#

cycle="${CYLC_TASK_CYCLE_POINT:-${CYLC_CYCLE_POINT:-1}}"

#
# Find latest output and checkpoint.
#

output_filename=$(
    ls -rt1 "$STDOUT_DIR"/output_"$RUN_NAME"* \
    2>/dev/null | tail -1 || true
)

checkpoint_filename=$(
    ls -rt1 "$CP_DIR"/"$RUN_NAME"*.nc \
    2>/dev/null | tail -1 || true
)

#
# Persist continuation state between cycles.
#

STATE_DIR="${CYLC_WORKFLOW_RUN_DIR}/state"
mkdir -p "$STATE_DIR"

LAST_CHECKPOINT_FILE="${STATE_DIR}/last_checkpoint"

previous_checkpoint=""

if [ -f "$LAST_CHECKPOINT_FILE" ]
then
    previous_checkpoint=$(cat "$LAST_CHECKPOINT_FILE")
fi

#
# Replicate continuation.sh run selection logic (without output file checking as Cylc handles this automatically)
#

if [ -n "$output_filename" ] && [ -n "$checkpoint_filename" ]
then

    #
    # Previous run produced both output and checkpoint.
    # Continue only if this is a new checkpoint.
    #

    if [ -z "$previous_checkpoint" ] || \
       [ "$previous_checkpoint" != "$checkpoint_filename" ]
    then

        RUN_MONC_CP=1

    else

        echo \
        "Not running MONC as the latest checkpoint file is the same that the previous run executed with"

        exit 1

    fi

elif [ -n "$checkpoint_filename" ] && \
     [ -z "$previous_checkpoint" ]
then

    #
    # Existing checkpoint before continuation chain begins.
    #

    RUN_MONC_CONFIG=2

else

    #
    # No checkpoint available.
    #
    # Cold start.
    #

    RUN_MONC_CONFIG=1

fi

#
# Create MONC stdout.
#

outputfn="${STDOUT_DIR}/output_${RUN_NAME}_${cycle}"

echo "This cycle is controlled by:Cylc workflow ${CYLC_WORKFLOW_ID}" \
    > "$outputfn"

echo "This cycle job:${PBS_JOBID}:${PBS_JOBNAME}" \
    >> "$outputfn"

echo "Next cycle job:Managed by Cylc" \
    >> "$outputfn"

echo "" >> "$outputfn"

export OMP_NUM_THREADS=1
export MPICH_MAX_THREAD_SAFETY=multiple

NPES=$(wc -l < "$PBS_NODEFILE")

cmd="mpiexec -n ${NPES} --label --line-buffer"

echo "NPES=$NPES" >> "$outputfn"

echo "PBS_NODEFILE lines=$(wc -l < "$PBS_NODEFILE")" >> "$outputfn"

#
# Run MONC
#

set +e

# Cold start

if [ "$RUN_MONC_CONFIG" -eq 1 ]
then

    echo "Start MONC with configuration file $TESTCASE"

    eval "$cmd \
        $MONC_EXEC \
        --config=$TESTCASE \
        >> $outputfn 2>&1"

# Reconfiguration

elif [ "$RUN_MONC_CONFIG" -eq 2 ]
then

    echo "Reconfigure MONC with configuration file:"
    echo "    $TESTCASE"
    echo "Starting from checkpoint file:"
    echo "    $checkpoint_filename"

    eval "$cmd \
        $MONC_EXEC \
        --reconfig=$TESTCASE \
        --checkpoint=$checkpoint_filename \
        --retain_model_time=.false. \
        >> $outputfn 2>&1"

# Restart

elif [ "$RUN_MONC_CP" -eq 1 ]
then

    echo "Restarting MONC with checkpoint file $checkpoint_filename"

    eval "$cmd \
        $MONC_EXEC \
        --checkpoint=$checkpoint_filename \
        >> $outputfn 2>&1"

fi

# Record error state

status=$?

set -e

if [ "$status" -ne 0 ]
then
    exit "$status"
fi

#
# Preserve original error detection.
#

if grep -qi \
    'error\|Caught signal\|ATP analysis\|Segmentation' \
    "$outputfn"
then
    exit 1
fi

#
# Record checkpoint file that run started with, and name of current output file, only if run successful
#

[ -n "$checkpoint_filename" ] && \
    echo "$checkpoint_filename" > "$LAST_CHECKPOINT_FILE"

exit 0
