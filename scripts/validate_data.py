#!/usr/bin/env python3
"""
validate_data.py
Checks that all official data files, rules catalog, and knowledge base files
are complete, well-formed, and documented with sources.
"""

import json
import sys
from pathlib import Path
import yaml

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "backend" / "app" / "data"
RULES_DIR = ROOT_DIR / "backend" / "app" / "rules"
KB_DIR = ROOT_DIR / "backend" / "app" / "rag" / "kb"


def validate():
    errors = []
    warnings = []
    print("[*] Validating Mig_Guard Data Files and Catalog...")

    # 1. Check SOURCES.md
    sources_path = DATA_DIR / "SOURCES.md"
    if not sources_path.exists():
        errors.append(f"Missing {sources_path}")
    else:
        text = sources_path.read_text(encoding="utf-8")
        if "BMET" not in text or "ILO" not in text:
            warnings.append("SOURCES.md missing references to primary authorities (BMET / ILO)")
        print(f"  [OK] SOURCES.md present ({len(text)} bytes)")

    # 2. Check JSON data files
    json_files = [
        "fee_caps.json",
        "helplines.json",
        "high_risk_patterns.json",
        "licensed_agencies.json",
        "salary_benchmarks.json",
    ]
    for jf in json_files:
        p = DATA_DIR / jf
        if not p.exists():
            errors.append(f"Missing data file: {jf}")
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"  [OK] {jf} valid JSON (keys: {len(data)})")
        except Exception as e:
            errors.append(f"Invalid JSON in {jf}: {e}")

    # 3. Check rules catalog.yaml
    catalog_path = RULES_DIR / "catalog.yaml"
    if not catalog_path.exists():
        errors.append("Missing catalog.yaml")
    else:
        try:
            with open(catalog_path, "r", encoding="utf-8") as f:
                catalog = yaml.safe_load(f)
            rule_count = len(catalog)
            print(f"  [OK] catalog.yaml valid YAML with {rule_count} rules")
            if rule_count < 15:
                warnings.append(f"Catalog has only {rule_count}/15 expected rules")
            for rid, meta in catalog.items():
                for field in ["severity", "weight", "title_en", "title_bn", "explanation_en", "explanation_bn", "question_en", "question_bn"]:
                    if field not in meta:
                        errors.append(f"Rule {rid} missing required field '{field}'")
        except Exception as e:
            errors.append(f"Invalid YAML in catalog.yaml: {e}")

    # 4. Check Knowledge Base files
    kb_files = list(KB_DIR.glob("*.md"))
    if not kb_files:
        errors.append("No KB markdown files found in backend/app/rag/kb")
    else:
        total_sections = 0
        for kbf in kb_files:
            content = kbf.read_text(encoding="utf-8")
            sections = content.count("\n## ")
            total_sections += sections
        print(f"  [OK] KB has {len(kb_files)} files with {total_sections} curated passages")
        if total_sections < 20:
            warnings.append(f"KB has only {total_sections} passages (target is 20-30)")

    print("\n--- Summary ---")
    if errors:
        print(f"[FAIL] Found {len(errors)} error(s):")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("[PASS] All data files and catalog structures valid!")

    if warnings:
        print(f"[WARN] {len(warnings)} warning(s):")
        for w in warnings:
            print(f"  - {w}")


if __name__ == "__main__":
    validate()

