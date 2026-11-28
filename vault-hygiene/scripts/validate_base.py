"""Validate a .base file against the Bases schema, not just YAML syntax.

Valid YAML is not enough: `filters: ['x']` parses fine and then fails in Obsidian with
"filters may only have one of an 'and', 'or', or 'not' key". One bad view fails the whole
file, so every embed of every view breaks -- which is why this is worth checking before saving.

    validate_base.py                 # every .base in the vault
    validate_base.py "Vault Health.base"
"""
import os, re, sys, glob

try:
    import yaml
except ImportError:
    sys.exit("pyyaml required: python -m pip install pyyaml")

VAULT = os.environ.get("VAULT_ROOT") or os.getcwd()
FILTER_KEYS = {"and", "or", "not"}
VIEW_TYPES = {"table", "cards", "list", "map"}


def check_filters(node, where, errs):
    """A filter is a string, or a dict with exactly one of and/or/not holding a list."""
    if isinstance(node, str):
        return
    if isinstance(node, list):
        errs.append(f"{where}: filters is a bare list; it must be a string or a single "
                    f"and/or/not key (wrap it, or use a plain string for one condition)")
        return
    if not isinstance(node, dict):
        errs.append(f"{where}: filters must be a string or a mapping, got {type(node).__name__}")
        return
    if len(node) != 1 or not set(node) <= FILTER_KEYS:
        errs.append(f"{where}: filters may only have one of 'and', 'or', 'not' — got {list(node)}")
        return
    key, val = next(iter(node.items()))
    if not isinstance(val, list):
        errs.append(f"{where}: '{key}' must hold a list")
        return
    for i, child in enumerate(val):
        if isinstance(child, dict):
            check_filters(child, f"{where} > {key}[{i}]", errs)


def check(path):
    errs = []
    rel = os.path.relpath(path, VAULT)
    try:
        doc = yaml.safe_load(open(path, encoding="utf-8"))
    except yaml.YAMLError as e:
        return [f"{rel}: invalid YAML — {e}"]
    if not isinstance(doc, dict):
        return [f"{rel}: top level must be a mapping"]

    formulas = set(doc.get("formulas") or {})
    if "filters" in doc:
        check_filters(doc["filters"], f"{rel}: global filters", errs)

    views = doc.get("views") or []
    if not isinstance(views, list):
        return errs + [f"{rel}: 'views' must be a list"]

    for v in views:
        name = v.get("name", "<unnamed>")
        where = f"{rel}: view '{name}'"
        if v.get("type") not in VIEW_TYPES:
            errs.append(f"{where}: type must be one of {sorted(VIEW_TYPES)}, got {v.get('type')!r}")
        if "filters" in v:
            check_filters(v["filters"], where, errs)
        # every formula.X referenced must exist in the formulas block
        refs = {o[8:] for o in v.get("order") or [] if str(o).startswith("formula.")}
        refs |= set(re.findall(r"formula\.(\w+)", str(v.get("filters", ""))))
        refs |= set(re.findall(r"formula\.(\w+)", str(v.get("groupBy", ""))))
        for r in sorted(refs - formulas):
            errs.append(f"{where}: references formula.{r}, which is not defined")

    for k in doc.get("properties") or {}:
        if k.startswith("formula.") and k[8:] not in formulas:
            errs.append(f"{rel}: properties references {k}, which is not defined")

    for fname, expr in (doc.get("formulas") or {}).items():
        s = str(expr)
        if s.count("(") != s.count(")"):
            errs.append(f"{rel}: formula '{fname}' has unbalanced parentheses")
    return errs


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    paths = [os.path.join(VAULT, a) for a in args] or \
            glob.glob(os.path.join(VAULT, "**", "*.base"), recursive=True)
    if not paths:
        print("no .base files found")
        return
    all_errs = []
    for p in sorted(paths):
        errs = check(p)
        all_errs += errs
        print(f"{'FAIL' if errs else 'ok  '}  {os.path.relpath(p, VAULT)}")
    for e in all_errs:
        print(f"  - {e}")
    sys.exit(1 if all_errs else 0)


if __name__ == "__main__":
    main()
