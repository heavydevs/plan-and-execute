# Project test resource map

This project-local router maps every automated validation to its toolchain prerequisites, runtime services, and health checks. Keep credentials outside this file. Preflight commands and health probes must be bounded and read-only.

<!-- pae-service-map:begin -->
```json
{
  "schema_version": 1,
  "inventory_reviewed": true,
  "snapshot": {
    "algorithm": "sha256-path-content-v2-streamed",
    "digest": "0ba30b69233488d427496a7b0d8bc579a5df18d8f633638de8798818926029ab",
    "source_count": 56
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
      "name": "Plan 1 001 evidence packet gate",
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
      "name": "Plan 1 002 evidence packet gate",
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
      "name": "Plan 1 003 evidence packet gate",
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
      "name": "Plan 1 004 evidence packet gate",
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
      "name": "Plan 1 005 evidence packet gate",
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
      "name": "Plan 1 006 evidence packet gate",
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
      "name": "Plan 1 007 evidence packet gate",
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
      "name": "Plan 1 008 evidence packet gate",
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
      "name": "Plan 1 009 evidence packet gate",
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
      "name": "Plan 1 010 evidence packet gate",
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
      "name": "Plan 1 011 evidence packet gate",
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
      "name": "Plan 1 012 evidence packet gate",
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
      "name": "Plan 1 013 evidence packet gate",
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
      "name": "Plan 1 014 evidence packet gate",
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
      "name": "Plan 1 015 evidence packet gate",
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
      "name": "Plan 1 016 evidence packet gate",
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
      "name": "Plan 1 017 evidence packet gate",
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
      "name": "Plan 1 018 evidence packet gate",
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
      "name": "Plan 1 019 evidence packet gate",
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
      "name": "Plan 1 020 evidence packet gate",
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
      "name": "Plan 1 021 evidence packet gate",
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
      "name": "Plan 1 022 evidence packet gate",
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
      "name": "Plan 1 023 evidence packet gate",
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
      "name": "Plan 1 024 evidence packet gate",
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
      "name": "Plan 1 025 evidence packet gate",
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
      "name": "Plan 1 026 evidence packet gate",
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
      "name": "Plan 1 027 evidence packet gate",
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
      "name": "Plan 1 028 evidence packet gate",
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
      "name": "Plan 1 029 evidence packet gate",
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
      "name": "Plan 1 030 evidence packet gate",
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
      "name": "Plan 1 031 evidence packet gate",
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
      "name": "Plan 1 032 evidence packet gate",
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
      "name": "Plan 1 033 evidence packet gate",
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
      "name": "Plan 1 034 evidence packet gate",
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
      "name": "Plan 1 035 evidence packet gate",
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
      "name": "Plan 1 036 evidence packet gate",
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
      "name": "Plan 1 037 evidence packet gate",
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
      "name": "Plan 1 038 evidence packet gate",
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
      "name": "Plan 1 039 evidence packet gate",
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
      "name": "Plan 1 040 evidence packet gate",
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
      "name": "Plan 1 041 evidence packet gate",
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
      "name": "Plan 1 042 evidence packet gate",
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
      "name": "Plan 1 043 evidence packet gate",
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
      "name": "Plan 1 044 evidence packet gate",
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
      "name": "Plan 1 045 evidence packet gate",
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
      "name": "Plan 1 046 evidence packet gate",
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
      "name": "Plan 1 047 evidence packet gate",
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
      "name": "Plan 1 048 evidence packet gate",
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
      "name": "Plan 1 049 evidence packet gate",
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
      "name": "Plan 1 050 evidence packet gate",
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
      "name": "Plan 1 051 evidence packet gate",
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
      "name": "Plan 1 052 evidence packet gate",
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
      "name": "Plan 1 053 evidence packet gate",
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
      "name": "Plan 1 054 evidence packet gate",
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
      "name": "Plan 1 055 evidence packet gate",
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
      "name": "Plan 1 056 evidence packet gate",
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
      "name": "Plan 1 057 evidence packet gate",
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
      "name": "Plan 1 058 evidence packet gate",
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
      "name": "Plan 1 059 evidence packet gate",
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
      "name": "Plan 1 060 evidence packet gate",
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
      "name": "Plan 1 061 evidence packet gate",
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
      "name": "Plan 1 062 evidence packet gate",
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
      "name": "Plan 1 063 evidence packet gate",
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
      "name": "Plan 1 064 evidence packet gate",
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
      "name": "Plan 1 065 evidence packet gate",
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
      "name": "Plan 1 066 evidence packet gate",
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
      "name": "Plan 1 067 evidence packet gate",
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
      "name": "Plan 1 068 evidence packet gate",
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
      "name": "Plan 1 069 evidence packet gate",
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
      "name": "Plan 1 070 evidence packet gate",
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
      "name": "Plan 1 071 evidence packet gate",
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
      "name": "Plan 1 072 evidence packet gate",
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
      "name": "Plan 1 073 evidence packet gate",
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
      "name": "Plan 1 074 evidence packet gate",
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
      "name": "Plan 1 075 evidence packet gate",
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
      "name": "Plan 1 076 evidence packet gate",
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
      "name": "Plan 1 077 evidence packet gate",
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
      "name": "Plan 1 078 evidence packet gate",
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
      "name": "Plan 1 079 evidence packet gate",
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
      "name": "Plan 1 080 evidence packet gate",
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
      "name": "Plan 1 081 evidence packet gate",
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
      "name": "Plan 1 082 evidence packet gate",
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
      "name": "Plan 1 083 evidence packet gate",
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
      "name": "Plan 1 084 evidence packet gate",
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
      "name": "Plan 1 085 evidence packet gate",
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
      "name": "Plan 1 086 evidence packet gate",
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
      "name": "Plan 1 structure and requirement coverage",
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
      "name": "Plan 1 evidence validator self-tests",
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
