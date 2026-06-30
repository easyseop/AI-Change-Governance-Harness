#!/usr/bin/env bash
set -u

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR" || exit 1

python3 - <<'PY'
import json
import subprocess
import sys

import yaml


GATES = {
    "check-change-intent": ".harness/gates/check-change-intent.py",
    "check-sensitive-zones": ".harness/gates/check-sensitive-zones.py",
    "generate-change-evidence": ".harness/gates/generate-change-evidence.py",
    "extract-python-inventory": ".harness/gates/extract-python-inventory.py",
}


def run_command(command):
    return subprocess.run(
        command,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def load_output(gate, stdout):
    if gate in ("check-change-intent", "check-sensitive-zones"):
        return json.loads(stdout)
    return yaml.safe_load(stdout)


def case_command(case):
    gate = case["gate"]
    data = case.get("input", {})
    script = GATES[gate]

    if gate == "check-change-intent":
        return [
            "python3",
            script,
            data["name_status"],
            data["change_intent"],
            "--json",
        ]

    if gate == "check-sensitive-zones":
        return [
            "python3",
            script,
            data["name_status"],
            "policies/sensitive-zones.yaml",
            "--json",
        ]

    if gate == "generate-change-evidence":
        command = [
            "python3",
            script,
            data["name_status"],
            "--change-intent",
            data["change_intent"],
            "--sensitive-zones",
            "policies/sensitive-zones.yaml",
            "--approval-routing",
            "policies/approval-routing.yaml",
            "--generated-on",
            "2026-06-30",
        ]
        if data.get("numstat"):
            command.extend(["--numstat-input", data["numstat"]])
        return command

    if gate == "extract-python-inventory":
        return [
            "python3",
            script,
            data["source_file"],
            "--json",
        ]

    raise ValueError(f"unsupported gate: {gate}")


def values_at(records, key):
    return [record.get(key) for record in records]


def assert_equal(errors, label, actual, expected):
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def check_path_records(errors, label, records, expected_paths):
    actual_paths = values_at(records, "path")
    assert_equal(errors, label, actual_paths, expected_paths)


def validate_json_gate(case, result, exit_code):
    expect = case["expect"]
    errors = []
    assert_equal(errors, "exit_code", exit_code, expect["exit_code"])
    assert_equal(errors, "verdict", result.get("verdict"), expect["verdict"])

    for key in ("out_of_scope_paths", "forbidden_touched"):
        if key in expect:
            assert_equal(errors, key, result.get(key), expect[key])

    for key in ("frozen_touched", "protected_touched", "watched_touched"):
        if key in expect:
            check_path_records(errors, key, result.get(key, []), expect[key])

    if "required_approval" in expect:
        approvals = values_at(result.get("protected_touched", []), "required_approval")
        assert_equal(errors, "required_approval", approvals, expect["required_approval"])

    return errors


def validate_evidence(case, result, exit_code):
    expect = case["expect"]
    errors = []
    evidence = result.get("change_evidence", {})

    assert_equal(errors, "exit_code", exit_code, expect["exit_code"])
    assert_equal(errors, "verdict", evidence.get("verdict"), expect["verdict"])
    assert_equal(errors, "summary.files_changed", evidence.get("summary", {}).get("files_changed"), expect["files_changed"])
    assert_equal(errors, "summary.lines_added", evidence.get("summary", {}).get("lines_added"), expect["lines_added"])
    assert_equal(errors, "summary.lines_removed", evidence.get("summary", {}).get("lines_removed"), expect["lines_removed"])
    assert_equal(errors, "changed_files", evidence.get("changed_files"), expect["changed_files"])
    return errors


def validate_inventory(case, result, exit_code):
    expect = case["expect"]
    errors = []
    assert_equal(errors, "exit_code", exit_code, expect["exit_code"])

    if expect.get("parse_error_present"):
        if not result.get("parse_error"):
            errors.append("parse_error: expected a parse error, got none")
    elif "parse_error" in expect:
        assert_equal(errors, "parse_error", result.get("parse_error"), expect["parse_error"])

    if "items" in expect:
        assert_equal(errors, "items", result.get("items"), expect["items"])
    return errors


def main():
    with open("tests/cases.yaml", "r", encoding="utf-8") as stream:
        cases = yaml.safe_load(stream)["cases"]

    passed = 0
    failed = 0

    for case in cases:
        command = case_command(case)
        completed = run_command(command)
        try:
            result = load_output(case["gate"], completed.stdout)
            if case["gate"] == "generate-change-evidence":
                errors = validate_evidence(case, result, completed.returncode)
            elif case["gate"] == "extract-python-inventory":
                errors = validate_inventory(case, result, completed.returncode)
            else:
                errors = validate_json_gate(case, result, completed.returncode)
        except Exception as error:
            errors = [f"could not validate output: {error}"]

        if errors:
            failed += 1
            print(f"FAIL {case['name']} ({case['gate']})")
            for error in errors:
                print(f"  - {error}")
            if completed.stderr:
                print("  stderr:")
                print(completed.stderr.rstrip())
            if completed.stdout:
                print("  stdout:")
                print(completed.stdout.rstrip())
        else:
            passed += 1
            print(f"PASS {case['name']} ({case['gate']})")

    print(f"Summary: {passed}/{len(cases)} PASS")
    if failed:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
PY
