#!/bin/bash
set -euo pipefail

DATASET_NAME="${1:-}"
EVAL_HARNESS="${AGENT_EVAL_HARNESS:-$HOME/repos/agent-eval-harness}"
WORKTREE="${2:-anova}"

if [ -z "$DATASET_NAME" ]; then
    echo "Usage: $0 <dataset-name> [worktree-name]"
    echo ""
    echo "  dataset-name   Directory under datasets/ (e.g., harbor-maas-v1)"
    echo "  worktree-name  Eval harness worktree (default: anova)"
    echo ""
    echo "Environment:"
    echo "  AGENT_EVAL_HARNESS  Path to agent-eval-harness repo"
    echo "                      (default: ~/repos/agent-eval-harness)"
    echo ""
    echo "Available datasets:"
    ls -d datasets/*/ 2>/dev/null | sed 's|datasets/||;s|/||' | sed 's/^/  /'
    exit 1
fi

DATASET_DIR="datasets/$DATASET_NAME"
if [ ! -d "$DATASET_DIR" ]; then
    echo "Error: dataset not found: $DATASET_DIR"
    exit 1
fi

if [ ! -f "$DATASET_DIR/eval.yaml" ]; then
    echo "Error: no eval.yaml in $DATASET_DIR"
    exit 1
fi

TARGET_WORKTREE="$EVAL_HARNESS/.claude/worktrees/$WORKTREE"
if [ ! -d "$TARGET_WORKTREE" ]; then
    echo "Error: worktree not found: $TARGET_WORKTREE"
    echo "Available worktrees:"
    ls -d "$EVAL_HARNESS/.claude/worktrees"/*/ 2>/dev/null | xargs -I{} basename {} | sed 's/^/  /'
    exit 1
fi

TARGET_DATASET="$TARGET_WORKTREE/datasets/$DATASET_NAME"

echo "Deploying dataset: $DATASET_NAME"
echo "  Source: $DATASET_DIR"
echo "  Target: $TARGET_DATASET"
echo ""

mkdir -p "$TARGET_WORKTREE/datasets"
rm -rf "$TARGET_DATASET"
cp -r "$DATASET_DIR" "$TARGET_DATASET"

cp "$DATASET_DIR/eval.yaml" "$TARGET_WORKTREE/eval.yaml"

TASK_COUNT=$(ls -d "$TARGET_DATASET"/task-*/ 2>/dev/null | wc -l | tr -d ' ')
echo "Deployed $TASK_COUNT tasks to $TARGET_WORKTREE"
echo "eval.yaml copied to $TARGET_WORKTREE/eval.yaml"
echo ""
echo "Next steps:"
echo "  cd $TARGET_WORKTREE"
echo "  claude"
echo "  /eval-anova --dry-run    # validate + estimate cost"
echo "  /eval-anova              # run the experiment"
