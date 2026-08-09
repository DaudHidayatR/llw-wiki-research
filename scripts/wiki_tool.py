#!/usr/bin/env python3
"""Deterministic schema-2 Knowledge OS maintenance CLI (stdlib only)."""
from __future__ import annotations
import argparse, datetime as dt, hashlib, json, os, re, shutil, subprocess, sys, tempfile, unicodedata
from pathlib import Path

ROOT = Path(os.environ.get("WIKI_ROOT", Path(__file__).resolve().parents[1])).resolve()
SCHEMA = 2
CANONICAL_ROOTS = ("Raw/Sources", "Wiki", "Research", "Memory", "Decisions", "Context/Profiles")
WIKI_TYPES = {"topic":"Wiki/Topics", "concept":"Wiki/Concepts", "entity":"Wiki/Entities", "project":"Wiki/Projects", "comparison":"Wiki/Comparisons", "synthesis":"Wiki/Synthesis", "log":"Wiki/Logs"}
TYPE_DIRS = {**WIKI_TYPES, "source":"Raw/Sources", "research-question":"Research/Questions", "investigation":"Research/Investigations", "finding":"Research/Findings", "research-open":"Research/Open", "episodic-memory":"Memory/Episodic", "preference-memory":"Memory/Preferences", "observation-memory":"Memory/Observations", "decision":"Decisions/Active", "context-profile":"Context/Profiles"}
STATUS = {"seed","active","mature","needs-review","deprecated","open","closed","candidate","tentative","superseded"}
CONFIDENCE = {"low","medium","high","mixed","confirmed"}
SOURCE_TYPES = {"markdown","web","pdf","book","video","audio","code","repository","documentation","meeting","dataset","note","other"}
DATE_KEYS = {"created","updated","last_verified","review_after","Captured","Created","Published","expires"}
REQUIRED = {"schema_version","id","type","title"}
COMMON_REQUIRED = REQUIRED|{"created","updated"}
TYPE_REQUIRED = {
 "source":{"Author","Reference","SourceType","ContentType","Published","Captured","Created","ContentHash","Processed","tags"},
 **{x:{"topics","aliases","status","confidence","sources","source_count","related","relationships","supersedes","superseded_by","last_verified","review_after"} for x in WIKI_TYPES if x!="log"},
 "log":{"status","topics","sources","source_count"},"research-question":{"status","priority","related_wiki"},
 "investigation":{"status","question","confidence","sources","related_wiki","related_decisions"},"finding":{"status","confidence","sources","related_wiki"},
 "episodic-memory":{"status","importance","subject","expires"},"preference-memory":{"status","confidence","subject","supersedes","superseded_by"},
 "observation-memory":{"status","confidence","subject","expires"},"decision":{"status","scope","supersedes","superseded_by","related_wiki","related_research"},
 "context-profile":{"name","max_items","include_memory","include_decisions","include_research","include_raw"}}
TYPE_STATUS={**{x:{"seed","active","mature","needs-review","deprecated"} for x in WIKI_TYPES},"research-question":{"open","closed"},"investigation":{"active","closed"},"finding":{"candidate","mature","deprecated"},"research-open":{"open","closed"},"episodic-memory":{"active","deprecated"},"preference-memory":{"active","superseded","deprecated"},"observation-memory":{"tentative","confirmed","deprecated"},"decision":{"active","superseded"}}
TYPE_CONFIDENCE={**{x:{"low","medium","high","mixed"} for x in WIKI_TYPES},"investigation":{"low","medium","high","mixed"},"finding":{"low","medium","high","mixed"},"preference-memory":CONFIDENCE,"observation-memory":CONFIDENCE}
LIST_KEYS = {"topics","aliases","sources","related","relationships","supersedes","superseded_by","related_wiki","related_research","related_decisions","ContentType","tags"}
INDEX_NAMES = {"index.md"}
STRUCTURE = tuple(TYPE_DIRS.values())+("Raw/Files","Decisions/Superseded","Context/Packs","Schema","_templates",".agents/skills","scripts","tests","tests/fixtures")
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
CLAIM_REF_RE = re.compile(r"\[(C-\d{3})\]")
LEDGER_RE = re.compile(r"^- (C-\d{3}) \| confidence=(low|medium|high|mixed) \| (.+)$")
SOURCE_LEDGER_RE = re.compile(r"^  - source: \[\[(Raw/Sources/[^\]#]+\.md)(?:#([^\]]+))?\]\]$")
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")

class FrontmatterError(ValueError): pass

def rel(path: Path) -> str: return path.resolve().relative_to(ROOT).as_posix()
def jsonline(obj): return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",",":"))
def scalar(raw: str):
    raw = raw.strip()
    if not raw: return ""
    if raw in {"true","false"}: return raw == "true"
    if raw in {"null","~"}: return ""
    if re.fullmatch(r"-?\d+", raw): return int(raw)
    if raw.startswith('"') and raw.endswith('"'):
        try: return json.loads(raw)
        except json.JSONDecodeError as e: raise FrontmatterError(str(e))
    if raw.startswith("'") and raw.endswith("'"): return raw[1:-1].replace("''", "'")
    if raw.startswith("[") and raw.endswith("]"):
        inner=raw[1:-1].strip()
        if not inner: return []
        try:
            v=json.loads(raw)
            if not isinstance(v,list) or not all(isinstance(x,str) for x in v): raise FrontmatterError("only flat string lists supported")
            return v
        except json.JSONDecodeError: return [x.strip().strip('"\'') for x in inner.split(',') if x.strip()]
    if raw.startswith(('{','[')): raise FrontmatterError("nested/invalid YAML unsupported")
    return raw

def parse_text(text: str):
    text=text.replace("\r\n","\n").replace("\r","\n")
    if not text.startswith("---\n"): raise FrontmatterError("missing opening frontmatter delimiter")
    end=text.find("\n---\n",4)
    if end<0: raise FrontmatterError("missing closing frontmatter delimiter")
    raw=text[4:end]; body=text[end+5:]; data={}; current=None
    for n,line in enumerate(raw.splitlines(),1):
        if not line.strip() or line.lstrip().startswith("#"): continue
        if line.startswith("  - "):
            if current is None: raise FrontmatterError(f"orphan list item line {n}")
            if not isinstance(data[current],list): raise FrontmatterError(f"mixed scalar/list at {current}")
            val=scalar(line[4:])
            if not isinstance(val,str): raise FrontmatterError("list values must be strings")
            data[current].append(val); continue
        if line.startswith((" ","\t")): raise FrontmatterError(f"nested YAML unsupported line {n}")
        if ":" not in line: raise FrontmatterError(f"invalid field line {n}")
        key,value=line.split(":",1); key=key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*",key): raise FrontmatterError(f"invalid key {key}")
        if key in data: raise FrontmatterError(f"duplicate key {key}")
        data[key]=[] if not value.strip() else scalar(value); current=key if data[key]==[] else None
    return data,body

