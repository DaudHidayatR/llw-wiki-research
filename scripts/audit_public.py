#!/usr/bin/env python3
"""Conservative public-export safety audit (not a complete secret scanner)."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'site-output'
DENY = {'Raw', 'Memory', 'Context', 'Schema', '.agents', 'scripts', 'tests'}
PATTERNS = [
    ('private key', re.compile(r'-----BEGIN (?:[A-Z0-9]+ )?PRIVATE KEY-----')),
    ('labeled credential', re.compile(
        r'(?i)\b(?:api[_ -]?key|client[_ -]?secret|secret|token|password|passwd|pwd)'
        r'["\']?\s*[:=]\s*["\']?[^\s"\']{8,}'
    )),
    ('dotenv value', re.compile(r'(?m)^[A-Z][A-Z0-9_]{2,}\s*=\s*\S+')),
    ('bearer token', re.compile(r'(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{12,}')),
    ('JWT', re.compile(r'\beyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b')),
    ('GitHub token', re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b')),
    ('AWS access key ID', re.compile(r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b')),
    ('absolute local path', re.compile(
        r'(?<![\w/:])(?:/(?:srv|workspace|tmp)\b|/(?!/)[A-Za-z0-9._-]+(?:/[A-Za-z0-9._~-]+)+|[A-Za-z]:[\\/])'
    )),
]

errors = []
if not OUT.is_dir() or OUT.is_symlink():
    errors.append(f'missing output: {OUT}')
else:
    for path in sorted(OUT.rglob('*')):
        relative = path.relative_to(OUT)
        if path.is_symlink():
            errors.append(f'symlink: {relative}')
            continue
        if DENY.intersection(relative.parts):
            errors.append(f'denied path: {relative}')
        if '.obsidian' in relative.parts:
            errors.append(f'obsidian state: {relative}')
        if path.is_file():
            if path.suffix.lower() != '.md':
                errors.append(f'binary/non-markdown: {relative}')
                continue
            try:
                text = path.read_text(encoding='utf-8')
            except (UnicodeDecodeError, OSError):
                errors.append(f'binary content: {relative}')
                continue
            if '\0' in text:
                errors.append(f'binary content: {relative}')
                continue
            for label, pattern in PATTERNS:
                if pattern.search(text):
                    errors.append(f'{label}: {relative}')
if errors:
    print('audit_public: FAIL\n' + '\n'.join('- ' + error for error in errors))
    sys.exit(1)
print(f'audit_public: PASS ({sum(1 for _ in OUT.rglob("*.md"))} files)')
