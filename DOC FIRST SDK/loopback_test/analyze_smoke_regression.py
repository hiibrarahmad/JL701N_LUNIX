#!/usr/bin/env python3
"""Analyze merged dual-bud logs for smoke and regression signals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze merged loopback log file")
    parser.add_argument("--log", required=True, help="Path to merged log")
    parser.add_argument(
        "--profile",
        default="tools/loopback_test/profiles/smoke_regression_default.json",
        help="Path to smoke/regression profile JSON",
    )
    parser.add_argument(
        "--expected-fw-token",
        default="",
        help="Expected firmware marker token, such as commit ID, version string, or unique log tag",
    )
    parser.add_argument(
        "--report",
        default="",
        help="Optional output report path (markdown). If omitted, report is placed next to the log file.",
    )
    return parser.parse_args()


def load_profile(profile_path: Path) -> dict:
    with profile_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def count_matches(lines: list[str], keywords: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    lowered = [line.lower() for line in lines]
    for kw in keywords:
        token = kw.lower()
        counts[kw] = sum(1 for line in lowered if token in line)
    return counts


def extract_role_lines(lines: list[str], role: str) -> list[str]:
    marker = f"[{role}]"
    return [line for line in lines if marker in line]


def main() -> int:
    args = parse_args()
    log_path = Path(args.log)
    profile_path = Path(args.profile)

    if not log_path.exists():
        raise SystemExit(f"Log file not found: {log_path}")
    if not profile_path.exists():
        raise SystemExit(f"Profile file not found: {profile_path}")

    profile = load_profile(profile_path)
    lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()

    right_lines = extract_role_lines(lines, "RIGHT")
    left_lines = extract_role_lines(lines, "LEFT")

    forbidden = profile.get("forbidden_keywords", [])
    warning = profile.get("warning_keywords", [])
    tws_expected = profile.get("tws_expected_keywords", [])

    forbidden_counts = count_matches(lines, forbidden)
    warning_counts = count_matches(lines, warning)
    tws_counts = count_matches(lines, tws_expected)
    serial_error_count = sum(1 for line in lines if "[SERIAL_ERROR]" in line)

    fw_token = args.expected_fw_token.strip()
    fw_match_count = 0
    if fw_token:
        fw_match_count = sum(1 for line in lines if fw_token.lower() in line.lower())

    hard_fail = any(v > 0 for v in forbidden_counts.values())
    tws_present = any(v > 0 for v in tws_counts.values())
    missing_side = len(right_lines) == 0 or len(left_lines) == 0

    summary_status = "PASS"
    if hard_fail:
        summary_status = "FAIL"
    elif serial_error_count > 0:
        summary_status = "FAIL"
    elif missing_side:
        summary_status = "FAIL"
    elif not tws_present:
        summary_status = "WARN"

    report_path = Path(args.report) if args.report else log_path.with_suffix(".report.md")

    with report_path.open("w", encoding="utf-8") as report:
        report.write("# Loopback Smoke Regression Report\n\n")
        report.write(f"- Status: **{summary_status}**\n")
        report.write(f"- Log file: {log_path}\n")
        report.write(f"- Total lines: {len(lines)}\n")
        report.write(f"- RIGHT lines: {len(right_lines)}\n")
        report.write(f"- LEFT lines: {len(left_lines)}\n")
        report.write(f"- Serial errors: {serial_error_count}\n")
        report.write("\n")

        if fw_token:
            report.write("## Firmware Token Check\n")
            report.write(f"- Expected token: `{fw_token}`\n")
            report.write(f"- Match count: {fw_match_count}\n\n")

        report.write("## Forbidden Keyword Counts\n")
        for key, value in forbidden_counts.items():
            report.write(f"- {key}: {value}\n")
        report.write("\n")

        report.write("## Warning Keyword Counts\n")
        for key, value in warning_counts.items():
            report.write(f"- {key}: {value}\n")
        report.write("\n")

        report.write("## TWS Signal Keyword Counts\n")
        for key, value in tws_counts.items():
            report.write(f"- {key}: {value}\n")
        report.write("\n")

        report.write("## Outcome Rules\n")
        report.write("- FAIL: any forbidden keyword appears\n")
        report.write("- FAIL: any serial port error appears\n")
        report.write("- FAIL: either right or left bud has zero captured lines\n")
        report.write("- WARN: no TWS keywords appear\n")
        report.write("- PASS: no forbidden keywords and TWS keywords appear\n")

    print(f"Analysis complete: {summary_status}")
    print(f"Report: {report_path}")
    return 0 if summary_status != "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
