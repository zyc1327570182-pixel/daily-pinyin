#!/usr/bin/env python3
"""Install/undo the reviewed clipboard module in the current user prefix."""
import argparse,datetime,hashlib,json,shutil
from pathlib import Path
from install import ROOT,copy_path,session_environment,stop,restart
TARGETS=['.local/lib/daily-pinyin/fcitx5/libclipboard.so','.local/share/fcitx5/addon/clipboard.conf']
def main():
    ap=argparse.ArgumentParser(description='升级剪贴板方向键与防误删交互，保留个人词库')
    ap.add_argument('--restore',action='store_true');args=ap.parse_args()
    home=Path.home();state=home/'.local/share/daily-pinyin';pointer=state/'latest-clipboard-module-backup'
    if args.restore and not pointer.exists():return
    source=ROOT/'payload/runtime/fcitx5/libclipboard.so';target=home/TARGETS[0]
    if not args.restore:
        if not source.is_file():raise SystemExit('请从 Releases 下载包含剪贴板模块的安装包。')
        if not (home/'.local/lib/daily-pinyin/lib/librime.so.1').is_file():raise SystemExit('请先安装日用拼音。')
        if target.is_file() and hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(source.read_bytes()).digest() and (home/TARGETS[1]).is_file():return
    env=session_environment();stop(env)
    try:
        if args.restore:
            backup=Path(pointer.read_text());info=json.loads((backup/'manifest.json').read_text())
            for rel in TARGETS:
                p=home/rel
                if p.exists():p.unlink()
                if rel in info['existed']:copy_path(backup/rel,p)
            pointer.unlink()
        else:
            backup=state/'clipboard-module-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f');backup.mkdir(parents=True)
            existed=[]
            for rel in TARGETS:
                if (home/rel).exists():copy_path(home/rel,backup/rel);existed.append(rel)
            (backup/'manifest.json').write_text(json.dumps({'existed':existed}))
            copy_path(source,target)
            addon=(ROOT/'payload/clipboard-addon.conf').read_text().replace('Library=libclipboard','Library='+str(target.with_suffix('')))
            (home/TARGETS[1]).parent.mkdir(parents=True,exist_ok=True);(home/TARGETS[1]).write_text(addon)
            pointer.write_text(str(backup))
    finally:restart(home,env)
    print('剪贴板模块已'+('恢复。' if args.restore else '升级：方向键选择与翻页，Delete 仅删当前项，清空需确认。'))
if __name__=='__main__':main()
