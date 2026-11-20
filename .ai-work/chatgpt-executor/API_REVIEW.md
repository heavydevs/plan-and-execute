# Optional provider-independent-from-CLI code-review adapter

See `api_review.py`. The script invokes a **separate model using the OpenAI Responses API**, not a fabricated reviewer or the in-chat model. It requires explicit, separately authorized API credentials in `OPENAI_API_KEY`. The chat environment currently provides no credential; GitHub Actions similarly cannot receive it unless configured as a repository secret. Do **not** commit credentials or place them in log output.

Offline dry-run (checks real checkout and bounds):

```bash
python .ai-work/chatgpt-executor/api_review.py --task 015 --dry-run
```

Actual user-authorized invocation from a secure environment with an API key:

```bash
python .ai-work/chatgpt-executor/api_review.py --task 015
```

The adapter sends **reviewed source code** to a third-party hosted API and may be billed. Do not run automatically on every push. All listed task inputs must be readable, within the 800 KB bound and unchanged during review. Review results carry real source hashes, model, response ID, effort and usage. The returned record is **supplemental review**, not a substitute for `review_dispatch.py` or the existing `015` delivery gate. If an integration requires acceptance of this alternate provider, amend the plan's gate through the authorized revision procedure, and test rejection of forged/stale records before use.

API reference: [Responses create](https://platform.openai.com/docs/api-reference/responses/create), [Structured outputs](https://platform.openai.com/docs/guides/structured-outputs).