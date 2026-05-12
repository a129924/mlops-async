# /// script
# requires-python = ">=3.10"
# ///
"""Step status tracker for plan/<topic>/<topic>.step.md files.

Usage:
  python step_tracker.py read_all <topic>
  python step_tracker.py read_not_run <topic>
  python step_tracker.py read_success <topic>
  python step_tracker.py check_all_succeeded <topic>
  python step_tracker.py check_impl_steps_succeeded <topic>
"""

import sys
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Literal
import argparse


@dataclass
class Step:
    """Represents a single step in the tracking file."""

    text: str
    status: Literal["done", "pending"]
    bracket: str  # Original bracket marker: [X], [x], or [ ]


IMPLEMENTATION_STEPS_HEADER = "## Implementation Steps"


def parse_steps(topic: str, plan_dir: Path = Path("plan")) -> list[Step]:
    """Parse steps from plan/<topic>/<topic>.step.md.

    Args:
        topic: Topic name (e.g., 'my-feature')
        plan_dir: Base plan directory (default: 'plan')

    Returns:
        List of Step objects

    Raises:
        FileNotFoundError: If .step.md file does not exist
    """
    step_file = plan_dir / topic / f"{topic}.step.md"

    if not step_file.exists():
        raise FileNotFoundError(f"找不到檔案: {step_file}")

    with open(step_file, encoding="utf-8") as f:
        steps = _parse_step_lines(list(enumerate(f.readlines(), start=1)))

    return steps


def parse_impl_steps(topic: str, plan_dir: Path = Path("plan")) -> list[Step]:
    """Parse only steps in the '## Implementation Steps' section."""
    step_file = plan_dir / topic / f"{topic}.step.md"

    if not step_file.exists():
        raise FileNotFoundError(f"File not found: {step_file}")

    with open(step_file, encoding="utf-8") as f:
        lines = f.readlines()

    impl_lines: list[tuple[int, str]] = []
    in_impl_section = False
    found_impl_section = False

    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped == IMPLEMENTATION_STEPS_HEADER:
            in_impl_section = True
            found_impl_section = True
            continue

        if in_impl_section and stripped.startswith("## "):
            break

        if in_impl_section:
            impl_lines.append((line_num, line))

    if not found_impl_section:
        raise ValueError(f"缺少必要區段: {IMPLEMENTATION_STEPS_HEADER}")

    return _parse_step_lines(impl_lines)


def _parse_step_lines(lines: list[tuple[int, str]]) -> list[Step]:
    """Parse checkbox step lines into Step objects."""
    steps: list[Step] = []
    pattern = re.compile(r"^\- \[(.)\](.*)")

    for line_num, line in lines:
        match = pattern.match(line.rstrip())
        if match:
            bracket_char = match.group(1)
            step_text = match.group(2).strip()
            bracket = f"[{bracket_char}]"

            if bracket_char == "X":
                status = "done"
            elif bracket_char == " ":
                status = "pending"
            elif bracket_char == "x":
                status = "pending"
                print(
                    f"警告: 在第 {line_num} 行發現小寫 [x]; 將視為待完成",
                    file=sys.stderr,
                )
            else:
                status = "pending"
                print(
                    (
                        "警告: 在第 "
                        f"{line_num} 行發現未預期的括號內容 [{bracket_char}]; 將視為待完成"
                    ),
                    file=sys.stderr,
                )

            steps.append(Step(text=step_text, status=status, bracket=bracket))

    return steps


def format_step(step: Step) -> str:
    """Format a step for display using original bracket."""
    return f"{step.bracket} {step.text}"


def read_all(topic: str, plan_dir: Path = Path("plan")) -> int:
    """Read and display all steps."""
    try:
        steps = parse_steps(topic, plan_dir)
    except FileNotFoundError as e:
        print(f"錯誤: {e}", file=sys.stderr)
        return 1

    for step in steps:
        print(format_step(step))

    return 0


