"""Verify official assets, permitting only recorded compatibility patches."""
import hashlib
import json
from pathlib import Path
from apply_compat import REPLACEMENTS

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / "upstream-manifest.json").read_text())
    rows = []
    for item in manifest["files"]:
        target = ROOT / "robotics_transformer" / item["path"]
        content = target.read_bytes()
        patched = False
        if hashlib.sha256(content).hexdigest() != item["sha256"]:
            original = ROOT / "upstream_originals" / item["path"]
            if not original.exists():
                raise AssertionError(f"Unexpected modification: {target}")
            before = original.read_bytes()
            expected = before
            for old, new in REPLACEMENTS.items():
                expected = expected.replace(old.encode(), new.encode())
            if hashlib.sha256(before).hexdigest() != item["sha256"] or content != expected:
                raise AssertionError(f"Unexpected patch: {target}")
            patched = True
        rows.append({"path": item["path"], "compatibility_patch": patched})
    report = {"revision": manifest["revision"], "verified_files": len(rows),
              "patched_files": sum(row["compatibility_patch"] for row in rows), "files": rows}
    output = ROOT / "outputs/artifact-verification.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {report['verified_files']} files verified; {report['patched_files']} compatibility patches")


if __name__ == "__main__":
    main()
