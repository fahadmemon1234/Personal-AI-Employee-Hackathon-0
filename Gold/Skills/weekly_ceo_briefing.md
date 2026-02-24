# Weekly CEO Briefing Skill

**Skill ID:** `weekly_ceo_briefing`  
**Version:** 1.0  
**Tier:** Gold  
**Status:** ✅ Operational

---

## Overview

Automated weekly briefing generation for CEO review. This skill uses the **Ralph Wiggum Reasoning Loop** to process multiple data sources and generate comprehensive business insights.

---

## Trigger

- **Scheduled:** Sunday night (automated via scheduler)
- **Manual:** Run on-demand via CLI or MCP command

---

## Data Sources

| Source | File/API | Purpose |
|--------|----------|---------|
| Business Goals | `Business_Goals.md` | Strategic objectives and targets |
| Completed Tasks | `/Completed/*.md` | Tasks finished last week |
| Odoo Financials | Odoo MCP (port 8082) | Revenue, receivables, payables |
| Social Media | Meta MCP (8083) + X MCP (8084) | Social activity summary |
| Bottlenecks | `/Needs_Action`, `/Pending_Approval` | Identify blockers |

---

## Ralph Wiggum Reasoning Loop

The skill uses a multi-step reasoning loop where each step depends on previous results:

```
┌─────────────────────────────────────────────────────────────────┐
│ Ralph Wiggum Reasoning Loop - CEO Briefing                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. read_business_goals ─────────────────┐                      │
│     (No dependencies)                    │                      │
│                                           ↓                      │
│  2. read_completed_tasks ────────────────┼──┐                   │
│     (No dependencies)                    │  │                   │
│                                           ↓  ↓                   │
│  3. get_odoo_financials ─────────────────┼──┼──┐                │
│     (No dependencies)                    │  │  │                │
│                                           ↓  ↓  ↓                │
│  4. get_social_media_summary ────────────┼──┼──┼──┐             │
│     (No dependencies)                    │  │  │  │             │
│                                           ↓  ↓  ↓  ↓             │
│  5. identify_bottlenecks ────────────────┼──┘  │  │             │
│     (depends on: completed, financials)   │     │  │             │
│                                           ↓     │  │             │
│  6. generate_suggestions ────────────────┼─────┘  │             │
│     (depends on: bottlenecks, financials) │        │             │
│                                           ↓        │             │
│  7. calculate_key_metrics ───────────────┼────────┘             │
│     (depends on: completed, social, financials)                 │
│                                           ↓                      │
│  8. generate_briefing_document ───────────┼─────────────────────┘
│     (depends on: ALL previous steps)                             │
│                                           ↓                      │
│  9. update_dashboard ─────────────────────┘                      │
│     (depends on: briefing_document)                              │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### Step Details

| Step | Function | Dependencies | Output |
|------|----------|--------------|--------|
| 1 | `read_business_goals` | None | Strategic goals, quarterly targets |
| 2 | `read_completed_tasks` | None | Completed tasks list |
| 3 | `get_odoo_financials` | None | Revenue, receivables, payables |
| 4 | `get_social_media_summary` | None | Social posts count |
| 5 | `identify_bottlenecks` | 2, 3 | Bottleneck list |
| 6 | `generate_suggestions` | 5, 3 | Action suggestions |
| 7 | `calculate_key_metrics` | 2, 4, 3 | Efficiency score |
| 8 | `generate_briefing_document` | 1-7 | Briefing markdown file |
| 9 | `update_dashboard` | 8 | Dashboard updated |

---

## Output

### Briefing Document

**Location:** `/Briefings/YYYY-MM-DD_Monday_Briefing.md`

**Sections:**
1. Executive Summary (key metrics table)
2. Business Goals Progress
3. Completed Tasks (last 7 days)
4. Financial Summary
5. Social Media Activity
6. Bottlenecks & Issues
7. Proactive Suggestions
8. Action Items for CEO

### Dashboard Update

Updates `Dashboard.md` with "Last Briefing" section:
- Date of last briefing
- Link to briefing file
- Status indicator

---

## Usage

### CLI (Manual Trigger)

```bash
cd "D:\Fahad Project\AI-Driven\Personal-AI-Employee-Hackathon-0\Gold"
python Skills\weekly_ceo_briefing.py
```

### Via MCP Server (if enabled)

```bash
curl -X POST http://localhost:8080/tools/generate_ceo_briefing
```

### Scheduled (Automatic)

Add to `scheduler.py`:

```python
from Skills.weekly_ceo_briefing import WeeklyCEOBriefing

