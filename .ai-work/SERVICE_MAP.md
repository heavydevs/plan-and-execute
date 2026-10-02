# Project test resource map

This project-local router maps every automated validation to its toolchain prerequisites, runtime services, and health checks. Keep credentials outside this file. Preflight commands and health probes must be bounded and read-only.

<!-- pae-service-map:begin -->
```json
{
  "schema_version": 1,
  "inventory_reviewed": true,
  "snapshot": {
    "algorithm": "sha256-path-content-v2-streamed",
    "digest": "ee2640c991aa6bfd08952c5645ffa2cdcbecb871b1299764c9a3bf9376e4fb0b",
    "source_count": 42
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
      "no_progress_timeout_seconds": 300
    }
  ],
  "resources": []
}
```
<!-- pae-service-map:end -->

## Maintenance

`service_map.py check` compares this snapshot with a deterministic index of test, build, CI, container, and service configuration inputs. When it reports changes, inspect only those paths, reconcile the validation/resource/check entries, then run `service_map.py stamp --confirm-reconciled`. A fresh digest does not replace the review bit: set `inventory_reviewed` to `true` only after the map is complete.
