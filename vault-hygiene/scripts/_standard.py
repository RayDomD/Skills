"""Read the vault's `.vault-standard.yml`.

The skill is portable procedure; the vault supplies the parameters. Both scripts in this folder
resolve their scope through here so there is exactly one place a vault's rules are read from.

The file's presence is also the marker that says "this directory is a vault". Without it these
scripts refuse to run, so a globally-installed skill can never fire in an unrelated project.
"""
import os
import sys

try:
    import yaml
except ImportError:
    sys.exit("This script needs pyyaml: pip install pyyaml")

STANDARD_FILENAME = ".vault-standard.yml"


def load(vault_root: str) -> dict:
    path = os.path.join(vault_root, STANDARD_FILENAME)
    if not os.path.isfile(path):
        sys.exit(
            f"No {STANDARD_FILENAME} at {path}.\n"
            f"This directory is not a vault, or the standard is missing. Refusing to run:\n"
            f"guessing the rules is how a cleanup pass confidently mangles the wrong files."
        )
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def scope_dirs(vault_root: str) -> list[str]:
    """Folders the standard is enforced in. Capture, archive and session internals are not
    included: an explicit path still reaches them, which is how Mode C normalizes archived
    material without a default pass ever sweeping the whole queue."""
    return list((load(vault_root).get("scope") or {}).get("enforced") or [])


def skip_dirs(vault_root: str) -> set[str]:
    return set((load(vault_root).get("scope") or {}).get("prune") or [])
