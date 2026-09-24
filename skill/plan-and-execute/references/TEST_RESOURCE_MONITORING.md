# Test resource inventory and monitoring

Read this reference before creating an ORCHESTRATED plan or changing its automated validation commands. The goal is to make every validation reproducible and to preserve enough runtime evidence to distinguish a code failure from an unhealthy dependency.

## 1. Reuse the project router

The durable project map defaults to `.ai-work/SERVICE_MAP.md`; it is outside any individual plan directory and survives plan cleanup/reset. This local Markdown cache reuses discoveries on the same checkout. If the team needs the map across clones/hosts, keep it in tracked project Markdown and pass that same `--map` path to `check`, `audit-plan`, and every watcher command. DIRECT work must still create no `.ai-work` state.

Start with the deterministic freshness check; its normal output is one compact line:

```bash
python <skill-dir>/scripts/service_map.py check --repo-root .
python <skill-dir>/scripts/service_map.py list --repo-root .
```

- If fresh, use `list` to retrieve only the validation IDs and resource names needed for this plan. Do not reread the whole map when the output already gives the needed identifiers.
- If missing, create the draft and inspect only likely test/build/CI/container inputs found by repository search:

  ```bash
  python <skill-dir>/scripts/service_map.py init --repo-root .
  rg -l -i "tomcat|mysql|postgres|redis|selenium|webdriver|playwright|junit|pytest|node(\.js)?|python|testcontainers|compose|DATABASE_URL|BASE_URL" --glob '!**/build/**' --glob '!**/target/**' --glob '!**/node_modules/**'
  ```

- If stale, `check` lists only paths whose content or presence changed since the last stamp. Read those paths and reconcile the map; do not repeat a workspace-wide study. New validation files, build/dependency manifests, CI jobs, Compose/container definitions, test fixtures, service config, or launch scripts can change the required resource map.
- Populate every automated validation command, including commands with no external service (`resources: []` explicitly means none). Map toolchain prerequisites separately from services: preflight each required runtime/framework once, and continuously monitor only processes/services whose health can change during the test. For each service record its role, source evidence, checks, timeouts, and interval. Set `inventory_reviewed: true` only after checking validation-to-toolchain and validation-to-resource coverage. After reconciling, update fingerprints explicitly:

  ```bash
  python <skill-dir>/scripts/service_map.py stamp --repo-root . --confirm-reconciled
  python <skill-dir>/scripts/service_map.py check --repo-root .
  ```

`service_map.py` fingerprints paths and content for test sources, build/test manifests, CI/container definitions, runtime-version files, and likely service configuration. It recognizes Node and Python version files, package-manager manifests/locks, Playwright config variants, pytest fixtures/config, JUnit Platform config, Maven/Gradle build inputs, and common Selenium/browser test sources. It streams candidates without a fixed size or file-count cutoff. Its `.ai-work/<map-name>.index.json` sidecar stores only path/hash metadata for concise deltas; the Markdown map remains the human-readable and reusable router. It excludes secret `.env` files and never stores file contents. An unreadable discovered input makes the map stale until access is restored. The digest detects changed inputs but does not prove semantic completeness: the planner still reconciles changed inputs and reviews validation-to-toolchain and validation-to-resource coverage. For projects resumed on different operating systems, add health-check variants with `platforms: ["posix"]` and/or `["windows"]`; the watcher runs only checks matching the current host and requires at least one applicable check per resource.

The machine-readable JSON lives in a fenced block inside the Markdown file. Use this shape:

