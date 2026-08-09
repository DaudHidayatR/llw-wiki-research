#!/usr/bin/env python3
"""Conservative public-export safety audit (not a complete secret scanner)."""
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'site-output'
DENY={'Raw','Memory','Context','Schema','.agents','scripts','tests'}
PATTERNS=[('private key',re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),('API token',re.compile(r'(?i)(?:api[_-]?key|secret|token|password)\s*[:=]\s*["\']?[A-Za-z0-9_\-/+=]{12,}')),('dotenv value',re.compile(r'(?m)^[A-Z][A-Z0-9_]{2,}=\S+')),('absolute local path',re.compile(r'(?<![\w])(?:/home/|/Users/|/root/|[A-Za-z]:\\Users\\)'))]
errors=[]
if OUT.exists():
 for p in sorted(OUT.rglob('*')):
  rp=p.relative_to(OUT)
  if rp.parts and rp.parts[0] in DENY: errors.append(f'denied path: {rp}')
  if p.is_file():
   if p.suffix.lower() not in {'.md'}: errors.append(f'binary/non-markdown: {rp}')
   else:
    try: text=p.read_text(encoding='utf-8')
    except UnicodeDecodeError: errors.append(f'binary content: {rp}'); continue
    for label,rx in PATTERNS:
     if rx.search(text): errors.append(f'{label}: {rp}')
if errors: print('audit_public: FAIL\n'+'\n'.join('- '+e for e in errors)); sys.exit(1)
print(f'audit_public: PASS ({sum(1 for _ in OUT.rglob("*.md")) if OUT.exists() else 0} files)')
