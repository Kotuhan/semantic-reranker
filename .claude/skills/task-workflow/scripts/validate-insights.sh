#!/bin/bash
# validate-insights.sh - Validate agent output completeness
# Usage: bash .claude/skills/task-workflow/scripts/validate-insights.sh {task-id} [agent-name]

set -e

TASK_ID="$1"
AGENT_NAME="$2"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
INSIGHTS_DIR="$PROJECT_ROOT/docs/tasks/$TASK_ID/insights"

if [ -z "$TASK_ID" ]; then
    echo "Error: Task ID is required"
    echo "Usage: bash validate-insights.sh {task-id} [agent-name]"
    exit 1
fi

if [ ! -d "$INSIGHTS_DIR" ]; then
    echo "Error: Insights directory not found at $INSIGHTS_DIR"
    echo "Run prepare-task.sh first to create the task structure."
    exit 1
fi

validate_po() {
    local file="$INSIGHTS_DIR/po-agent.md"
    echo "Validating PO Agent output..."

    if [ ! -f "$file" ]; then
        echo "  [MISSING] $file"
        return 1
    fi

    local missing=0
    for section in "Problem Statement" "Success Criteria" "Acceptance Criteria" "Out of Scope"; do
        if ! grep -q "## $section" "$file"; then
            echo "  [MISSING] Section: $section"
            missing=1
        else
            echo "  [OK] Section: $section"
        fi
    done

    return $missing
}

validate_tl() {
    local file="$INSIGHTS_DIR/tl-agent.md"
    echo "Validating TL Agent output..."

    if [ ! -f "$file" ]; then
        echo "  [MISSING] $file"
        return 1
    fi

    local missing=0
    for section in "Technical Notes" "Implementation Steps" "Test Strategy"; do
        if ! grep -q "## $section" "$file"; then
            echo "  [MISSING] Section: $section"
            missing=1
        else
            echo "  [OK] Section: $section"
        fi
    done

    return $missing
}

validate_qa() {
    local file="$INSIGHTS_DIR/qa-agent.md"
    echo "Validating QA Agent output..."

    if [ ! -f "$file" ]; then
        echo "  [MISSING] $file"
        return 1
    fi

    local missing=0
    for section in "Test Cases" "Test Coverage Matrix" "Definition of Done"; do
        if ! grep -q "## $section" "$file"; then
            echo "  [MISSING] Section: $section"
            missing=1
        else
            echo "  [OK] Section: $section"
        fi
    done

    return $missing
}

validate_fe_dev() {
    local file="$INSIGHTS_DIR/fe-dev.md"
    echo "Validating FE Developer output..."

    if [ ! -f "$file" ]; then
        echo "  [MISSING] $file"
        return 1
    fi

    local missing=0
    for section in "Overview" "Implementation Steps Analysis"; do
        if ! grep -q "## $section" "$file"; then
            echo "  [MISSING] Section: $section"
            missing=1
        else
            echo "  [OK] Section: $section"
        fi
    done

    return $missing
}

validate_be_dev() {
    local file="$INSIGHTS_DIR/be-dev.md"
    echo "Validating BE Developer output..."

    if [ ! -f "$file" ]; then
        echo "  [MISSING] $file"
        return 1
    fi

    local missing=0
    for section in "Overview" "Database Changes" "Implementation Steps Analysis"; do
        if ! grep -q "## $section" "$file"; then
            echo "  [MISSING] Section: $section"
            missing=1
        else
            echo "  [OK] Section: $section"
        fi
    done

    return $missing
}

echo "=== Insights Validation for Task: $TASK_ID ==="
echo ""

if [ -n "$AGENT_NAME" ]; then
    # Validate specific agent
    case "$AGENT_NAME" in
        po|po-agent|product-owner)
            validate_po
            ;;
        tl|tl-agent|team-lead)
            validate_tl
            ;;
        qa|qa-agent|qa-engineer)
            validate_qa
            ;;
        fe|fe-dev|frontend-developer)
            validate_fe_dev
            ;;
        be|be-dev|backend-developer)
            validate_be_dev
            ;;
        *)
            echo "Unknown agent: $AGENT_NAME"
            echo "Valid agents: po, tl, qa, fe, be"
            exit 1
            ;;
    esac
else
    # Validate all agents
    echo "Checking all agent outputs..."
    echo ""

    total=0
    passed=0

    for agent in po tl qa fe be; do
        total=$((total + 1))
        case "$agent" in
            po) validate_po && passed=$((passed + 1)) ;;
            tl) validate_tl && passed=$((passed + 1)) ;;
            qa) validate_qa && passed=$((passed + 1)) ;;
            fe) validate_fe_dev && passed=$((passed + 1)) ;;
            be) validate_be_dev && passed=$((passed + 1)) ;;
        esac
        echo ""
    done

    echo "=== Summary ==="
    echo "Passed: $passed / $total"

    if [ $passed -eq $total ]; then
        echo "All agent outputs are complete!"
        exit 0
    else
        echo "Some agent outputs are incomplete."
        exit 1
    fi
fi
