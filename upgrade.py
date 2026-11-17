#!/usr/bin/env python3
"""Apply the intelligence and theme update without touching learned words."""
import argparse
import datetime
import json
from pathlib import Path
import shutil
import yaml
from install import ROOT, copy_path, session_environment, stop, restart

FILES = ['.local/share/fcitx5/rime/wanxiang.custom.yaml',
         '.local/share/fcitx5/rime/build/wanxiang.schema.yaml',
         '.local/share/fcitx5/rime/build/wanxiang.prism.bin',
         '.config/fcitx5/conf/classicui.conf',
         '.local/share/fcitx5/themes/fluent-light']

def main():
    ap = argparse.ArgumentParser(description='升级本地智能输入与微软风格皮肤')
    ap.add_argument('--home', type=Path, default=Path.home())
    ap.add_argument('--no-restart', action='store_true')
    args = ap.parse_args()
    home = args.home.resolve()
    path = home / FILES[0]
    if not path.is_file(): raise SystemExit('请先运行 install.sh 安装日用拼音。')
    env = None
    if not args.no_restart:
        env = session_environment()
        stop(env)
    backup = home / '.local/share/daily-pinyin/upgrades' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True)
    existed = []
    for rel in FILES:
        p = home / rel
        if p.exists():
            copy_path(p, backup / rel)
            existed.append(rel)
    (backup/'manifest.json').write_text(json.dumps({'home':str(home),'targets':FILES,'existed':existed},ensure_ascii=False,indent=2))
    try:
        current = yaml.safe_load(path.read_text()) or {}
        patch = current.setdefault('patch', {})
        update = yaml.safe_load((ROOT/'payload/rime/wanxiang.custom.yaml').read_text())['patch']
        for k in ['translator/enable_correction', 'translator/enable_word_completion',
                  'translator/max_word_length', 'context_reorder/context_timeout']:
            patch[k] = update[k]
        rules = patch.setdefault('speller/algebra/+', [])
        for rule in update['speller/algebra/+']:
            if rule not in rules: rules.append(rule)
        path.write_text(yaml.safe_dump(current,allow_unicode=True,sort_keys=False))
        for name in ['wanxiang.schema.yaml','wanxiang.prism.bin']:
            copy_path(ROOT/'payload/rime/build'/name, home/'.local/share/fcitx5/rime/build'/name)
        copy_path(ROOT/'payload/theme/fluent-light',home/'.local/share/fcitx5/themes/fluent-light')
        copy_path(ROOT/'payload/classicui.conf',home/'.config/fcitx5/conf/classicui.conf')
        (home/'.local/share/daily-pinyin/latest-upgrade').write_text(str(backup))
        if not args.no_restart: restart(home,env)
    except Exception:
        for rel in FILES:
            p=home/rel
            if p.exists():
                if p.is_dir():shutil.rmtree(p)
                else:p.unlink()
            if rel in existed:copy_path(backup/rel,p)
        if not args.no_restart:restart(home,env)
        raise
    print('智能输入与浅色皮肤已升级。备份：'+str(backup))

if __name__=='__main__': main()
