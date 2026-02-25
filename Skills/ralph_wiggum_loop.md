# Ralph Wiggum Autonomous Loop

**Skill ID:** `ralph_wiggum_loop`  
**Version:** 1.0  
**Tier:** Gold  
**Status:** ✅ Operational

---

## Overview

Autonomous task execution loop that continues iterating until a task is complete. Uses the **stop hook pattern** to keep running Claude Code until completion signals are detected.

**Reference:** https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

---

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│ Ralph Wiggum Autonomous Loop                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Load/Create task                                           │
│       ↓                                                         │
│  2. Generate prompt (initial or continuation)                  │
│       ↓                                                         │
│  3. Run Claude Code                                            │
│       ↓                                                         │
│  4. Check for completion signals:                              │
│     - TASK_COMPLETE marker                                     │
│     - Task file moved to /Done                                 │
│     - Completion phrases                                       │
│       ↓                                                         │
│  5. If complete → END                                          │
│     If not complete → Continue to next iteration               │
│       ↓                                                         │
│  6. Check max iterations (20)                                  │
│       ↓                                                         │
│  7. Save state and continue                                    │
│                                                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## Stop Hook Pattern

The loop checks for completion after each iteration:

### Completion Signals

1. **TASK_COMPLETE Marker**
   ```
   TASK_COMPLETE
   ```
   Output this exact phrase when task is done.

2. **Task File Movement**
   - Task file exists in `Needs_Action/`
   - File moved to `Done/` directory
   - Indicates manual or automatic completion

3. **Completion Phrases**
   - "task is complete"
   - "task completed"
   - "finished successfully"
   - "all steps completed"
   - "✅ complete"

---

## Installation

### Prerequisites

- Python 3.10+
- Claude Code installed and configured
- MCP servers running (optional, task-dependent)

### Setup

```bash
# Navigate to Gold directory
cd "D:\Fahad Project\AI-Driven\Personal-AI-Employee-Hackathon-0\Gold"

# Verify orchestrator exists
dir ralph_orchestrator.py

# Test help
python ralph_orchestrator.py --help
```

---

## Usage

### Basic Usage

```bash
# Run with task description
python ralph_orchestrator.py --task "Process complex invoice from email"

# Run with task file
python ralph_orchestrator.py --task-file "Needs_Action/invoice_001.md"

# Custom max iterations
python ralph_orchestrator.py --task "My task" --max-iterations 10

# Resume from existing state
python ralph_orchestrator.py --resume
```

### Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--task` | `-t` | Task description to execute |
| `--task-file` | `-f` | Path to task file |
| `--max-iterations` | `-m` | Maximum iterations (default: 20) |
| `--resume` | `-r` | Resume from existing state file |

---

## Example Workflows

### Example 1: Process Complex Invoice

**Task:** Process invoice from email, create in Odoo, send confirmation

```bash
python ralph_orchestrator.py \
  --task "Process invoice: 1) Read email in Needs_Action, 2) Extract invoice details, 3) Create vendor bill in Odoo, 4) Send confirmation email, 5) Move to Completed"
```

**Loop Execution:**
```
Iteration 1: Read email, extract invoice data
Iteration 2: Create vendor in Odoo (if new)
Iteration 3: Create vendor bill in Odoo
Iteration 4: Send confirmation email
Iteration 5: Move files to Completed, output TASK_COMPLETE
```

### Example 2: Customer Onboarding

**Task:** Setup new customer in Odoo and send welcome email

```bash
python ralph_orchestrator.py \
  --task "Onboard new customer: 1) Create customer in Odoo, 2) Generate welcome email, 3) Send email, 4) Create follow-up task"
```

### Example 3: Social Media Campaign

**Task:** Create and post social media content across platforms

```bash
python ralph_orchestrator.py \
  --task "Execute social media campaign: 1) Generate content from brief, 2) Post to Facebook, 3) Post to Instagram, 4) Post to Twitter, 5) Log all posts"
```

---

## State Management

### State File: `ralph_state.json`

```json
{
  "task": "Process complex invoice",
  "started_at": "2026-02-24T16:00:00",
  "iterations": 5,
  "status": "completed",
  "last_output": "...",
  "errors": [],
  "state_files": [],
  "completed_at": "2026-02-24T16:15:00"
}
```

### State Files

| File | Purpose |
|------|---------|
| `ralph_state.json` | Current loop state |
| `ralph_task.md` | Task details and progress |
| `ralph_loop.log` | Execution log |
| `Ralph_Context/` | Prompts and outputs per iteration |

---

## Output Structure

### Console Output

```
======================================================================
Ralph Wiggum Autonomous Loop Started
======================================================================
Task: Process complex invoice
Max Iterations: 20
State File: ralph_state.json
======================================================================

============================================================
ITERATION 1 / 20
============================================================
Running Claude Code (iteration 1)...
Claude output: 2500 chars

============================================================
ITERATION 2 / 20
============================================================
...

======================================================================
✅ TASK COMPLETE!
======================================================================

======================================================================
Ralph Wiggum Loop - Execution Summary
======================================================================
Task: Process complex invoice
Status: completed
Iterations: 5
Started: 2026-02-24T16:00:00
Completed: 2026-02-24T16:15:00
======================================================================
```

