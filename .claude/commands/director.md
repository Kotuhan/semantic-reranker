# Director - Workflow Orchestrator

Orchestrate the agent-driven workflow for tasks: $ARGUMENTS

## ⚠️ MANDATORY COMPLETION SEQUENCE

**CRITICAL**: After `implementation`, the following stages are MANDATORY and AUTOMATIC:
```
implementation → qa-verification → context-update → arch-update → po-summary → (ask user) → git-commit → done
```
Do NOT:
- Ask user "should I continue?" for QA/context-update/arch-update/po-summary - just proceed automatically
- Skip to commit/finalize before completing all stages
- Mark task as done without context-updater running
- Run git-commit without user approval

## Workflow Stages

### Standard Task (no decomposition)
```
backlog → arch-context? → po-analysis → domain-research? → tl-design → arch-review → tech-research? → dev-planning → implementation → qa-verification* → context-update* → arch-update* → po-summary* → git-commit → done
```

### Decomposed Task (large/complex tasks)
```
Parent:  backlog → arch-context? → po-analysis → domain-research? → tl-design → arch-review → tech-research? → decomposed → (wait for subtasks) → parent-qa* → context-update* → arch-update* → po-summary* → git-commit → done
Subtask: dev-planning → implementation → qa-verification* → context-update* → git-commit → done
```

* = MANDATORY (automatic, do not ask user)
? = optional (Director decides based on criteria)
git-commit = requires user approval (user confirms testing is complete before committing)

Note: Research stages are conditional - Director proposes specialists, user decides.
Note: Decomposition is semi-automatic — Director recommends after TL design, user approves.
Note: Subtasks skip all architect stages (arch-context, arch-review, arch-update) — architect governs parent-level only.

## Instructions

### Step 1: Determine Target Task

If `$ARGUMENTS` is provided:
- Use it as the task ID (e.g., "1" or "task-001")
- Look up the task in `.taskmaster/tasks/tasks.json`

If no arguments:
- Read `.taskmaster/tasks/tasks.json`
- Find the task with:
  1. Earliest stage (not "done")
  2. All dependencies satisfied (dependency tasks are "done")
  3. Highest priority among eligible tasks
- If no eligible tasks, show status summary and suggest actions

### Step 1b: Read Workflow History (MANDATORY)

**Before reading any other context**, read the task's workflow history:

```
Read: docs/tasks/{folder}/insights/workflow-history.md
```

**Workflow-history is the source of truth for actual stage:**

| Last entry in workflow-history | Actual stage |
|-------------------------------|--------------|
| Empty/missing | `backlog` |
| "Arch Context" completed/skipped | `arch-context` |
| "PO Analysis" completed | `po-analysis` |
| "Domain Research" completed/skipped | `domain-research` |
| "TL Design" completed | `tl-design` |
| "Arch Review" completed (APPROVED) | `arch-review` |
| "Arch Review" completed (REJECTED) | `tl-design` (back to TL) |
| "Tech Research" completed/skipped | `tech-research` |
| "Task Decomposed" completed | `decomposed` |
| "Dev Planning" completed | `dev-planning` |
| "Implementation" completed | `implementation` |
| "QA Verification" completed | `qa-verification` |
| "Parent QA" completed | `parent-qa` |
| "Context Update" completed | `context-update` |
| "Arch Update" completed | `arch-update` |
| "PO Summary" completed | `po-summary` |
| "Git Commit" completed | `git-commit` |
| "Task Complete" | `done` |

**For decomposed tasks**: Also check `subtasks/*/insights/workflow-history.md` for subtask progress.

**If tasks.json stage differs from workflow-history** → workflow-history is correct, update tasks.json.

### Step 2: Read Task Context

1. Read the task's `task.md` from `docs/tasks/{folder}/task.md`
2. Read `docs/product/PRD.md` for product context
3. Read any existing insights in `docs/tasks/{folder}/insights/`
4. Read any existing research in `docs/tasks/{folder}/research/`
5. Check current stage from tasks.json

