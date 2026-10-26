#!/usr/bin/env python3.11
"""Install each tool by its distribution name and smoke-test the CLI.

Package names have no 01_ / 04_ prefixes. Paper 6 has no neuroinsight-agent command.
Requires a writable venv. Does not download MRI. Does not call a model API.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PACKAGES = [
    ("scicap", ROOT / "01_SciCap"),
    ("sciguard", ROOT / "02_SciGuard"),
    ("neuroagentbench", ROOT / "03_NeuroAgentBench"),
    ("evidencegraph", ROOT / "04_EvidenceGraph"),
    ("neuroworkbench", ROOT / "05_NeuroInsight"),
    ("neuroworkbench-proposer", ROOT / "06_NeuroInsight_Agent"),
]

COMMANDS = ("scicap", "sciguard", "neuroagentbench", "evidencegraph", "neuroworkbench")
FORBIDDEN_COMMANDS = ("neuroinsight-agent", "neuroinsight")


def run(cmd: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, text=True, capture_output=True, env=env)


def main() -> int:
    python = sys.executable
    failures: list[str] = []

    print("== editable install ==")
    for dist_name, path in PACKAGES:
        install_env = os.environ.copy()
        install_env["PIP_INDEX_URL"] = os.environ.get("PIP_INDEX_URL", "https://pypi.org/simple")
        proc = run(
            [
                python,
                "-m",
                "pip",
                "install",
                "--no-build-isolation",
                "--no-deps",
                "-e",
                str(path),
                "-q",
            ],
            env=install_env,
        )
        if proc.returncode != 0:
            failures.append(f"install {dist_name}: {proc.stderr[-800:]}")
            print(f"FAIL install {dist_name}")
        else:
            print(f"OK   install {dist_name}")

    meta = run(
        [
            python,
            "-c",
            "import importlib.metadata as m; "
            "print(','.join(sorted({d.metadata['Name'] for d in m.distributions()})))",
        ]
    )
    names = {item.lower() for item in meta.stdout.strip().split(",") if item}
    for dist_name, _ in PACKAGES:
        if dist_name.lower() not in names:
            failures.append(f"metadata missing {dist_name}")
            print(f"FAIL metadata {dist_name}")
        else:
            print(f"OK   metadata {dist_name}")
        if dist_name.replace("-", "_").startswith(("01_", "02_", "03_", "04_", "05_", "06_")):
            failures.append(f"numbered distribution name {dist_name}")

    bin_dir = Path(sys.prefix) / ("Scripts" if os.name == "nt" else "bin")
    for cmd in COMMANDS:
        exe = bin_dir / cmd
        if not exe.is_file():
            failures.append(f"missing command {cmd}")
            print(f"FAIL command {cmd}")
        else:
            print(f"OK   command {cmd}")
    for cmd in FORBIDDEN_COMMANDS:
        if (bin_dir / cmd).exists():
            failures.append(f"forbidden command present: {cmd}")
            print(f"FAIL forbidden {cmd}")
        else:
            print(f"OK   no {cmd} command")

    smokes = [
        (
            "scicap",
            [
                "scicap",
                "invoke",
                str(
                    ROOT
                    / "01_SciCap/packages/scicap-neuro/capabilities/neuro.t1.hippocampal_volumes.yaml"
                ),
                "--instance",
                str(ROOT / "01_SciCap/examples/instances/complete_t1w.json"),
            ],
            0,
            "ALLOW",
        ),
        (
            "sciguard",
            [
                "sciguard",
                "validate",
                str(
                    ROOT
                    / "02_SciGuard/fixtures/invalid/labels_t1w_to_dwi_no_transform.yaml"
                ),
            ],
            0,
            "FAIL",
        ),
        (
            "neuroagentbench",
            [
                "neuroagentbench",
                "evaluate",
                "--task",
                str(ROOT / "03_NeuroAgentBench/tasks/connectome/nab-atlas-wrong.yaml"),
                "--run",
                str(ROOT / "03_NeuroAgentBench/examples/runs/atlas-wrong"),
            ],
            0,
            "false_success",
        ),
        (
            "evidencegraph",
            [
                "evidencegraph",
                "ingest",
                "--doi",
                "10.9999/restricted-mock",
                "--license-check",
            ],
            2,
            "not redistributable",
        ),
        (
            "neuroworkbench",
            [
                "neuroworkbench",
                "pin-check",
                str(ROOT / "05_NeuroInsight/examples/requests/t1w_human.yaml"),
            ],
            None,
            "pin_",
        ),
    ]

    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}{os.pathsep}{env.get('PATH', '')}"
    print("== smoke CLIs ==")
    for name, cmd, expect_code, needle in smokes:
        exe = bin_dir / cmd[0]
        if not exe.is_file():
            failures.append(f"smoke {name}: command not in {bin_dir}")
            print(f"FAIL smoke {name}: not in {bin_dir}")
            continue
        cmd = [python, str(exe), *cmd[1:]]
        proc = run(cmd, env=env)
        out = proc.stdout + proc.stderr
        code_ok = expect_code is None or proc.returncode == expect_code
        if not code_ok or needle.lower() not in out.lower():
            failures.append(
                f"smoke {name}: code={proc.returncode} expected={expect_code} "
                f"needle={needle!r} out={out[-600:]}"
            )
            print(f"FAIL smoke {name} code={proc.returncode}")
        else:
            print(f"OK   smoke {name}")

    print("== paper 6 import ==")
    proc = run(
        [
            python,
            "-c",
            "from proposer.propose import propose; "
            "from proposer.forbidden import assert_execution_not_loaded; "
            "assert_execution_not_loaded(); "
            "print('proposer_ok')",
        ]
    )
    if proc.returncode != 0 or "proposer_ok" not in proc.stdout:
        failures.append(f"paper6 import: {proc.stderr[-600:]}")
        print("FAIL paper6 import")
    else:
        print("OK   paper6 import")

    summary = {
        "ok": not failures,
        "failures": failures,
        "distribution_names": [name for name, _ in PACKAGES],
        "commands": list(COMMANDS),
        "forbidden_commands": list(FORBIDDEN_COMMANDS),
    }
    print(json.dumps(summary, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