### Log File: `ralph_loop.log`

```
2026-02-24 16:00:00 - ralph_orchestrator - INFO - Starting Ralph Wiggum autonomous loop...
2026-02-24 16:00:01 - ralph_orchestrator - INFO - ITERATION 1 / 20
2026-02-24 16:00:05 - ralph_orchestrator - INFO - Running Claude Code...
2026-02-24 16:00:30 - ralph_orchestrator - INFO - ✓ Found TASK_COMPLETE marker
```

---

## Error Handling

### Max Iterations Reached

```
⚠️ MAX ITERATIONS (20) REACHED
Status: max_iterations
```

**Solution:**
- Increase `--max-iterations`
- Review logs to identify blockers
- Break task into smaller subtasks

### Claude Command Not Found

```
ERROR: claude command not found
```

**Solution:**
```bash
# Install claude-code
npm install -g @anthropic/claude-code

# Or verify installation
claude --version
```

### Timeout Error

```
ERROR: Iteration 5 timed out after 300s
```

**Solution:**
- Increase timeout in `ralph_orchestrator.py`
- Check for infinite loops in task
- Verify MCP servers are responsive

---

## Integration with MCP Servers

The Ralph Wiggum loop can utilize all MCP servers:

### Available Servers

| Server | Port | Use Case |
|--------|------|----------|
| Email MCP | 8080 | Read/send emails |
| Browser MCP | 8081 | Web automation |
| Odoo MCP | 8082 | ERP operations |
| Social MCP | 8083 | Social media posting |
| X MCP | 8084 | Twitter posting |

### Example: Multi-Server Workflow

```bash
python ralph_orchestrator.py \
  --task "Complete customer request: 1) Read email (Email MCP), 2) Check order in Odoo (Odoo MCP), 3) Post update to social (Social MCP), 4) Send reply (Email MCP)"
```

---

## Best Practices

### Task Design

1. **Clear Objectives**: Define what "complete" means
2. **Break Down Steps**: Complex tasks → smaller steps
3. **Error Handling**: Specify what to do on failures
4. **Completion Signal**: Always output TASK_COMPLETE when done

### Iteration Management

1. **Start Small**: Test with 5 iterations first
2. **Monitor Progress**: Check state file between runs
3. **Resume Capability**: Use `--resume` to continue
4. **Log Review**: Check `ralph_loop.log` for issues

### State Management

1. **Save Frequently**: State auto-saves every iteration
2. **Backup State**: Copy `ralph_state.json` before resuming
3. **Clean Context**: Remove old `Ralph_Context/` files periodically

---

## Troubleshooting

### Loop Won't Stop

**Symptoms:** Keeps iterating beyond completion

**Solution:**
- Ensure TASK_COMPLETE is output exactly
- Check task file movement to /Done
- Review completion phrases in output

### Loop Stops Too Early

**Symptoms:** Stops before task is done

**Solution:**
- Increase max iterations
- Check for false completion signals
- Review output for accidental completion phrases

### State File Corrupted

**Symptoms:** Can't resume, errors loading state

**Solution:**
```bash
# Delete corrupted state
del ralph_state.json

# Start fresh
python ralph_orchestrator.py --task "My task"
```

---

## Advanced Usage

### Custom Completion Detection

Edit `check_task_complete()` in `ralph_orchestrator.py`:

```python
def check_task_complete(self, output: str) -> bool:
    # Add custom completion logic
    if 'CUSTOM_COMPLETE_MARKER' in output:
        return True
    # ... existing checks
```

### Pre/Post Hooks

Add custom logic before/after iterations:

```python
def before_iteration(self):
    # Custom pre-iteration logic
    pass

def after_iteration(self, output: str):
    # Custom post-iteration logic
    pass
```

### Integration with Scheduler

```python
# scheduler.py
from ralph_orchestrator import RalphWiggumLoop

def process_invoice_task():
    loop = RalphWiggumLoop(task="Process pending invoices")
    loop.run()
```

---

## Files

| File | Purpose |
|------|---------|
| `ralph_orchestrator.py` | Main orchestrator script |
| `ralph_state.json` | Runtime state |
| `ralph_task.md` | Task details |
| `ralph_loop.log` | Execution log |
| `Ralph_Context/` | Iteration context files |
| `Done/` | Completed task files |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-24 | Initial implementation |

---

**Skill Owner:** AI Digital FTE Employee  
**Last Updated:** 2026-02-24  
**Status:** ✅ Production Ready

---

*For more information, see:*
- *Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum*
- *Documentation: `/Skills/mcp_management.md`*
- *Dashboard: `/Dashboard.md`*
