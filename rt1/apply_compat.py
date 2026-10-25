"""Apply the explicitly scoped TF2 import and test-directory patches to RT-1.

Run after download_official.py; original files and a unified diff are retained.
The model math, weights, tensor dimensions and test assertions are unchanged.
"""
import difflib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "robotics_transformer"
OLD = "from tensor2robot.utils import tensorspec_utils"
NEW = "from robotics_transformer import tensorspec_compat as tensorspec_utils"
REPLACEMENTS = {OLD: NEW, "'/tmp/unittest/policy/0'": "self.get_temp_dir()"}


def main():
    patches = []
    for path in sorted(SOURCE.rglob("*.py")):
        before = path.read_text(encoding="utf-8")
        if not any(old in before or new in before for old, new in REPLACEMENTS.items()):
            continue
        relative = path.relative_to(SOURCE)
        backup = ROOT / "upstream_originals" / relative
        if not backup.exists():
            backup.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(path.read_bytes())
        after = before
        for old, new in REPLACEMENTS.items():
            after = after.replace(old, new)
        path.write_text(after, encoding="utf-8", newline="\n")
        patches.extend(difflib.unified_diff(
            backup.read_text(encoding="utf-8").splitlines(True),
            path.read_text(encoding="utf-8").splitlines(True),
            fromfile=f"a/{relative.as_posix()}", tofile=f"b/{relative.as_posix()}"))
        print(f"Patched {relative}")
    (ROOT / "compatibility.patch").write_text("".join(patches), encoding="utf-8")


if __name__ == "__main__":
    main()