```json
{
  "schema_version": 1,
  "inventory_reviewed": true,
  "snapshot": {"algorithm": "sha256-path-content-v2-streamed", "digest": "...", "source_count": 42},
  "toolchains": [
    {"id": "node", "name": "Node.js runtime", "command": ["node", "--version"], "version_regex": "^v20\\.", "timeout_seconds": 5},
    {"id": "python", "name": "Python runtime", "command": ["python", "--version"], "timeout_seconds": 5},
    {"id": "pytest", "name": "Python test runner", "command": ["python", "-m", "pytest", "--version"], "timeout_seconds": 10},
    {"id": "java", "name": "JVM runtime", "command": ["java", "-version"], "timeout_seconds": 5},
    {"id": "playwright", "name": "Project-local Playwright package", "command": ["node", "-e", "require.resolve('@playwright/test')"], "timeout_seconds": 5},
    {"id": "selenium-python", "name": "Python Selenium client", "command": ["python", "-c", "import selenium; print(selenium.__version__)"], "timeout_seconds": 5}
  ],
  "validations": [
    {"id": "VAL001", "name": "database integration tests", "command": ["./gradlew", "integrationTest"], "toolchains": ["java"], "resources": ["mysql"], "no_progress_timeout_seconds": 300},
    {"id": "VAL002", "name": "Python unit tests", "command": ["python", "-m", "pytest"], "toolchains": ["python", "pytest"], "resources": [], "no_progress_timeout_seconds": 900},
    {"id": "VAL003", "name": "Playwright browser tests", "command": ["npm", "test"], "toolchains": ["node", "playwright"], "resources": [], "no_progress_timeout_seconds": 300},
    {"id": "VAL004", "name": "Selenium browser tests", "command": ["python", "-m", "pytest", "tests/browser"], "toolchains": ["python", "pytest", "selenium-python"], "resources": ["selenium-grid"], "no_progress_timeout_seconds": 300}
  ],
  "resources": [
    {
      "id": "mysql", "name": "integration database", "type": "database",
      "evidence": ["compose.test.yaml", "src/test/resources/application-test.properties"],
      "checks": [
        {"id": "lock-waits", "description": "No pending metadata or InnoDB row-lock waits", "command": ["mysql", "--batch", "--skip-column-names", "--execute", "SELECT ..."], "every_seconds": 60, "timeout_seconds": 5, "startup_grace_seconds": 30, "success_exit_codes": [0], "healthy_regex": "^0$", "record_excerpt": true}
      ]
    },
    {
      "id": "selenium-grid", "name": "remote browser Grid", "type": "browser-grid",
      "evidence": ["compose.test.yaml", "tests/browser/conftest.py"],
      "checks": [
        {"id": "grid-ready", "description": "Grid ready and able to create sessions", "command": ["python", "-c", "import json,sys,urllib.request; data=json.load(urllib.request.urlopen('http://localhost:4444/status',timeout=3)); value=data.get('value',{}); sys.exit(0 if value.get('ready') is True else 1)"], "every_seconds": 60, "timeout_seconds": 5, "success_exit_codes": [0]}
      ]
    }
  ]
}
```

Validation, toolchain, and health-check commands are argv arrays and execute without an implicit shell. If a project specifically needs shell syntax, make the shell and script explicit in the array. Never put passwords, tokens, or `.env` values in Markdown or command arguments; use the project's existing local credential mechanism. Keep preflights/probes read-only and bounded. Toolchains are checked once before the test; a toolchain ID may name Node.js, Python, Java, a local Playwright/Selenium package, pytest, or a project build runner. Do not turn libraries/frameworks into fake long-lived services. Probe output is not persisted by default; set `record_excerpt: true` only when the output is known to be safe and useful (for example a lock count or filtered log error).

Each validation may set `no_progress_timeout_seconds` (default `300`, range `0..7200`; `0` disables). On POSIX, the watcher samples the test process group every 20 seconds and counts changed normalized output or increased aggregate CPU time as progress. If neither advances for the configured window while mapped dependencies are healthy, it records a bounded process snapshot, terminates that test process group, and returns a semantic failure so the next fresh worker is elevated. CPU activity prevents a quiet but working test from being interrupted. Increase this value for long silent phases; use the test's own per-test/global timeout for a more precise bound. Resource `every_seconds` checks continue independently at their configured interval (normally 60 seconds), so a 10-minute test receives repeated service samples. When process metrics are unavailable or the host is Windows, the watcher does not infer a stall from silence alone; repeated identical validation failures still feed the cross-attempt escalation clock.

## 2. Build a test-to-resource map

Inventory all automated validation commands used by the plan, then link each validation ID to every external process/service the command requires. Look for resources in test annotations/fixtures, test profile configuration, local launch scripts, build files, container definitions, CI jobs, environment variable names, and existing test documentation. Include resources the test starts itself (for example Testcontainers containers) as well as long-lived local backends. Record evidence paths so a later invocation can review only likely sources.

For each service, prefer a layered check that answers the failure question:

