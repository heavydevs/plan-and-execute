#!/usr/bin/env python3
"""Restore a hash-bound GitHub Actions git-archive into a temporary safe directory.

The only acceptable archive source is a saved Actions artifact with exactly the
expected pair of files. Never use this utility to overwrite a live checkout.
"""
from __future__ import annotations
import argparse
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import sys
import tarfile
import tempfile
import zipfile

SCHEMA='pae-checkout-snapshot/1'
MAX_ARCHIVE_SIZE=90 * 1024 * 1024
MAX_EXTRACT_BYTES=350 * 1024 * 1024
MAX_MEMBERS=25000
SHA40=re.compile(r'^[0-9a-f]{40}$')

class SnapshotError(ValueError):pass

def get_payload(artifact:Path)->tuple[dict,bytes]:
    if not artifact.is_file() or artifact.stat().st_size>MAX_ARCHIVE_SIZE+2_000_000:
        raise SnapshotError('Missing or oversized workflow artifact')
    with zipfile.ZipFile(artifact) as z:
        names=z.namelist()
        if len(names)!=2 or sorted(Path(n).name for n in names)!=['pae-snapshot.json','pae-snapshot.tar.gz']:
            raise SnapshotError('Only exact manifest/archive pair is allowed')
        if any(n.startswith('/') or '..' in PurePosixPath(n).parts for n in names):
            raise SnapshotError('Unsafe outer ZIP filename')
        infos=z.infolist()
        if any(i.file_size>MAX_ARCHIVE_SIZE for i in infos):raise SnapshotError('ZIP member too large')
        meta=z.read(next(n for n in names if n.endswith('pae-snapshot.json')))
        body=z.read(next(n for n in names if n.endswith('pae-snapshot.tar.gz')))
    if len(meta)>65536:raise SnapshotError('Metadata too large')
    try:info=json.loads(meta.decode('utf-8'))
    except (UnicodeError, json.JSONDecodeError) as ex:raise SnapshotError('Invalid snapshot manifest') from ex
    if not isinstance(info,dict) or info.get('schema')!=SCHEMA:
        raise SnapshotError('Unexpected snapshot schema')
    if not isinstance(info.get('archive_size'),int) or info['archive_size'] != len(body):
        raise SnapshotError('Archive length mismatch')
    if len(body)>MAX_ARCHIVE_SIZE:raise SnapshotError('Archive too large')
    if info.get('archive_sha256')!=hashlib.sha256(body).hexdigest():
        raise SnapshotError('Snapshot SHA-256 mismatch')
    if not isinstance(info.get('head_sha'),str) or not SHA40.fullmatch(info['head_sha']):
        raise SnapshotError('Invalid source commit SHA')
    if info.get('repository')!='heavydevs/plan-and-execute':
        raise SnapshotError('Snapshot is not from expected repository')
    return info,body

def unpack(archive:bytes,target:Path)->int:
    if target.exists():raise SnapshotError('Destination already exists; never overwrite')
    parent=target.parent.resolve()
    if target.is_symlink() or not parent.is_dir():raise SnapshotError('Unsafe target')
    # Validate the complete member table before writing a single file.
    with tarfile.open(fileobj=io.BytesIO(archive),mode='r:gz') as tf:
        members=tf.getmembers()
        if len(members)>MAX_MEMBERS:raise SnapshotError('Too many tracked files')
        total=0
        seen=set()
        for x in members:
            path=PurePosixPath(x.name)
            if path.is_absolute() or not path.parts or '..' in path.parts or '\\' in x.name:
                raise SnapshotError('Unsafe tracked filename')
            if not (x.isfile() or x.isdir()):
                raise SnapshotError('Symlink, hardlink or unusual file is not extracted')
            if x.name in seen:raise SnapshotError('Duplicate tracked filename')
            seen.add(x.name)
            if x.size<0:raise SnapshotError('Invalid file size')
            total+=x.size
            if total>MAX_EXTRACT_BYTES:raise SnapshotError('Expanded snapshot too large')
        target.mkdir(mode=0o700)
        try:
            for member in members:
                path=target.joinpath(*PurePosixPath(member.name).parts)
                if member.isdir():path.mkdir(parents=True,exist_ok=True)
                else:
                    path.parent.mkdir(parents=True,exist_ok=True)
                    inp=tf.extractfile(member)
                    if inp is None:raise SnapshotError('Missing archive content')
                    with path.open('xb') as out:shutil.copyfileobj(inp,out)
                    path.chmod(0o600)
        except BaseException:
            shutil.rmtree(target)
            raise
    return len(members)

def restore(artifact:Path,target:Path,expected_sha:str)->dict:
    if not SHA40.fullmatch(expected_sha):raise SnapshotError('Expected SHA must be 40 lower-case hex characters')
    meta,tar=get_payload(artifact)
    if meta['head_sha']!=expected_sha:raise SnapshotError('Artifact source commit differs from expected')
    count=unpack(tar,target)
    evidence={'status':'restored','source_sha':expected_sha,'repository':meta['repository'],
              'archive_sha256':meta['archive_sha256'],'file_count':count,
              'target':str(target),'not_git_checkout':True,
              'note':'Tracked snapshot without .git; tests may run, but git-aware commands require a real checkout'}
    (target/'.pae-checkout-snapshot.json').write_text(json.dumps(evidence,indent=2)+'\n')
    return evidence

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--artifact',type=Path,required=True)
    ap.add_argument('--destination',type=Path,required=True)
    ap.add_argument('--sha',required=True)
    args=ap.parse_args()
    try: print(json.dumps(restore(args.artifact,args.destination,args.sha),indent=2));return 0
    except (SnapshotError,OSError,zipfile.BadZipFile,tarfile.TarError) as ex:
        print(json.dumps({'status':'blocked','reason':str(ex),'no_verified_checkout':True}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