### Step 3: Determine Next Agent

Based on current stage, determine the next agent to invoke:

| Current Stage | Next Action | Prerequisites |
|---------------|-------------|---------------|
| backlog | Assess arch-context needs (Step 5h) | Task exists |
| arch-context | PO (product-owner) | Arch context complete or skipped |
| po-analysis | Assess domain research needs | PO analysis complete |
| domain-research | TL (team-lead) | Research complete or skipped |
| tl-design | Arch Review (Step 5i) — MANDATORY | TL design complete |
| arch-review (APPROVED) | Assess tech research + decomposition needs | Arch review approved |
| arch-review (REJECTED) | Back to TL with feedback | Iteration < 2; else escalate to user |
| tech-research | Assess decomposition needs | Research complete or skipped |
| decomposed | Delegate to next incomplete subtask | Subtasks created |
| dev-planning | DOER (general-purpose) | plan.md complete |
| implementation | QA (qa-engineer) | Code implemented |
| qa-verification | context-updater | QA verification complete |
| parent-qa | context-updater | All subtasks done, integrated QA complete |
| context-update | Arch Update (Step 5j) — MANDATORY | Context update complete |
| arch-update | PO Summary (product-owner) | Arch update complete |
| po-summary | git-commit (workflow command) | PO summary complete |
| git-commit | - | Move to done |

**Note on decomposition**: After arch-review APPROVED (or tech-research), the Director assesses whether to decompose. See Step 5d.
**Note on architect stages**: Subtasks skip all architect stages. See Workflow Stages above.

### Step 4: Validate Prerequisites

Before invoking agent, check:
- **For PO**: task.md exists
- **For TL**: insights/po-analysis.md exists and has acceptance criteria
- **For DEV**: insights/tl-design.md exists with implementation steps
- **For DOER**: plan.md has file-by-file implementation plan
- **For QA**: Code implemented per plan.md

If prerequisites missing, report what's needed and stop.

### Step 5: Invoke the Agent

Use the Task tool with the appropriate `subagent_type`:

For PO stage:
```
Use Task tool with subagent_type: "product-owner"
Prompt: "Analyze task in {folder}. Read PRD at docs/product/PRD.md.
Write analysis to insights/po-analysis.md and update task.md sections:
Problem, Success Criteria, Acceptance Criteria, Out of Scope.
If you have questions that cannot be answered, ask the user immediately.

When complete, provide a summary listing:
- Files read (full paths)
- Files written/modified (full paths)"
```

For TL stage:
```
Use Task tool with subagent_type: "team-lead"
Prompt: "Design implementation for task in {folder}. Read PRD, task.md,
insights/po-analysis.md, and any research/ files. Explore the codebase for patterns.
Write to insights/tl-design.md and update task.md Technical Notes
and Implementation Steps. Include complexity estimate.

When complete, provide a summary listing:
- Files read (full paths)
- Files written/modified (full paths)
- Codebase files explored"
```

For DEV stage:
```
Use Task tool with subagent_type: "backend-developer" (or frontend-developer)
Prompt: "Create detailed implementation plan for task in {folder}.
Read all context files including research/. Write plan.md with:
- File-by-file changes (files to create/modify)
- Specific code changes per file
- Code patterns to follow
- Verification steps
Do NOT write actual code, only the plan.

When complete, provide a summary listing:
- Files read (full paths)
- Files written/modified (full paths)
- Codebase files explored for patterns"
```

For DOER (implementation) stage:
```
Use Task tool with subagent_type: "general-purpose"
Prompt: "Implement the plan for task in {folder}.

MINIMAL CONTEXT START - Only read plan.md first:
1. Read ONLY {folder}/plan.md to understand what to implement
2. For each file in the plan, read only that specific file before modifying
3. Do NOT read task.md, insights/, or research/ unless plan.md explicitly references them

IMPLEMENTATION:
- Follow plan.md exactly - file by file, change by change
- Write actual code, create files, modify existing files
- Run any verification steps specified in the plan
- If the plan is unclear on a detail, ask the user

When complete, provide a summary listing:
- Files read (full paths)
- Files created (full paths)
- Files modified (full paths)
- Verification steps executed and results"
```