def read_not_run(topic: str, plan_dir: Path = Path("plan")) -> int:
    """Read and display only pending steps."""
    try:
        steps = parse_steps(topic, plan_dir)
    except FileNotFoundError as e:
        print(f"錯誤: {e}", file=sys.stderr)
        return 1

    pending_steps = [s for s in steps if s.status == "pending"]

    for step in pending_steps:
        print(format_step(step))

    return 0


def read_success(topic: str, plan_dir: Path = Path("plan")) -> int:
    """Read and display only completed steps."""
    try:
        steps = parse_steps(topic, plan_dir)
    except FileNotFoundError as e:
        print(f"錯誤: {e}", file=sys.stderr)
        return 1

    done_steps = [s for s in steps if s.status == "done"]

    for step in done_steps:
        print(format_step(step))

    return 0


def check_all_succeeded(topic: str, plan_dir: Path = Path("plan")) -> int:
    """Check if all steps are complete. Exit 0 if yes, 1 if any pending."""
    try:
        steps = parse_steps(topic, plan_dir)
    except FileNotFoundError as e:
        print(f"錯誤: {e}", file=sys.stderr)
        return 1

    pending_steps = [s for s in steps if s.status == "pending"]

    if not pending_steps:
        total = len(steps)
        print(f"✅ 成功: 全部 {total} 個步驟都已完成")
        return 0

    print(f"❌ 阻擋: 仍有 {len(pending_steps)} 個步驟待完成 (exit code 1)")
    for step in pending_steps:
        print(format_step(step))

    return 1


def check_impl_steps_succeeded(topic: str, plan_dir: Path = Path("plan")) -> int:
    """Check if all implementation steps are complete. Exit 0 if yes, 1 if any pending."""
    try:
        steps = parse_impl_steps(topic, plan_dir)
    except (FileNotFoundError, ValueError) as e:
        print(f"錯誤: {e}", file=sys.stderr)
        return 1

    pending_steps = [s for s in steps if s.status == "pending"]

    if not pending_steps:
        total = len(steps)
        print(f"✅ 成功: 全部 {total} 個實作步驟都已完成")
        return 0

    print(f"❌ 阻擋: 仍有 {len(pending_steps)} 個實作步驟待完成 (exit code 1)")
    for step in pending_steps:
        print(format_step(step))

    return 1


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="查詢 plan/<topic>/<topic>.step.md 的步驟狀態")
    subparsers = parser.add_subparsers(dest="operation", required=True)

    # read_all
    read_all_parser = subparsers.add_parser("read_all", help="讀取全部步驟 (已完成與待完成)")
    read_all_parser.add_argument("topic", help="topic 名稱")

    # read_not_run
    read_not_run_parser = subparsers.add_parser("read_not_run", help="只讀取待完成步驟")
    read_not_run_parser.add_argument("topic", help="topic 名稱")

    # read_success
    read_success_parser = subparsers.add_parser("read_success", help="只讀取已完成步驟")
    read_success_parser.add_argument("topic", help="topic 名稱")

    # check_all_succeeded
    check_all_parser = subparsers.add_parser(
        "check_all_succeeded",
        help="檢查全部步驟是否完成; 全部完成回傳 0, 否則回傳 1",
    )
    check_all_parser.add_argument("topic", help="topic 名稱")

    # check_impl_steps_succeeded
    check_impl_steps_parser = subparsers.add_parser(
        "check_impl_steps_succeeded",
        help="檢查實作步驟是否完成; 全部完成回傳 0, 否則回傳 1",
    )
    check_impl_steps_parser.add_argument("topic", help="topic 名稱")

    args = parser.parse_args()

    topic = args.topic
    plan_dir = Path("plan")

    if args.operation == "read_all":
        return read_all(topic, plan_dir)
    elif args.operation == "read_not_run":
        return read_not_run(topic, plan_dir)
    elif args.operation == "read_success":
        return read_success(topic, plan_dir)
    elif args.operation == "check_all_succeeded":
        return check_all_succeeded(topic, plan_dir)
    elif args.operation == "check_impl_steps_succeeded":
        return check_impl_steps_succeeded(topic, plan_dir)

    return 1


if __name__ == "__main__":
    sys.exit(main())
