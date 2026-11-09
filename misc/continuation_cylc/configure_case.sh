#!/bin/bash

set -euo pipefail

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