def parse(path: Path):
    data,body=parse_text(path.read_text(encoding="utf-8")); return data,body

def dump_value(v):
    if isinstance(v,bool): return "true" if v else "false"
    if isinstance(v,int): return str(v)
    return json.dumps(str(v),ensure_ascii=False)

def render(data, body):
    lines=["---"]
    for k,v in data.items():
        if isinstance(v,list):
            if not v: lines.append(f"{k}: []")
            else:
                lines.append(f"{k}:"); lines.extend(f"  - {json.dumps(x,ensure_ascii=False)}" for x in v)
        else: lines.append(f"{k}: {dump_value(v)}")
    return "\n".join(lines)+"\n---\n"+body

def write_note(path,data,body): path.parent.mkdir(parents=True,exist_ok=True); path.write_text(render(data,body),encoding="utf-8",newline="\n")
def slugify(s):
    s=unicodedata.normalize("NFKD",s); s="".join(c for c in s if not unicodedata.combining(c)); s=s.encode("ascii","ignore").decode().lower(); return re.sub(r"^-|-$","",re.sub(r"-+","-",re.sub(r"[^a-z0-9]+","-",s)))
def body_hash(body): return "sha256:"+hashlib.sha256(body.replace("\r\n","\n").replace("\r","\n").encode()).hexdigest()
def markdown_files(base):
    p=ROOT/base
    if not p.exists(): return []
    return sorted(x for x in p.rglob("*.md") if x.name not in INDEX_NAMES and not x.name.startswith(".") and not x.is_symlink())
def canonical_files():
    out=[]
    for base in CANONICAL_ROOTS: out.extend(markdown_files(base))
    return sorted(set(out),key=rel)
def records(base):
    out=[]
    for p in markdown_files(base):
        try: d,b=parse(p); out.append((p,d,b))
        except (FrontmatterError,OSError,UnicodeError): continue
    return out

def all_records(): return [(p,*parse(p)) for p in canonical_files()]
def idmap(): return {d.get("id"):(p,d,b) for p,d,b in all_records() if d.get("id")}
def iso_ok(v):
    if v in {"",None}: return True
    try: dt.date.fromisoformat(str(v)); return True
    except ValueError: return False
def safe_source_path(value):
    if not isinstance(value,str) or not value.startswith("Raw/Sources/") or Path(value).is_absolute():return None,"must be under Raw/Sources"
    target=ROOT/value
    cur=ROOT
    for part in Path(value).parts:
        cur=cur/part
        if cur.is_symlink():return None,"symlink not allowed"
    try:
        target.resolve().relative_to((ROOT/"Raw/Sources").resolve())
    except (OSError,ValueError):return None,"escapes repository"
    return target,None

def source_refs(body): return sorted(set(m.group(1) for m in re.finditer(r"\[\[(Raw/Sources/[^\]#]+\.md)(?:#[^\]]+)?\]\]",body)))
def source_manifest_path(): return ROOT/"Schema/source-manifest.jsonl"
def load_jsonl(path):
    if not path.exists(): return []
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
def write_jsonl(path,rows): path.parent.mkdir(parents=True,exist_ok=True); path.write_text("".join(jsonline(x)+"\n" for x in rows),encoding="utf-8",newline="\n")

def source_rows(preserve=True):
    old={x["path"]:x for x in load_jsonl(source_manifest_path())} if preserve else {}
    coverage={}
    for p,d,b in records("Wiki"):
        if d.get("type") in WIKI_TYPES:
            for s in d.get("sources",[]): coverage.setdefault(s,[]).append(d.get("id"))
    rows=[]
    for p,d,b in records("Raw/Sources"):
        rp=rel(p); prev=old.get(rp,{}); current=body_hash(b); fresh=d.get("ContentHash","")==current; available=sorted(coverage.get(rp,[])); processed=bool(d.get("Processed",False)) and fresh
        rows.append({"path":rp,"id":d.get("id",""),"title":d.get("title",""),"content_hash":d.get("ContentHash",""),"current_hash":current,"processed":processed,"covered_by":available if processed else [],"available_coverage":available,"excluded":bool(prev.get("excluded",False)),"updated":str(d.get("Created",d.get("updated","")))})
    return sorted(rows,key=lambda x:x["path"])

def catalog_row(p,d):
    keys=("schema_version","id","title","type","topics","aliases","sources","related","relationships","confidence","status","last_verified","review_after","updated")
    row={k:d.get(k,[] if k in LIST_KEYS else "") for k in keys}; row["path"]=rel(p)
    return {"schema_version":row.pop("schema_version",2),"id":row.pop("id"),"path":row.pop("path"),**row}
def simple_catalog(base,keys):
    rows=[]
    for p,d,b in records(base):
        row={"schema_version":d.get("schema_version",2),"id":d.get("id",""),"path":rel(p)}
        row.update({k:d.get(k,[] if k in LIST_KEYS else "") for k in keys}); rows.append(row)
    return sorted(rows,key=lambda x:x["path"])

def graph_rows():
    recs=all_records(); ids={d.get("id") for _,d,_ in recs}; path_ids={p.relative_to(ROOT).with_suffix('').as_posix():d.get("id") for p,d,_ in recs}; stems={}
    for p,d,b in recs:stems.setdefault(p.stem,[]).append(d.get("id"))
    edges=set()
    for p,d,b in recs:
        src=d.get("id");
        if not src: continue
        for r in d.get("relationships",[]):
            if "|" in r:
                relation,target=r.split("|",1); edges.add((src,relation,target,"frontmatter"))
        for s in d.get("sources",[]): edges.add((src,"supported-by",s,"sources"))
        for link in WIKILINK_RE.findall(b):
            clean=Path(link).with_suffix('').as_posix().lstrip('./'); choices=stems.get(Path(clean).stem,[]); target=path_ids.get(clean) if '/' in clean else choices[0] if len(choices)==1 else None
            if target and target!=src: edges.add((src,"links-to",target,"wikilink"))
    return [{"from":a,"relation":b,"to":c,"source":d} for a,b,c,d in sorted(edges)]

def make_index(title,rows):
    lines=[f"# {title}","","> Generated deterministically; do not edit.",""]
    for r in rows: lines.append(f"- [[{Path(r['path']).with_suffix('').as_posix()}|{r.get('title') or r['id']}]] — `{r.get('type','')}` (`{r['id']}`)")
    return "\n".join(lines)+"\n"

