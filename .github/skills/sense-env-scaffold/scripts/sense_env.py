#!/usr/bin/env python3
"""
CLI entrypoint for the repository environment sensing scaffold.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sense_env_runtime import (
    RunMode,
    find_repo_root,
    resolve_output_path,
    run_acceptance,
    run_discovery,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Repository environment sensing scaffold (v1). "
            "Supports assertion kinds: path_exists, path_type, command_available. "
            "Does not claim general YAML support."
        )
    )
    parser.add_argument(
        "--mode",
        required=True,
        choices=[mode.value for mode in RunMode],
        help="Run mode: 'discovery' collects facts; 'acceptance' evaluates contract assertions.",
    )
    parser.add_argument(
        "--contract-file",
        default=None,
        help=(
            "Path to contract document containing a ```yaml [sensing-assertions] block. "
            "Acceptance mode only. Falls back to retrofit-plan.md then blueprint.md."
        ),
    )
    parser.add_argument(
        "--output",
        default=None,
        help=(
            "Output path for the live manifest JSON. "
            "Defaults to <repo_root>/.github/env-manifest.json."
        ),
    )
    parser.add_argument(
        "--snapshot",
        action="store_true",
        default=False,
        help=(
            "Also write a filtered snapshot to "
            "<repo_root>/.github/env-manifest.snapshot.json "
            "(only when the run exits 0)."
        ),
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    repo_root = find_repo_root(Path.cwd())
    output_path = resolve_output_path(args.output, repo_root)
    mode = RunMode(args.mode)

    if mode is RunMode.DISCOVERY:
        return int(run_discovery(repo_root, output_path, args.snapshot))

    return int(
        run_acceptance(
            repo_root=repo_root,
            output_path=output_path,
            contract_file=args.contract_file,
            snapshot=args.snapshot,
        )
    )


if __name__ == "__main__":
    sys.exit(main())
