#!/bin/bash
# prepare-subtask.sh - Create subtask directory structure under a parent task
# Usage: bash prepare-subtask.sh {parent-folder} {subtask-id} {slug}
# Example: bash prepare-subtask.sh task-020-custom-web-ui 020.1 scaffolding

set -e

PARENT_FOLDER="$1"
SUBTASK_ID="$2"
SLUG="$3"

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
TASKS_DIR="$PROJECT_ROOT/docs/tasks"
PARENT_DIR="$TASKS_DIR/$PARENT_FOLDER"
TEMPLATE_FILE="$TASKS_DIR/_template/subtask.md"

if [ -z "$PARENT_FOLDER" ] || [ -z "$SUBTASK_ID" ] || [ -z "$SLUG" ]; then
    echo "Error: All three arguments are required"
    echo "Usage: bash prepare-subtask.sh {parent-folder} {subtask-id} {slug}"
    echo "Example: bash prepare-subtask.sh task-020-custom-web-ui 020.1 scaffolding"
    exit 1
fi

if [ ! -d "$PARENT_DIR" ]; then
    echo "Error: Parent task directory not found at $PARENT_DIR"
    exit 1
fi

SUBTASK_DIR="$PARENT_DIR/subtasks/${SUBTASK_ID}-${SLUG}"

if [ -d "$SUBTASK_DIR" ]; then
    echo "Warning: Subtask directory already exists at $SUBTASK_DIR"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Create subtask directory structure
echo "Creating subtask directory structure..."
mkdir -p "$SUBTASK_DIR/insights"

# Copy subtask template
if [ -f "$TEMPLATE_FILE" ]; then
    cp "$TEMPLATE_FILE" "$SUBTASK_DIR/task.md"
    echo "  Created task.md from subtask template"
else
    echo "  Warning: Subtask template not found at $TEMPLATE_FILE, creating minimal task.md"
    cat > "$SUBTASK_DIR/task.md" << EOF
# Subtask ${SUBTASK_ID}: ${SLUG}

## Parent Task
${PARENT_FOLDER}

## Description
TODO: Extract from parent TL design step

## Acceptance Criteria
TODO: Subset of parent acceptance criteria

## Files to Create/Modify
TODO: List files
EOF
fi

# Create empty plan.md
cat > "$SUBTASK_DIR/plan.md" << 'EOF'
# Implementation Plan

## Overview
<!-- DEV agent fills this during dev-planning -->

## File-by-File Changes
<!-- Detailed changes per file -->

## Verification Steps
<!-- How to verify this subtask -->
EOF

# Create empty workflow-history
cat > "$SUBTASK_DIR/insights/workflow-history.md" << EOF
# Workflow History - Subtask ${SUBTASK_ID}: ${SLUG}

_Parent task: ${PARENT_FOLDER}_
_Tracks subtask workflow stages: dev-planning → implementation → qa-verification → context-update → git-commit → done_
EOF

echo ""
echo "Subtask directory created successfully!"
echo "  Location: $SUBTASK_DIR"
echo "  Files created:"
echo "    - task.md (from subtask template)"
echo "    - plan.md (empty)"
echo "    - insights/workflow-history.md (empty)"
echo ""
echo "Next steps:"
echo "  1. Fill in task.md with details from parent TL design"
echo "  2. Run /director to start subtask workflow"
