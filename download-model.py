#!/usr/bin/env python3
"""Fetch the exact upstream model once; input processing stays local."""
import argparse,hashlib,json,os,tempfile,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
NAME='wanxiang-lts-zh-hans.gram'
# Fixed asset ID retains the reviewed model even when the upstream tag moves.
URL='https://api.github.com/repos/amzxyz/rime-wanxiang-data/releases/assets/747939897'

def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def fetch(destination,url,expected):
    destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.is_file() and digest(destination)==expected:
        print('本地模型已通过校验。');return
    request=urllib.request.Request(url,headers={'Accept':'application/octet-stream','User-Agent':'daily-pinyin/0.1.0'})
    temp=None
    try:
        with tempfile.NamedTemporaryFile(prefix=NAME+'.',suffix='.part',dir=destination.parent,delete=False) as out:
            temp=Path(out.name)
            with urllib.request.urlopen(request,timeout=60) as response:
                total=0
                for block in iter(lambda:response.read(1024*1024),b''):
                    out.write(block);total+=len(block)
                    if total%(32*1024*1024)==0:print(f'已下载 {total//(1024*1024)} MiB',flush=True)
        if digest(temp)!=expected:raise RuntimeError('模型 SHA256 校验不符，未安装。请检查上游文件或下载地址。')
        os.replace(temp,destination);temp=None
        print('模型下载并校验完成。')
    finally:
        if temp is not None:temp.unlink(missing_ok=True)

def main():
    ap=argparse.ArgumentParser(description='首次联网下载并校验万象模型，约 389 MiB')
    ap.add_argument('--destination',type=Path,default=ROOT/'payload/rime'/NAME)
    args=ap.parse_args()
    expected=json.loads((ROOT/'versions.json').read_text())['model']['sha256']
    print('首次安装将从万象官方 GitHub 下载模型；不上传输入内容。',flush=True)
    fetch(args.destination,URL,expected)
if __name__=='__main__':main()
