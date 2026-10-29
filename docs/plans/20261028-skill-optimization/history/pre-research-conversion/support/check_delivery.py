#!/usr/bin/env python3
"""Plan-local evidence gate. Never dispatches a model or mutates plan state."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
DOC=Path('docs/plans/20261028-skill-optimization')
CONTROL=Path('.ai-work/20261028-skill-study-provider-switch')
class GateError(ValueError): pass
def require(ok, message):
    if not ok: raise GateError(message)
def local(root: Path, name: str) -> Path:
    require(isinstance(name,str) and bool(name),'Empty path')
    relative=Path(name)
    require(not relative.is_absolute() and '..' not in relative.parts,'Path must remain repository-relative')
    path=root/relative
    require(path.resolve().is_relative_to(root.resolve()),'Path escapes repository')
    for part in [path,*list(path.parents)[:len(relative.parts)-1]]:
        require(not part.is_symlink(),'Symlink is not evidence')
    return path
def load(path):
    require(path.is_file(),f'Missing evidence: {path}')
    require(path.stat().st_size<=2_000_000,'Oversized evidence packet')
    return json.loads(path.read_text(encoding='utf-8'))
def verified_files(root, values):
    require(isinstance(values,list) and bool(values),'At least one hashed artifact is required')
    for item in values:
        p=local(root,item.get('path',''))
        require(p.is_file(),'Missing hashed artifact')
        require(hashlib.sha256(p.read_bytes()).hexdigest()==item.get('sha256'),'Reviewed input hash is stale')
def structural(root: Path):
    spec=load(root/DOC/'PLAN1_SPEC.json'); entries=load(root/DOC/'TASK_INPUTS.json')['tasks']
    features=load(root/DOC/'FEATURE_SEED.json')['features']
    tasks={f"{t['id']:03}":t for t in spec['tasks']}
    require(len(tasks)==len(entries),'Task metadata count mismatch')
    require(spec['autostart'] is False,'Authorization gate must remain closed during preparation')
    req={r['id'] for r in spec['requirements']}
    covered={r for t in tasks.values() for r in t['requirement_ids']}
    require(req==covered,'Requirement coverage mismatch')
    for tid,t in tasks.items():
        require(set(t.get('dependencies',[]))<=tasks.keys(),'Unknown dependency')
        require(all(int(d)<int(tid) for d in t.get('dependencies',[])),'Graph is not topologically ordered')
    for f in features:
        a,b=f['research_task'],f['review_task']
        require(a in tasks and b in tasks,'Missing research/review task')
        require(tasks[b]['model_tier']=='max' and a in tasks[b]['dependencies'],'Topic lacks max review gate')
        for name in f['source_paths']: require(local(root,name).is_file(),f'Missing source {name}')
    require('whole-skill' in tasks[max(tasks)]['title'].lower(),'Last task must be whole-skill review')
    for entry in entries:
        require(entry['id'] in tasks,'Unknown packet entry')
        for key in ('output','report'): local(root,entry[key])
    request=root/CONTROL/'REQUEST.md'
    if request.is_file():
        require(hashlib.sha256(request.read_bytes()).hexdigest()=='81867f0f0a31a2fcf48c78bf7b548160924d1459ad3252fa4513fefd7de03e77','Original request bytes changed')
    print(json.dumps({'structural_check':'passed','tasks':len(tasks),'features':len(features),'requirements':len(req),
                      'semantic_review':'pending independent max reviewer','product_implementation':'not performed'}))
def check(root: Path, task_id: str):
    catalog=load(root/DOC/'TASK_INPUTS.json')['tasks']
    entry=next((t for t in catalog if t['id']==task_id),None)
    require(entry is not None,'Unknown task')
    packet=load(local(root,entry['output']))
    require(packet.get('schema_version')==1,'Invalid schema_version')
    require(packet.get('task_id')==task_id and packet.get('kind')==entry['kind'],'Wrong task/kind')
    require(packet.get('status')=='completed','Incomplete deliverable')
    require(isinstance(packet.get('summary'),str) and 0<len(packet['summary'])<=1600,'Invalid summary')
    require(local(root,entry['report']).is_file(),'Missing decision/review report')
    text=json.dumps(packet)
    require(not re.search(r'sk-[A-Za-z0-9_-]{12,}|Authorization\s*:\s*(?:Bearer|Basic)\s+[^\s<]+',text,re.I),'Possible unredacted credential')
    evidence=packet.get('evidence')
    require(isinstance(evidence,list) and bool(evidence),'Missing evidence')
    sources=packet.get('sources',[])
    source_ids={s.get('id') for s in sources if isinstance(s,dict)}
    for e in evidence:
        require(e.get('classification') in ('verified','inference') and bool(e.get('claim')),'Unsupported claim classification')
        refs=e.get('source_refs',[])
        require(isinstance(refs,list) and bool(refs),'Missing evidence refs')
        for ref in refs:
            require(isinstance(ref,str) and bool(ref),'Invalid evidence reference')
            require(ref in source_ids or local(root,ref.split('#',1)[0]).is_file(),f'Unresolved evidence ref: {ref}')
    verified_files(root,packet.get('verified_artifacts'))
    if entry['kind']=='research':
        require(len(sources)>=2,'Research needs more than one checked source')
        require(any(s.get('source_type') in ('official_documentation','official_code') for s in sources),'No primary technical source')
        for source in sources:
            for key in ('id','title','publisher','url','accessed_at','source_type','checked_version','finding','verification_scope'):
                require(isinstance(source.get(key),str) and bool(source[key]),'Incomplete source record')
            require(re.fullmatch(r'E[0-9]{3,}',source['id']) is not None,'Source id must be E###')
            require(source['url'].startswith(('https://','http://')),'Source URL missing')
            date.fromisoformat(source['accessed_at'])
        alternatives=packet.get('alternatives',[])
        require(len(alternatives)>=2 and any(a.get('id')=='current_baseline' for a in alternatives),'Missing baseline/alternative comparison')
        for a in alternatives:
            require(all(k in a for k in ('costs','benefits','risks','source_refs')),'Incomplete alternative')
        require(bool(packet.get('decision')) and bool(packet.get('evaluation')),'Missing decision/evaluation')
        require('unknowns' in packet and 'proposed_changes' in packet,'Missing uncertainty/change disposition')
    if entry['kind']=='review':
        reviewer=packet.get('reviewer',{})
        require(reviewer.get('model_tier')=='max' and reviewer.get('fresh_context') is True,'Review must use fresh maximum capability')
        for key in ('provider','model','native_effort','session_id'):
            require(isinstance(reviewer.get(key),str) and bool(reviewer[key]),'Actual review route is missing')
        require(reviewer['provider'] not in ('simulated','host','mock'),'Simulated reviewer is not accepted')
        require(local(root,reviewer.get('capability_evidence','')).is_file(),'Missing actual dispatch/capability metadata')
        require(packet.get('verdict')=='approved','Review is not approved')
        findings=packet.get('findings')
        require(isinstance(findings,list),'Missing findings list')
        require(not any(f.get('severity') in ('critical','high') and f.get('status')!='resolved' for f in findings),'Unresolved blocking review findings')
        verified_files(root,packet.get('reviewed_inputs'))
        if entry.get('review_of'):
            previous=next(t for t in catalog if t['id']==entry['review_of'])
            required={previous['output'],previous['report']}
            actual={x['path'] for x in packet['reviewed_inputs']}
            require(required<=actual,'Review did not pin the assigned deliverables')
    if entry['kind']=='implementation':
        results=packet.get('validation_results')
        require(isinstance(results,list) and bool(results),'Missing executed deterministic validation')
        for result in results:
            require(bool(result.get('command')) and isinstance(result.get('exit_code'),int),'Invalid validation result')
            require(local(root,result.get('log_path','')).is_file(),'Missing validation log')
            if result['exit_code'] != 0:
                require(result.get('classification') in ('preexisting_failure','environmental'),'New validation failure blocks acceptance')
                require(local(root,result.get('baseline_reference','')).is_file(),'Unproven baseline exception')
        require(any(r['exit_code']==0 for r in results),'No successful affected validation')
    print(f'task={task_id} packet=passed; semantic acceptance and real dispatch identity remain orchestrator checks')
def main():
    p=argparse.ArgumentParser();p.add_argument('--repo-root',default='.');p.add_argument('--task');p.add_argument('--structure',action='store_true')
    a=p.parse_args();root=Path(a.repo_root).resolve()
    try:
        if a.structure: structural(root)
        elif a.task: check(root,a.task.zfill(3))
        else: p.error('Choose --structure or --task')
    except (GateError,ValueError,KeyError,TypeError) as exc:
        print('evidence-gate: '+str(exc),file=sys.stderr);return 1
    return 0
if __name__=='__main__': raise SystemExit(main())
