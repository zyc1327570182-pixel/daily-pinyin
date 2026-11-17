from pathlib import Path
import hashlib,importlib.util,tempfile,unittest
from unittest.mock import patch
SPEC=importlib.util.spec_from_file_location('download_model',Path(__file__).resolve().parents[1]/'download-model.py')
model=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(model)
class ModelDownloadTest(unittest.TestCase):
    def test_verified_download_is_atomic_and_cached(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source';source.write_bytes(b'fixed model fixture')
            dest=Path(tmp)/'model';expected=hashlib.sha256(source.read_bytes()).hexdigest()
            model.fetch(dest,source.as_uri(),expected)
            self.assertEqual(dest.read_bytes(),source.read_bytes())
            with patch.object(model.urllib.request,'urlopen',side_effect=AssertionError('Cache should avoid download')):
                model.fetch(dest,source.as_uri(),expected)
    def test_wrong_hash_keeps_existing_model_and_removes_partial(self):
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'source';source.write_bytes(b'unexpected model')
            dest=Path(tmp)/'model';dest.write_bytes(b'previous model')
            with self.assertRaises(RuntimeError):model.fetch(dest,source.as_uri(),'0'*64)
            self.assertEqual(dest.read_bytes(),b'previous model')
            self.assertFalse(list(Path(tmp).glob('*.part')))
if __name__=='__main__':unittest.main()