# Run every Sunday at 20:00
if datetime.now().weekday() == 6 and datetime.now().hour == 20:
    briefing = WeeklyCEOBriefing()
    briefing.generate()
```

---

## Example Output

```
======================================================================
📊 Weekly CEO Briefing Generation
======================================================================
Period: 2026-02-17 to 2026-02-24

======================================================================
🔄 Ralph Wiggum Reasoning Loop - CEO Briefing Generation
======================================================================

📌 Step: read_business_goals
--------------------------------------------------
   Found 5 strategic goals
✅ Completed: read_business_goals

📌 Step: read_completed_tasks
--------------------------------------------------
   Found 6 completed tasks
✅ Completed: read_completed_tasks

... (continues for all steps)

======================================================================
✅ CEO Briefing Generation Complete!
======================================================================
Briefing: Briefings\2026-02-24_Monday_Briefing.md
Efficiency: 35/100 (Needs Improvement)
```

---

## Key Metrics Calculated

| Metric | Calculation | Target |
|--------|-------------|--------|
| Tasks Completed | Count from /Completed | ≥ 10/week |
| Tasks Per Day | Tasks / 7 | ≥ 1.5/day |
| Social Posts | Facebook + Instagram + Twitter | ≥ 5/week |
| Revenue | Sum of paid invoices | Varies |
| Receivables | Outstanding invoices | < PKR 100k |
| Efficiency Score | Weighted sum (max 100) | ≥ 80 |

### Efficiency Score Breakdown

- Tasks ≥ 10: +30 points
- Tasks ≥ 5: +20 points
- Social posts ≥ 5: +20 points
- Social posts ≥ 2: +10 points
- Odoo connected: +30 points
- Odoo disconnected: +15 points

**Rating:**
- 80-100: Excellent
- 60-79: Good
- < 60: Needs Improvement

---

## Bottleneck Detection

The skill automatically identifies:

1. **Low Productivity** - < 5 tasks completed
2. **Cash Flow Issues** - Receivables > PKR 100,000
3. **Approval Bottleneck** - > 5 items pending approval
4. **Backlog** - > 50 items in Needs_Action

Each bottleneck includes:
- Severity level (high/medium/low)
- Description
- Suggested action

---

## Proactive Suggestions

Based on analysis, the skill suggests:

1. **Financial Actions** - Payment scheduling, invoice follow-up
2. **Operational Improvements** - Address bottlenecks
3. **Growth Activities** - Strategic goal reviews

---

## Troubleshooting

### Odoo MCP Not Connected

**Error:** `Odoo MCP connection error`

**Solution:**
```bash
python mcp_odoo_server.py
```

### Social Media MCP Not Connected

**Error:** `Could not fetch Meta summary`

**Solution:**
```bash
python mcp_social_server.py
python mcp_x_server.py
```

### Business Goals Not Found

**Error:** `Business_Goals.md not found`

**Solution:** Create `Business_Goals.md` with strategic goals section.

---

## Files

| File | Purpose |
|------|---------|
| `Skills/weekly_ceo_briefing.py` | Main skill implementation |
| `Business_Goals.md` | Strategic objectives |
| `Briefings/*.md` | Generated briefings |
| `Dashboard.md` | Updated with last briefing |

---

## Integration

### With Scheduler

```python
# scheduler.py
from Skills.weekly_ceo_briefing import WeeklyCEOBriefing

def weekly_briefing_job():
    """Run weekly CEO briefing every Sunday at 8 PM"""
    if datetime.now().weekday() == 6 and datetime.now().hour == 20:
        briefing = WeeklyCEOBriefing()
        result = briefing.generate()
        logger.info(f"Briefing generated: {result}")
```

### With MCP Email Server

Send briefing to CEO via email:

```python
from Skills.weekly_ceo_briefing import WeeklyCEOBriefing
from mcp_email_server import send_email

briefing = WeeklyCEOBriefing()
briefing_path = briefing.generate()

# Email briefing to CEO
with open(briefing_path, 'r') as f:
    content = f.read()

send_email(
    to='ceo@company.com',
    subject=f'Weekly CEO Briefing - {datetime.now().strftime("%Y-%m-%d")}',
    body=content
)
```

---

## Best Practices

1. **Review Briefings Weekly** - CEO should review every Monday morning
2. **Track Trends** - Compare efficiency scores week-over-week
3. **Address Bottlenecks** - Prioritize high-severity items
4. **Update Goals** - Keep Business_Goals.md current
5. **Archive Briefings** - Keep historical briefings for reference

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-02-24 | Initial implementation |

---

**Skill Owner:** AI Digital FTE Employee  
**Last Updated:** 2026-02-24  
**Status:** ✅ Production Ready
