#!/usr/bin/env python3
import argparse
import fnmatch
import json
import os
import subprocess
import sys
from pathlib import PurePosixPath

import yaml


PASS = 0
BLOCKED = 1
APPROVAL_REQUIRED = 2


def normalize_path(path):
    return str(PurePosixPath(path.replace("\\", "/")))


def match_glob(path, pattern):
    path_parts = [part for part in normalize_path(path).split("/") if part]
    pattern_parts = [part for part in normalize_path(pattern).split("/") if part]

    def match_parts(path_index, pattern_index):
        if pattern_index == len(pattern_parts):
            return path_index == len(path_parts)

        pattern_part = pattern_parts[pattern_index]
        if pattern_part == "**":
            if pattern_index == len(pattern_parts) - 1:
                return True
            for next_path_index in range(path_index, len(path_parts) + 1):
                if match_parts(next_path_index, pattern_index + 1):
                    return True
            return False

        if path_index >= len(path_parts):
            return False
        if not fnmatch.fnmatchcase(path_parts[path_index], pattern_part):
            return False
        return match_parts(path_index + 1, pattern_index + 1)

    return match_parts(0, 0)


def load_intent(path):
    if not os.path.exists(path):
        raise FileNotFoundError("의도 선언 누락: change-intent.yaml 파일을 찾을 수 없습니다.")

    with open(path, "r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream) or {}

    intent = data.get("change_intent") or {}
    return {
        "allowed_paths": intent.get("allowed_paths") or [],
        "forbidden_paths": intent.get("forbidden_paths") or [],
        "requirement_id": intent.get("requirement_id"),
        "author": intent.get("author"),
    }


def read_name_status(diff_input):
    if os.path.exists(diff_input):
        with open(diff_input, "r", encoding="utf-8") as stream:
            return stream.read().splitlines()

    result = subprocess.run(
        ["git", "diff", "--name-status", diff_input],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff 실행 실패")
    return result.stdout.splitlines()


def parse_changed_files(name_status_lines):
    files = []
    for line in name_status_lines:
        line = line.strip()
        if not line:
            continue

        parts = line.split("\t")
        status = parts[0]
        if status.startswith(("R", "C")) and len(parts) >= 3:
            path = parts[2]
        elif len(parts) >= 2:
            path = parts[1]
        else:
            continue
        files.append(normalize_path(path))
    return files


def check_files(files, intent):
    allowed_paths = intent["allowed_paths"]
    forbidden_paths = intent["forbidden_paths"]

    forbidden_touched = []
    out_of_scope = []

    for path in files:
        in_forbidden = any(match_glob(path, pattern) for pattern in forbidden_paths)
        in_allowed = any(match_glob(path, pattern) for pattern in allowed_paths)

        if in_forbidden:
            forbidden_touched.append(path)
        elif not in_allowed:
            out_of_scope.append(path)

    if forbidden_touched:
        verdict = "blocked"
        exit_code = BLOCKED
    elif out_of_scope:
        verdict = "approval_required"
        exit_code = APPROVAL_REQUIRED
    else:
        verdict = "pass"
        exit_code = PASS

    return {
        "gate": "check-change-intent",
        "verdict": verdict,
        "changed_files": files,
        "out_of_scope_paths": out_of_scope,
        "forbidden_touched": forbidden_touched,
        "exit_code": exit_code,
    }


def print_text(result):
    verdict = result["verdict"]
    if verdict == "pass":
        print("PASS: 변경 파일이 change-intent allowed_paths 범위 안에 있습니다.")
    elif verdict == "blocked":
        print("BLOCKED: forbidden_paths 변경이 감지되었습니다.")
    else:
        print("APPROVAL_REQUIRED: allowed_paths 밖 변경이 감지되었습니다.")

    if not result["changed_files"]:
        print("changed_files: 0")
    for path in result["forbidden_touched"]:
        print(f"forbidden: {path}")
    for path in result["out_of_scope_paths"]:
        print(f"out_of_scope: {path}")


def main():
    parser = argparse.ArgumentParser(
        description="Check whether changed files stay within change-intent path scope."
    )
    parser.add_argument("diff_input", help="git diff ref (base..head) or name-status file")
    parser.add_argument("change_intent", help="change-intent.yaml path")
    parser.add_argument("--json", action="store_true", help="print structured JSON")
    args = parser.parse_args()

    try:
        intent = load_intent(args.change_intent)
        files = parse_changed_files(read_name_status(args.diff_input))
        result = check_files(files, intent)
    except FileNotFoundError as error:
        result = {
            "gate": "check-change-intent",
            "verdict": "blocked",
            "error": str(error),
            "exit_code": BLOCKED,
        }
    except Exception as error:
        result = {
            "gate": "check-change-intent",
            "verdict": "blocked",
            "error": str(error),
            "exit_code": BLOCKED,
        }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    elif "error" in result:
        print(f"BLOCKED: {result['error']}")
    else:
        print_text(result)

    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