def cmd_build(_=None,quiet=False):
    wiki=sorted([catalog_row(p,d) for p,d,b in records("Wiki")],key=lambda x:x["path"])
    write_jsonl(ROOT/"Wiki/catalog.jsonl",wiki); write_jsonl(ROOT/"Wiki/graph.jsonl",graph_rows()); write_jsonl(source_manifest_path(),source_rows())
    (ROOT/"Wiki/index.md").write_text(make_index("Wiki Index",wiki),encoding="utf-8")
    for typ,folder in WIKI_TYPES.items():
        rs=[r for r in wiki if r["type"]==typ]; (ROOT/folder/"index.md").write_text(make_index(typ.title()+" Index",rs),encoding="utf-8")
    specs=[("Research",("type","title","status","question","related_wiki","updated")),("Memory",("type","title","status","importance","subject","updated")),("Decisions",("type","title","status","scope","supersedes","superseded_by","updated"))]
    for base,keys in specs:
        rows=simple_catalog(base,keys); write_jsonl(ROOT/base/"catalog.jsonl",rows); (ROOT/base/"index.md").write_text(make_index(base+" Index",rows),encoding="utf-8")
    if not quiet: print(f"build: wiki={len(wiki)} research={len(records('Research'))} memory={len(records('Memory'))} decisions={len(records('Decisions'))}")
    return 0

def lint_errors(strict=False):
    errors=[]; seen={}; recs=[]
    for p in canonical_files():
        rp=rel(p)
        try: d,b=parse(p)
        except (FrontmatterError,OSError,UnicodeError) as e: errors.append(f"{rp}: frontmatter: {e}"); continue
        recs.append((p,d,b)); typ=d.get("type",""); common=REQUIRED if typ=="source" else COMMON_REQUIRED; missing=(common|TYPE_REQUIRED.get(typ,set()))-set(d)
        if missing: errors.append(f"{rp}: missing fields {sorted(missing)}")
        if d.get("schema_version")!=2: errors.append(f"{rp}: schema_version must be 2")
        ident=d.get("id","")
        if not ID_RE.fullmatch(str(ident)): errors.append(f"{rp}: invalid id {ident!r}")
        if ident in seen: errors.append(f"{rp}: duplicate id {ident} also {seen[ident]}")
        seen[ident]=rp
        expected=TYPE_DIRS.get(typ)
        if not expected: errors.append(f"{rp}: invalid type {typ!r}")
        elif typ=="decision":
            status=d.get("status"); allowed="Decisions/Superseded" if status=="superseded" else "Decisions/Active"
            if not rp.startswith(allowed+"/"): errors.append(f"{rp}: decision status/location mismatch")
        elif not rp.startswith(expected+"/"): errors.append(f"{rp}: type {typ} belongs under {expected}")
        if not SLUG_RE.fullmatch(p.name): errors.append(f"{rp}: invalid filename slug")
        if typ in TYPE_DIRS and ident and not ident.startswith(typ+"-") and not d.get("migration_legacy_id",False): errors.append(f"{rp}: id must start {typ}-")
        if "status" in d and d["status"] not in TYPE_STATUS.get(typ,set()): errors.append(f"{rp}: invalid status {d['status']} for {typ}")
        if "confidence" in d and d["confidence"] not in TYPE_CONFIDENCE.get(typ,set()): errors.append(f"{rp}: invalid confidence {d['confidence']} for {typ}")
        for k in DATE_KEYS:
            if k in d and not iso_ok(d[k]): errors.append(f"{rp}: invalid ISO date {k}={d[k]}")
        for k in LIST_KEYS:
            if k in d and not isinstance(d[k],list): errors.append(f"{rp}: {k} must be flat list")
        src=d.get("sources",[])
        if typ in WIKI_TYPES and d.get("source_count") != len(src): errors.append(f"{rp}: source_count mismatch")
        for s in src:
            fp,reason=safe_source_path(s)
            if reason:errors.append(f"{rp}: source {s}: {reason}")
            elif not fp.is_file(): errors.append(f"{rp}: broken/invalid source {s}")
        if typ=="source":
            if d.get("SourceType") not in SOURCE_TYPES: errors.append(f"{rp}: invalid SourceType")
        for x in d.get("supersedes",[])+d.get("superseded_by",[]):
            if x==ident: errors.append(f"{rp}: self supersession")
        # Evidence ledger
        refs=set(CLAIM_REF_RE.findall(b)); entries={}; sources_by_claim={}; current=None
        in_ledger=False
        for line in b.splitlines():
            if line=="## Evidence Ledger": in_ledger=True; continue
            if in_ledger and line.startswith("## "): in_ledger=False
            if not in_ledger: continue
            if line and (line.startswith("- C-") or line.startswith("  - source:")) and not (LEDGER_RE.match(line) or SOURCE_LEDGER_RE.match(line)):errors.append(f"{rp}: malformed evidence ledger: {line}")
            m=LEDGER_RE.match(line)
            if m:
                current=m.group(1)
                if current in entries: errors.append(f"{rp}: duplicate ledger claim {current}")
                entries[current]=m.group(2); sources_by_claim.setdefault(current,0); continue
            m=SOURCE_LEDGER_RE.match(line)
            if m:
                if not current: errors.append(f"{rp}: evidence source without claim"); continue
                sp,anchor=m.groups(); sources_by_claim[current]+=1
                fp,reason=safe_source_path(sp)
                if reason: errors.append(f"{rp}: ledger source {sp}: {reason}")
                elif not fp.is_file(): errors.append(f"{rp}: missing ledger source {sp}")
                elif anchor:
                    try: sb=parse(fp)[1]
                    except FrontmatterError: sb=""
                    target=slugify(anchor)
                    headings={slugify(h) for h in re.findall(r"^#+\s+(.+)$",sb,re.M)}
                    if target not in headings: errors.append(f"{rp}: missing source anchor {sp}#{anchor}")
        for c in refs-entries.keys(): errors.append(f"{rp}: claim reference {c} has no ledger entry")
        for c in entries.keys()-refs: errors.append(f"{rp}: ledger claim {c} is not referenced")
        for c,n in sources_by_claim.items():
            if n==0: errors.append(f"{rp}: ledger claim {c} has no source")
        if strict and typ in {"comparison","synthesis","finding","investigation"} and "## Evidence Ledger" in b and not entries: errors.append(f"{rp}: required Evidence Ledger has zero valid claims")
    ids=set(seen)
    for p,d,b in recs:
        rp=rel(p)
        for field in ("related","related_wiki","related_research","related_decisions","supersedes","superseded_by"):
            for target in d.get(field,[]):
                if target not in ids: errors.append(f"{rp}: unresolved {field} id {target}")
        for r in d.get("relationships",[]):
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*\|[a-z0-9]+(?:-[a-z0-9]+)*",r): errors.append(f"{rp}: bad relationship {r}")
            elif r.split("|",1)[1] not in ids: errors.append(f"{rp}: unresolved relationship target {r}")
    def cyclic(start,graph):
        todo=list(graph.get(start,[])); visited=set()
        while todo:
            x=todo.pop()
            if x==start:return True
            if x not in visited:visited.add(x);todo.extend(graph.get(x,[]))
        return False
    graphs=[{d.get("id"):d.get(field,[]) for p,d,b in recs} for field in ("supersedes","superseded_by")]
    for ident in sorted(x for x in ids if x and any(cyclic(x,graph) for graph in graphs)):errors.append(f"{seen[ident]}: supersession cycle involving {ident}")
    return errors

