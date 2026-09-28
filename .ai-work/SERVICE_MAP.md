# Project test resource map

This project-local router maps every automated validation to its toolchain prerequisites, runtime services, and health checks. Keep credentials outside this file. Preflight commands and health probes must be bounded and read-only.

<!-- pae-service-map:begin -->
```json
{
  "schema_version": 1,
  "inventory_reviewed": true,
  "snapshot": {
    "algorithm": "sha256-path-content-v2-streamed",
    "digest": "037ef4f67f1e31158cf55c0ab25e01c861f586e4552e1eea8125e4caaf8e125a",
    "source_count": 26
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
