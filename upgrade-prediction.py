#!/usr/bin/env python3
"""Enable next-word suggestions without replacing personal dictionaries."""
import argparse,datetime,json,os,shutil,subprocess,sys
from pathlib import Path
import yaml
from install import ROOT,copy_path,session_environment,stop,restart

TARGETS=['.local/lib/daily-pinyin/lib/librime.so.1.17.0',
         '.local/lib/daily-pinyin/fcitx5/librime.so',
         '.local/lib/daily-pinyin/bin/rime_deployer',
         '.local/share/fcitx5/rime/wanxiang.custom.yaml',
         '.local/share/fcitx5/rime/daily-predict.db',
         '.local/share/fcitx5/rime/build']

def patch_prediction(current,enabled=True):
    patch=current.setdefault('patch',{})
    for path,name in [('engine/processors','predictor'),('engine/translators','predict_translator')]:
        if isinstance(patch.get(path),list):patch[path]=[name]+[x for x in patch[path] if x!=name]
        else:patch[path+'/@before 0']=name
    switches=patch.setdefault('switches/+',[])
    if not isinstance(switches,list):raise ValueError('switches/+ must be a list')
    switches[:]=[s for s in switches if s.get('name')!='prediction']
    switches.append({'name':'prediction','states':['联想关','联想开'],'reset':int(enabled)})
    patch.update({'predictor/db':'daily-predict.db','predictor/max_candidates':5,
                  'predictor/max_iterations':3,'super_processor/enable_predict_space':False})
    return current

def recover(home,backup):
    info=json.loads((backup/'manifest.json').read_text())
    if info['home']!=str(home):raise RuntimeError('备份用户目录不匹配。')
    for rel in info['targets']:
        p=home/rel
        if p.exists() or p.is_symlink():
            if p.is_dir() and not p.is_symlink():shutil.rmtree(p)
            else:p.unlink()
        if rel in info['existed']:copy_path(backup/rel,p)

def main():
    ap=argparse.ArgumentParser(description='升级下一词联想；--restore 撤销；--disable 默认关闭联想')
    ap.add_argument('--home',type=Path,default=Path.home());ap.add_argument('--no-restart',action='store_true')
    ap.add_argument('--restore',action='store_true');ap.add_argument('--disable',action='store_true');args=ap.parse_args()
    home=args.home.resolve();data=home/'.local/share/fcitx5/rime';state=home/'.local/share/daily-pinyin'
    pointer=state/'latest-prediction-backup'
    if args.restore:
        backup=Path(pointer.read_text());info=json.loads((backup/'manifest.json').read_text())
        if info['home']!=str(home):raise SystemExit('备份用户目录不匹配。')
    else:
        for rel in ['payload/runtime/lib/librime.so.1.17.0','payload/runtime/fcitx5/librime.so','payload/runtime/bin/rime_deployer','payload/rime/daily-predict.db']:
            if not (ROOT/rel).is_file():raise SystemExit('升级包不完整：'+rel)
        if not (data/'wanxiang.custom.yaml').is_file() or not (data/'wanxiang.schema.yaml').is_file():raise SystemExit('请先安装日用拼音。')
        current=yaml.safe_load((data/'wanxiang.custom.yaml').read_text()) or {}
        patch_prediction(current,not args.disable)
    env=None
    if not args.no_restart:env=session_environment()
    if args.restore:
        if not args.no_restart:stop(env)
        try:recover(home,backup)
        finally:
            if not args.no_restart:restart(home,env)
        print('已撤销联想升级，个人词库保留。');return
    backup=state/'prediction-backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f');backup.mkdir(parents=True)
    existed=[]
    stopped=False
    try:
        if not args.no_restart:stop(env);stopped=True
        for rel in TARGETS:
            if (home/rel).exists():copy_path(home/rel,backup/rel);existed.append(rel)
        (backup/'manifest.json').write_text(json.dumps({'home':str(home),'targets':TARGETS,'existed':existed},ensure_ascii=False,indent=2))
        for name in ['lib/librime.so.1.17.0','fcitx5/librime.so','bin/rime_deployer']:
            copy_path(ROOT/'payload/runtime'/name,home/'.local/lib/daily-pinyin'/name)
        copy_path(ROOT/'payload/rime/daily-predict.db',data/'daily-predict.db')
        (data/'wanxiang.custom.yaml').write_text(yaml.safe_dump(current,allow_unicode=True,sort_keys=False))
        log=backup/'deployment.log'
        with log.open('w') as out:
            subprocess.run([str(ROOT/'payload/runtime/bin/rime_deployer'),'--compile',str(data/'wanxiang.schema.yaml'),str(data),str(data),str(data/'build')],stdout=out,stderr=subprocess.STDOUT,check=True,timeout=180)
        compiled=yaml.safe_load((data/'build/wanxiang.schema.yaml').read_text())
        if compiled['engine']['processors'][0]!='predictor' or 'predict_translator' not in compiled['engine']['translators']:
            raise RuntimeError('联想方案未正确编译。')
        pointer.write_text(str(backup))
    except Exception:
        if (backup/'manifest.json').exists():recover(home,backup)
        if stopped:restart(home,env)
        raise
    if not args.no_restart:restart(home,env)
    print('下一词联想已'+('安装并默认关闭。' if args.disable else '启用。'))
    print('数字选择，或上下键选中后 Enter 接词；空格和直接 Enter 保持原行为，Esc 收起。')
    print('备份：'+str(backup))
if __name__=='__main__':main()
