#!/bin/bash
set -e

# If arguments are passed, execute them instead of the default sequence.
# This enables: docker-compose run reranker python benchmark.py
if [ $# -gt 0 ]; then
    exec "$@"
fi

# Default: run demo then evaluation
echo "=== Running Re-Ranker Demo ==="
python main.py

echo ""
echo "=== Running Evaluation ==="
python evaluate.py