For QA stage:
```
Use Task tool with subagent_type: "qa-engineer"
Prompt: "Verify task in {folder}. Read all context including plan.md.
Write insights/qa-plan.md with:
- Test cases from acceptance criteria
- Verification checklist
- Issues found (if any)
If critical issues found, document them for TL review.

When complete, provide a summary listing:
- Files read (full paths)
- Files written/modified (full paths)"
```

For context-update stage:
```
Use Task tool with subagent_type: "context-updater"
Prompt: "Analyze task {folder} which is now complete.
Review all insights, research/, plan.md, and task.md.
Update relevant CLAUDE.md files with:
- New patterns discovered
- Architecture decisions made
- Conventions established
- Gotchas or warnings for future work
Focus on what would help future development sessions.

When complete, provide a summary listing:
- Files read (full paths)
- Files written/modified (full paths)"
```

For po-summary stage:
```
Use Task tool with subagent_type: "product-owner"
Prompt: "Create a completion summary for task in {folder}.

Read these files:
- {folder}/task.md (requirements and acceptance criteria)
- {folder}/insights/workflow-history.md (what happened at each stage)
- {folder}/plan.md (what was planned)

Write {folder}/insights/summary.md using the template from
docs/tasks/_template/insights/summary.md with:
- What Was Done (1-3 plain-language sentences, no jargon)
- Key Decisions (notable choices and why)
- What Changed (components/areas affected)
- Impact (what's now possible, tasks unblocked)

Also append a row to docs/README.md Completed Tasks table:
| {task-id} | {YYYY-MM-DD} | {one-line summary} |

Keep it concise and business-facing.

When complete, provide a summary listing:
- Files read (full paths)
- Files written/modified (full paths)"
```

For git-commit stage:
```
Use the Skill tool with skill: "workflow:git-commit", args: "{task-id}"

This stages and commits all task-related files with a structured commit message.
The command will:
1. Identify task-related files from workflow-history
2. Exclude runtime files (*.db, .storage/, logs)
3. Update workflow-history with commit entry
4. Stage and commit with Co-Authored-By trailer
5. Report committed files and hash
```

### Step 5b: Research Stage Assessment

After PO analysis (for domain-research):
1. Analyze the PO analysis and task requirements
2. Identify domain areas that need expert research:
   - NestJS module patterns and best practices
   - Authentication/authorization approaches
   - Claude API integration patterns
   - Payment/billing integration
   - Database schema design considerations
3. Present recommendations to user:

```
## Domain Research Recommendations

Based on PO analysis, the following domain expertise would help:

1. **Claude API Expert** - Research structured output patterns and prompt engineering
   - Estimated value: High
   - Focus: AI integration patterns

2. **Billing Specialist** - Research payment provider subscription lifecycle
   - Estimated value: Medium
   - Focus: Webhook handling, subscription management

Do you want to engage these specialists? [Y/n/select specific]
```

After TL design (for tech-research):
1. Analyze the TL design and implementation steps
2. Identify technical areas needing deep research:
   - Specific libraries or frameworks
   - Integration patterns with existing code
   - Performance considerations
   - Security implications
3. Present recommendations similarly

### Step 5c: Execute Research

If user approves research:
```
Use Task tool with subagent_type: "Explore" (for codebase) or use WebSearch
Prompt: "Research {topic} for task in {folder}.
Write comprehensive findings to research/{topic-slug}.md including:
- Best practices and patterns
- Code examples from documentation
- Gotchas and common mistakes
- Recommendations for this specific task
- Links to sources"
```

Create research files like:
- `research/claude-api-structured-output.md`
- `research/payment-subscription-webhooks.md`
- `research/prisma-migration-patterns.md`

### Step 5d: Decomposition Assessment (after TL design or tech-research)

