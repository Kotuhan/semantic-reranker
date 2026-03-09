#!/bin/bash
# prepare-task.sh - Initialize task directory structure from template
# Usage: bash .claude/skills/task-workflow/scripts/prepare-task.sh {task-id}

set -e

TASK_ID="$1"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
TASKS_DIR="$PROJECT_ROOT/docs/tasks"
TEMPLATE_FILE="$TASKS_DIR/_template.md"
TASK_DIR="$TASKS_DIR/$TASK_ID"

if [ -z "$TASK_ID" ]; then
    echo "Error: Task ID is required"
    echo "Usage: bash prepare-task.sh {task-id}"
    exit 1
fi

if [ ! -f "$TEMPLATE_FILE" ]; then
    echo "Error: Template file not found at $TEMPLATE_FILE"
    exit 1
fi

if [ -d "$TASK_DIR" ]; then
    echo "Warning: Task directory already exists at $TASK_DIR"
    read -p "Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted."
        exit 0
    fi
fi

# Create task directory structure
echo "Creating task directory structure for $TASK_ID..."
mkdir -p "$TASK_DIR/insights"

# Copy template and replace placeholders
echo "Copying template..."
sed "s/TASK-XXX/$TASK_ID/g" "$TEMPLATE_FILE" > "$TASK_DIR/task.md"

# Create empty plan file
cat > "$TASK_DIR/plan.md" << 'EOF'
# Implementation Plan

## Overview
<!-- High-level implementation approach -->

## Steps
<!-- Detailed implementation steps from TL Agent -->

## Progress
<!-- Track progress as implementation proceeds -->

## Notes
<!-- Any additional notes or decisions -->
EOF

# Create placeholder insight files
touch "$TASK_DIR/insights/.gitkeep"

echo ""
echo "Task directory created successfully!"
echo "  Location: $TASK_DIR"
echo "  Files created:"
echo "    - task.md (from template)"
echo "    - plan.md (empty)"
echo "    - insights/ (for agent outputs)"
echo ""
echo "Next steps:"
echo "  1. Fill in the task details in task.md"
echo "  2. Run the Director agent to start the workflow"