def cmd_lint(a):
    errors=lint_errors(a.strict_evidence)
    if errors: print("lint: FAIL"); print("\n".join("- "+x for x in errors)); return 1
    print(f"lint: PASS ({len(canonical_files())} canonical notes, strict_evidence={a.strict_evidence})"); return 0

def hash_action(a):
    changed=[]; bad=[]
    target=Path(a.path) if getattr(a,"path",None) else None
    target_path=None
    if a.mode=="accept-change":
        if not target or target.is_absolute():print("source-hash: invalid target",file=sys.stderr);return 1
        target_path,reason=safe_source_path(target.as_posix())
        if reason or not target_path.is_file():print("source-hash: invalid target: "+(reason or "not found"),file=sys.stderr);return 1
    parsed=[]
    for p in markdown_files("Raw/Sources"):
        try:parsed.append((p,*parse(p)))
        except (FrontmatterError,OSError,UnicodeError) as e:bad.append(f"{p.relative_to(ROOT).as_posix()}: frontmatter: {e}")
    if bad: print("source-hash: FAIL\n"+"\n".join(bad)); return 1
    for p,d,b in parsed:
        rp=rel(p); actual=body_hash(b); stored=d.get("ContentHash","")
        if a.mode=="update-missing" and not stored: d["ContentHash"]=actual; write_note(p,d,b); changed.append(rp)
        elif a.mode=="accept-change" and p.resolve()==target_path.resolve():
            if stored==actual:print("source-hash: target has no content change",file=sys.stderr);return 1
            d["ContentHash"]=actual; d["Processed"]=False; write_note(p,d,b); changed.append(rp)
            rows=source_rows();
            for row in rows:
                if row["path"]==rp: row["covered_by"]=[]; row["processed"]=False
            write_jsonl(source_manifest_path(),rows)
            refs=[rel(x) for x,y,z in all_records() if rp in y.get("sources",[])]; print("review required:",", ".join(refs) or "none")
        elif a.mode=="check" and stored!=actual: bad.append(f"{rp}: stored={stored or '<missing>'} actual={actual}")
    if a.mode=="accept-change" and not changed: print("source-hash: target not found",file=sys.stderr); return 1
    if bad: print("source-hash: FAIL\n"+"\n".join(bad)); return 1
    print(f"source-hash: PASS changed={len(changed)} sources={len(parsed)}"); return 0

def cmd_source_scan(a):
    rows=source_rows()
    if a.accept_covered:
        errors=lint_errors(True)
        if errors:print("source-scan: refuse accept-covered because strict lint failed\n"+"\n".join(errors),file=sys.stderr);return 1
        stale=[r["path"] for r in rows if r["content_hash"]!=r["current_hash"]]
        if stale:print("source-scan: refuse accept-covered for changed sources: "+", ".join(stale),file=sys.stderr);return 1
        for r in rows:
            r["covered_by"]=r["available_coverage"]
            if r["covered_by"]:
                r["processed"]=True
                p=ROOT/r["path"]; d,b=parse(p); d["Processed"]=True; write_note(p,d,b)
    if a.update or a.accept_covered: write_jsonl(source_manifest_path(),rows)
    print(f"source-scan: sources={len(rows)} changed={sum(r['content_hash']!=r['current_hash'] for r in rows)} accepted={sum(bool(r['covered_by']) for r in rows)} update={a.update}"); return 0

def cmd_source_lint(_):
    bad=[]
    for p in markdown_files("Raw/Sources"):
        try:parse(p)
        except (FrontmatterError,OSError,UnicodeError) as e:bad.append(f"{p.relative_to(ROOT).as_posix()}: frontmatter: {e}")
    for r in source_rows():
        if r["content_hash"]!=r["current_hash"]: bad.append(r["path"]+": hash mismatch")
        if r["processed"] and not (r["covered_by"] or r["excluded"]): bad.append(r["path"]+": processed without accepted coverage/exclusion")
    if bad: print("source-lint: FAIL\n"+"\n".join(bad)); return 1
    print(f"source-lint: PASS ({len(source_rows())} sources)"); return 0

def cmd_source_delta(_):
    rows=source_rows(); delta=[r for r in rows if r["content_hash"]!=r["current_hash"] or r["available_coverage"]!=r["covered_by"]]
    print("source-delta:",len(delta)); [print(jsonline(r)) for r in delta]; return 0

def cmd_source_coverage(_):
    rows=source_rows(); uncovered=[r["path"] for r in rows if not r["covered_by"] and not r["excluded"]]
    print(f"source-coverage: covered={len(rows)-len(uncovered)}/{len(rows)} uncovered={len(uncovered)}"); [print("- "+x) for x in uncovered]; return 1 if uncovered else 0

def tokenize(s, stop=True):
    toks=[]; cur=""
    for c in unicodedata.normalize("NFKC",str(s)).casefold():
        if c.isalnum(): cur+=c
        elif cur: toks.append(cur); cur=""
    if cur:toks.append(cur)
    stops=set((ROOT/"Schema/search-stopwords.txt").read_text().split()) if stop and (ROOT/"Schema/search-stopwords.txt").exists() else set()
    return [x for x in toks if x not in stops]
def normalized(s): return " ".join(tokenize(s))
def updated_key(d):
    value=str(d.get("updated","")).replace("-","")
    return -int(value) if value.isdigit() else 1
def score_rows(query,recs,priority):
    q=set(tokenize(query)); full=normalized(query); rows=[]
    for p,d,b in recs:
        title=str(d.get("title","")); aliases=d.get("aliases",[]); topics=d.get("topics",[]); score=0
        if normalized(title)==full: score+=100
        if any(normalized(x)==full for x in aliases): score+=90
        score+=min(60,20*len(q&set(tokenize(title))))
        score+=min(45,15*len({t for t in q if any(t in tokenize(x) for x in aliases)}))
        score+=min(30,10*len({t for t in q if any(t in tokenize(x) for x in topics)}))
        score+=min(25,5*len(q&set(tokenize(b))))
        if score: rows.append((score,p,d,b))
    order={t:i for i,t in enumerate(priority)}
    rows.sort(key=lambda x:(-x[0],order.get(x[2].get("type"),99),updated_key(x[2]),rel(x[1])))
    return rows
