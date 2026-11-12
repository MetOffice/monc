#!/bin/bash
# Some content in this file was generated or refactored with assistance from
# - University of Reading Microsoft Copilot (OpenAI GPT-5.6 SoI); PR #9.

set -euo pipefail # fail loudly:
# -e:          exit on error;
# -u:          undefined variables are errors;
# -o pipefail: pipeline status is nonzero if ANY command in pipeline fails,
#              not just the last command

CASE_FILE="$1"

WORKFLOW_DIR="$(cd "$(dirname "$0")" && pwd)"

cp "$CASE_FILE" \
   "${WORKFLOW_DIR}/CASE_FILE.jinja2"

WORKFLOW_NAME=$(
    awk -F'"' '/set WORKFLOW_NAME/ {print $2; exit}' "$CASE_FILE"
)

echo "$WORKFLOW_NAME" > WORKFLOW_NAME

echo "Configured workflow to use:"
echo "  $CASE_FILE"

echo
echo "Workflow name:"
echo "  $WORKFLOW_NAME"

echo
echo "Now run:"
echo "  cylc validate ."
echo "  cylc install --workflow-name $WORKFLOW_NAME"
echo "  cylc play $WORKFLOW_NAME"
