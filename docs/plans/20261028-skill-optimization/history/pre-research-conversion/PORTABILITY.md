# Portability and guarded execution

The archived native manifest is bound to `/mnt/data/workspaces/plan-and-execute`.
It is an unstarted plan: all 86 tasks are pending. Do not rewrite manifest state or
absolute paths by hand. Preserve the archive and use native creation on another host.
Run from the source repository root, with the planning/research directories and the
updated service map copied intact. Inspect local changes before copying anything.

Use a unique plan id if this name already exists:

```bash
python skill/plan-and-execute/scripts/planctl_concise.py create --repo-root . --spec docs/plans/20261028-skill-optimization/PLAN1_SPEC.json --plan-id skill-study-local --request-file docs/plans/20261028-skill-optimization/REQUEST_ORIGINAL.md
python skill/plan-and-execute/scripts/studyctl_concise.py attach --spec docs/plans/20261028-skill-optimization/PREPARATION_STUDY.json --plan .ai-work/skill-study-local --json
python skill/plan-and-execute/scripts/planctl_concise.py validate --plan .ai-work/skill-study-local
python skill/plan-and-execute/scripts/service_map.py check --repo-root .
python skill/plan-and-execute/scripts/service_map.py audit-plan --repo-root . --plan .ai-work/skill-study-local
```

These preparation commands do not dispatch authenticated models. If source discovery
inputs differ, reconcile the map before stamping it; a fresh timestamp alone is not
semantic reconciliation. Update source-baseline evidence when the Git tree differs.

Only after explicit authorization and non-generative capability/authentication checks
may the orchestrator activate execution and obtain the real maximum-model review for
TODO 001. Native plan_review approval is structural only, not that independent review.
Do not auto-run a model merely to discover whether its account is authenticated.

The archive's local base and remote main have identical trees but different commit
identifiers because the prior publication used the GitHub connector. Preserve the
working tree and reconcile ancestry before a future authorized commit/push. Never
force-push or reset away these uncommitted planning files.

Plan 2 does not yet exist. TODO 084 writes its durable input spec; the manager, not the
isolated worker, creates and validates the second native plan before accepting it.