def search_rows(query):return score_rows(query,records("Wiki"),("synthesis","comparison","concept","topic","entity","project"))

def expanded(query,profile):
    def eligible(d):
        typ=d.get("type")
        if typ in {"source","context-profile","log"}: return False
        if typ in {"episodic-memory","preference-memory","observation-memory"}: return bool(profile.get("include_memory",False))
        if typ in {"investigation","research-question","finding","research-open"}: return bool(profile.get("include_research",True)) and d.get("status") in {"active","open"}
        if typ == "decision": return bool(profile.get("include_decisions",True)) and d.get("status")=="active"
        return True
    priority=profile.get("type_priority",["synthesis","comparison","concept","topic","entity","project","investigation","research-question","finding","decision","episodic-memory","preference-memory","observation-memory"])
    candidates=[x for x in all_records() if eligible(x[1])]
    direct=score_rows(query,candidates,priority)
    if not direct and profile.get("include_raw") in {True,"always","fallback"}:direct=score_rows(query,records("Raw/Sources"),priority)
    elif profile.get("include_raw") in {True,"always"}:direct+=score_rows(query,records("Raw/Sources"),priority);direct=score_rows(query,[(p,d,b) for s,p,d,b in direct],priority)
    seeds=direct[:8]; scores={d["id"]:s for s,p,d,b in seeds}; seedids=set(scores); rec={d["id"]:(p,d,b) for p,d,b in all_records() if d.get("id")}; edges=graph_rows()
    for ident,(p,d,b) in rec.items():
        if ident in seedids or not eligible(d): continue
        typ=d.get("type")
        bonus=0
        if any(e["source"]=="frontmatter" and ((e["from"]==ident and e["to"] in seedids) or (e["to"]==ident and e["from"] in seedids)) for e in edges): bonus+=25
        if any(e["source"]=="wikilink" and ((e["from"]==ident and e["to"] in seedids) or (e["to"]==ident and e["from"] in seedids)) for e in edges): bonus+=20
        ss=set(d.get("sources",[]))
        if ss and any(ss & set(rec[x][1].get("sources",[])) for x in seedids if x in rec): bonus+=10
        typ=d.get("type")
        if typ in {"investigation","research-question","finding","research-open"} and profile.get("include_research",True) and seedids&set(d.get("related_wiki",[])): bonus+=15
        if typ=="decision" and profile.get("include_decisions",True) and seedids&set(d.get("related_wiki",[])): bonus+=15
        if typ.endswith("memory") and profile.get("include_memory",False) and seedids&set(d.get("related_wiki",[])): bonus+=10
        if bonus:scores[ident]=bonus
    priority={t:i for i,t in enumerate(priority)}
    items=[(score,*rec[i]) for i,score in scores.items() if i in rec]
    items.sort(key=lambda x:(-x[0],priority.get(x[2].get("type"),99),updated_key(x[2]),rel(x[1])))
    return items[:int(profile.get("max_items",20))]

def load_profile(name):
    for p,d,b in records("Context/Profiles"):
        if d.get("name")==name:
            d=dict(d); m=re.search(r"preferred type order:\s*\n((?:\s+\w[\w-]*\s*\n?)+)",b,re.I)
            if m:d["type_priority"]=[x.strip() for x in m.group(1).splitlines()]
            return d
    return {"max_items":20,"include_memory":False,"include_decisions":True,"include_research":True,"include_raw":"fallback"}
def context_items(query,profile_name): return expanded(query,load_profile(profile_name))
def cmd_search(a):
    rows=search_rows(a.query); print(f"search-catalog: {len(rows)} hits")
    for s,p,d,b in rows: print(f"{s:3} {d['id']} {rel(p)}")
    return 0
def cmd_related(a):
    edges=[e for e in graph_rows() if e["from"]==a.id or e["to"]==a.id]
    print(f"related: {len(edges)} edges"); [print(jsonline(e)) for e in edges]; return 0 if a.id in idmap() else 1
def cmd_graph(_): write_jsonl(ROOT/"Wiki/graph.jsonl",graph_rows()); print(f"graph-build: {len(graph_rows())} edges"); return 0

def cmd_context(a):
    profile=a.profile or "default-research"; items=context_items(a.query,profile); slug=slugify(a.query)[:60] or "query"; out=ROOT/"Context/Packs"/(slug+".md")
    lines=["# Context Pack","","## Query","",a.query,"","## Query Classification","",a.classification or "unclassified","","## Ranking Metadata","",f"- profile: `{profile}`",f"- selected: {len(items)}","- scorer: schema-2-deterministic","","## Primary Synthesis",""]
    syn=[x for x in items if x[2].get("type")=="synthesis"]
    lines += [f"- `{rel(p)}` (score {s})" for s,p,d,b in syn[:1]] or ["- none"]
    sections=[("Core Knowledge",WIKI_TYPES.keys()),("Active Research",{"research-question","investigation","finding","research-open"}),("Relevant Decisions",{"decision"}),("Relevant Memory",{"episodic-memory","preference-memory","observation-memory"})]
    for title,types in sections:
        lines += ["",f"## {title}",""]+[f"- `{rel(p)}` — `{d['id']}` (score {s})" for s,p,d,b in items if d.get("type") in types] or ["- none"]
    lines += ["","## Evidence Fallback","","- Open listed Raw sources only when exact verification is required.","","## Relationship Expansion",""]
    selected={d["id"] for s,p,d,b in items}; lines += ["- `"+jsonline(e)+"`" for e in graph_rows() if e["from"] in selected and (e["to"] in selected or e["relation"]=="supported-by")] or ["- none"]
    lines += ["","## Open Questions","","- Read selected Research/Open items.","","## Files To Read",""]+[f"{i}. `{rel(p)}`" for i,(s,p,d,b) in enumerate(items,1)]
    out.write_text("\n".join(lines)+"\n",encoding="utf-8"); print(f"context-pack: {out} items={len(items)}"); [print(f"{i+1}. {d['id']} score={s}") for i,(s,p,d,b) in enumerate(items)]; return 0

