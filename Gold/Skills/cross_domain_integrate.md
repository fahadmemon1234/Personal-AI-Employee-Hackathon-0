# Agent Skill: Cross-Domain Integration

## Skill ID: `cross_domain_integrate`

**Purpose:** Scan /Needs_Action for items from last 24h, classify as Personal/Business, create integrated plans.

## Usage

```bash
python reasoning_loop.py --skill=cross_domain_integrate
```

## Workflow

1. Scan /Needs_Action (last 24h)
2. Classify each item (Personal/Business/Cross-Domain)
3. Create Plans in /Plans
4. Link cross-domain workflows
5. Update Dashboard.md

## Output

- Plan files in /Plans
- Dashboard.md updated with "## Cross-Domain Status"

---

*For full documentation, see the original skill implementation*
