#!/usr/bin/env python3
import argparse
import importlib.util
import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path, PurePosixPath


GATE_DIR = Path(__file__).resolve().parent
TYPE_DECLARATIONS = {
    "class_declaration",
    "interface_declaration",
    "enum_declaration",
    "record_declaration",
}
CALLABLE_DECLARATIONS = {"method_declaration", "constructor_declaration"}
REFLECTIVE_METHODS = {"forName", "getMethod", "getDeclaredMethod", "invoke", "newInstance"}


def load_gate_module(filename, module_name):
    spec = importlib.util.spec_from_file_location(module_name, GATE_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


java_inventory_gate = load_gate_module(
    "extract-java-inventory.py", "extract_java_inventory_for_callgraph"
)


def normalize_path(path):
    return str(PurePosixPath(str(path).replace("\\", "/")))


def node_text(source_bytes, node):
    return source_bytes[node.start_byte : node.end_byte].decode("utf-8", errors="replace")


def node_line(node):
    return node.start_point.row + 1


def simple_name(value):
    return str(value).split(".")[-1]


def named_text(source_bytes, node, field):
    child = node.child_by_field_name(field)
    return node_text(source_bytes, child).strip() if child is not None else None


def walk(node):
    yield node
    for child in node.named_children:
        yield from walk(child)


def java_files(repo):
    for root, dirnames, filenames in os.walk(repo):
        dirnames[:] = sorted(name for name in dirnames if name != ".git")
        for filename in sorted(filenames):
            if filename.endswith(".java"):
                absolute = Path(root) / filename
                yield normalize_path(os.path.relpath(str(absolute), repo)), absolute


def type_names(source_bytes, node):
    if node is None:
        return []
    return sorted(
        {
            simple_name(node_text(source_bytes, child).strip())
            for child in walk(node)
            if child.type in {"type_identifier", "scoped_type_identifier"}
        }
    )


def declaration_name(source_bytes, node):
    name = named_text(source_bytes, node, "name")
    return name or "<anonymous>"


def declaration_supertypes(source_bytes, node):
    names = []
    for field in ("superclass", "interfaces"):
        names.extend(type_names(source_bytes, node.child_by_field_name(field)))
    for child in node.children:
        if child.type in {"extends_interfaces", "super_interfaces", "superclass"}:
            names.extend(type_names(source_bytes, child))
    return sorted(set(names))


def declared_type(source_bytes, node):
    type_node = node.child_by_field_name("type")
    names = type_names(source_bytes, type_node)
    if names:
        return names[-1]
    if type_node is not None:
        return simple_name(node_text(source_bytes, type_node).strip())
    return None


def variable_names(source_bytes, node):
    names = []
    name = node.child_by_field_name("name")
    if name is not None:
        names.append(node_text(source_bytes, name).strip())
    for child in node.named_children:
        if child.type == "variable_declarator":
            child_name = child.child_by_field_name("name")
            if child_name is not None:
                names.append(node_text(source_bytes, child_name).strip())
    return sorted(set(names))


def collect_bindings(source_bytes, node):
    bindings = {}
    for child in walk(node):
        if child.type not in {
            "field_declaration",
            "formal_parameter",
            "spread_parameter",
            "local_variable_declaration",
        }:
            continue
        type_name = declared_type(source_bytes, child)
        if not type_name:
            continue
        for name in variable_names(source_bytes, child):
            bindings[name] = type_name
    return bindings


def parse_source(path, absolute):
    try:
        source = absolute.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        return None, None, {"error": "unreadable", "path": path, "message": str(error)}
    source_bytes = source.encode("utf-8")
    try:
        parser = java_inventory_gate.make_java_parser()
    except (ImportError, OSError) as error:
        return None, None, {
            "error": "java_analysis_unavailable",
            "path": path,
            "message": str(error),
        }
    tree = parser.parse(source_bytes)
    if tree.root_node.has_error:
        return None, None, {"error": "parse_error", "path": path, "message": "syntax error"}
    return source_bytes, tree, None


def collect_declarations(path, source_bytes, tree):
    types = []
    methods = []

    def direct_field_bindings(node):
        bindings = {}
        body = node.child_by_field_name("body")
        if body is None:
            return bindings
        for child in body.named_children:
            if child.type != "field_declaration":
                continue
            type_name = declared_type(source_bytes, child)
            if not type_name:
                continue
            for name in variable_names(source_bytes, child):
                bindings[name] = type_name
        return bindings

    def visit(node, type_stack, enclosing_bindings):
        if node.type in TYPE_DECLARATIONS:
            local = declaration_name(source_bytes, node)
            qualified = ".".join(type_stack + [local])
            types.append(
                {
                    "name": qualified,
                    "simple": local,
                    "kind": node.type,
                    "supers": declaration_supertypes(source_bytes, node),
                    "path": path,
                }
            )
            class_bindings = dict(enclosing_bindings)
            class_bindings.update(direct_field_bindings(node))
            for child in node.named_children:
                visit(child, type_stack + [local], class_bindings)
            return
        if node.type in CALLABLE_DECLARATIONS and type_stack:
            local = "<init>" if node.type == "constructor_declaration" else declaration_name(source_bytes, node)
            owner = ".".join(type_stack)
            methods.append(
                {
                    "id": f"{owner}.{local}",
                    "path": path,
                    "name": local,
                    "owner": owner,
                    "line": node_line(node),
                    "type": "constructor" if local == "<init>" else "method",
                    "tree_node": node,
                    "bindings": {
                        **enclosing_bindings,
                        **collect_bindings(source_bytes, node),
                    },
                }
            )
        for child in node.named_children:
            visit(child, type_stack, enclosing_bindings)

    visit(tree.root_node, [], {})
    return types, methods


def type_relationships(types):
    by_simple = defaultdict(set)
    direct = defaultdict(set)
    parents = defaultdict(set)
    for item in types:
        by_simple[item["simple"]].add(item["name"])
    for item in types:
        for parent in item["supers"]:
            direct[parent].add(item["name"])
            parents[item["name"]].update(by_simple.get(parent, {parent}))

    changed = True
    while changed:
        changed = False
        for parent in list(direct):
            expanded = set(direct[parent])
            for child in list(direct[parent]):
                expanded.update(direct.get(simple_name(child), set()))
            if not expanded.issubset(direct[parent]):
                direct[parent].update(expanded)
                changed = True
    changed = True
    while changed:
        changed = False
        for child in list(parents):
            expanded = set(parents[child])
            for parent in list(parents[child]):
                expanded.update(parents.get(parent, set()))
            if not expanded.issubset(parents[child]):
                parents[child].update(expanded)
                changed = True
    return by_simple, direct, parents


def receiver_type(source_bytes, object_node, bindings, current_owner):
    if object_node is None:
        return simple_name(current_owner)
    if object_node.type == "object_creation_expression":
        names = type_names(source_bytes, object_node.child_by_field_name("type"))
        return names[-1] if names else None
    text = node_text(source_bytes, object_node).strip()
    root = re.split(r"[.(]", text, maxsplit=1)[0]
    if root == "this" and text.startswith("this."):
        field = text.split(".", 2)[1]
        if field in bindings:
            return bindings[field]
    if root in {"this", "super"}:
        return simple_name(current_owner)
    if root in bindings:
        return bindings[root]
    if root[:1].isupper():
        return simple_name(root)
    qualified = simple_name(text)
    if qualified[:1].isupper():
        return qualified
    return None


def method_targets(
    method_name,
    owner_type,
    methods_by_owner,
    implementations,
    ancestors,
    type_names_by_simple,
    interface_names,
):
    owners = set(type_names_by_simple.get(owner_type, set()))
    owners.update(implementations.get(owner_type, set()))
    for owner in list(owners):
        owners.update(ancestors.get(owner, set()))
    targets = set()
    for owner in owners:
        targets.update(methods_by_owner.get((owner, method_name), set()))
    return sorted(targets)


def collect_calls(
    source_bytes,
    method,
    methods_by_owner,
    implementations,
    ancestors,
    type_names_by_simple,
    interface_names,
):
    edges = set()
    unresolved = set()
    body = method["tree_node"].child_by_field_name("body")
    if body is None:
        return edges, unresolved

    for node in walk(body):
        if node.type == "method_invocation":
            name = named_text(source_bytes, node, "name") or "<dynamic>"
            object_node = node.child_by_field_name("object")
            owner_type = receiver_type(
                source_bytes, object_node, method["bindings"], method["owner"]
            )
            targets = method_targets(
                name,
                owner_type,
                methods_by_owner,
                implementations,
                ancestors,
                type_names_by_simple,
                interface_names,
            ) if owner_type else []
            call_text = node_text(source_bytes, node).split("(", 1)[0].strip()
            if targets:
                for target in targets:
                    edges.add((method["id"], target, node_line(node), call_text))
            else:
                kind = "dynamic" if name in REFLECTIVE_METHODS else "unresolved"
                unresolved.add((method["id"], kind, call_text or name, node_line(node)))

        elif node.type == "object_creation_expression":
            names = type_names(source_bytes, node.child_by_field_name("type"))
            owner_type = names[-1] if names else None
            targets = method_targets(
                "<init>",
                owner_type,
                methods_by_owner,
                implementations,
                ancestors,
                type_names_by_simple,
                interface_names,
            ) if owner_type else []
            for target in targets:
                edges.add((method["id"], target, node_line(node), f"new {owner_type}"))
            anonymous_body = next(
                (child for child in node.named_children if child.type == "class_body"),
                None,
            )
            if anonymous_body is not None:
                unresolved.add(
                    (method["id"], "anonymous_class", f"new {owner_type}", node_line(node))
                )
            elif owner_type and not targets:
                unresolved.add(
                    (method["id"], "unresolved", f"new {owner_type}", node_line(node))
                )
    return edges, unresolved


def extract_callgraph(repo):
    repo = os.path.abspath(repo)
    parsed = []
    errors = []
    all_types = []
    all_methods = []
    for path, absolute in java_files(repo):
        source_bytes, tree, error = parse_source(path, absolute)
        if error:
            errors.append(error)
            continue
        types, methods = collect_declarations(path, source_bytes, tree)
        parsed.append((source_bytes, methods))
        all_types.extend(types)
        all_methods.extend(methods)

    type_names_by_simple, implementations, ancestors = type_relationships(all_types)
    interface_names = {
        item["name"] for item in all_types if item["kind"] == "interface_declaration"
    }
    methods_by_owner = defaultdict(set)
    for method in all_methods:
        methods_by_owner[(method["owner"], method["name"])].add(method["id"])

    edges = set()
    unresolved = set()
    for source_bytes, methods in parsed:
        for method in methods:
            found_edges, found_unresolved = collect_calls(
                source_bytes,
                method,
                methods_by_owner,
                implementations,
                ancestors,
                type_names_by_simple,
                interface_names,
            )
            edges.update(found_edges)
            unresolved.update(found_unresolved)

    unresolved_records = [
        {"caller": caller, "kind": kind, "name": name, "line": line}
        for caller, kind, name, line in sorted(
            unresolved, key=lambda item: (item[0], item[3], item[1], item[2])
        )
    ]
    return {
        "gate": "extract-java-callgraph",
        "repo": repo,
        "lang": "java",
        "nodes": [
            {
                "id": item["id"],
                "path": item["path"],
                "name": item["name"],
                "line": item["line"],
                "type": item["type"],
            }
            for item in sorted(
                all_methods, key=lambda item: (item["id"], item["line"], item["path"])
            )
        ],
        "edges": [
            {"caller": caller, "callee": callee, "line": line, "call": call}
            for caller, callee, line, call in sorted(
                edges, key=lambda item: (item[0], item[1], item[2], item[3])
            )
        ],
        "unresolved_calls": unresolved_records,
        "coverage": {"unevaluated": unresolved_records},
        "errors": sorted(
            errors,
            key=lambda item: (item.get("path", ""), item.get("error", ""), item.get("line", 0)),
        ),
    }


def print_text(result):
    for edge in result["edges"]:
        print(f"{edge['caller']} -> {edge['callee']} line={edge['line']} call={edge['call']}")
    for item in result["unresolved_calls"]:
        print(
            f"unresolved: {item['caller']} {item['kind']} "
            f"{item['name']} line={item['line']}"
        )
    for error in result["errors"]:
        print(f"error: {error['path']} {error['error']} {error.get('message', '')}".rstrip())


def main():
    parser = argparse.ArgumentParser(
        description="Extract a deterministic conservative Java intra-repository call graph."
    )
    parser.add_argument("repo", nargs="?", default=".", help="repository root to inspect")
    parser.add_argument("--json", action="store_true", help="print structured JSON")
    args = parser.parse_args()

    result = extract_callgraph(args.repo)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    else:
        print_text(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