1. **Process/container exists:** is the expected Tomcat, browser, database, or Compose service process running?
2. **Ready for this test:** can the expected port or HTTP health endpoint answer, and does it report useful readiness (for example an available Selenium Node or an application health state)?
3. **Can make progress:** do service logs show startup failure, repeated exceptions, or a deadlock; is the database reporting blocked waits?

A listening port alone proves only that something accepted a connection. Use the narrowest useful health endpoint or native health check. Do not make a service healthy merely because its PID exists.

Typical probes to adapt to the repository:

| Resource | Runtime check | Diagnostic evidence |
|---|---|---|
| Node.js / Python / Java / test runner | Add a `toolchains` entry with a read-only version/import check and attach its ID to each validation that needs it. Checks run once before validation; a missing runtime is `environmental`. | Capture only a short version string or bounded failure message. Include version files and package manifests in the fingerprinted inventory. |
| Playwright | Preflight Node and the project-local Playwright package. Local browser/driver processes are children of the test process group; monitor that group. Check a remote browser service only when the project uses one. | Prefer traces on the first retry or only on failure; traces for every test add runtime and storage cost. Keep the failing trace with the current validation attempt. |
| JUnit | Treat JUnit as a Maven/Gradle-resolved framework, not a separate service or standalone runtime. Preflight Java and the project's build runner; its dependency/config files are fingerprinted, so do not add a fake JUnit process check. | Configure a bounded JUnit timeout and optional thread dump on timeout to preserve stack evidence before an outer timeout kills the JVM. |
| Python / pytest | Preflight the configured interpreter and test runner. For hangs, enable `faulthandler.dump_traceback_later()` through project test configuration or a test-owned bootstrap. | A bounded thread traceback is usually more useful than rereading several minutes of unrelated output. |
| Tomcat/backend | Check the OS process (Linux/macOS `pgrep` or `ps`; Windows service/process tools), then query the app's health URL. Use local JMX only if already enabled and authorized. | Use `log_watch.py scan` for new matching Catalina/application lines; its persistent path/device/inode/offset cursor emits only bounded new matches across intervals and retries. |
| MySQL | Run a short read-only connection/query using existing local credentials. To catch contention, count `PENDING` rows in `performance_schema.metadata_locks` and waits in `performance_schema.data_lock_waits`; inspect `performance_schema.processlist` when a failure needs the waiting thread/query. | Retain the lock counts and bounded relevant diagnostics, not a full process list containing unrelated SQL or customer data. A granted lock is normal; a pending request/wait edge is the useful signal. Instrumentation and privileges vary by MySQL version/config. |
| Selenium | Preflight the client library as a toolchain (for example Python `import selenium`); query remote Grid `/status` as a service and assert readiness plus the expected registered Node/slot. When a local driver is launched directly, also check the driver/browser process and WebDriver endpoint. | Record status/readiness and node availability. A live Hub process without a usable Node is not ready for browser tests. |
| Docker Compose/container | Prefer an existing `healthcheck`; query the container's health state while the validation runs. Use `depends_on: condition: service_healthy` to gate startup when the project owns the Compose definition. | Capture the service state and a small, bounded log tail on failure. Do not run `up`, `restart`, or `down` from a health probe. |

Tests that create containers should use the project's native readiness strategy (HTTP success, a service health check, or a bounded log condition) before using the service; the resource watcher then checks that it remains healthy during longer validations. A check's optional `failure_class` defaults to `environmental`. Choose `semantic` only for a project-owned diagnostic signal that directly indicates a code/test defect, such as a persistent lock wait created by the validation; this lets model routing respond to the signal.

Example health-check entries to adapt (paths, endpoint fields, and process names must come from the current project):

```json
{"id":"tomcat-process","command":["pgrep","-af","org.apache.catalina.startup.Bootstrap"],"platforms":["posix"],"every_seconds":60,"timeout_seconds":3,"success_exit_codes":[0]}
{"id":"tomcat-errors","command":["python","<skill-dir>/scripts/log_watch.py","scan","--repo-root",".","--file","logs/catalina.out","--id","tomcat-errors","--pattern","SEVERE|Address already in use","--max-matches","5"],"every_seconds":60,"timeout_seconds":5,"startup_grace_seconds":0,"success_exit_codes":[0],"record_excerpt":true}
{"id":"mysql-lock-waits","command":["mysql","--batch","--silent","--skip-column-names","--execute","SELECT (SELECT COUNT(*) FROM performance_schema.metadata_locks WHERE LOCK_STATUS='PENDING') + (SELECT COUNT(*) FROM performance_schema.data_lock_waits)"],"every_seconds":60,"timeout_seconds":5,"startup_grace_seconds":30,"success_exit_codes":[0],"healthy_regex":"^0$","record_excerpt":true}
{"id":"selenium-grid","command":["python","-c","import json,sys,urllib.request; data=json.load(urllib.request.urlopen('http://localhost:4444/status',timeout=3)); value=data.get('value',{}); sys.exit(0 if value.get('ready') is True else 1)"],"every_seconds":60,"timeout_seconds":5,"success_exit_codes":[0]}
```

