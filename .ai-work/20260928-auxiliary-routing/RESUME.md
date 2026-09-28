# Resume from this checkpoint

1. Checkout `feature/auxiliary-assistants-tier-routing-20260928` and inspect the latest
   `TODO.md`, task report and source changes. Do not restart completed work.
2. In a different filesystem location, run
   `python .ai-work/20260928-auxiliary-routing/rebind.py --repo-root .`.
   This changes only the repository location, not progress or retry evidence.
3. Run the plan/study validations and service-map freshness check. Reconcile changed
   test inputs before stamping the map; do not mark unmapped validations complete.
4. Use `lifecyclectl_concise.py activate --plan .ai-work/20260928-auxiliary-routing`;
   then `run_concise.py --plan .ai-work/20260928-auxiliary-routing --no-cleanup` on
   a host with a configured provider CLI, or use the documented host-managed loop.
5. Commit source and plan changes after each deterministic validation. The user
   explicitly requested retention; do not run successful-plan cleanup here.

This implementation session uses host-managed execution because no provider CLI
is installed in the chat container. Do not infer independent-model review from
its recommended task routes. Native-provider and Windows behavior need their own
verification. Original baseline CI fails the fixed SKILL.md character budget.