def cmd_benchmark(_):
    cases=load_jsonl(ROOT/"Schema/retrieval-benchmark.jsonl"); r5=r10=rr=zero=count=0
    for c in cases:
        ids=[d["id"] for s,p,d,b in context_items(c["query"],c.get("profile","default-research"))]; count+=len(ids); exp=c["expected_ids"]
        hit5=sum(x in ids[:5] for x in exp)/len(exp) if exp else 1; hit10=sum(x in ids[:10] for x in exp)/len(exp) if exp else 1; r5+=hit5; r10+=hit10
        ranks=[ids.index(x)+1 for x in exp if x in ids[:10]]; rr+=1/min(ranks) if ranks else 0; zero+=not ids
    n=len(cases) or 1; metrics={"cases":len(cases),"Recall@5":r5/n,"Recall@10":r10/n,"MRR@10":rr/n,"zero_hit_count":zero,"zero_hit_rate":zero/n,"average_selected_items":count/n}
    print(json.dumps(metrics,indent=2,sort_keys=True)); ok=metrics["Recall@10"]>=.85 and metrics["MRR@10"]>=.65 and metrics["zero_hit_rate"]<=.1
    print("benchmark-retrieval:","PASS" if ok else "FAIL"); return 0 if ok else 1

def cmd_doctor(_):
    needed=[*STRUCTURE,"Schema/version.json"]
    catalogs=["Schema/source-manifest.jsonl","Wiki/catalog.jsonl","Wiki/graph.jsonl","Wiki/index.md",*[folder+"/index.md" for folder in WIKI_TYPES.values()],"Research/catalog.jsonl","Research/index.md","Memory/catalog.jsonl","Memory/index.md","Decisions/catalog.jsonl","Decisions/index.md"]
    missing=[x for x in needed if not (ROOT/x).exists()]; missing_catalogs=[x for x in catalogs if not (ROOT/x).exists()]; malformed=[]; recs=[]
    for p in canonical_files():
        try:recs.append((p,*parse(p)))
        except (FrontmatterError,OSError,UnicodeError) as e:malformed.append(f"{p.relative_to(ROOT).as_posix()}: {e}")
    for relative in catalogs:
        path=ROOT/relative
        if path.exists() and path.suffix==".jsonl":
            try:load_jsonl(path)
            except (OSError,UnicodeError,json.JSONDecodeError,TypeError,ValueError) as e:malformed.append(f"{relative}: {e}")
    idents=[d.get("id") for p,d,b in recs if d.get("id")]; dup=len(idents)-len(set(idents)); stale=0; due=[]
    for p,d,b in recs:
        if d.get("type")=="source" and d.get("ContentHash")!=body_hash(b):stale+=1
        if d.get("review_after") and iso_ok(d["review_after"]) and dt.date.fromisoformat(str(d["review_after"]))<dt.date.today():due.append(p)
    try: git=subprocess.run(["git","status","--porcelain"],cwd=ROOT,text=True,capture_output=True); gs="unavailable" if git.returncode else "dirty" if git.stdout.strip() else "clean"
    except OSError: gs="unavailable"
    try:migration=json.loads((ROOT/"Schema/version.json").read_text()).get("knowledge_os_schema")!=2
    except (OSError,json.JSONDecodeError,AttributeError):migration=True;malformed.append("Schema/version.json")
    fixtures=ROOT/"tests/fixtures"; fixture_payloads=fixtures.exists() and any(p.is_file() and p.name!=".gitkeep" for p in fixtures.rglob("*"))
    print(f"doctor: python={sys.version.split()[0]} git={gs} canonical_notes={len(recs)} duplicate_ids={dup} stale_hashes={stale} review_due={len(due)} migration_required={migration} missing={len(missing)} missing_catalogs={len(missing_catalogs)} tests={'present' if (ROOT/'tests').exists() else 'missing'} fixture_payloads={'present' if fixture_payloads else 'missing'} malformed={len(malformed)}")
    for x in missing:print("- missing: "+x)
    for x in missing_catalogs:print("- missing catalog: "+x)
    for x in malformed:print("- malformed: "+x)
    return 1 if missing or missing_catalogs or dup or stale or migration or malformed or not fixture_payloads else 0

def classify():
    if not any(ROOT.iterdir()): return "A"
    v=ROOT/"Schema/version.json"
    if v.exists():
        try:
            if json.loads(v.read_text()).get("knowledge_os_schema")==2:return "D"
        except Exception: pass
    if (ROOT/"Wiki").exists() or (ROOT/"Raw").exists(): return "C"
    if (ROOT/".obsidian").exists() or list(ROOT.glob("*.md")): return "B"
    return "E"
def git_repo():
    try:
        r=subprocess.run(["git","rev-parse","--show-toplevel"],cwd=ROOT,text=True,capture_output=True)
        return Path(r.stdout.strip()).resolve()==ROOT if r.returncode==0 else False
    except OSError:return False
def tree_state():
    out={}
    for p in ROOT.rglob('*'):
        if '.git' in p.parts:continue
        rp=p.relative_to(ROOT).as_posix()
        if p.is_symlink():out[rp]='symlink:'+os.readlink(p)
        elif p.is_file():out[rp]=hashlib.sha256(p.read_bytes()).hexdigest()
    return out
def backup_tree():
    parent=Path(tempfile.mkdtemp());backup=parent/'root'
    shutil.copytree(ROOT,backup,symlinks=True,ignore=lambda p,n:{'.git'} if Path(p).resolve()==ROOT else set())
    return backup
def restore_tree(backup):
    for p in ROOT.iterdir():
        if p.name=='.git':continue
        if p.is_symlink() or p.is_file():p.unlink()
        else:shutil.rmtree(p)
    shutil.copytree(backup,ROOT,dirs_exist_ok=True,symlinks=True)
def migration_candidates():
    out=[];issues=[]
    for p in sorted(ROOT.rglob('*')):
        if any(x in p.parts for x in ('.git','Context','tests')):continue
        if p.is_symlink():issues.append({'path':p.relative_to(ROOT).as_posix(),'reason':'symlink not allowed during migration'})
    for p in sorted(ROOT.rglob("*.md")):
        rp=p.relative_to(ROOT).as_posix()
        if any(x in p.parts for x in (".git","Context","tests")) or p.name in INDEX_NAMES or p.is_symlink():continue
        try:p.resolve().relative_to(ROOT)
        except (OSError,ValueError):issues.append({'path':rp,'reason':'path escapes repository'});continue
        try:d,b=parse(p)
        except (FrontmatterError,OSError,UnicodeError) as e:issues.append({'path':rp,'reason':f'unparseable Markdown: {e}'});continue
        tags=d.get("tags",[]); inferred=[x for x in tags if x in WIKI_TYPES]
        typ=d.get("type")
        if typ and inferred and inferred!=[typ]:out.append((p,d,b,None,"type conflicts with tags"));continue
        if not typ:
            if len(inferred)!=1:out.append((p,d,b,None,"requires exactly one compiled-note type tag"));continue
            typ=inferred[0]
        if typ not in WIKI_TYPES:continue
        out.append((p,d,b,typ,None))
    return out,issues
