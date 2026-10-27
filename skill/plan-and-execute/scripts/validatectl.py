#!/usr/bin/env python3
"""Plan-free mapped validation with owned receipts, bounded logs and repair routing.

No plan manifest, TODO, active pointer, model call or provider switch is implicit.
The host performs repairs from evidence and reruns this deterministic controller.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import re
import socket
import signal
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Any, Iterator

sys.dont_write_bytecode = True
import assistant_triage
import process_tree
import resource_watch
import routingctl
import service_map

SENTINEL = '.validate-or-fix'
STATE_LIMIT = 65536
SCAN_LIMIT = 65536
PACKET_LIMIT = 4096
MAX_LOG_BYTES = 8 * 1024 * 1024
ID = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,63}')
RESERVED = {'CON', 'PRN', 'AUX', 'NUL', *(f'{kind}{n}' for kind in ('COM','LPT') for n in range(1,10))}


class ValidationError(ValueError):
    pass


def safe_id(value: str) -> str:
    if not isinstance(value, str) or not ID.fullmatch(value) or value.upper() in RESERVED:
        raise ValidationError('Validation ID must be a portable identifier, not a path')
    return value


def guarded(root: Path, relative: str) -> Path:
    """Reject symlink components before resolving; no cleanup may escape repo."""
    path = root / relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValidationError('Expected a repository-relative path')
    current = root
    for part in Path(relative).parts:
        current = current / part
        if current.is_symlink():
            raise ValidationError('Symlink validation paths are forbidden')
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValidationError('Validation path escapes repository')
    return path


def atomic(path: Path, data: dict[str, Any]) -> None:
    if path.is_symlink():
        raise ValidationError('Refusing symlink state')
    payload = (json.dumps(data, sort_keys=True, ensure_ascii=True, allow_nan=False) + '\n').encode()
    if len(payload) > STATE_LIMIT:
        raise ValidationError('Validation state exceeds bounded budget')
    fd, raw = tempfile.mkstemp(prefix='.'+path.name+'.', suffix='.tmp', dir=path.parent)
    tmp = Path(raw)
    try:
        with os.fdopen(fd,'wb') as stream:
            stream.write(payload);stream.flush();os.fsync(stream.fileno())
        os.replace(tmp,path)
    finally:
        tmp.unlink(missing_ok=True)


def read_json(path: Path, default: Any = None) -> Any:
    if path.is_symlink():
        raise ValidationError('Refusing symlink state')
    try:
        with path.open('rb') as source: data=source.read(STATE_LIMIT+1)
    except FileNotFoundError:
        return default
    if len(data)>STATE_LIMIT:
        raise ValidationError('Oversized validation state')
    try:
        value=assistant_triage.strict_json(data.decode('utf-8'))
    except (ValueError,UnicodeError) as exc:
        raise ValidationError('Corrupt validation state; preserve evidence and repair explicitly') from exc
    if not isinstance(value,dict):
        raise ValidationError('Expected a state object')
    return value


def directory(root: Path, validation: str, *, create: bool = False) -> Path:
    validation=safe_id(validation)
    dest=guarded(root, f'.ai-work/validation/{validation}')
    expected={'version':1,'kind':'validate-or-fix','repo':str(root.resolve()),'validation':validation}
    if not dest.exists():
        if not create: return dest
        dest.mkdir(parents=True)
        atomic(dest/SENTINEL,expected)
    elif read_json(dest/SENTINEL)!=expected:
        raise ValidationError('Unowned validation directory; refusing overwrite or cleanup')
    return dest


def local_alive(pid: Any) -> bool:
    if type(pid) is not int or pid<=0: return False
    try: os.kill(pid,0)
    except ProcessLookupError:return False
    except PermissionError:return True
    except OSError:return False
    return True


@contextlib.contextmanager
def lock(dest: Path, name: str = '.lock') -> Iterator[None]:
    target=dest/name
    if target.is_symlink():raise ValidationError('Refusing symlink lock')
    try: fd=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
    except FileExistsError:
        raise ValidationError('Validation is locked; status is read-only; recover a dead local owner explicitly') from None
    nonce=f'{os.getpid()}-{time.time_ns()}'
    with os.fdopen(fd,'w') as out:
        json.dump({'pid':os.getpid(),'hostname':socket.gethostname(),'nonce':nonce},out)
    try: yield
    finally:
        if read_json(target,{}).get('nonce')==nonce:target.unlink(missing_ok=True)


def contract(root: Path, map_name: str, validation: str) -> tuple[dict, str]:
    path=service_map.repo_path(root,map_name)
    _,data=service_map.load_map(path)
    errors=service_map.validate_data(data)
    fresh,_,truncated,_=service_map.current_status(root,path,data)
    if errors or not fresh or truncated:raise ValidationError('service_map_invalid: reconcile the inventory before validation')
    entry=next((v for v in data['validations'] if v['id']==validation),None)
    if entry is None:raise ValidationError('validation_not_mapped: explicitly map the command and dependencies')
    return entry,service_map.validation_fingerprint(data,validation)


def report_tail(path: Path) -> list[dict]:
    if path.is_symlink():raise ValidationError('Refusing symlink report')
    try:
        with path.open('rb') as f:
            f.seek(0,2);size=f.tell();f.seek(max(0,size-SCAN_LIMIT));data=f.read(SCAN_LIMIT)
    except FileNotFoundError:return []
    if size>SCAN_LIMIT:data=data.partition(b'\n')[2]
    out=[]
    for line in data.splitlines():
        try:item=json.loads(line)
        except (ValueError,UnicodeError):continue
        if isinstance(item,dict):out.append(item)
    return out


def classification(code: int, events: list[dict]) -> str | None:
    """Trust supervisor events and exit codes, never log instructions or model advice."""
    if code in (130,143,-2,-15):return 'interrupted'
    for event in reversed(events):
        if event.get('kind') != 'validation_result' or event.get('exit_code') != code:
            continue
        value = event.get('failure_class')
        if value in ('environmental', 'semantic', 'timeout_ceiling', 'unknown'):
            return value
        if value is None and code == 0:
            return None
    # Explicit health evidence overrides a later timeout from a broken environment.
    if any(e.get('state')=='unhealthy' and e.get('failure_class','environmental')=='environmental' for e in events):return 'environmental'
    if code==125 or any(e.get('kind')=='toolchain' and e.get('state')!='healthy' for e in events):return 'environmental'
    if any(e.get('kind')=='validation_ceiling' for e in events):return 'timeout_ceiling'
    if any(e.get('kind')=='validation_stalled' for e in events):return 'semantic'
    if any(e.get('state')=='unhealthy' and e.get('failure_class')=='semantic' for e in events):return 'semantic'
    if code==0:return None
    # A test may itself return 124 or 126. Without a trusted supervisor event,
    # these are ordinary test failures, not fabricated timeout classifications.
    return 'unknown'


def repair_route(classes: list[str], signals: list[str]) -> dict:
    floor=routingctl.minimum_route(signals)
    if floor['tier']=='tool':floor={'tier':'standard','effort':'medium'}
    if classes and classes[-1] in ('environmental','timeout_ceiling','interrupted','plan_defect'):
        return {'action':'repair_environment' if classes[-1]=='environmental' else 'review_blocker','floor':floor,'escalated':False}
    # Same canonical evidence rules as orchestrated execution, but no provider
    # dispatch. Host resolves an eligible workload profile at this logical rung.
    rungs=[(tier,effort) for tier in routingctl.TIER_ORDER for effort in ('medium','high','xhigh','max')
           if routingctl.TIER_ORDER.index(tier)>=routingctl.TIER_ORDER.index(floor['tier'])
           and (tier!=floor['tier'] or routingctl.EFFORT_ORDER.index(effort)>=routingctl.EFFORT_ORDER.index(floor['effort']))]
    if not rungs:rungs=[(floor['tier'],floor['effort'])]
    step=routingctl.escalation_step(classes,rungs)
    tier,effort=rungs[min(step,len(rungs)-1)]
    return {'action':'review_blocker' if routingctl.escalation_exhausted(classes,rungs) else 'repair_and_rerun',
            'workload':'validation_repair','floor':floor,'tier':tier,'effort':effort,'escalated':(tier,effort)!=(floor['tier'],floor['effort'])}


class Spool:
    """Bound disk output and memory while draining the child pipe without blocking."""
    def __init__(self, head: Path, tail: Path, limit: int):
        self.head=head;self.tail=tail;self.limit=limit;self.total=0;self.written=0;self.buffer=b'';self.error=None
    def flush_tail(self) -> None:
        if self.tail.is_symlink():
            raise OSError('Refusing symlink tail')
        fd, raw = tempfile.mkstemp(prefix='.' + self.tail.name + '.', suffix='.tmp', dir=self.tail.parent)
        temporary = Path(raw)
        try:
            with os.fdopen(fd, 'wb') as out:
                out.write(self.buffer)
            os.replace(temporary, self.tail)
        finally:
            temporary.unlink(missing_ok=True)

    def drain(self, stream) -> None:
        target=None
        try:
            try:target=self.head.open('xb')
            except OSError as exc:self.error=type(exc).__name__
            last_flush=0.0
            while chunk:=(stream.read1(8192) if hasattr(stream,"read1") else stream.read(8192)):
                self.total+=len(chunk)
                prefix=chunk[:max(0,self.limit-self.written)]
                self.buffer=(self.buffer+chunk)[-SCAN_LIMIT:]
                if self.error:continue  # Drain even when the disk is full.
                try:
                    if prefix:target.write(prefix);target.flush();self.written+=len(prefix)
                    if self.total>self.limit and time.monotonic()-last_flush>=1:
                        self.flush_tail();last_flush=time.monotonic()
                except OSError as exc:self.error=type(exc).__name__
            if self.total>self.limit and not self.error:
                try:self.flush_tail()
                except OSError as exc:self.error=type(exc).__name__
        except (OSError, ValueError) as exc:
            self.error = type(exc).__name__
        finally:
            if target:
                try:target.close()
                except OSError as exc:self.error=type(exc).__name__
    def metadata(self):
        return {'output_bytes':self.total,'retained_prefix_bytes':self.written,'retained_tail_bytes':len(self.buffer) if self.total>self.limit else 0,
                'omitted_bytes':max(0,self.total-self.written-(len(self.buffer) if self.total>self.limit else 0))}


def packet(dest: Path, state: dict, *, consume: bool = False) -> dict:
    receipt=state.get('receipt') or {}
    log_name=receipt.get('log')
    tail_name=receipt.get('tail')
    if tail_name:
        if not isinstance(tail_name,str) or not re.fullmatch(r'run-[0-9]+-tail\.log',tail_name):
            raise ValidationError('Unsafe tail reference in receipt')
        tail=dest/tail_name
        if tail.is_symlink():raise ValidationError('Refusing symlink evidence')
        # The receipt is finalized only after exit; live inspection must already
        # follow the atomically replaced tail once the prefix retention fills.
        if tail.is_file() and tail.stat().st_size>0:log_name=tail_name
    if not log_name:return {'schema':'validation-evidence/v1','latest_delta':[]}
    # State is data, never a license to open arbitrary paths.
    if not re.fullmatch(r'run-[0-9]+(?:-tail)?\.log',str(log_name)):
        raise ValidationError('Unsafe log reference in receipt')
    log=dest/log_name
    if log.is_symlink():raise ValidationError('Refusing symlink evidence')
    cursor=read_json(dest/'cursor.json',{})
    generation=receipt.get('run_id')
    previous=cursor if cursor.get('run_id')==generation else {}
    result=resource_watch.build_failure_packet(log,exit_code=receipt.get('exit_code'),seen=previous.get('seen',[]),budget_bytes=PACKET_LIMIT-512)
    # Redact before any output or optional model call. Raw logs stay local.
    def redact_value(value):
        if isinstance(value,str):return assistant_triage.redact(value)
        if isinstance(value,list):return [redact_value(x) for x in value]
        if isinstance(value,dict):return {k:redact_value(v) for k,v in value.items()}
        return value
    clean=redact_value(result['packet'])
    clean['run_id']=generation
    clean['omitted_output_bytes']=receipt.get('omitted_bytes',0)
    clean['advisory_only']=True
    # The immutable first-failure breadcrumb is not new evidence on every read.
    if previous:clean['first_failure']=''
    if consume:atomic(dest/'cursor.json',{'run_id':generation,'seen':result['seen']})
    return clean


def run(args: argparse.Namespace) -> int:
    root=Path(args.repo_root).resolve();validation=safe_id(args.validation)
    try:entry,fingerprint=contract(root,args.map,validation)
    except (ValidationError,service_map.MapError,OSError) as exc:
        print(json.dumps({'status':'blocked','failure_class':'environmental','reason':str(exc),'repair_route':{'action':'reconcile_map','escalated':False}}));return 125
    # Validate input before any artifact creation or command invocation.
    routingctl.minimum_route(args.signals.split(','))
    dest=directory(root,validation,create=True)
    with lock(dest):
        state=read_json(dest/'state.json',{})
        if state.get('status')=='running':raise ValidationError('Unfinished validation requires explicit recovery before another run')
        if (dest/'.evidence-lock').exists():raise ValidationError('Evidence is being inspected; retry after the observer finishes')
        if state.get('status')=='passed' and not (dest/'observer.lock').exists():
            observer_state=dest/'observer.json'
            if observer_state.is_symlink():raise ValidationError('Unsafe observer state')
            observer_state.unlink(missing_ok=True)
        if state.get('fingerprint')!=fingerprint:state={'version':1,'fingerprint':fingerprint,'attempts':0,'failure_classes':[]}
        if state.get('attempts',0)>=args.max_attempts:
            print(json.dumps({'status':'blocked','reason':'attempt_budget_exhausted','action':'review then reset-attempts explicitly'}));return 75
        run_id=str(time.time_ns());name=f'run-{run_id}'
        log=dest/f'{name}.log';tail=dest/f'{name}-tail.log';events=dest/f'{name}.jsonl'
        receipt={'run_id':run_id,'log':log.name,'tail':tail.name,'events':events.name,'exit_code':None}
        state.update(status='running',validation=validation,receipt=receipt,started_at=time.time(),attempts=state.get('attempts',0)+1,
                     owner={'pid':os.getpid(),'hostname':socket.gethostname()},signals=args.signals.split(','))
        atomic(dest/'state.json',state)
        env={**os.environ,'PYTHONUNBUFFERED':'1','PYTHONDONTWRITEBYTECODE':'1','PAE_ARTIFACT_SCOPE':'temporary','PAE_ARTIFACT_OWNER':f'validation-{validation}'}
        command=[sys.executable,str(Path(__file__).with_name('resource_watch.py')),'run','--repo-root',str(root),'--map',args.map,'--validation',validation,'--report',str(events.relative_to(root))]
        child=None;reader=None;spool=Spool(log,tail,args.max_log_bytes)
        code=125
        try:
            child=process_tree.launch(command,cwd=root,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,start_new_session=True)
            state['supervisor_pid']=child.pid;atomic(dest/'state.json',state)
            reader=threading.Thread(target=spool.drain,args=(child.stdout,),daemon=True);reader.start()
            code=child.wait()
        except KeyboardInterrupt:
            code=130
        except OSError:
            code=125
        finally:
            if child is not None:
                if child.poll() is None:process_tree.terminate(child)
                if reader:reader.join(timeout=10)
                process_tree.close(child)
                if child.stdout:child.stdout.close()
        event_list=report_tail(events)
        cls=classification(code,event_list)
        if spool.error:
            cls='environmental';code=125;receipt['log_capture_error']=spool.error
        receipt.update(exit_code=code,**spool.metadata())
        classes=state.get('failure_classes',[])
        if cls:classes=(classes+[cls])[-32:]
        else:classes=[]
        state.update(status='passed' if cls is None else ('interrupted' if cls=='interrupted' else 'failed'),
                     failure_class=cls,finished_at=time.time(),failure_classes=classes,
                     repair_route=repair_route(classes,args.signals.split(',')) if cls else {'action':'done','escalated':False})
        # A successful rerun starts a new retry budget without losing the receipt.
        if cls is None:state['attempts']=0
        atomic(dest/'state.json',state)
        result={'status':state['status'],'validation':validation,'exit_code':code,'failure_class':cls,
                'repair_route':state['repair_route'],'receipt':str((dest/'state.json').relative_to(root)),
                'output':spool.metadata()}
        if cls:result['evidence']=packet(dest,state)
        print(json.dumps(result,ensure_ascii=True))
        return code if code>=0 else 130


def status(args: argparse.Namespace) -> int:
    root=Path(args.repo_root).resolve();dest=directory(root,args.validation)
    state=read_json(dest/'state.json',{}) if dest.exists() else {}
    result={k:state[k] for k in ('status','validation','attempts','failure_class','repair_route','started_at','finished_at') if k in state}
    if not state:result={'status':'absent','validation':args.validation}
    elif state.get('status')=='running':
        owner=state.get('owner',{});local=owner.get('hostname')==socket.gethostname()
        result['owner_alive']=local_alive(owner.get('pid')) if local else 'remote_unknown'
        if local and not result['owner_alive']:result['status']='interrupted';result['action']='recover'
        receipt=state.get('receipt',{});event_name=receipt.get('events','')
        if not re.fullmatch(r'run-[0-9]+\.jsonl',event_name):raise ValidationError('Unsafe report reference')
        events=report_tail(dest/event_name)
        if events:
            last=events[-1];result['observation']={k:last[k] for k in ('kind','phase','state','failure_class','test_running','timestamp') if k in last}
    if args.command=='inspect' and state:
        with lock(dest,'.evidence-lock'):result['evidence']=packet(dest,state,consume=True)
    print(json.dumps(result,ensure_ascii=True));return 0


def recover(args: argparse.Namespace) -> int:
    root=Path(args.repo_root).resolve();dest=directory(root,args.validation)
    if not dest.exists():raise ValidationError('No owned validation exists')
    state=read_json(dest/'state.json',{})
    if state.get('status')=='running' and state.get('owner',{}).get('hostname',socket.gethostname())!=socket.gethostname():
        raise ValidationError('Refusing recovery of an unknown remote owner')
    if state.get('status')=='running' and local_alive(state.get('supervisor_pid')):
        raise ValidationError('Supervisor still alive; inspect it before recovery')
    owner=read_json(dest/'.lock')
    if owner:
        if owner.get('hostname')!=socket.gethostname() or local_alive(owner.get('pid')):
            raise ValidationError('Refusing recovery of a live or remote owner')
        dest.joinpath('.lock').unlink()
    with lock(dest):
        state=read_json(dest/'state.json',{})
        if state.get('status')=='running':
            # Never launch a duplicate test or kill a PID based only on a file.
            if local_alive(state.get('supervisor_pid')):raise ValidationError('Supervisor still alive; inspect it before recovery')
            state.update(status='interrupted',failure_class='interrupted')
        if args.reset_attempts:state['attempts']=0;state['failure_classes']=[]
        atomic(dest/'state.json',state)
    print(json.dumps({'status':'recovered','restarted':False}));return 0


def cleanup(args: argparse.Namespace) -> int:
    root=Path(args.repo_root).resolve();dest=directory(root,args.validation)
    if not dest.exists():print(json.dumps({'removed':0}));return 0
    with lock(dest):
        state=read_json(dest/'state.json',{})
        if state.get('status')!='passed':raise ValidationError('Preserve active, interrupted and failed evidence; cleanup requires a passing receipt')
        if (dest/'.evidence-lock').exists() or (dest/'observer.lock').exists():
            raise ValidationError('Evidence is in use; do not clean up during observation')
        # Do not accept file paths from logs, models, receipts or the registry.
        targets=[p for p in dest.iterdir() if re.fullmatch(r'run-[0-9]+(?:-tail)?\.(?:log|jsonl)',p.name)]
        if any(p.is_symlink() or not p.is_file() for p in targets) or any((dest/name).is_symlink() for name in ('cursor.json','observer.json')):
            raise ValidationError('Unsafe validation artifact; preserve all evidence for review')
        removed=0
        for p in targets:
            p.unlink();removed+=1
        for name in ('cursor.json','observer.json'):
            p=dest/name
            if p.is_symlink():raise ValidationError('Unsafe cursor')
            p.unlink(missing_ok=True)
        state['artifacts_cleaned']=True;state['receipt']={};atomic(dest/'state.json',state)
    print(json.dumps({'removed':removed,'preserved':['receipt','service map','source','tests','external logs']}));return 0



def advise(args: argparse.Namespace) -> int:
    # This command is explicit: ordinary run/status/inspect never call a model.
    import observer
    import planctl
    import routing_config
    root=Path(args.repo_root).resolve();dest=directory(root,args.validation)
    if not dest.exists():raise ValidationError('No validation evidence exists')
    try:
        config=routing_config.load(planctl.default_config(), Path(args.config) if args.config else None)
        opt=observer.options(config)
    except (routing_config.ConfigError, observer.ObserverError, ValueError) as exc:
        raise ValidationError('Invalid observer configuration; review its documented schema') from exc
    if not opt['enabled']:
        print(json.dumps({'status':'skipped','reason':'disabled'}));return 0
    with lock(dest,'.evidence-lock'):
        state=read_json(dest/'state.json',{})
        eligible=state.get('status')=='failed'
        if state.get('status')=='running':
            name=(state.get('receipt') or {}).get('events','')
            if not re.fullmatch(r'run-[0-9]+\.jsonl',name):raise ValidationError('Unsafe evidence reference')
            events=report_tail(dest/name)
            eligible=any(e.get('kind')=='validation_stalled' or e.get('state')=='unhealthy' for e in events)
        if not eligible:
            print(json.dumps({'status':'skipped','reason':'no_anomaly'}));return 0
        data=packet(dest,state)
        if not data.get('latest_delta') and not data.get('first_failure'):
            print(json.dumps({'status':'skipped','reason':'no_new_evidence'}));return 0
        # Run ids and receipt timestamps do not make the same error novel.
        data.pop('run_id',None)
        failed={'command':args.validation,'exit_code':(state.get('receipt') or {}).get('exit_code'),
                'output_tail':json.dumps(data,ensure_ascii=True)}
        prompt,refs,signature=assistant_triage.evidence({},failed,'validation_anomaly',opt['max_input_chars'])
        try:
            result=observer.diagnose(config,prompt,refs,signature,dest/'observer.json')
        except (observer.ObserverError, ValueError) as exc:
            raise ValidationError('Invalid observer state; preserve evidence for explicit repair') from exc
        if result.get('status')=='advice' or result.get('attempts'):
            packet(dest,state,consume=True)
        print(json.dumps(result,ensure_ascii=True));return 0


def parser() -> argparse.ArgumentParser:
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ('run','status','inspect','cleanup','recover','advise'):
        item=sub.add_parser(name);item.add_argument('--repo-root',default='.');item.add_argument('--validation',required=True)
        if name=='run':
            item.add_argument('--map',default='.ai-work/SERVICE_MAP.md')
            item.add_argument('--signals',default='validation_repair')
            item.add_argument('--max-attempts',type=int,choices=range(1,21),default=5)
            item.add_argument('--max-log-bytes',type=int,default=MAX_LOG_BYTES)
        if name=='recover':item.add_argument('--reset-attempts',action='store_true')
        if name=='advise':item.add_argument('--config',help='Explicit routing overlay; otherwise use the user-global configuration')
    return p


def main(argv: list[str] | None = None) -> int:
    p=parser();args=p.parse_args(argv)
    previous = None
    if args.command == 'run' and threading.current_thread() is threading.main_thread():
        previous = signal.getsignal(signal.SIGTERM)
        def interrupted(signum, frame):
            raise KeyboardInterrupt
        signal.signal(signal.SIGTERM, interrupted)
    try:
        safe_id(args.validation)
        if args.command=='run' and not 65536<=args.max_log_bytes<=64*1024*1024:raise ValidationError('max-log-bytes must be 64KiB..64MiB')
        return {'run':run,'status':status,'inspect':status,'cleanup':cleanup,'recover':recover,'advise':advise}[args.command](args)
    except (ValidationError,service_map.MapError,routingctl.RoutingError,OSError) as exc:
        print(json.dumps({'status':'blocked','reason':str(exc)}));return 2
    finally:
        if previous is not None:
            signal.signal(signal.SIGTERM, previous)


if __name__=='__main__':raise SystemExit(main())
