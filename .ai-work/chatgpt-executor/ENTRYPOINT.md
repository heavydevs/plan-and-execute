# ChatGPT task execution — routing entrypoint

Read **only** what this phase needs, not the whole task history:

- **Implement or continue:** read [`PLAYBOOK.md`](PLAYBOOK.md) then the selected task's definition and assigned context.
- **Review:** read [`REVIEW.md`](REVIEW.md) and the implementation receipt plus exact changed files. A ChatGPT self-review is preliminary only.
- **Run tests / troubleshoot environment:** read [`PLAYBOOK.md`](PLAYBOOK.md) and invoke `python .ai-work/chatgpt-executor/taskctl.py doctor` and `run-checks`.
- **Architecture, security, provider alternatives:** read [`ARCHITECTURE.md`](ARCHITECTURE.md).

Use the GitHub connector to read/write/commit with compare-and-swap if this chat's container cannot access GitHub; use GitHub Actions for execution on a real remote checkout. The connector is a **transport**, not an independent reviewer or test runner. Follow the per-task scope and original validation IDs. **Never** mark a task completed from a review packet, pre-research, compile-only pass, or successful self-test of this harness.