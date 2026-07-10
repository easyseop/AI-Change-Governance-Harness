#!/usr/bin/env python3
import argparse
import ast
import json
import sys
from collections import defaultdict

import yaml


DEFAULT_POLICY = "policies/sensitive-capabilities.yaml"
VALID_LEVELS = {"protected", "watched"}
VALID_MATURITY = {"enforcing", "shadow"}
DEFAULT_INVALID_LEVEL = "protected"


def read_source(path):
    if path == "-":
        return sys.stdin.read()
    with open(path, "r", encoding="utf-8") as stream:
        return stream.read()


def signal_list(signals, key):
    values = signals.get(key) or []
    return [str(value) for value in values]


def load_catalog(path):
    with open(path, "r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream) or {}

    capabilities = []
    errors = []
    for raw in data.get("capabilities") or []:
        cap_id = raw.get("id")
        if not cap_id:
            errors.append({"error": "missing_capability_id"})
            continue

        level = raw.get("level")
        if level not in VALID_LEVELS:
            errors.append(
                {
                    "error": "invalid_capability_level",
                    "id": cap_id,
                    "level": level,
                }
            )
            level = DEFAULT_INVALID_LEVEL
        maturity = raw.get("maturity", "enforcing")
        if maturity not in VALID_MATURITY:
            errors.append(
                {
                    "error": "invalid_maturity",
                    "id": cap_id,
                    "maturity": maturity,
                }
            )
            maturity = "enforcing"

        signals = raw.get("signals") or {}
        known = {"imports", "calls", "builtins"}
        for key in sorted(set(signals) - known):
            errors.append({"error": "unknown_signal_kind", "id": cap_id, "kind": key})

        capabilities.append(
            {
                "id": cap_id,
                "level": level,
                "maturity": maturity,
                "reason": raw.get("reason"),
                "reviewer": raw.get("reviewer"),
                "imports": signal_list(signals, "imports"),
                "calls": signal_list(signals, "calls"),
                "builtins": signal_list(signals, "builtins"),
            }
        )

    return capabilities, errors


def module_matches(imported, signal_module):
    return imported == signal_module or imported.startswith(f"{signal_module}.")


def build_indexes(capabilities):
    import_index = defaultdict(list)
    call_index = defaultdict(list)
    builtin_index = defaultdict(list)
    catalog_modules = defaultdict(list)

    for cap in capabilities:
        for name in cap["imports"]:
            import_index[name].append(cap)
            catalog_modules[name].append(cap)
        for name in cap["calls"]:
            call_index[name].append(cap)
            module = name.rsplit(".", 1)[0]
            while module:
                catalog_modules[module].append(cap)
                if "." not in module:
                    break
                module = module.rsplit(".", 1)[0]
        for name in cap["builtins"]:
            builtin_index[name].append(cap)

    return import_index, call_index, builtin_index, catalog_modules


def caps_for_import(imported, import_index):
    matched = []
    for module, caps in import_index.items():
        if module_matches(imported, module):
            matched.extend(caps)
    return matched


def caps_for_catalog_module(module, catalog_modules):
    matched = []
    for catalog_module, caps in catalog_modules.items():
        if module_matches(module, catalog_module):
            matched.extend(caps)
    return matched


def add_signal(found, cap, kind, name, line):
    found[cap["id"]]["level"] = cap["level"]
    found[cap["id"]]["reason"] = cap["reason"]
    found[cap["id"]]["reviewer"] = cap["reviewer"]
    found[cap["id"]]["signals"].add((kind, name, line))


def imported_root(name):
    return name.split(".", 1)[0]


def build_import_bindings(tree, found, import_index, catalog_modules):
    bindings = {}
    unresolved_dynamic = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bound = alias.asname or imported_root(alias.name)
                target = alias.name
                if "." in alias.name and not alias.asname:
                    target = imported_root(alias.name)
                bindings[bound] = target
                for cap in caps_for_import(alias.name, import_index):
                    add_signal(found, cap, "import", alias.name, node.lineno)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if alias.name == "*":
                    unresolved_dynamic.append(
                        {"kind": "star_import", "module": module, "line": node.lineno}
                    )
                    for cap in caps_for_catalog_module(module, catalog_modules):
                        add_signal(found, cap, "star_import", module, node.lineno)
                    continue

                bound = alias.asname or alias.name
                target = f"{module}.{alias.name}" if module else alias.name
                bindings[bound] = target
                for cap in caps_for_import(module, import_index):
                    add_signal(found, cap, "import", module, node.lineno)
        elif isinstance(node, ast.Assign):
            target = resolve_getattr_call_name(node.value, bindings, require_bound_base=True)
            if not target:
                value_name = dotted_name(node.value)
                if not value_name:
                    continue
                root, _, rest = value_name.partition(".")
                if root not in bindings:
                    continue
                target = f"{bindings[root]}.{rest}" if rest else bindings[root]
            for target_node in node.targets:
                if isinstance(target_node, ast.Name):
                    bindings[target_node.id] = target

    unresolved_dynamic.sort(key=lambda item: (item["line"], item["kind"], item["module"]))
    return bindings, unresolved_dynamic


def dotted_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parent = dotted_name(node.value)
        if parent:
            return f"{parent}.{node.attr}"
    return None


def resolve_call_name(func, bindings):
    getattr_name = resolve_getattr_call_name(func, bindings)
    if getattr_name:
        return getattr_name
    name = dotted_name(func)
    if not name:
        return None
    root, _, rest = name.partition(".")
    if root in bindings:
        resolved = bindings[root]
        return f"{resolved}.{rest}" if rest else resolved
    return name


def resolve_getattr_call_name(func, bindings, require_bound_base=False):
    if not isinstance(func, ast.Call):
        return None
    if not isinstance(func.func, ast.Name) or func.func.id != "getattr":
        return None
    if len(func.args) < 2:
        return None
    if not isinstance(func.args[1], ast.Constant) or not isinstance(func.args[1].value, str):
        return None

    base_name = dotted_name(func.args[0])
    if not base_name:
        return None
    root, _, rest = base_name.partition(".")
    if root in bindings:
        resolved = bindings[root]
        base_name = f"{resolved}.{rest}" if rest else resolved
    elif require_bound_base:
        return None
    return f"{base_name}.{func.args[1].value}"


def public_capabilities(found):
    capabilities = []
    for cap_id in sorted(found):
        record = found[cap_id]
        signals = [
            {"kind": kind, "name": name, "line": line}
            for kind, name, line in sorted(record["signals"], key=lambda item: (item[2], item[0], item[1]))
        ]
        capabilities.append(
            {
                "id": cap_id,
                "level": record["level"],
                "signals": signals,
            }
        )
    return capabilities


def extract_from_source(source, source_path, policy_path):
    capabilities, catalog_errors = load_catalog(policy_path)
    try:
        tree = ast.parse(source, filename=source_path)
    except SyntaxError as error:
        return {
            "path": source_path,
            "capabilities": [],
            "unresolved_dynamic": [],
            "errors": catalog_errors,
            "parse_error": f"{error.msg} at line {error.lineno}, column {error.offset}",
            "unreadable": False,
        }

    import_index, call_index, builtin_index, catalog_modules = build_indexes(capabilities)
    found = defaultdict(lambda: {"level": None, "reason": None, "reviewer": None, "signals": set()})
    bindings, unresolved_dynamic = build_import_bindings(
        tree, found, import_index, catalog_modules
    )

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name):
            for cap in builtin_index.get(node.func.id, []):
                add_signal(found, cap, "builtin", node.func.id, node.lineno)

        call_name = resolve_call_name(node.func, bindings)
        if call_name:
            for cap in call_index.get(call_name, []):
                add_signal(found, cap, "call", call_name, node.lineno)

    return {
        "path": source_path,
        "capabilities": public_capabilities(found),
        "unresolved_dynamic": unresolved_dynamic,
        "errors": catalog_errors,
        "parse_error": False,
        "unreadable": False,
    }


