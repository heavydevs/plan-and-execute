# Project test resource map

This project-local router maps every automated validation to its toolchain prerequisites, runtime services, and health checks. Keep credentials outside this file. Preflight commands and health probes must be bounded and read-only.

<!-- pae-service-map:begin -->
```json
{
  "schema_version": 1,
  "inventory_reviewed": true,
  "snapshot": {
    "algorithm": "sha256-path-content-v2-streamed",
    "digest": "e8f405abb47f9c2e8f190779943d66e6bfa8ef3327536a11891cd00a99013728",
    "source_count": 55
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
