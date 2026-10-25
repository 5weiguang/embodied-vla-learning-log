"""Download pinned RT-1 sources and rt1main SavedModel from official GitHub.

Verify Git blob SHA-1 for regular files and SHA-256 for Git LFS objects.
Already verified files are reused; downloads are written atomically.
"""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import time
import urllib.request

ROOT = Path(__file__).resolve().parent
REVISION = "4569641b8111f3f402c32d8e24becd2a6e952ecc"
REPO = "google-research/robotics_transformer"


def get(url):
    for attempt in range(4):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "rt1-reproduction"})
            with urllib.request.urlopen(request, timeout=120) as response:
                return response.read()
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def blob_hash(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources-only", action="store_true")
    args = parser.parse_args()
    tree_path = ROOT / "upstream-tree.json"
    if not tree_path.exists():
        tree_path.write_bytes(get(f"https://api.github.com/repos/{REPO}/git/trees/{REVISION}?recursive=1"))
    tree = json.loads(tree_path.read_text())
    if tree["sha"] != REVISION or tree.get("truncated"):
        raise RuntimeError("Unexpected or incomplete upstream tree")
    selected = []
    for item in tree["tree"]:
        path = item["path"]
        if item["type"] != "blob":
            continue
        if path.startswith("trained_checkpoints/"):
            if args.sources_only or not path.startswith("trained_checkpoints/rt1main/"):
                continue
            if "/ckpt-" in path or path.endswith("/checkpoint"):
                continue  # SavedModel inference only needs variables/, not training checkpoints.
        selected.append(item)

    def download(item):
        path = item["path"]
        target = ROOT / "robotics_transformer" / path
        target.parent.mkdir(parents=True, exist_ok=True)
        existing = target.read_bytes() if target.exists() else None
        if existing is not None and blob_hash(existing) == item["sha"]:
            data = existing
        else:
            data = get(f"https://raw.githubusercontent.com/{REPO}/{REVISION}/{path}")
        if blob_hash(data) != item["sha"]:
            raise RuntimeError(f"Git blob checksum mismatch: {path}")
        if data.startswith(b"version https://git-lfs.github.com/spec/v1"):
            pointer = dict(line.split(" ", 1) for line in data.decode().splitlines())
            expected = pointer["oid"].split(":")[1]
            if existing is not None and hashlib.sha256(existing).hexdigest() == expected:
                data = existing
            else:
                data = get(f"https://media.githubusercontent.com/media/{REPO}/{REVISION}/{path}")
            if len(data) != int(pointer["size"]) or hashlib.sha256(data).hexdigest() != expected:
                raise RuntimeError(f"LFS checksum mismatch: {path}")
        partial = target.with_name(target.name + ".partial")
        partial.write_bytes(data)
        partial.replace(target)
        print(f"OK {path} ({len(data):,} bytes)", flush=True)
        return {"path": path, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "git_blob": item["sha"]}

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        records = list(pool.map(download, selected))
    name = "sources-manifest.json" if args.sources_only else "upstream-manifest.json"
    (ROOT / name).write_text(json.dumps({"repository": REPO, "revision": REVISION, "files": records}, indent=2) + "\n")
    print(f"Verified {len(records)} official files at {REVISION}")


if __name__ == "__main__":
    main()
