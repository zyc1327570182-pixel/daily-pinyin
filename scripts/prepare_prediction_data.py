from pathlib import Path
import ctypes,ctypes.util,collections,json,hashlib,argparse
ap=argparse.ArgumentParser(description='Convert the reviewed upstream prediction corpus to simplified Chinese TSV')
ap.add_argument('--input',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);ap.add_argument('--metadata',type=Path)
args=ap.parse_args();source=args.input
lib=ctypes.CDLL(ctypes.util.find_library('opencc'))
lib.opencc_open.argtypes=[ctypes.c_char_p];lib.opencc_open.restype=ctypes.c_void_p
lib.opencc_convert_utf8.argtypes=[ctypes.c_void_p,ctypes.c_char_p,ctypes.c_size_t];lib.opencc_convert_utf8.restype=ctypes.c_void_p
lib.opencc_convert_utf8_free.argtypes=[ctypes.c_void_p];lib.opencc_close.argtypes=[ctypes.c_void_p]
converter=lib.opencc_open(b'/usr/share/opencc/t2s.json');assert converter not in {None,ctypes.c_void_p(-1).value}
raw=source.read_bytes()
if hashlib.sha256(raw).hexdigest()!='df0f7a9ef96569da402d9ea2376aefad4d15382ebcccb05ec84a0acbc00c7f83':raise ValueError('Input hash differs from the reviewed upstream data-1.0 asset')
ptr=lib.opencc_convert_utf8(converter,raw,len(raw));assert ptr
text=ctypes.string_at(ptr).decode();lib.opencc_convert_utf8_free(ptr);lib.opencc_close(converter)
def chinese(s):return bool(s) and all('\u3400'<=c<='\u9fff' for c in s)
data=collections.defaultdict(dict)
for line in text.splitlines():
 parts=line.split('\t')
 if len(parts)!=3:continue
 key,word,weight=parts
 if not chinese(key) or not chinese(word) or len(word)>8 or word==key:continue
 weight=float(weight)
 data[key][word]=max(weight,data[key].get(word,0))
path=args.output;path.parent.mkdir(parents=True,exist_ok=True)
with path.open('w') as out:
 for key,words in sorted(data.items()):
  for word,weight in sorted(words.items(),key=lambda kv:(-kv[1],kv[0]))[:16]:out.write(f'{key}\t{word}\t{weight:.0f}\n')
print('contexts',len(data),'rows',sum(min(len(v),16) for v in data.values()))
(args.metadata or path.with_suffix('.metadata.json')).write_text(json.dumps({'source':'https://github.com/rime/librime-predict/releases/tag/data-1.0','asset':'predict.txt','upstream_sha256':hashlib.sha256(raw).hexdigest(),'transform':'OpenCC t2s; Chinese-only; deduplicated by maximum weight; up to 16 next words per context','contexts':len(data),'tsv_sha256':hashlib.sha256(path.read_bytes()).hexdigest()},ensure_ascii=False,indent=2)+'\n')
