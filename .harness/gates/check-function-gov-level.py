#!/usr/bin/env python3
import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from pathlib import PurePosixPath

import yaml


PASS = 0
BLOCKED = 1
APPROVAL_REQUIRED = 2


GATE_DIR = Path(__file__).resolve().parent


def load_gate_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(module_name, GATE_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


map_gate = load_gate_module("map-diff-to-functions.py", "map_diff_to_functions_gate")
classify_gate = load_gate_module(
    "classify-python-function-changes.py", "classify_python_function_changes_gate"
)
gov_gate = load_gate_module("extract-gov-annotations.py", "extract_gov_annotations_gate")


def normalize_path(path):
    return str(PurePosixPath(path.replace("\\", "/")))


def run_git(args, repo="."):
    result = subprocess.run(
        ["git", *args],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=repo,
    )
    stdout = result.stdout.decode("utf-8")
    stderr = result.stderr.decode("utf-8", errors="replace")
    if result.returncode != 0:
        raise RuntimeError(stderr.strip() or f"git {' '.join(args)} failed")
    return stdout


def split_rev_range(rev_range):
    if ".." not in rev_range:
        raise ValueError("diff input must be a git rev range like <base>..<head>")
    base, head = rev_range.split("..", 1)
    if not base or not head:
        raise ValueError("diff input must include both base and head refs")
    return base, head


def load_policy(path):
    with open(path, "r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream) or {}
    defaults = data.get("defaults") or {}
    return {
        "block_levels": defaults.get("block_levels") or [],
        "approve_levels": defaults.get("approve_levels") or [],
        "warn_levels": defaults.get("warn_levels") or [],
    }


def level_strength(level, policy):
    if level in policy["block_levels"]:
        return 3
    if level in policy["approve_levels"]:
        return 2
    if level in policy["warn_levels"]:
        return 1
    return 0


def strongest_level(levels, policy):
    valid = [level for level in levels if level_strength(level, policy)]
    if not valid:
        return None
    return max(valid, key=lambda level: level_strength(level, policy))


def source_at_ref(ref, path, repo):
    return run_git(["show", f"{ref}:{path}"], repo)


def path_exists_at_ref(ref, path, repo):
    result = subprocess.run(
        ["git", "cat-file", "-e", f"{ref}:{path}"],
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=repo,
    )
    return result.returncode == 0


def absent_annotation_result(path):
    return {
        "path": path,
        "module": None,
        "annotations": [],
        "parse_error": False,
        "unreadable": None,
        "absent": True,
    }


def extract_annotations_at_ref(ref, path, repo):
    try:
        source = source_at_ref(ref, path, repo)
    except (RuntimeError, UnicodeDecodeError, UnicodeEncodeError) as error:
        return {
            "path": path,
            "module": None,
            "annotations": [],
            "parse_error": False,
            "unreadable": f"unreadable source: {error}",
        }
    return gov_gate.parse_source(source, path)


def annotation_index(result):
    return {
        (annotation.get("name"), annotation.get("def_line")): annotation
        for annotation in result.get("annotations", [])
    }


def annotation_errors(annotation):
    if not annotation:
        return []
    return sorted(set(annotation.get("errors") or []))


def annotation_level(annotation):
    if not annotation:
        return None
    return annotation.get("effective_level") or annotation.get("level")


def module_annotation(result):
    module = result.get("module")
    if not module:
        return None
    return {
        "name": "<module>",
        "def_line": None,
        "effective_level": module.get("level"),
        "level": module.get("level"),
        "reason": module.get("reason"),
        "errors": module.get("errors") or [],
        "unresolved": False,
        "type": "module",
    }


def sensitive_levels_in_result(result, policy):
    levels = []
    module = module_annotation(result)
    if module:
        levels.append(annotation_level(module))
    for annotation in result.get("annotations", []):
        levels.append(annotation_level(annotation))
    return [
        level
        for level in levels
        if level in policy["block_levels"] or level in policy["approve_levels"]
    ]


def parse_failed(result):
    return bool(result.get("parse_error") or result.get("unreadable"))


def changed_candidates_from_map(mapping):
    candidates = []
    for file_record in mapping.get("files", []):
        path = normalize_path(file_record.get("path", ""))
        if not path.endswith(".py"):
            continue
        for function in file_record.get("touched_functions", []):
            candidates.append(
                {
                    "path": path,
                    "name": function.get("name"),
                    "type": function.get("type"),
                    "before_line": None,
                    "after_line": function.get("start_line"),
                    "source": "map",
                }
            )
    return candidates


def changed_candidates_from_classification(classification):
    candidates = []
    for file_record in classification.get("files", []):
        path = normalize_path(file_record.get("path", ""))
        if not path.endswith(".py"):
            continue
        if file_record.get("fallback"):
            candidates.append(
                {
                    "path": path,
                    "name": "<module>",
                    "type": "module",
                    "before_line": None,
                    "after_line": None,
                    "source": "classify_fallback",
                }
            )
            continue
        for change in file_record.get("function_changes", []):
            change_type = change.get("change_type")
            candidates.append(
                {
                    "path": path,
                    "name": change.get("name"),
                    "type": change.get("type"),
                    "before_line": change.get("before_start_line")
                    if change_type == "modified"
                    else change.get("start_line"),
                    "after_line": change.get("after_start_line")
                    if change_type == "modified"
                    else change.get("start_line"),
                    "source": f"classify_{change_type}",
                }
            )
    return candidates


def unique_candidates(candidates):
    unique = {}
    for candidate in candidates:
        key = (
            candidate.get("path"),
            candidate.get("name"),
            candidate.get("before_line"),
            candidate.get("after_line"),
        )
        if key not in unique:
            unique[key] = candidate
            continue
        existing = unique[key]
        sources = existing["source"].split(",") + [candidate["source"]]
        existing["source"] = ",".join(sorted(set(sources)))
    return [
        unique[key]
        for key in sorted(
            unique,
            key=lambda item: (
                item[0],
                item[1] or "",
                item[2] if item[2] is not None else -1,
                item[3] if item[3] is not None else -1,
            ),
        )
    ]


def lookup_annotation(candidate, side_result, side):
    if candidate.get("name") == "<module>":
        return module_annotation(side_result)
    line_key = candidate.get(f"{side}_line")
    if line_key is None:
        return None
    return annotation_index(side_result).get((candidate.get("name"), line_key))


def touched_record(candidate, level, annotation, side, errors, reason):
    record = {
        "path": candidate["path"],
        "name": candidate["name"],
        "level": level,
        "side": side,
        "reason": reason,
        "errors": errors,
    }
    if annotation and annotation.get("def_line") is not None:
        record["def_line"] = annotation.get("def_line")
    return record


def evaluate_candidate(candidate, base_result, head_result, policy):
    base_annotation = lookup_annotation(candidate, base_result, "before")
    head_annotation = lookup_annotation(candidate, head_result, "after")
    side_annotations = [("base", base_annotation), ("head", head_annotation)]
    records = []

    for side, annotation in side_annotations:
        if not annotation:
            continue
        level = annotation_level(annotation)
        errors = annotation_errors(annotation)
        if errors or annotation.get("unresolved"):
            records.append(
                touched_record(
                    candidate,
                    "protected",
                    annotation,
                    side,
                    errors or ["unresolved"],
                    annotation.get("reason"),
                )
            )
        if level:
            records.append(
                touched_record(
                    candidate,
                    level,
                    annotation,
                    side,
                    errors,
                    annotation.get("reason"),
                )
            )

    return records


def fail_closed_record(path, reason, level="protected", side="head"):
    return {
        "path": path,
        "name": "<file>",
        "level": level,
        "side": side,
        "reason": reason,
        "errors": ["fail_closed"],
    }


def public_record(record):
    result = {
        "path": record["path"],
        "name": record["name"],
        "level": record["level"],
        "side": record["side"],
        "reason": record.get("reason"),
        "errors": record.get("errors") or [],
    }
    if "def_line" in record:
        result["def_line"] = record["def_line"]
    return result


def classify_records(records, policy):
    frozen_touched = []
    protected_touched = []
    watched_touched = []
    seen = set()

    for record in sorted(
        records,
        key=lambda item: (
            item["path"],
            item["name"],
            -level_strength(item["level"], policy),
            item["side"],
            item.get("def_line") or -1,
        ),
    ):
        public = public_record(record)
        key = json.dumps(public, ensure_ascii=False, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)

        level = record["level"]
        if level in policy["block_levels"]:
            frozen_touched.append(public)
        elif level in policy["approve_levels"]:
            protected_touched.append(public)
        elif level in policy["warn_levels"]:
            watched_touched.append(public)

    if frozen_touched:
        verdict = "blocked"
        exit_code = BLOCKED
    elif protected_touched:
        verdict = "approval_required"
        exit_code = APPROVAL_REQUIRED
    else:
        verdict = "pass"
        exit_code = PASS

    return verdict, exit_code, frozen_touched, protected_touched, watched_touched


def check_function_gov_level(rev_range, sensitive_zones, repo="."):
    base, head = split_rev_range(rev_range)
    policy = load_policy(sensitive_zones)
    mapping = map_gate.map_diff_to_functions(rev_range, repo)
    classification = classify_gate.classify_python_function_changes(rev_range, repo)

    errors = []
    if mapping.get("error"):
        errors.append({"gate": "map-diff-to-functions", "error": mapping["error"]})
    if classification.get("error"):
        errors.append(
            {"gate": "classify-python-function-changes", "error": classification["error"]}
        )
    upstream_errors = list(errors)

    candidates = unique_candidates(
        changed_candidates_from_map(mapping) + changed_candidates_from_classification(classification)
    )
    paths = sorted({candidate["path"] for candidate in candidates if candidate["path"].endswith(".py")})
    records = []

    for path in paths:
        base_exists = path_exists_at_ref(base, path, repo)
        head_exists = path_exists_at_ref(head, path, repo)
        base_result = (
            extract_annotations_at_ref(base, path, repo)
            if base_exists
            else absent_annotation_result(path)
        )
        head_result = (
            extract_annotations_at_ref(head, path, repo)
            if head_exists
            else absent_annotation_result(path)
        )

        if base_exists and parse_failed(base_result):
            errors.append(
                {
                    "path": path,
                    "side": "base",
                    "error": base_result.get("parse_error") or base_result.get("unreadable"),
                }
            )
            records.append(
                fail_closed_record(
                    path,
                    "base file could not be parsed before the change",
                    side="base",
                )
            )
        if head_exists and parse_failed(head_result):
            errors.append(
                {
                    "path": path,
                    "side": "head",
                    "error": head_result.get("parse_error") or head_result.get("unreadable"),
                }
            )
            base_sensitive_levels = sensitive_levels_in_result(base_result, policy)
            base_level = strongest_level(base_sensitive_levels, policy)
            records.append(
                fail_closed_record(
                    path,
                    "head file could not be parsed after the change",
                    level=base_level or "protected",
                )
            )
        if not head_exists:
            base_sensitive_levels = sensitive_levels_in_result(base_result, policy)
            if base_sensitive_levels:
                base_level = strongest_level(base_sensitive_levels, policy)
                errors.append(
                    {
                        "path": path,
                        "side": "head",
                        "error": "file absent after the change",
                    }
                )
                records.append(
                    fail_closed_record(
                        path,
                        "base had frozen/protected @gov annotation but head file is absent",
                        level=base_level or "protected",
                    )
                )

        for candidate in [item for item in candidates if item["path"] == path]:
            records.extend(evaluate_candidate(candidate, base_result, head_result, policy))

    if upstream_errors:
        records.append(fail_closed_record("<unknown>", "upstream function analysis failed"))

    verdict, exit_code, frozen_touched, protected_touched, watched_touched = classify_records(
        records, policy
    )
    return {
        "gate": "check-function-gov-level",
        "verdict": verdict,
        "base_commit": run_git(["rev-parse", base], repo).strip(),
        "head_commit": run_git(["rev-parse", head], repo).strip(),
        "changed_functions": candidates,
        "frozen_touched": frozen_touched,
        "protected_touched": protected_touched,
        "watched_touched": watched_touched,
        "errors": errors,
        "exit_code": exit_code,
    }


def print_text(result):
    verdict = result["verdict"]
    if verdict == "blocked":
        print("BLOCKED: frozen @gov 함수 변경이 감지되었습니다.")
    elif verdict == "approval_required":
        print("APPROVAL_REQUIRED: protected 또는 invalid @gov 함수 변경이 감지되었습니다.")
    elif result["watched_touched"]:
        print("PASS: watched @gov 함수 변경이 감지되었습니다.")
    else:
        print("PASS: @gov 민감 함수 변경이 감지되지 않았습니다.")

    for key in ("frozen_touched", "protected_touched", "watched_touched"):
        for item in result.get(key, []):
            print(f"{item['level']}: {item['path']}::{item['name']} side={item['side']}")


def main():
    parser = argparse.ArgumentParser(
        description="Check changed Python functions against base/head @gov effective levels."
    )
    parser.add_argument("diff_input", help="git diff ref range, for example <base>..<head>")
    parser.add_argument("sensitive_zones", help="policies/sensitive-zones.yaml path")
    parser.add_argument("--repo", default=".", help="git repository to inspect")
    parser.add_argument("--json", action="store_true", help="print structured JSON")
    args = parser.parse_args()

    try:
        result = check_function_gov_level(args.diff_input, args.sensitive_zones, args.repo)
    except Exception as error:
        result = {
            "gate": "check-function-gov-level",
            "verdict": "approval_required",
            "error": str(error),
            "changed_functions": [],
            "frozen_touched": [],
            "protected_touched": [
                {
                    "path": "<unknown>",
                    "name": "<file>",
                    "level": "protected",
                    "side": "analysis",
                    "reason": "function @gov analysis failed",
                    "errors": ["fail_closed"],
                }
            ],
            "watched_touched": [],
            "errors": [{"error": str(error)}],
            "exit_code": APPROVAL_REQUIRED,
        }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    elif "error" in result:
        print(f"APPROVAL_REQUIRED: {result['error']}")
    else:
        print_text(result)
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
