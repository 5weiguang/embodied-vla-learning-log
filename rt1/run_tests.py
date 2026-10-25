"""Run every upstream *_test.py in an isolated process and retain logs."""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--module", action="append", help="Run only the given dotted module; retain other results")
    args = parser.parse_args()
    output = ROOT / "outputs" / "tests"
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(TF_CPP_MIN_LOG_LEVEL="2", TF_NUM_INTRAOP_THREADS="4", TF_NUM_INTEROP_THREADS="2", PYTHONHASHSEED="0")
    env["TEST_TMPDIR"] = str(ROOT / "outputs/test-tmp")
    summary = output / "summary.json"
    results = json.loads(summary.read_text()) if args.module and summary.exists() else []
    for path in sorted((ROOT / "robotics_transformer").rglob("*_test.py")):
        module = ".".join(path.relative_to(ROOT).with_suffix("").parts)
        if args.module and module not in args.module:
            continue
        print(f"RUN {module}", flush=True)
        started = time.perf_counter()
        command = [sys.executable, "-m", module]
        if "if __name__ ==" not in path.read_text(encoding="utf-8"):
            command = [sys.executable, "-m", "unittest", "-v", module]
        result = subprocess.run(command, cwd=ROOT, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                encoding="utf-8", errors="replace")
        (output / f"{path.stem}.log").write_text(result.stdout, encoding="utf-8")
        match = re.search(r"Ran (\d+) tests? in", result.stdout)
        skipped = re.search(r"skipped=(\d+)", result.stdout)
        row = {"module": module, "exit_code": result.returncode if match else (result.returncode or 1),
               "tests": int(match[1]) if match else None,
               "skipped": int(skipped[1]) if skipped else 0,
               "seconds": round(time.perf_counter() - started, 2)}
        results = [previous for previous in results if previous["module"] != module] + [row]
        summary.write_text(json.dumps(results, indent=2) + "\n")
        print(json.dumps(row), flush=True)
        if row["exit_code"]:
            print(result.stdout[-7000:], flush=True)
    if args.module and not any(row["module"] in args.module for row in results):
        parser.error("No test module matched")
    return int(any(row["exit_code"] != 0 for row in results))


if __name__ == "__main__":
    sys.exit(main())
