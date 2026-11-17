#!/usr/bin/env python3
"""Restore the last enhancement without changing personal dictionaries."""
from pathlib import Path
import argparse,json,shutil
from install import copy_path,session_environment,stop,restart

def main():
    ap=argparse.ArgumentParser(description='撤销最近一次智能与皮肤升级')
    ap.add_argument('--home',type=Path,default=Path.home())
    ap.add_argument('--no-restart',action='store_true')
    args=ap.parse_args();home=args.home.resolve()
    backup=Path((home/'.local/share/daily-pinyin/latest-upgrade').read_text())
    info=json.loads((backup/'manifest.json').read_text())
    if Path(info['home'])!=home:raise SystemExit('备份目录不匹配。')
    env=None
    if not args.no_restart:env=session_environment();stop(env)
    for rel in info['targets']:
        p=home/rel
        if p.exists():
            if p.is_dir():shutil.rmtree(p)
            else:p.unlink()
        if rel in info['existed']:copy_path(backup/rel,p)
    if not args.no_restart:restart(home,env)
    print('已撤销最近一次升级，个人词库保留。')

if __name__=='__main__':main()
