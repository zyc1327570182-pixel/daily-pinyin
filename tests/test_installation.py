"""Check backup/restore and upgrade safety in disposable homes."""
from pathlib import Path
import shutil,subprocess,sys,tempfile,unittest
import yaml

PROJECT=Path(__file__).resolve().parents[1]
class InstallationTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        root=Path(self.tmp.name);self.package=root/'package';self.home=root/'home'
        self.package.mkdir();self.home.mkdir()
        for name in ['install.py','restore.py','upgrade.py','restore-upgrade.py']:
            shutil.copy2(PROJECT/name,self.package/name)
        shutil.copytree(PROJECT/'payload',self.package/'payload',ignore=shutil.ignore_patterns('runtime'))
        for name in ['runtime/lib/librime.so.1','rime/build/wanxiang.table.bin','rime/build/wanxiang.schema.yaml','rime/build/wanxiang.prism.bin']:
            p=self.package/'payload'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('fixture')
        self.rime=self.home/'.local/share/fcitx5/rime';self.rime.mkdir(parents=True)
        (self.rime/'private.userdb').mkdir();(self.rime/'private.userdb/record').write_bytes(b'personal words sentinel')
        (self.rime/'wanxiang.custom.yaml').write_text('patch:\n  custom_setting: keep\n')
        config=self.home/'.config/fcitx5/config';config.parent.mkdir(parents=True)
        config.write_text('[Behavior]\nActiveByDefault=False\n')
    def run_script(self,name):
        return subprocess.run([sys.executable,str(self.package/name),'--home',str(self.home),'--no-restart'],capture_output=True,text=True,check=True)
    def test_full_install_restore_keeps_original_and_saves_new_learning(self):
        self.run_script('install.py')
        backup=Path((self.home/'.local/share/daily-pinyin/latest-backup').read_text())
        self.assertEqual((backup/'.local/share/fcitx5/rime/private.userdb/record').read_bytes(),b'personal words sentinel')
        (self.rime/'new.userdb').mkdir();(self.rime/'new.userdb/record').write_text('new learning sentinel')
        self.run_script('restore.py')
        self.assertEqual((self.rime/'private.userdb/record').read_bytes(),b'personal words sentinel')
        self.assertEqual((self.home/'.config/fcitx5/config').read_text(),'[Behavior]\nActiveByDefault=False\n')
        saved=list(backup.glob('使用后保存-*'))
        self.assertEqual(len(saved),1)
        self.assertEqual((saved[0]/'.local/share/fcitx5/rime/new.userdb/record').read_text(),'new learning sentinel')
    def test_upgrade_restore_preserves_user_words_and_unrelated_settings(self):
        original=(self.rime/'wanxiang.custom.yaml').read_bytes()
        pointer=self.home/'.local/share/daily-pinyin/latest-backup';pointer.parent.mkdir(parents=True);pointer.write_text('original backup pointer')
        self.run_script('upgrade.py')
        patch=yaml.safe_load((self.rime/'wanxiang.custom.yaml').read_text())['patch']
        self.assertEqual(patch['custom_setting'],'keep')
        self.assertEqual(patch['translator/max_word_length'],12)
        self.assertEqual(patch['context_reorder/context_timeout'],30000)
        self.assertEqual(pointer.read_text(),'original backup pointer')
        self.assertEqual((self.rime/'private.userdb/record').read_bytes(),b'personal words sentinel')
        self.run_script('restore-upgrade.py')
        self.assertEqual((self.rime/'wanxiang.custom.yaml').read_bytes(),original)
        self.assertEqual((self.rime/'private.userdb/record').read_bytes(),b'personal words sentinel')
    def test_upgrade_rules_are_not_duplicated(self):
        self.run_script('upgrade.py');self.run_script('upgrade.py')
        rules=yaml.safe_load((self.rime/'wanxiang.custom.yaml').read_text())['patch']['speller/algebra/+']
        self.assertEqual(len(rules),3);self.assertEqual(len(set(rules)),3)
if __name__=='__main__':unittest.main()
