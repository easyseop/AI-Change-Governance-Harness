#!/usr/bin/env python3
import argparse
import ast
import fnmatch
import importlib.util
import json
import os
import sys
from pathlib import Path, PurePosixPath

import yaml


PASS = 0
VALID_MATURITY = {"enforcing", "shadow"}
DEFAULT_MATURITY = "shadow"
DEFAULT_HOPS = 1

GATE_DIR = Path(__file__).resolve().parent


def load_gate_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(module_name, GATE_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gov_gate = load_gate_module("extract-gov-annotations.py", "extract_gov_annotations_gate")


def normalize_path(path):
    return str(PurePosixPath(str(path).replace("\\", "/")))


def module_name_for_path(path):
    pure = PurePosixPath(normalize_path(path))
    without_suffix = pure.with_suffix("")
    parts = list(without_suffix.parts)
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def full_function_name(path, local_name):
    module = module_name_for_path(path)
    return f"{module}.{local_name}" if module else local_name


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
            return any(
                match_parts(next_path_index, pattern_index + 1)
                for next_path_index in range(path_index, len(path_parts) + 1)
            )
        if path_index >= len(path_parts):
            return False
        if not fnmatch.fnmatchcase(path_parts[path_index], pattern_part):
            return False
        return match_parts(path_index + 1, pattern_index + 1)

    return match_parts(0, 0)


def read_yaml(path):
    with open(path, "r", encoding="utf-8") as stream:
        return yaml.safe_load(stream) or {}


def load_sensitive_zones(path):
    data = read_yaml(path)
    defaults = data.get("defaults") or {}
    return {
        "block_levels": defaults.get("block_levels") or [],
        "zones": data.get("zones") or [],
    }


def registry_defaults(data):
    defaults = data.get("defaults") or {}
    return {
        "maturity": defaults.get("maturity", DEFAULT_MATURITY),
        "hops": defaults.get("hops", DEFAULT_HOPS),
    }


def iter_python_files(repo):
    for root, dirnames, filenames in os.walk(repo):
        dirnames[:] = sorted(name for name in dirnames if name != ".git")
        for filename in sorted(filenames):
            if filename.endswith(".py"):
                absolute = Path(root) / filename
                yield normalize_path(os.path.relpath(absolute, repo)), absolute


def node_type(node):
    if isinstance(node, ast.AsyncFunctionDef):
        return "async_function"
    return "function"


class FunctionVisitor(ast.NodeVisitor):
    def __init__(self, path):
        self.path = path
        self.parents = []
        self.functions = []

    def normalized_name(self, name):
        if not self.parents:
            return name
        return ".".join(self.parents + [name])

    def visit_ClassDef(self, node):
        self.parents.append(node.name)
        self.generic_visit(node)
        self.parents.pop()

    def visit_FunctionDef(self, node):
        self.visit_function(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_function(node)

    def visit_function(self, node):
        name = self.normalized_name(node.name)
        self.functions.append(
            {
                "path": self.path,
                "name": name,
                "function": full_function_name(self.path, name),
                "line": node.lineno,
                "type": node_type(node),
                "decorators": [
                    gov_gate.decorator_name(decorator)
                    for decorator in node.decorator_list
                ],
            }
        )
        self.parents.append(node.name)
        self.generic_visit(node)
        self.parents.pop()


def parse_functions(source, path):
    tree = ast.parse(source, filename=path)
    visitor = FunctionVisitor(path)
    visitor.visit(tree)
    return visitor.functions


def collect_repo_functions(repo):
    functions = []
    errors = []
    source_by_path = {}
    for relative_path, absolute_path in iter_python_files(repo):
        try:
            source = absolute_path.read_text(encoding="utf-8")
            source_by_path[relative_path] = source
            functions.extend(parse_functions(source, relative_path))
        except UnicodeDecodeError as error:
            errors.append({"error": "unreadable", "path": relative_path, "message": str(error)})
        except SyntaxError as error:
            errors.append(
                {
                    "error": "parse_error",
                    "path": relative_path,
                    "message": f"{error.msg} at line {error.lineno}, column {error.offset}",
                }
            )
    return functions, source_by_path, errors


def sink_record(sink_id, function, source, path, name, line, reason, owner, maturity, hops):
    return {
        "id": sink_id,
        "function": function,
        "source": source,
        "path": path,
        "name": name,
        "line": line,
        "reason": reason,
        "owner": owner,
        "maturity": maturity,
        "hops": hops,
    }


def gov_sinks(source_by_path):
    sinks = []
    errors = []
    for path in sorted(source_by_path):
        result = gov_gate.parse_source(source_by_path[path], path)
        for annotation in result.get("annotations", []):
            if not annotation.get("sink"):
                continue
            function = full_function_name(path, annotation["name"])
            sinks.append(
                sink_record(
                    f"gov:{function}",
                    function,
                    "gov_annotation",
                    path,
                    annotation["name"],
                    annotation.get("def_line"),
                    annotation.get("reason"),
                    annotation.get("owner"),
                    DEFAULT_MATURITY,
                    DEFAULT_HOPS,
                )
            )
            if annotation.get("errors"):
                errors.append(
                    {
                        "error": "gov_annotation_error",
                        "function": function,
                        "errors": annotation.get("errors"),
                    }
                )
    return sinks, errors


def frozen_zone_paths(policy):
    block_levels = set(policy.get("block_levels") or [])
    return [
        zone
        for zone in policy.get("zones") or []
        if zone.get("path") and zone.get("level") in block_levels
    ]


def frozen_sinks(functions, policy):
    zones = frozen_zone_paths(policy)
    sinks = []
    for function in functions:
        matches = [zone for zone in zones if match_glob(function["path"], zone["path"])]
        if not matches:
            continue
        zone = sorted(matches, key=lambda item: normalize_path(item["path"]))[0]
        sinks.append(
            sink_record(
                f"frozen:{function['function']}",
                function["function"],
                "frozen_zone",
                function["path"],
                function["name"],
                function["line"],
                zone.get("reason"),
                zone.get("required_approval"),
                "enforcing",
                DEFAULT_HOPS,
            )
        )
    return sinks


def normalize_maturity(value, errors, index, sink_id):
    if value in VALID_MATURITY:
        return value
    errors.append({"error": "invalid_maturity", "index": index, "id": sink_id, "maturity": value})
    return "enforcing"


def normalize_hops(value, errors, index, sink_id):
    if isinstance(value, int) and value >= 1:
        return value
    errors.append({"error": "invalid_hops", "index": index, "id": sink_id, "hops": value})
    return DEFAULT_HOPS


def registry_sinks(registry_path, functions_by_name):
    if not registry_path or not os.path.exists(registry_path):
        return [], []

    data = read_yaml(registry_path)
    defaults = registry_defaults(data)
    errors = []
    default_maturity = normalize_maturity(defaults["maturity"], errors, "defaults", "<defaults>")
    default_hops = normalize_hops(defaults["hops"], errors, "defaults", "<defaults>")
    sinks = []

    for index, entry in enumerate(data.get("sinks") or []):
        sink_id = entry.get("id")
        missing = [
            field
            for field in ("id", "function", "reason", "owner")
            if not entry.get(field)
        ]
        for field in missing:
            errors.append(
                {"error": "missing_required_field", "index": index, "id": sink_id, "field": field}
            )

        function = entry.get("function")
        maturity = normalize_maturity(entry.get("maturity", default_maturity), errors, index, sink_id)
        hops = normalize_hops(entry.get("hops", default_hops), errors, index, sink_id)
        function_record = functions_by_name.get(function)
        if function and function_record is None:
            errors.append(
                {
                    "error": "unresolved_registry_function",
                    "index": index,
                    "id": sink_id,
                    "function": function,
                }
            )
            continue
        if missing or function_record is None:
            continue

        sinks.append(
            sink_record(
                sink_id,
                function,
                "sink_registry",
                function_record["path"],
                function_record["name"],
                function_record["line"],
                entry.get("reason"),
                entry.get("owner"),
                maturity,
                hops,
            )
        )
    return sinks, errors


def unique_sorted_sinks(sinks):
    unique = {}
    for sink in sinks:
        key = (sink["function"], sink["source"], sink["id"])
        unique[key] = sink
    return [unique[key] for key in sorted(unique)]


def extract_sinks(repo, sensitive_zones, sink_registry):
    repo = os.path.abspath(repo)
    functions, source_by_path, errors = collect_repo_functions(repo)
    functions_by_name = {function["function"]: function for function in functions}
    policy = load_sensitive_zones(sensitive_zones)

    gov_records, gov_errors = gov_sinks(source_by_path)
    registry_records, registry_errors = registry_sinks(sink_registry, functions_by_name)
    sinks = gov_records + frozen_sinks(functions, policy) + registry_records
    errors.extend(gov_errors)
    errors.extend(registry_errors)

    return {
        "gate": "extract-sinks",
        "repo": repo,
        "sinks": unique_sorted_sinks(sinks),
        "errors": sorted(errors, key=lambda item: json.dumps(item, sort_keys=True)),
        "exit_code": PASS,
    }


def print_text(result):
    print(f"sinks: {len(result['sinks'])}")
    for sink in result["sinks"]:
        print(
            f"{sink['source']} {sink['id']} {sink['function']} "
            f"maturity={sink['maturity']} hops={sink['hops']}"
        )
    for error in result["errors"]:
        print(f"error: {error}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract deterministic MVP-2 sink registrations from a Python repo."
    )
    parser.add_argument("repo", nargs="?", default=".", help="repository root to scan")
    parser.add_argument(
        "--sensitive-zones",
        default="policies/sensitive-zones.yaml",
        help="sensitive-zones policy path",
    )
    parser.add_argument(
        "--sink-registry",
        default="policies/sink-registry.yaml",
        help="optional sink-registry policy path",
    )
    parser.add_argument("--json", action="store_true", help="print structured JSON")
    args = parser.parse_args()

    result = extract_sinks(args.repo, args.sensitive_zones, args.sink_registry)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print_text(result)
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