def migration_defaults(d,typ,rp,used):
    out=dict(d); out["schema_version"]=2; out["type"]=typ
    tags=[x for x in out.get("tags",[]) if x!=typ]
    if tags:out["tags"]=tags
    else:out.pop("tags",None)
    ident=out.get("id")
    if ident and ID_RE.fullmatch(str(ident)):
        if not str(ident).startswith(typ+"-"):out["migration_legacy_id"]=True
    else:
        base=typ+"-"+(slugify(out.get("title","")) or slugify(Path(rp).stem) or "note")
        ident=base if base not in used else base+"-"+hashlib.sha256(f"{typ}\n{rp}".encode()).hexdigest()[:6]
        while ident in used:ident=base+"-"+hashlib.sha256(f"{typ}\n{rp}\n{ident}".encode()).hexdigest()[:6]
        out["id"]=ident
    today=dt.date.today().isoformat(); out.setdefault("created",today); out.setdefault("updated",today)
    defaults={"topics":[],"aliases":[],"status":"seed","confidence":"medium","sources":[],"source_count":0,"related":[],"relationships":[],"supersedes":[],"superseded_by":[],"last_verified":"","review_after":""}
    for k,v in defaults.items():out.setdefault(k,v)
    used.add(out["id"]); return out
def migration_plan():
    cls=classify(); version=None; v=ROOT/"Schema/version.json"
    if v.exists():
        try:version=json.loads(v.read_text()).get("knowledge_os_schema")
        except (OSError,json.JSONDecodeError):pass
    create=[x for x in STRUCTURE if not (ROOT/x).exists()]
    for x in ("Schema/version.json","Schema/search-stopwords.txt"):
        if not (ROOT/x).exists():create.append(x)
    if cls=="D":
        missing=[]
        for p,d,b in records("Raw/Sources"):
            if d.get("ContentHash")!=body_hash(b):missing.append(rel(p))
        return {"repository_class":cls,"schema_version":version,"create":sorted(create),"move":[],"frontmatter_transformations":[],"ambiguous":[],"id_collisions":[],"missing_source_integrity":missing,"safe_to_apply":not missing}
    candidates,ambiguous=migration_candidates(); used={d.get("id") for p,d,b,t,e in candidates if d.get("id")}
    transforms=[]; moves=[]; collisions=[];destinations={}
    generated=set(); valid_existing=set(used)
    for p,d,b,typ,error in candidates:
        rp=p.relative_to(ROOT).as_posix()
        if error:ambiguous.append({"path":rp,"reason":error});continue
        dest=(Path(TYPE_DIRS[typ])/p.name).as_posix()
        if rp!=dest:
            if os.path.lexists(ROOT/dest):ambiguous.append({"path":rp,"reason":f"destination exists: {dest}"});continue
            if dest in destinations:ambiguous.append({"path":rp,"reason":f"duplicate destination {dest} also planned from {destinations[dest]}"});continue
            destinations[dest]=rp;moves.append({"from":rp,"to":dest})
        before=d.get("id"); nd=migration_defaults(d,typ,rp,used)
        if before is None and nd["id"].rsplit("-",1)[-1].isalnum() and len(nd["id"].rsplit("-",1)[-1])==6 and nd["id"].removesuffix("-"+nd["id"].rsplit("-",1)[-1]) in generated|valid_existing:collisions.append({"path":rp,"id":nd["id"]})
        generated.add(nd["id"]); transforms.append({"path":rp,"set":{"schema_version":2,"type":typ,"id":nd["id"]},"remove":["tags"] if "tags" in d and "tags" not in nd else []})
    missing=[]
    for p,d,b in records("Raw/Sources"):
        if d.get("ContentHash")!=body_hash(b):missing.append(rel(p))
    return {"repository_class":cls,"schema_version":version,"create":sorted(create),"move":moves,"frontmatter_transformations":transforms,"ambiguous":ambiguous,"id_collisions":collisions,"missing_source_integrity":missing,"safe_to_apply":cls in {"A","B","C","D"} and not ambiguous and not missing}
def cmd_migrate(a):
    before=tree_state(); plan=migration_plan(); cls=plan["repository_class"]
    print(json.dumps(plan,indent=2,sort_keys=True))
    if not a.apply:
        if before!=tree_state():print("migrate --check mutated repository",file=sys.stderr);return 1
        return 0
    if not plan["safe_to_apply"]:print("migrate: manual action required",file=sys.stderr);return 1
    has_git=git_repo();checkpoint=None
    if has_git:
        gs=subprocess.run(["git","status","--porcelain"],cwd=ROOT,text=True,capture_output=True)
        if gs.returncode or gs.stdout.strip():print("migrate: refuse dirty Git state",file=sys.stderr);return 1
        checkpoint="knowledge-os-pre-migrate-"+dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        tag=subprocess.run(["git","tag",checkpoint],cwd=ROOT,text=True,capture_output=True)
        if tag.returncode:print("migrate: checkpoint failed: "+tag.stderr.strip(),file=sys.stderr);return 1
    backup=backup_tree()
    try:
        if cls=="D":
            for folder in STRUCTURE:(ROOT/folder).mkdir(parents=True,exist_ok=True)
            cmd_build(quiet=True);errors=lint_errors(False)
            if errors:restore_tree(backup)
            print("migrate: already schema 2; validation","PASS" if not errors else "FAIL");return 1 if errors else 0
        raw_candidates,_=migration_candidates();candidates={p.relative_to(ROOT).as_posix():(p,d,b,t,e) for p,d,b,t,e in raw_candidates}
        used={d.get("id") for p,d,b,t,e in candidates.values() if d.get("id")}
        for item in plan["frontmatter_transformations"]:
            rp=item["path"];p,d,b,typ,error=candidates[rp];nd=migration_defaults(d,typ,rp,used);nd["id"]=item["set"]["id"];move=next((x for x in plan["move"] if x["from"]==rp),None);dest=ROOT/(move["to"] if move else rp);write_note(dest,nd,b)
            if dest.resolve()!=p.resolve():p.unlink()
        for folder in STRUCTURE:(ROOT/folder).mkdir(parents=True,exist_ok=True)
        (ROOT/"Schema/version.json").write_text(json.dumps({"knowledge_os_schema":2,"spec_version":"2.1.0"},indent=2)+"\n",encoding="utf-8")
        stop=ROOT/"Schema/search-stopwords.txt"
        if not stop.exists():stop.write_text("a\nan\nand\nthe\n",encoding="utf-8")
        cmd_build(quiet=True)
        tests=subprocess.run([sys.executable,"-m","unittest","discover","-s","tests"],cwd=ROOT,text=True,capture_output=True);errors=lint_errors(False)
        if tests.returncode or errors:
            print(tests.stdout+tests.stderr,file=sys.stderr);print("\n".join(errors),file=sys.stderr);restore_tree(backup);return 1
        print("migrate: apply PASS; build, graph, tests, lint PASS");return 0
    except (OSError,UnicodeError,FrontmatterError,KeyError,ValueError) as e:
        restore_tree(backup);print(f"migrate: apply failed and rolled back: {e}",file=sys.stderr);return 1
    finally:shutil.rmtree(backup.parent,ignore_errors=True)

