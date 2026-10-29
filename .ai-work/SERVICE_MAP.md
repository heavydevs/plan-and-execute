# Project test resource map

This project-local router maps every automated validation to its toolchain prerequisites, runtime services, and health checks. Keep credentials outside this file. Preflight commands and health probes must be bounded and read-only.

<!-- pae-service-map:begin -->
```json
{
  "schema_version": 1,
  "inventory_reviewed": true,
  "snapshot": {
    "algorithm": "sha256-path-content-v2-streamed",
    "digest": "a9209e97f1b983c6c255db936c0987521a2b43ef1b041a1f32868af3f696ca00",
    "source_count": 58
  },
  "toolchains": [
    {
      "id": "PYTHON",
      "command": [
        "python",
        "--version"
      ]
    },
    {
      "id": "NODE",
      "command": [
        "node",
        "--version"
      ]
    }
  ],
  "validations": [
    {
      "id": "REQUIREMENTS",
      "command": [
        "python",
        "-c",
        "from pathlib import Path; p=Path('docs/requests/auxiliary-model-assistants-and-tier-routing.md').read_text(); assert all(x in p for x in ('R001','R010','Acceptance','read-only','fallback')); assert Path('docs/research/AUXILIARY_ROUTING.md').stat().st_size > 1000"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "ROUTING_CONFIG",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/routing_config_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "AVAILABILITY",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/availability_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "CONFIGURE",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/configure_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "ASSISTANT",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/assistant_triage_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "MODEL_ROUTING",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/model_routing_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "PROVIDER",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/provider_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "ROUTING",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/routing_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "PREPLAN",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/preplan_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "DOC_BASELINE",
      "command": [
        "python",
        "tools/doc_baseline.py",
        "check",
        "--baseline",
        "docs/research/ROUTING_DOC_BASELINE.json"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "MODEL_CATALOG",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/model_catalog_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "CATALOG_REFRESH",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/model_catalogctl_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "MUSE",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/muse_provider_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "GLM",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/glm_provider_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "DEEPSEEK",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/deepseek_provider_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "MODEL_MATRIX",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/model_matrix_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "SELECTOR",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/route_selector_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "TELEMETRY",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/telemetry_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "DELEGATION",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/delegation_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "ARTIFACT_HYGIENE",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/artifact_hygiene_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "FAILURE_EVIDENCE",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/failure_evidence_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "CLI",
      "command": [
        "node",
        "--test",
        "test/cli.test.js"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "SKILL_DOCS",
      "command": [
        "node",
        "tools/validate-skill.js"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "EVAL_THRESHOLDS",
      "command": [
        "python",
        "tools/routing_eval_predeclaration_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "SHADOW_EVAL",
      "command": [
        "python",
        "tools/routing_eval_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "ROLLOUT",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/rollout_gate_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "BENCHMARK",
      "command": [
        "python",
        "tools/skill_benchmark_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "WORKTREE_AUDIT",
      "command": [
        "python",
        "tools/worktree_audit.py",
        "check",
        "--record",
        "docs/research/WORKTREE_AUDIT.json"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "RUNNER_SNAPSHOT",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/snapshot_runner_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "ALL",
      "command": [
        "npm",
        "run",
        "check"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 900,
      "name": "full npm run check"
    },
    {
      "id": "PROGRESS_SIGNAL",
      "name": "progress/error signal contract self-test",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/progress_signal_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "PROGRESS_WATCH",
      "name": "progress window self-test",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/progress_watch_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "PROGRESS_RUNNER",
      "name": "runner progress/timeout self-test",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/progress_runner_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "JOBCTL",
      "name": "supervised job controller self-test",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/jobctl_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "LIFECYCLE",
      "name": "lifecycle/lease self-test",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/lifecycle_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "SELF_TEST",
      "name": "core planctl/runner self-test",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "TOKEN_EFFICIENCY",
      "name": "prompt/token budget self-test",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/token_efficiency_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "WATCHDOG",
      "name": "watchdogctl status/watch self-test",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/watchdogctl_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "LOG_WATCH",
      "name": "log_watch scan/digest self-test",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/log_watch_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "INSTALLER",
      "name": "installer node tests",
      "command": [
        "node",
        "--test",
        "test/installer.test.js"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "CLEAN_TOOL",
      "name": "generated-file cleaner tolerates unreadable .ai-work trees",
      "command": [
        "node",
        "tools/clean-generated.js"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "VERSION_SYNC",
      "name": "package/lock/changelog version 0.10.0 and README/CHANGELOG mention watchdogctl",
      "command": [
        "python",
        "-c",
        "import json,pathlib,re; v='0.10.0'; p=json.loads(pathlib.Path('package.json').read_text(encoding='utf-8')); l=json.loads(pathlib.Path('package-lock.json').read_text(encoding='utf-8')); c=pathlib.Path('CHANGELOG.md').read_text(encoding='utf-8'); assert p['version']==v, p['version']; assert l.get('version')==v, l.get('version'); assert l.get('packages',{}).get('',{}).get('version',v)==v; assert re.search(r'^## 0\\.10\\.0 - 20\\d\\d-\\d\\d-\\d\\d', c, re.M), 'CHANGELOG heading'; assert all('watchdogctl' in pathlib.Path(n).read_text(encoding='utf-8') for n in ('README.md','README.pt-BR.md','CHANGELOG.md')), 'README/CHANGELOG must mention watchdogctl'; print('version-sync ok', v)"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "DELIVERY",
      "name": "HEAD on main pushed to origin with attribution and clean tree",
      "command": [
        "python",
        "-c",
        "import subprocess as s; g=lambda *a: s.run(['git',*a],capture_output=True,text=True,check=True).stdout.strip(); assert g('rev-parse','--abbrev-ref','HEAD')=='main'; assert g('status','--porcelain')=='', 'working tree not clean'; h=g('rev-parse','HEAD'); r=g('ls-remote','origin','refs/heads/main').split()[0]; assert h==r, ('remote main differs', h, r); assert 'Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>' in g('log','-1','--format=%B'), 'attribution trailer'; assert '\"version\": \"0.10.0\"' in g('show','HEAD:package.json'), 'version not committed'; assert g('ls-tree','--name-only','HEAD','skill/plan-and-execute/scripts/watchdogctl.py'), 'watchdogctl not committed'; print('delivery ok', h[:12])"
      ],
      "resources": [
        "github-origin"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 120
    },
    {
      "id": "HOST_INSTALL",
      "name": "installed claude/codex/antigravity user copies match skill/ hash",
      "command": [
        "node",
        "bin/plan-and-execute.js",
        "status",
        "all",
        "--scope",
        "user",
        "--verify"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "TALEPACE_PLAN",
      "name": "read-only validate of the active TalePace plan with the installed codex copy",
      "command": [
        "python",
        "C:/Users/luizc/.agents/skills/plan-and-execute/scripts/planctl_concise.py",
        "validate",
        "--plan",
        "C:/Users/luizc/projetos/talepace/git/talepace/.ai-work/20261011-021332-corrigir-as-falhas-de-processamento-e-provar-100-de-completude-d"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "NODE_TESTS",
      "name": "all node tests (installer, cli, clean)",
      "command": [
        "npm",
        "run",
        "test:node"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "WORKLOAD_ROUTING",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/workload_routing_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "STANDALONE_VALIDATION",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/validatectl_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "OBSERVER",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/observer_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "COMPANION",
      "command": [
        "python",
        "skill/plan-and-execute/scripts/companion_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "COMPANION_INSTALL",
      "command": [
        "node",
        "--test",
        "test/companion.test.js",
        "test/installer.test.js"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_001",
      "name": "Implementation 001 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "001"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_002",
      "name": "Implementation 002 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "002"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_003",
      "name": "Implementation 003 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "003"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_004",
      "name": "Implementation 004 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "004"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_005",
      "name": "Implementation 005 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "005"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_006",
      "name": "Implementation 006 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "006"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_007",
      "name": "Implementation 007 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "007"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_008",
      "name": "Implementation 008 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "008"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_009",
      "name": "Implementation 009 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "009"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_010",
      "name": "Implementation 010 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "010"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_011",
      "name": "Implementation 011 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "011"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_012",
      "name": "Implementation 012 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "012"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_013",
      "name": "Implementation 013 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "013"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_014",
      "name": "Implementation 014 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "014"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_015",
      "name": "Implementation 015 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "015"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_016",
      "name": "Implementation 016 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "016"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_017",
      "name": "Implementation 017 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "017"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_018",
      "name": "Implementation 018 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "018"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_019",
      "name": "Implementation 019 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "019"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_020",
      "name": "Implementation 020 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "020"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_021",
      "name": "Implementation 021 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "021"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_022",
      "name": "Implementation 022 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "022"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_023",
      "name": "Implementation 023 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "023"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_024",
      "name": "Implementation 024 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "024"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_025",
      "name": "Implementation 025 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "025"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_026",
      "name": "Implementation 026 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "026"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_027",
      "name": "Implementation 027 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "027"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_028",
      "name": "Implementation 028 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "028"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_029",
      "name": "Implementation 029 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "029"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_030",
      "name": "Implementation 030 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "030"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_031",
      "name": "Implementation 031 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "031"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_032",
      "name": "Implementation 032 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "032"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_033",
      "name": "Implementation 033 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "033"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_034",
      "name": "Implementation 034 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "034"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_035",
      "name": "Implementation 035 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "035"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_036",
      "name": "Implementation 036 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "036"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_037",
      "name": "Implementation 037 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "037"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_038",
      "name": "Implementation 038 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "038"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_039",
      "name": "Implementation 039 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "039"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_040",
      "name": "Implementation 040 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "040"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_041",
      "name": "Implementation 041 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "041"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_042",
      "name": "Implementation 042 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "042"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_043",
      "name": "Implementation 043 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "043"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_044",
      "name": "Implementation 044 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "044"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_045",
      "name": "Implementation 045 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "045"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_046",
      "name": "Implementation 046 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "046"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_047",
      "name": "Implementation 047 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "047"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_048",
      "name": "Implementation 048 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "048"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_049",
      "name": "Implementation 049 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "049"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_050",
      "name": "Implementation 050 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "050"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_051",
      "name": "Implementation 051 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "051"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_052",
      "name": "Implementation 052 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "052"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_053",
      "name": "Implementation 053 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "053"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_054",
      "name": "Implementation 054 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "054"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_055",
      "name": "Implementation 055 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "055"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_056",
      "name": "Implementation 056 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "056"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_057",
      "name": "Implementation 057 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "057"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_058",
      "name": "Implementation 058 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "058"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_059",
      "name": "Implementation 059 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "059"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_060",
      "name": "Implementation 060 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "060"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_061",
      "name": "Implementation 061 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "061"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_062",
      "name": "Implementation 062 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "062"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_063",
      "name": "Implementation 063 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "063"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_064",
      "name": "Implementation 064 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "064"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_065",
      "name": "Implementation 065 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "065"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_066",
      "name": "Implementation 066 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "066"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_067",
      "name": "Implementation 067 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "067"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_068",
      "name": "Implementation 068 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "068"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_069",
      "name": "Implementation 069 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "069"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_070",
      "name": "Implementation 070 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "070"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_071",
      "name": "Implementation 071 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "071"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_072",
      "name": "Implementation 072 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "072"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_073",
      "name": "Implementation 073 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "073"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_074",
      "name": "Implementation 074 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "074"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_075",
      "name": "Implementation 075 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "075"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_076",
      "name": "Implementation 076 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "076"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_077",
      "name": "Implementation 077 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "077"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_078",
      "name": "Implementation 078 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "078"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_079",
      "name": "Implementation 079 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "079"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_080",
      "name": "Implementation 080 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "080"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_081",
      "name": "Implementation 081 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "081"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_082",
      "name": "Implementation 082 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "082"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_083",
      "name": "Implementation 083 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "083"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_084",
      "name": "Implementation 084 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "084"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_085",
      "name": "Implementation 085 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "085"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_086",
      "name": "Implementation 086 receipt gate",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--task",
        "086"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_STRUCTURE",
      "name": "Single implementation plan and prepared-research structure",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/check_delivery.py",
        "--repo-root",
        ".",
        "--structure"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_GATE_TESTS",
      "name": "Plan-local receipt and research integrity regression tests",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/delivery_gate_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_001",
      "name": "Implementation 001 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "001"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_002",
      "name": "Implementation 002 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "002"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_003",
      "name": "Implementation 003 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "003"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_004",
      "name": "Implementation 004 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "004"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_005",
      "name": "Implementation 005 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "005"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_006",
      "name": "Implementation 006 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "006"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_007",
      "name": "Implementation 007 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "007"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_008",
      "name": "Implementation 008 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "008"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_009",
      "name": "Implementation 009 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "009"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_010",
      "name": "Implementation 010 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "010"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_011",
      "name": "Implementation 011 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "011"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_012",
      "name": "Implementation 012 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "012"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_013",
      "name": "Implementation 013 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "013"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_014",
      "name": "Implementation 014 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "014"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_015",
      "name": "Implementation 015 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "015"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_016",
      "name": "Implementation 016 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "016"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_017",
      "name": "Implementation 017 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "017"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_018",
      "name": "Implementation 018 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "018"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_019",
      "name": "Implementation 019 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "019"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_020",
      "name": "Implementation 020 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "020"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_021",
      "name": "Implementation 021 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "021"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_022",
      "name": "Implementation 022 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "022"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_023",
      "name": "Implementation 023 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "023"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_024",
      "name": "Implementation 024 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "024"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_025",
      "name": "Implementation 025 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "025"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_026",
      "name": "Implementation 026 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "026"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_027",
      "name": "Implementation 027 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "027"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_028",
      "name": "Implementation 028 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "028"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_029",
      "name": "Implementation 029 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "029"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_030",
      "name": "Implementation 030 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "030"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_031",
      "name": "Implementation 031 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "031"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_032",
      "name": "Implementation 032 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "032"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_033",
      "name": "Implementation 033 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "033"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_034",
      "name": "Implementation 034 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "034"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_035",
      "name": "Implementation 035 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "035"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_036",
      "name": "Implementation 036 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "036"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_037",
      "name": "Implementation 037 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "037"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_038",
      "name": "Implementation 038 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "038"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_039",
      "name": "Implementation 039 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "039"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_040",
      "name": "Implementation 040 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "040"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_041",
      "name": "Implementation 041 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "041"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_042",
      "name": "Implementation 042 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "042"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_043",
      "name": "Implementation 043 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "043"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_044",
      "name": "Implementation 044 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "044"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_045",
      "name": "Implementation 045 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "045"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_046",
      "name": "Implementation 046 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "046"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_047",
      "name": "Implementation 047 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "047"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_048",
      "name": "Implementation 048 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "048"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_049",
      "name": "Implementation 049 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "049"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_050",
      "name": "Implementation 050 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "050"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_051",
      "name": "Implementation 051 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "051"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_052",
      "name": "Implementation 052 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "052"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_053",
      "name": "Implementation 053 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "053"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_054",
      "name": "Implementation 054 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "054"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_055",
      "name": "Implementation 055 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "055"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_056",
      "name": "Implementation 056 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "056"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_057",
      "name": "Implementation 057 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "057"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_058",
      "name": "Implementation 058 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "058"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_059",
      "name": "Implementation 059 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "059"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_060",
      "name": "Implementation 060 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "060"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_061",
      "name": "Implementation 061 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "061"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_062",
      "name": "Implementation 062 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "062"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_063",
      "name": "Implementation 063 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "063"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_064",
      "name": "Implementation 064 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "064"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_065",
      "name": "Implementation 065 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "065"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_066",
      "name": "Implementation 066 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "066"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_067",
      "name": "Implementation 067 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "067"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_068",
      "name": "Implementation 068 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "068"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_069",
      "name": "Implementation 069 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "069"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_070",
      "name": "Implementation 070 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "070"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_071",
      "name": "Implementation 071 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "071"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_072",
      "name": "Implementation 072 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "072"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_073",
      "name": "Implementation 073 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "073"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_074",
      "name": "Implementation 074 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "074"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_075",
      "name": "Implementation 075 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "075"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_076",
      "name": "Implementation 076 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "076"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_077",
      "name": "Implementation 077 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "077"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_078",
      "name": "Implementation 078 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "078"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_079",
      "name": "Implementation 079 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "079"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_080",
      "name": "Implementation 080 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "080"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_081",
      "name": "Implementation 081 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "081"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_TESTS_082",
      "name": "Implementation 082 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "082"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 900
    },
    {
      "id": "P1_TESTS_083",
      "name": "Implementation 083 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "083"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 900
    },
    {
      "id": "P1_TESTS_084",
      "name": "Implementation 084 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "084"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 900
    },
    {
      "id": "P1_TESTS_085",
      "name": "Implementation 085 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "085"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 900
    },
    {
      "id": "P1_TESTS_086",
      "name": "Implementation 086 declared regression checks",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/run_task_checks.py",
        "--repo-root",
        ".",
        "--task",
        "086"
      ],
      "toolchains": [
        "PYTHON",
        "NODE"
      ],
      "resources": [],
      "no_progress_timeout_seconds": 900
    },
    {
      "id": "P1_RESEARCH_R2",
      "name": "Read-only research revision2 preparation validation",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/research_readiness.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_RESEARCH_R2_TESTS",
      "name": "Read-only research revision2 preparation validation",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/research_readiness_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    },
    {
      "id": "P1_DELIVERY_GATE_TESTS",
      "name": "Read-only research revision2 preparation validation",
      "command": [
        "python",
        "docs/plans/20261028-skill-optimization/support/delivery_gate_self_test.py"
      ],
      "resources": [],
      "toolchains": [
        "PYTHON"
      ],
      "no_progress_timeout_seconds": 300
    }
  ],
  "resources": [
    {
      "id": "github-origin",
      "name": "GitHub origin remote reachable over SSH",
      "type": "git-remote",
      "evidence": [
        ".git/config"
      ],
      "checks": [
        {
          "id": "origin-reachable",
          "description": "git ls-remote answers for origin main",
          "command": [
            "git",
            "ls-remote",
            "--exit-code",
            "origin",
            "refs/heads/main"
          ],
          "every_seconds": 60,
          "timeout_seconds": 30,
          "success_exit_codes": [
            0
          ]
        }
      ]
    }
  ]
}
```
<!-- pae-service-map:end -->

## Maintenance

`service_map.py check` compares this snapshot with a deterministic index of test, build, CI, container, and service configuration inputs. When it reports changes, inspect only those paths, reconcile the validation/resource/check entries, then run `service_map.py stamp --confirm-reconciled`. A fresh digest does not replace the review bit: set `inventory_reviewed` to `true` only after the map is complete.
