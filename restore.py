#!/usr/bin/env python3
"""Restore the pre-install input method, keeping post-install learning."""
import argparse
import datetime
import json
from pathlib import Path
import shutil
from install import copy_path, restart, session_environment, stop

def main():
    ap = argparse.ArgumentParser(description='恢复安装日用拼音之前的配置')
    ap.add_argument('--home', type=Path, default=Path.home())
    ap.add_argument('--no-restart', action='store_true')
    args = ap.parse_args()
    home = args.home.resolve()
    latest = home / '.local/share/daily-pinyin/latest-backup'
    backup = Path(latest.read_text(encoding='utf-8'))
    manifest = json.loads((backup / 'manifest.json').read_text(encoding='utf-8'))
    if Path(manifest['home']) != home:
        raise SystemExit('备份的用户目录不匹配。')
    env = None
    if not args.no_restart:
        env = session_environment()
        stop(env)
    saved = backup / ('使用后保存-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    for rel in manifest['targets']:
        target = home / rel
        if target.exists():
            copy_path(target, saved / rel)
            if target.is_dir(): shutil.rmtree(target)
            else: target.unlink()
        if rel in manifest['existed']:
            copy_path(backup / rel, target)
    if not args.no_restart: restart(home, env)
    print('已恢复原输入法。新产生的词库和配置保留在：' + str(saved))

if __name__ == '__main__':
    main()