After TL design completes (and optional tech-research), evaluate whether the task should be decomposed into subtasks.

**Evaluate BOTH step count AND complexity:**

1. Count implementation steps in `insights/tl-design.md`
2. Assess complexity factors:
   - **HIGH**: New module/project creation (e.g., new Next.js app, new Docker service)
   - **HIGH**: Multiple technology domains (e.g., frontend + Docker + API + WebSocket)
   - **MEDIUM**: External integrations (WebSocket, APIs, third-party libraries)
   - **MEDIUM**: Steps that each produce independently testable artifacts
   - **LOW**: Config-only or single-file changes
   - **LOW**: Steps that are tightly coupled (can't commit independently)

3. **Recommend decomposition** when ANY of:
   - Steps >= 5 (regardless of complexity)
   - Steps >= 3 AND at least 2 HIGH complexity factors
   - Steps >= 3 AND TL design explicitly suggests subtask breakdown
   - TL design estimates total effort > 2 days

4. **Do NOT recommend decomposition** when:
   - Steps < 3
   - Steps are 3-4 AND all LOW complexity
   - Steps are tightly coupled (can't be independently committed)

5. Present to user with reasoning:
```
## Decomposition Assessment

Task has {N} implementation steps.

Complexity factors found:
- {factor 1} → {HIGH/MEDIUM/LOW}
- {factor 2} → {HIGH/MEDIUM/LOW}

Recommendation: {Decompose into subtasks / Proceed without decomposition}

Decompose? [Y/n]
```

If user approves → proceed to Step 5e.
If user declines → proceed with normal `dev-planning` stage.

### Step 5e: Decomposition Execution

When decomposition is approved:

1. **Create subtask directories** under `docs/tasks/{folder}/subtasks/`:
   ```
   subtasks/{parentId}.{N}-{slug}/
   ├── task.md           # Lightweight (from template)
   ├── plan.md           # Empty (filled during dev-planning)
   └── insights/
       └── workflow-history.md  # Empty (tracks subtask stages)
   ```

2. **Create subtask task.md** for each TL implementation step using the subtask template:
   ```markdown
   # Subtask {parentId}.{N}: {Title}

   ## Parent Task
   {parent-folder}

   ## Description
   {Extracted from parent TL design step N}

   ## Acceptance Criteria
   {Subset of parent acceptance criteria relevant to this step}
   {Plus verification criteria from TL step}

   ## Files to Create/Modify
   {From TL design step}
   ```

3. **Register subtasks in TaskMaster**:
   ```bash
   task-master add-subtask --parent={id} --title="{step title}"
   ```

4. **Set parent stage** to `decomposed` in tasks.json.

5. **Log in parent workflow-history**:
   ```markdown
   ---

   ## {YYYY-MM-DD} {HH:MM} - Task Decomposed

   - **Agent**: director
   - **Result**: completed
   - **Summary**: Task decomposed into {N} subtasks based on TL design.
   - **Complexity assessment**: {factors found}
   - **Subtasks created**:
     - {parentId}.1-{slug}: {title}
     - {parentId}.2-{slug}: {title}
     - ...
   - **Next stage**: decomposed (subtask workflow begins)
   ```

### Step 5f: Decomposed Task — Subtask Delegation

When the Director encounters a task at stage `decomposed`:

1. **Read subtasks** from tasks.json (parent's `subtasks` array)
2. **Find next incomplete subtask**:
   - Status is not `done`
   - All subtask dependencies satisfied (earlier subtasks done, if sequential)
   - Highest priority among eligible
3. **If found**: Run the subtask through its **simplified workflow**:
   ```
   dev-planning → implementation → qa-verification* → context-update* → git-commit → done
   ```
   - Use the subtask's `docs/tasks/{parent-folder}/subtasks/{subtaskId}/` as the working directory
   - Subtask agents read parent's `task.md`, `insights/tl-design.md`, and `research/` for context
   - Subtask produces its own `plan.md` and `insights/workflow-history.md`
4. **If all subtasks done**: Advance parent to `parent-qa` stage

**Subtask agent prompts follow the same pattern as standard task prompts** (Step 5), but with these differences:
- **DEV agent** reads parent's TL step + research, writes subtask's `plan.md`
- **DOER agent** reads subtask's `plan.md`, implements code
- **QA agent** verifies subtask's acceptance criteria only
- **Context-updater** does a light update (skip if no notable patterns)
- **Git-commit** commits subtask changes with format: `{Verb} {description} (task-{parentId}.{N})`

After each subtask completes, log in parent workflow-history:
```markdown
---

## {YYYY-MM-DD} {HH:MM} - Subtask {parentId}.{N} Complete

- **Subtask**: {subtaskId}-{slug}
- **Commit**: {hash}
- **Summary**: {1-sentence from subtask QA/implementation}
- **Remaining subtasks**: {M} of {total}
```

### Step 5g: Parent Completion (after all subtasks done)

When all subtasks are done:

1. **Run parent-level QA** — integrated verification of all subtasks together:
   ```
   Use Task tool with subagent_type: "qa-engineer"
   Prompt: "Run integrated verification for decomposed task in {folder}.
   All {N} subtasks are complete. Verify the integrated result:
   - Read parent task.md acceptance criteria
   - Read all subtask insights/workflow-history.md for what was implemented
   - Verify the complete feature works end-to-end
   - Write insights/qa-integrated.md with results
   If critical issues: document which subtask needs revision."
   ```

2. **If QA passes**: Advance to `context-update` → `arch-update` → `po-summary` → `git-commit` → `done` (standard flow)
3. **If QA fails**: Document issues, ask user which subtask to revisit. Set that subtask back to `dev-planning`.

### Step 5h: Arch-Context Assessment (before PO)

When a task enters the workflow from `backlog`, assess whether the System Architect should provide pre-PO architectural context.

**Engage arch-context** if the task description mentions ANY of:
- Multiple components (API + Web, API + shared packages, etc.)
- New integrations or external services (third-party APIs, payment providers, etc.)
- Infrastructure modifications (Docker, database schema, new services)
- New API endpoints or protocol changes
- Cross-cutting architectural changes

**Skip arch-context** if the task is:
- Single-component bug fix
- Documentation-only change
- UI/dashboard-only change (within one component)
- Config-only change within one component
- Subtask of a decomposed task (subtasks never get arch-context)

If engaging:
```
Use Task tool with subagent_type: "system-architect"
Prompt: "Run in arch-context mode for task in {folder}.
1. Read architecture/CLAUDE.md and architecture/overview.md
2. Read relevant ADRs from architecture/decisions/
3. Read relevant contracts from architecture/contracts/
4. Read task.md for scope
5. Write insights/arch-context.md with: relevant architecture, existing decisions, constraints, integration points, recommendations for PO

When complete, provide summary of files read and written."
```

If skipping, log in workflow-history:
```markdown
## {YYYY-MM-DD} {HH:MM} - Arch Context (Skipped)
- **Agent**: director
- **Result**: skipped
- **Summary**: Task is {reason} — arch-context not needed.
- **Next stage**: po-analysis
```

### Step 5i: Arch-Review Gate (after TL design — MANDATORY)

After TL design completes, the System Architect MUST review the design. This is a mandatory hard gate — no exceptions.

```
Use Task tool with subagent_type: "system-architect"
Prompt: "Run in arch-review mode for task in {folder}. Iteration: {1|2}.
1. Read architecture/CLAUDE.md, architecture/overview.md, all ADRs in architecture/decisions/, relevant contracts
2. Read insights/tl-design.md (the design under review)
3. Read insights/po-analysis.md for scope context
4. Validate design against ADRs, contracts, naming conventions, component boundaries
5. Write insights/arch-review.md with APPROVED or REJECTED verdict
If REJECTED: cite specific ADR/contract references, provide constraints, suggest alternatives.

When complete, provide summary of files read and written."
```

**Handle the verdict:**

- **APPROVED**: Proceed to tech-research assessment (Step 5b) or decomposition assessment (Step 5d)
- **APPROVED with conditions**: Proceed, but log conditions in workflow-history for implementation to address
- **REJECTED (iteration 1)**: Log rejection in workflow-history with iteration count and violations. Route back to TL design:
  ```
  Use Task tool with subagent_type: "team-lead"
  Prompt: "Revise TL design for task in {folder}.
  The System Architect REJECTED the design. Read insights/arch-review.md for:
  - Specific violations cited
  - Constraints to respect
  - Suggested alternatives
  Update insights/tl-design.md to address all violations.
  ..."
  ```
  Then re-run arch-review with iteration: 2.
- **REJECTED (iteration 2)**: Escalate to user. Present both the architect's concerns and the TL's rationale. User decides whether to override the architect or require further revision.

**Workflow-history for arch-review:**
```markdown
## {YYYY-MM-DD} {HH:MM} - Arch Review
- **Agent**: system-architect
- **Result**: APPROVED | REJECTED
- **Iteration**: {1 | 2}
- **Summary**: {verdict summary}
- **Violations**: {list if rejected, or "none"}
- **Conditions**: {list if approved with conditions, or "none"}
- **Next stage**: {tech-research | tl-design (if rejected)}
```

### Step 5j: Arch-Update (after context-update — MANDATORY)

After context-update completes, the System Architect MUST assess and update architecture docs. This is mandatory — no exceptions.

```
Use Task tool with subagent_type: "system-architect"
Prompt: "Run in arch-update mode for task in {folder}.
1. Read architecture/CLAUDE.md and all architecture/ files
2. Read insights/workflow-history.md to understand what was done
3. Read plan.md and list of modified files
4. Assess architectural impact: new components, protocols, events, timing changes, implicit decisions
5. Update architecture/ files if needed
6. Create retroactive ADRs for implicit decisions using architecture/decisions/_template.md
7. Write insights/arch-update.md with impact assessment, updates made, ADRs created

When complete, provide summary of files read, written, and updated."
```

Proceeds to po-summary after completion.

**Workflow-history for arch-update:**
```markdown
## {YYYY-MM-DD} {HH:MM} - Arch Update
- **Agent**: system-architect
- **Result**: completed
- **Summary**: {impact assessment — updates made or "no architectural impact"}
- **Files modified**: {architecture/ files updated, or "none"}
- **ADRs created**: {list, or "none"}
- **Next stage**: po-summary
```

### Step 6: Review Agent Output

After agent completes:
1. Show summary of what was produced
2. List files created/modified
3. Highlight any blockers or open questions

### Step 7: Ask for Approval

Present options to user:
- **Proceed**: Advance to next stage
- **Revise**: Re-run the same agent with feedback
- **Stop**: Keep current stage, end session

### Step 8: Update Workflow History and Stage (MANDATORY)

**CRITICAL**: Update workflow-history BEFORE proceeding to next stage. This is NOT optional.

If user approves (or for mandatory stages):

1. **FIRST**: Append entry to `insights/workflow-history.md`:
   ```markdown
   ---

   ## {YYYY-MM-DD} {HH:MM} - {Stage Name}

   - **Agent**: {agent-name}
   - **Result**: completed
   - **Summary**: {1-2 sentence summary from agent output}
   - **Files read**:
     - {full path 1}
     - {full path 2}
   - **Files created**:
     - {full path} (or "none")
   - **Files modified**:
     - {full path} (or "none")
   - **Research engaged**: {topic} (or "none")
   - **Next stage**: {stage-name}
   ```

2. **THEN**: Update the task's `stage` field in `.taskmaster/tasks/tasks.json`

**For "Task Complete" entry** (when reaching `done`):
```markdown
---

## {YYYY-MM-DD} {HH:MM} - Task Complete

- **Final Status**: DONE
- **Total Duration**: {from first workflow-history entry to now}
- **Files Created**:
  - {consolidated list from all entries}
- **Files Modified**:
  - {consolidated list from all entries}
- **Commit**: {hash from git-commit stage, or "manual" if committed outside workflow}
- **Patterns Captured**: {from context-updater summary}
- **Unblocked Tasks**: {tasks that depended on this one}
```

### Step 9: Continue or Stop

After stage update:
- **MANDATORY STAGES**: If current stage is `implementation`, `qa-verification`, `context-update`, `arch-update`, `po-summary`, or `parent-qa`:
  - Do NOT ask user - automatically proceed to next stage
  - These stages form an atomic completion sequence that must not be interrupted
  - Only stop if a stage fails (e.g., QA finds critical issues)
- **GIT-COMMIT STAGE**: After po-summary completes, ask user for approval before committing:
  - Present summary of what will be committed
  - User confirms everything is tested and ready
  - Only then run `/workflow/git-commit`
- **DECOMPOSED STAGE**: When parent is at `decomposed`:
  - Automatically find and start the next incomplete subtask
  - After each subtask completes (git-commit → done), automatically start the next one
  - When all subtasks done, automatically advance parent to `parent-qa`
- For other stages: offer to continue to next stage
- If at "done", congratulate and show final summary

**CRITICAL**: The sequence `implementation → qa-verification → context-update → arch-update → po-summary` is MANDATORY and AUTOMATIC (for standard tasks).
For subtasks: `implementation → qa-verification → context-update → git-commit` (no architect stages).
For decomposed parents: `parent-qa → context-update → arch-update → po-summary` is also MANDATORY and AUTOMATIC.
After po-summary, ask user to approve the commit. A task is NOT complete until changes are committed.

## Special Cases

### Legacy Content (task.md filled, workflow-history empty)

If task.md has PO/TL sections filled BUT `insights/workflow-history.md` is empty:
1. This is "legacy" or "unverified" content
2. Ask user via AskUserQuestion:
   - **Option A: Accept existing content** → Add "Legacy Content Accepted" entry to workflow-history, start from `dev-planning`
   - **Option B: Re-validate through workflow** → Start from `backlog`, PO agent reviews existing content
3. Document the decision in workflow-history:
   ```
   ## {YYYY-MM-DD} {HH:MM} - Legacy Content Accepted
   - Agent: director
   - Result: accepted
   - Summary: Existing PO and TL content in task.md accepted without re-validation per user decision.
   - Files read: docs/tasks/{folder}/task.md
   - Next: dev-planning
   ```

### QA Finds Issues
If QA agent reports critical issues:
1. Set stage back to "tl-design"
2. Document issues in workflow-history.md
3. Notify user that task needs TL revision

### Missing Information
If any agent cannot proceed due to missing info:
1. Agent should ask user immediately using AskUserQuestion
2. Do not block - get the answer and continue
3. Document the Q&A in the insights file

### Skipping Research
If user declines research:
1. Log decision in workflow-history.md
2. Proceed to next stage
3. Note: research can still be added later if needed

### No Tasks Available
If no tasks are ready:
```
## Workflow Status

All tasks are either:
- Done: [list done tasks]
- Blocked by dependencies: [list blocked tasks with their blockers]

Suggested actions:
1. Review blocked tasks and complete dependencies
2. Add new tasks to the backlog
3. Run `/director {task-id}` to work on a specific task
```

## Research Topics Reference

Common domain research topics:
| Topic | When Needed | Output File |
|-------|-------------|-------------|
| Claude API | LLM integration tasks | research/claude-api-patterns.md |
| Payments | Billing/subscription tasks | research/payment-integration.md |
| NestJS | Backend module development | research/nestjs-patterns.md |
| Prisma | Database schema/migration tasks | research/prisma-patterns.md |
| Next.js | Frontend feature development | research/nextjs-patterns.md |
| Docker | Container setup | research/docker-patterns.md |
| TypeScript | TS service development | research/typescript-patterns.md |

## Example Usage

```
/director           # Auto-detect next task
/director 1         # Work on task ID 1
/director task-001  # Work on task-001
```
