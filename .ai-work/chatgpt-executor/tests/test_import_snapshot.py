#!/usr/bin/env python3
import hashlib, importlib.util, io, json, tarfile, tempfile, unittest, zipfile
from pathlib import Path

spec=importlib.util.spec_from_file_location('import_snapshot', Path(__file__).resolve().parents[1]/'import_snapshot.py')
x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x)
SHA='f'*40

def archive(path:str,data:bytes=b'hello',type=tarfile.REGTYPE):
    out=io.BytesIO()
    with tarfile.open(fileobj=out,mode='w:gz') as t:
        info=tarfile.TarInfo(path);info.size=len(data) if type==tarfile.REGTYPE else 0;info.type=type
        t.addfile(info,io.BytesIO(data) if type==tarfile.REGTYPE else None)
    return out.getvalue()

def zipit(path:Path,tar:bytes,sha:str=SHA):
    meta={'schema':x.SCHEMA,'repository':'heavydevs/plan-and-execute','head_sha':sha,
          'archive_sha256':hashlib.sha256(tar).hexdigest(),'archive_size':len(tar)}
    with zipfile.ZipFile(path,'w') as z:
        z.writestr('pae-snapshot.json',json.dumps(meta));z.writestr('pae-snapshot.tar.gz',tar)

class Tests(unittest.TestCase):
    def test_import_and_sha(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);p=root/'work.zip';zipit(p,archive('src/a.py'))
            receipt=x.restore(p,root/'checkout',SHA)
            self.assertEqual(receipt['source_sha'],SHA)
            self.assertEqual((root/'checkout/src/a.py').read_bytes(),b'hello')
            with self.assertRaises(x.SnapshotError):x.restore(p,root/'checkout',SHA)
            with self.assertRaises(x.SnapshotError):x.restore(p,root/'other','a'*40)
    def test_path_traversal_and_symlink_rejected_without_writes(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root)
            for name,kind in [('../bad.txt',tarfile.REGTYPE),('src/link',tarfile.SYMTYPE),('/tmp/evil',tarfile.REGTYPE)]:
                p=root/'work.zip';zipit(p,archive(name,type=kind))
                with self.assertRaises(x.SnapshotError):x.restore(p,root/'checkout',SHA)
                self.assertFalse((root/'checkout').exists())
    def test_archive_tamper(self):
        with tempfile.TemporaryDirectory() as root:
            root=Path(root);path=root/'work.zip';zipit(path,archive('ok'))
            with zipfile.ZipFile(path,'a') as z:z.writestr('extra','unexpected')
            with self.assertRaises(x.SnapshotError):x.restore(path,root/'checkout',SHA)

if __name__=='__main__':unittest.main()
