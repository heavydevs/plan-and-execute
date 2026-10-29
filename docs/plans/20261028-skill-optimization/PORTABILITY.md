# Portability and explicit execution

The exported native manifest is bound to `/mnt/data/workspaces/plan-and-execute`. Do not edit repo_root or task statuses manually. On another host, keep a backup, place this source package in the target repository, inspect existing changes, and move the old native control directory out of `.ai-work` before recreating it with the SAME plan ID. Keeping the ID makes the plan-local structure checker portable. Never overwrite a running/completed native plan.

```bash
python skill/plan-and-execute/scripts/planctl_concise.py create --repo-root . --spec docs/plans/20261028-skill-optimization/PLAN1_SPEC.json --plan-id 20261028-skill-study-provider-switch --request-file docs/plans/20261028-skill-optimization/REQUEST_CURRENT.md
python skill/plan-and-execute/scripts/studyctl_concise.py attach --spec docs/plans/20261028-skill-optimization/PREPARATION_STUDY.json --plan .ai-work/20261028-skill-study-provider-switch --json
python skill/plan-and-execute/scripts/planctl_concise.py validate --plan .ai-work/20261028-skill-study-provider-switch
python skill/plan-and-execute/scripts/service_map.py check --repo-root .
python skill/plan-and-execute/scripts/service_map.py audit-plan --repo-root . --plan .ai-work/20261028-skill-study-provider-switch
python docs/plans/20261028-skill-optimization/support/check_delivery.py --structure
```

These commands prepare and check a plan, not authenticated models. Review changed discovery inputs before stamping the map; a fresh hash cannot establish semantic resource coverage. An implementation adding test files must reconcile the map again.

All new tasks are pending. Future targeted tests and implementation receipts do not exist yet; that is intentional. Research is already supplied, so workers consume their assigned reports rather than rebuilding another plan. Independent code reviews still need an actually available permitted provider and fresh context. Paid execution, commit/push and publication retain the user's explicit confirmation boundary.

The current remote checkpoint is `d4fc2ae`; the restored local backup has older Git metadata. Do not force-push or reset away this work. Reconcile ancestry on the named checkpoint branch before any separately authorized publication. `history/pre-research-conversion` is archival evidence, not a second actionable plan.


## Revision2 archive and empty control directories

The delivered ZIP preserves empty native directories explicitly. Git does not preserve empty directories. Do not place `.gitkeep` in `learnings/`: schema-v4 validation rejects unregistered learning files. Recreate the unexecuted plan through the native create/attach commands above after moving the old control snapshot to an archive. Never recreate a partially executed plan this way.

Run the revision2 readiness checker after native validation:

```bash
python docs/plans/20261028-skill-optimization/support/research_readiness.py
```

It checks the prepared specification and inputs, not provider authentication or model quality. A missing future test or receipt owned by a pending task is recorded as a future output, never silently generated as fake evidence.


## Revision2 archive and empty control directories

The delivered ZIP preserves empty native directories explicitly. Git does not preserve empty directories. Do not place `.gitkeep` in `learnings/`: schema-v4 validation rejects unregistered learning files. Recreate the unexecuted plan through the native create/attach commands above after moving the old control snapshot to an archive. Never recreate a partially executed plan this way.

Run the revision2 readiness checker after native validation:

```bash
python docs/plans/20261028-skill-optimization/support/research_readiness.py
```

It checks the prepared specification and inputs, not provider authentication or model quality. A missing future test or receipt owned by a pending task is recorded as a future output, never silently generated as fake evidence.
