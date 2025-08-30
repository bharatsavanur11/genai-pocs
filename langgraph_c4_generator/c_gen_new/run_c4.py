#!/usr/bin/env python3
"""
Runner script for the modular C4 generator.

Usage:
  python run_c4.py --spec-file path/to/spec.txt --out generated_c4
  python run_c4.py --spec "inline text of your spec" --out generated_c4
"""

import argparse
import os
import sys
from pathlib import Path

# Ensure package root is on path
CURRENT_DIR = Path(__file__).parent
ROOT = CURRENT_DIR
sys.path.append(str(ROOT))

from mod.generator import generate_c4_architecture, save_dsl_files


def read_spec_from_file(path: str) -> str:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Spec file not found: {path}")
    return p.read_text()


def main():
    parser = argparse.ArgumentParser(description="Run C4 architecture generation")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--spec-file", type=str, help="Path to a file containing the technical specification")
    group.add_argument("--spec", type=str, help="Inline technical specification text")
    parser.add_argument("--out", type=str, default="generated_c4", help="Output directory for DSL files")
    args = parser.parse_args()

    if args.spec_file:
        spec = read_spec_from_file(args.spec_file)
    else:
        spec = args.spec

    result = generate_c4_architecture(spec)
    if result.get("success"):
        files = save_dsl_files(result, args.out)
        print(f"✅ Done. Wrote {len(files)} files to {args.out}")
        sys.exit(0)
    else:
        print(f"❌ Generation failed: {result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    main()


