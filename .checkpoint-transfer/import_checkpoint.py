#!/usr/bin/env python3
"""One-time, branch-scoped checkpoint transfer. Never execute repository code."""
import hashlib
import lzma
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

BASE = '193fefd96a3a8d9f2b4a655f237071fdf7c211f8'
BRANCH = 'checkpoint/plano1-estudo-provider-switch-20261028'
TREE = '9c6f9883e5a8b11c6d731fb49e4e95998bf18d84'
PACKED_HASH = '838c33609677a60caf8087e12d00c6bcf4d65fc534562cad4f8e3749c8e85138'
PATCH_HASH = '76ff6ce509d7222c0ab6f238b0b867441e4d152cc15bb658c8315e03a7357329'
WORKFLOW = '.github/workflows/checkpoint-import-20261028.yml'


def git(*args, data=None, env=None):
    return subprocess.check_output(['git', *args], input=data, env=env).decode().strip()


def require(test, message):
    if not test:
        raise RuntimeError(message)


def main():
    verify_only = sys.argv[1:] == ['--verify-only']
    require(verify_only or not sys.argv[1:], 'Unexpected arguments')
    if not verify_only:
        require(os.environ.get('GITHUB_REPOSITORY') == 'heavydevs/plan-and-execute', 'Wrong repository')
        require(os.environ.get('GITHUB_REF') == 'refs/heads/' + BRANCH, 'Wrong branch')
        require(git('rev-parse', 'HEAD') == os.environ.get('GITHUB_SHA'), 'Unexpected checkout')
    require(git('rev-parse', 'HEAD^') == BASE, 'Unexpected bootstrap ancestry')
    require(not git('status', '--porcelain'), 'Worktree is not clean')
    folder = Path('.checkpoint-transfer')
    parts = [folder / ('part-%02d.xzpart' % i) for i in range(10)]
    require(sorted(folder.glob('part-*.xzpart')) == parts, 'Unexpected transfer parts')
    packed = b''.join(p.read_bytes() for p in parts)
    require(len(packed) == 116628 and hashlib.sha256(packed).hexdigest() == PACKED_HASH, 'Corrupt transfer')
    patch = lzma.decompress(packed, memlimit=268435456)
    require(len(patch) == 1852738 and hashlib.sha256(patch).hexdigest() == PATCH_HASH, 'Corrupt patch')
    git('apply', '--check', '--index', '--whitespace=nowarn', '-', data=patch)
    git('apply', '--index', '--whitespace=nowarn', '-', data=patch)
    paths = git('diff', '--cached', '--name-only', 'HEAD').splitlines()
    allowed = ('.ai-work/', 'docs/plans/20261028-skill-optimization/', 'docs/research/20261028-skill-optimization/')
    require(len(paths) == 186 and all(p.startswith(allowed) for p in paths), 'Unexpected patch paths')
    require(not git('diff', '--cached', '--name-only', 'HEAD', '--', 'skill', 'bin', 'lib'), 'Product code changed')
    # Compare the target tree without the temporary transport, leaving the real index intact.
    git_dir = Path(git('rev-parse', '--git-dir')).resolve()
    with tempfile.TemporaryDirectory() as tmp:
        index = Path(tmp) / 'index'
        shutil.copyfile(git_dir / 'index', index)
        env = dict(os.environ, GIT_INDEX_FILE=str(index))
        transport = git('ls-files', '--', '.checkpoint-transfer', WORKFLOW).splitlines()
        git('update-index', '--force-remove', '--', *transport, env=env)
        require(git('write-tree', env=env) == TREE, 'Tree does not match the local checkpoint')
    print('Verified checkpoint tree:', TREE)
    print('Preserved changed files:', len(paths))
    if verify_only:
        return
    git('config', 'user.name', 'github-actions[bot]')
    git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
    git('commit', '-m', 'chore: import exact Plan 1 checkpoint, supporting tools and evidence')
    # A normal fast-forward push refuses any concurrent branch update. Never touch main.
    git('push', 'origin', 'HEAD:refs/heads/' + BRANCH)
    print('Published checkpoint commit:', git('rev-parse', 'HEAD'))


if __name__ == '__main__':
    main()
