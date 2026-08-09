#!/usr/bin/env python3
"""One-way allow-listed public Markdown export."""
from pathlib import Path
import shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'site-output'
ALLOW=('Wiki','Research','Decisions')
if OUT.exists(): shutil.rmtree(OUT)
OUT.mkdir()
for base in ALLOW:
    src=ROOT/base
    if src.exists():
        for p in src.rglob('*.md'):
            dst=OUT/p.relative_to(ROOT); dst.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,dst)
if (ROOT/'Welcome.md').exists(): shutil.copy2(ROOT/'Welcome.md',OUT/'Welcome.md')
print(f'export_public: {sum(1 for _ in OUT.rglob("*.md"))} markdown files -> {OUT}')