def extract_capabilities(path, policy_path):
    try:
        source = read_source(path)
    except (OSError, UnicodeDecodeError) as error:
        _, catalog_errors = load_catalog(policy_path)
        return {
            "path": path,
            "capabilities": [],
            "unresolved_dynamic": [],
            "errors": catalog_errors,
            "parse_error": False,
            "unreadable": f"unreadable source: {error}",
        }
    return extract_from_source(source, "stdin" if path == "-" else path, policy_path)


def print_text(result):
    if result["parse_error"]:
        print(f"parse_error: {result['parse_error']}")
    if result["unreadable"]:
        print(f"unreadable: {result['unreadable']}")
    for error in result["errors"]:
        print(f"error: {error}")
    for capability in result["capabilities"]:
        signal_text = ",".join(
            f"{signal['kind']}:{signal['name']}:{signal['line']}"
            for signal in capability["signals"]
        )
        print(f"{capability['id']} level={capability['level']} signals={signal_text}")


def main():
    parser = argparse.ArgumentParser(
        description="Extract deterministic sensitive Python capabilities from a source file."
    )
    parser.add_argument("source_file", nargs="?", default="-", help="Python source file, or '-' for stdin")
    parser.add_argument(
        "policy",
        nargs="?",
        default=DEFAULT_POLICY,
        help="sensitive capability catalog yaml",
    )
    parser.add_argument("--json", action="store_true", help="print structured JSON")
    args = parser.parse_args()

    result = extract_capabilities(args.source_file, args.policy)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print_text(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
