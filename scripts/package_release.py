#!/usr/bin/env python3
"""Build an offline release from reviewed static data, never live user data."""
import argparse,gzip,hashlib,json,shutil,tarfile,tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
VERSION='v0.1.0'
STAMP=1794873600

def validate(path):
    forbidden={'user.yaml','installation.yaml','sync','backups','upgrades','__pycache__','.git','.env'}
    for p in path.rglob('*'):
        rel=p.relative_to(path)
        if any(part in forbidden or '.userdb' in part or part.endswith(('.log','.pyc','.bak')) for part in rel.parts):
            raise ValueError('Private/generated file in release: '+str(rel))
        if p.is_symlink() and not p.resolve().is_relative_to(path.resolve()):
            raise ValueError('External symlink in release: '+str(rel))

def normalized(info):
    info.uid=info.gid=0;info.uname=info.gname='root';info.mtime=STAMP
    return info

def archive(source,target):
    with target.open('wb') as out,gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=STAMP) as gz,tarfile.open(fileobj=gz,mode='w|') as tar:
        tar.add(source,arcname=source.name,filter=normalized)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--payload-from',type=Path,required=True);ap.add_argument('--output',type=Path,default=ROOT/'dist');a=ap.parse_args()
    supplied=a.payload_from.resolve();out=a.output.resolve();out.mkdir(parents=True,exist_ok=True)
    for required in ['payload/runtime/lib/librime.so.1.17.0','payload/rime/build/wanxiang.table.bin','payload/rime/build/wanxiang.prism.bin','payload/rime/wanxiang-lts-zh-hans.gram','sources/frontend-source.tar.gz']:
        if not (supplied/required).is_file():raise SystemExit('Missing validated input: '+required)
    validate(supplied/'payload')
    with tempfile.TemporaryDirectory(prefix='daily-pinyin-release-') as temp:
        stage=Path(temp)/('daily-pinyin-'+VERSION)
        shutil.copytree(ROOT,stage,symlinks=True,ignore=shutil.ignore_patterns('.git','__pycache__','*.pyc','build','dist'))
        shutil.copytree(supplied/'payload',stage/'payload',symlinks=True,dirs_exist_ok=True)
        for name in ['default.custom.yaml','wanxiang.custom.yaml']:
            shutil.copy2(ROOT/'payload/rime'/name,stage/'payload/rime'/name)
        shutil.copytree(ROOT/'payload/theme',stage/'payload/theme',dirs_exist_ok=True)
        shutil.copy2(ROOT/'payload/classicui.conf',stage/'payload/classicui.conf')
        for p in (supplied/'sources').glob('*.tar.gz'):shutil.copy2(p,stage/'sources'/p.name)
        validate(stage)
        # Candidate compilation must match the shipped config additions.
        import yaml
        schema=yaml.safe_load((stage/'payload/rime/build/wanxiang.schema.yaml').read_text())
        if schema['translator']['max_word_length']!=12 or schema['context_reorder']['context_timeout']!=30000:
            raise SystemExit('Compiled schema does not match this version; redeploy and test before packaging.')
        digest=hashlib.sha256((stage/'payload/rime/wanxiang-lts-zh-hans.gram').read_bytes()).hexdigest()
        if digest!=json.loads((stage/'versions.json').read_text())['model']['sha256']:raise SystemExit('Model hash mismatch')
        package=out/f'daily-pinyin-{VERSION}-ubuntu24.04-x86_64.tar.gz';archive(stage,package)
        entries=[]
        with tarfile.open(package) as tar:
            for m in tar:
                entries.append(m.name)
        (out/'release-manifest.json').write_text(json.dumps({'version':VERSION,'files':entries},ensure_ascii=False,indent=2)+'\n')
        checksum=hashlib.sha256(package.read_bytes()).hexdigest()
        (out/'SHA256SUMS').write_text(f'{checksum}  {package.name}\n')
        print(package);print(checksum)
if __name__=='__main__':main()
