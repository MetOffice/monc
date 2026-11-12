#!/bin/bash
# Some content in this file was generated or refactored with assistance from
# - University of Reading Microsoft Copilot (OpenAI GPT-5.6 SoI); PR #9.

set -euo pipefail # fail loudly:
# -e:          exit on error;
# -u:          undefined variables are errors;
# -o pipefail: pipeline status is nonzero if ANY command in pipeline fails,
#              not just the last command

cd "$MONC_ROOT"

cycle="${CYLC_TASK_CYCLE_POINT:-${CYLC_CYCLE_POINT:-1}}"

echo "cycle=$cycle"
echo "STDOUT_DIR=$STDOUT_DIR"
echo "RUN_NAME=$RUN_NAME"

latest_output=$(
    ls -rt1 \
    "${STDOUT_DIR}/output_${RUN_NAME}"* \
    2>/dev/null | tail -1 || true
)

if [ -z "$latest_output" ]
then
    echo "No MONC output files found"
    exit 1
fi

echo "latest_output=$latest_output"

terminated_run=0

# Search for run termination statements in previous cycle output log file

search_line=$(grep \
    "Model run complete due to model time" \
    "$latest_output" || true)

if [ -n "$search_line" ]
then
    echo "Searching for model-time termination..."
    
    mtime=$(
	echo "$search_line" |
	sed -n 's/.*model time \([0-9.]*\).*/\1/p'
    )

    echo \
    "Terminating chain run as MONC has exceeded termination time, model time is $mtime seconds"

    terminated_run=1

else

    search_line=$(grep \
        "messages file containing termination command" \
        "$latest_output" || true)

    if [ -n "$search_line" ]
    then
	echo "Searching for termination-command termination..."
	
        mtime=$(
	    echo "$search_line" |
	    sed -n 's/.*model time \([0-9.]*\).*/\1/p'
        )

        echo \
        "Terminating chain run as MONC was instructed to finish, model time is $mtime seconds"

        terminated_run=1

    else

        search_line=$(grep \
            "timestep completion" \
            "$latest_output" || true)

        if [ -n "$search_line" ]
        then
	    echo "Searching for timestep-completion termination..."
	    
            mtime=$(
	        echo "$search_line" |
	        sed -n 's/.*model time \([0-9.]*\).*/\1/p'
            )

            echo \
            "Terminating chain run as MONC exceeded timestep limit, model time is $mtime seconds"

            terminated_run=1

        fi

    fi

fi

# Continuation logic

if [ "$terminated_run" -eq 1 ]
then
    echo "Workflow complete."
    echo "No continuation required."

    cylc message -- \
        "${CYLC_WORKFLOW_ID}" \
        "${CYLC_TASK_JOB}" \
        "STOP"

    exit 0
fi

if [ "$cycle" -ge "$MAX_CONTINUATION_RUNS" ]
then
    echo "Maximum continuation count reached."

    cylc message -- \
        "${CYLC_WORKFLOW_ID}" \
        "${CYLC_TASK_JOB}" \
        "STOP"

    exit 0
fi

echo "Continuation required."

cylc message -- \
    "${CYLC_WORKFLOW_ID}" \
    "${CYLC_TASK_JOB}" \
    "CONTINUE"

exit 0