def list_cmd(base,a):
    rows=simple_catalog(base,("type","title","status","importance","subject","scope","updated"))
    if getattr(a,"type",None): rows=[r for r in rows if r["type"]==a.type]
    if getattr(a,"status",None): rows=[r for r in rows if r["status"]==a.status]
    print(f"{base.lower()}-list: {len(rows)}"); [print(f"{r['id']} | {r.get('status','')} | {r['path']}") for r in rows]; return 0
def cmd_research_status(_):
    rows=simple_catalog("Research",("type","title","status","updated")); counts={}
    for r in rows: counts[r["status"]]=counts.get(r["status"],0)+1
    print("research-status:",json.dumps(counts,sort_keys=True)); return 0
def cmd_research_open(_):
    rows=[r for r in simple_catalog("Research",("type","title","status","updated")) if r["status"] in {"open","active"}]
    print(f"research-open: {len(rows)}"); [print(r["id"]+" | "+r["path"]) for r in rows]; return 0

def supersession_cycle(old,new,mapping):
    todo=[old]; seen=set()
    while todo:
        x=todo.pop()
        if x==new:return True
        if x in seen:continue
        seen.add(x); todo.extend(mapping.get(x,[]))
    return False
def cmd_supersede(a):
    ids={d.get("id"):(p,d,b) for p,d,b in records("Decisions") if d.get("id")}
    if a.old not in ids or a.new not in ids: print("decision-supersede: missing ID",file=sys.stderr); return 1
    op,od,ob=ids[a.old]; np,nd,nb=ids[a.new]
    if od.get("type")!="decision" or nd.get("type")!="decision" or nd.get("status")!="active": print("decision-supersede: both must be decisions and new active",file=sys.stderr); return 1
    dest=ROOT/"Decisions/Superseded"/op.name
    if dest.exists() and dest.resolve()!=op.resolve(): print("decision-supersede: destination exists",file=sys.stderr); return 1
    mapping={d["id"]:d.get("supersedes",[]) for p,d,b in records("Decisions")}
    if a.old==a.new or supersession_cycle(a.old,a.new,mapping): print("decision-supersede: cycle refused",file=sys.stderr); return 1
    od["status"]="superseded"; od["superseded_by"]=sorted(set(od.get("superseded_by",[])+[a.new])); nd["supersedes"]=sorted(set(nd.get("supersedes",[])+[a.old])); today=dt.date.today().isoformat(); od["updated"]=today; nd["updated"]=today
    dest=ROOT/"Decisions/Superseded"/op.name
    if dest.exists() and dest.resolve()!=op.resolve():print("decision-supersede: destination exists",file=sys.stderr);return 1
    write_note(np,nd,nb); write_note(dest,od,ob)
    if dest.resolve()!=op.resolve(): op.unlink()
    print(f"decision-supersede: {a.old} -> {a.new}; moved {rel(dest)}; body preserved"); return 0

def cmd_log(a):
    today=dt.date.today().isoformat(); slug=slugify(a.title)
    if not slug:print("log: empty slug",file=sys.stderr);return 1
    p=ROOT/"Wiki/Logs"/f"{today}-{slug}.md"; ident=f"log-{today}-{slug}"
    d={"schema_version":2,"id":ident,"type":"log","title":a.title,"status":"active","topics":[],"sources":[],"source_count":0,"created":today,"updated":today}; b=f"\n# {a.title}\n\n## Summary\n\n{a.details}\n\n## Changes\n\n## Why It Changed\n\n## Affected Knowledge\n\n## Related Research\n\n## Related Decisions\n\n## Sources\n"
    if p.exists(): print("log: exists",file=sys.stderr); return 1
    write_note(p,d,b); print("log:",rel(p)); return 0

def main(argv=None):
    ap=argparse.ArgumentParser(); sp=ap.add_subparsers(dest="cmd",required=True)
    sp.add_parser("doctor"); sp.add_parser("build")
    p=sp.add_parser("lint"); p.add_argument("--strict-evidence",action="store_true")
    p=sp.add_parser("migrate"); g=p.add_mutually_exclusive_group(required=True); g.add_argument("--check",action="store_true"); g.add_argument("--apply",action="store_true")
    p=sp.add_parser("source-scan"); p.add_argument("--update",action="store_true"); p.add_argument("--accept-covered",action="store_true")
    for x in ("source-lint","source-delta","source-coverage","graph-build","benchmark-retrieval","research-status","research-open"):sp.add_parser(x)
    p=sp.add_parser("source-hash"); g=p.add_mutually_exclusive_group(required=True); g.add_argument("--check",dest="mode",action="store_const",const="check"); g.add_argument("--update-missing",dest="mode",action="store_const",const="update-missing"); g.add_argument("--accept-change",dest="path",metavar="PATH");
    p=sp.add_parser("search-catalog"); p.add_argument("--query",required=True)
    p=sp.add_parser("related"); p.add_argument("--id",required=True)
    p=sp.add_parser("context-pack"); p.add_argument("--query",required=True); p.add_argument("--profile",default="default-research"); p.add_argument("--classification")
    p=sp.add_parser("memory-list"); p.add_argument("--type"); p.add_argument("--status")
    p=sp.add_parser("decision-list"); p.add_argument("--status")
    p=sp.add_parser("decision-supersede"); p.add_argument("--old",required=True); p.add_argument("--new",required=True)
    p=sp.add_parser("log"); p.add_argument("--title",required=True); p.add_argument("--details",required=True)
    a=ap.parse_args(argv)
    if a.cmd=="source-hash" and getattr(a,"path",None): a.mode="accept-change"
    funcs={"doctor":cmd_doctor,"build":cmd_build,"lint":cmd_lint,"migrate":cmd_migrate,"source-scan":cmd_source_scan,"source-lint":cmd_source_lint,"source-delta":cmd_source_delta,"source-coverage":cmd_source_coverage,"source-hash":hash_action,"search-catalog":cmd_search,"related":cmd_related,"graph-build":cmd_graph,"context-pack":cmd_context,"benchmark-retrieval":cmd_benchmark,"research-status":cmd_research_status,"research-open":cmd_research_open,"memory-list":lambda x:list_cmd("Memory",x),"decision-list":lambda x:list_cmd("Decisions",x),"decision-supersede":cmd_supersede,"log":cmd_log}
    return funcs[a.cmd](a)
if __name__=="__main__": raise SystemExit(main())
