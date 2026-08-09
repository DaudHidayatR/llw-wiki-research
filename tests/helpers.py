import hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/'scripts/wiki_tool.py'
DATE='2026-08-09'
def run(vault,*args):
 e=os.environ.copy();e['WIKI_ROOT']=str(vault)
 return subprocess.run([sys.executable,str(TOOL),*args],text=True,capture_output=True,env=e)
def base():
 t=Path(tempfile.mkdtemp());
 for p in ['Raw/Sources','Wiki/Topics','Wiki/Concepts','Wiki/Entities','Wiki/Projects','Wiki/Comparisons','Wiki/Synthesis','Wiki/Logs','Research/Questions','Research/Investigations','Research/Findings','Research/Open','Memory/Episodic','Memory/Preferences','Memory/Observations','Decisions/Active','Decisions/Superseded','Context/Profiles','Context/Packs','Schema','tests']:(t/p).mkdir(parents=True,exist_ok=True)
 (t/'Schema/version.json').write_text('{"knowledge_os_schema":2,"spec_version":"2.1.0"}\n')
 (t/'Schema/search-stopwords.txt').write_text('the\nand\nhow\n')
 return t
def fm(d,body):
 lines=['---']
 for k,v in d.items():
  if isinstance(v,list):
   if v: lines += [k+':']+['  - '+json.dumps(x) for x in v]
   else: lines += [k+': []']
  elif isinstance(v,bool):lines.append(f'{k}: '+str(v).lower())
  elif isinstance(v,int):lines.append(f'{k}: {v}')
  else:lines.append(f'{k}: '+json.dumps(v))
 return '\n'.join(lines)+'\n---\n'+body
def source(v,name='evidence',bad=False):
 body='\n# Evidence\n\n## Facts\n\nDurable architecture separates evidence and memory.\n'; h='sha256:'+hashlib.sha256(body.encode()).hexdigest()
 d={'schema_version':2,'id':'source-'+name,'type':'source','title':'Evidence','Author':'Tester','Reference':'owned','SourceType':'markdown','ContentType':['markdown'],'Published':'','Captured':DATE,'Created':DATE,'ContentHash':'bad' if bad else h,'Processed':False,'tags':['source']}; p=v/'Raw/Sources'/f'{name}.md';p.write_text(fm(d,body));return p
def wiki(v,typ='concept',slug='architecture',ident=None,sources=None,source_count=None,relationships=None,body=None):
 ident=ident or f'{typ}-{slug}'; sources=[] if sources is None else sources; relationships=[] if relationships is None else relationships; body=body or f'\n# Architecture\n\nDurable architecture separates evidence and memory.\n'
 d={'schema_version':2,'id':ident,'type':typ,'title':'Architecture','topics':['knowledge'],'aliases':[],'status':'active','confidence':'high','sources':sources,'source_count':len(sources) if source_count is None else source_count,'related':[],'relationships':relationships,'supersedes':[],'superseded_by':[],'last_verified':DATE,'review_after':'','created':DATE,'updated':DATE}
 folder={'concept':'Concepts','topic':'Topics','synthesis':'Synthesis','comparison':'Comparisons'}[typ];p=v/'Wiki'/folder/f'{slug}.md';p.write_text(fm(d,body));return p
def decision(v,ident,status='active',supersedes=None,superseded_by=None,body='\n# Decision\n\n## Why\n\nOriginal rationale marker.\n'):
 folder='Active' if status=='active' else 'Superseded';d={'schema_version':2,'id':ident,'type':'decision','title':ident,'status':status,'scope':'test','supersedes':supersedes or [],'superseded_by':superseded_by or [],'related_wiki':[],'related_research':[],'created':DATE,'updated':DATE};p=v/'Decisions'/folder/(ident.removeprefix('decision-')+'.md');p.write_text(fm(d,body));return p