Use a second Tomcat check against the app's actual readiness URL; the OS-process probe alone cannot tell whether the application deployed. `pgrep` is a Linux/macOS example: use the host's process/service query on Windows. The MySQL query counts pending metadata lock requests plus InnoDB lock-wait edges, not all granted locks. Selenium `/status` must be interpreted for the Grid version in use; if a usable browser Node is required, prefer a small project-specific checker that also asserts expected Node availability/slots rather than only HTTP 200. `log_watch.py` examines only the last 128 KiB on first use and then only appended bytes (capped at 1 MiB per sample), emits at most five matching 500-character lines, and detects rotation/truncation without changing the source log. If a sample would skip bytes beyond that cap, it fails as unhealthy and reports the gap while retaining the raw log. Its small cursor under `.ai-work/resource-watch/log-cursors/` persists across plan retries, so old errors are not emitted again; delete the specific cursor file to replay the recent tail. Set `startup_grace_seconds: 0` when the first log sample must count existing recent errors; ordinary process/readiness probes may need startup grace. `every_seconds` is 10–300 and defaults to 60, so a 10-minute run gets repeated service samples; the test PID and bounded POSIX process-group snapshot are also recorded every 60 seconds.

## 3. Run mapped validations under the watcher

For every task validation, store one wrapper command that names exactly one map validation ID:

```bash
python <skill-dir>/scripts/resource_watch.py run \
  --repo-root . --map .ai-work/SERVICE_MAP.md --validation VAL001
```

The test argv comes from that map entry, which binds it to its toolchain IDs and resource IDs. The watcher checks toolchains before starting, samples services at each configured interval, tracks the test process group, and writes JSONL evidence under `.ai-work/resource-watch/`. A 10-minute validation therefore receives periodic service/process samples throughout its run. Startup failures may use `startup_grace_seconds`; an unhealthy check uses its configured failure class (environmental by default). A no-progress timeout preserves the process snapshot, stops a stalled test group, and triggers a stronger next worker; the regular outer validation timeout remains the final bound.

The wrapper runs commands directly from argv; it does not start, stop, repair, or reconfigure project services. A health command's nonzero exit, timeout, missing executable, or failed regex is recorded as unhealthy. Environmental health failure keeps the model route stable; a deliberately semantic diagnostic may elevate it. On POSIX, monitored validations require process enumeration via `ps` or `/proc` so timeouts can also clean nested probe processes; without either, the watcher fails before starting the test.

Before execution, audit that every task validation is a standalone Python watcher invocation, refers to a known validation ID, uses the expected map, and the map is still fresh. The audit rejects shell pipelines, comments, and trailing commands:

```bash
python <skill-dir>/scripts/service_map.py audit-plan \
  --repo-root . --map .ai-work/SERVICE_MAP.md --plan .ai-work/<plan-id>
```

After a worker changes a test, test configuration, or service dependency, reconcile and restamp the project map before the validation wrapper runs. If the change introduces a new resource or a new validation command, update the map and plan mapping first; do not silently accept an unmapped dependency. Successful plan cleanup deletes only `.ai-work/<plan-id>/`, not `SERVICE_MAP.md`, its hash index, or runtime-monitor reports.

## 4. Research notes

Vendor-specific setup details change. Prefer the project's existing mechanisms and current official docs; do not enable remote management interfaces just to satisfy monitoring. Tomcat notes, MySQL lock queries, Selenium readiness, Compose startup health, and Testcontainers wait strategies are summarized with source links in [`docs/RESEARCH_BASIS.md`](../../../docs/RESEARCH_BASIS.md#test-resource-observability).
