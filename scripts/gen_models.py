#!/usr/bin/env python
from __future__ import annotations
import subprocess
import sys
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SPEC_DIR = ROOT / "spec"
OUT_DIR = ROOT / "src" / "tollbit" / "_apis" / "models" / "_generated"

def run():
    specs = sorted(SPEC_DIR.glob("*.y*ml"))
    if not specs:
        print(f"No OpenAPI YAMLs found in {SPEC_DIR}", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    OUT_DIR.joinpath("__init__.py").touch()

    for spec in specs:
        safe_name = re.sub(r"[^0-9a-zA-Z_]", "_", spec.stem).lower()
        
        mod_file = OUT_DIR / f"{safe_name}.py"

        # Generate Pydantic v2 models for this spec
        # Notes:
        #  - targets Python 3.10+ typing
        #  - field aliases from JSON schema
        #  - keep model names stable
        cmd = [
            sys.executable, "-m", "datamodel_code_generator",
            "--input", str(spec),
            "--input-file-type", "openapi",
            "--output", str(mod_file),
            "--target-python-version", "3.10",
            "--use-union-operator",               # | syntax for unions
            "--strict-nullable",
            "--disable-timestamp",
        ]
        print("Generating:", spec.name, "->", mod_file.name)
        subprocess.run(cmd, check=True)

    print("Done. Generated models under", OUT_DIR)

if __name__ == "__main__":
    run()
