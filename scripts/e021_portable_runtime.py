#!/usr/bin/env python3
"""Install one complete owned E021 runtime from pre-resolved publisher hashes.

Only official pinned software payloads are acquired. Existing corrupt payloads or
partial prefixes refuse without fallback. Native source/library/import/device
admission is a separate gate; successful installation alone is not science-ready.
"""
import argparse,concurrent.futures,email.parser,hashlib,json,os,subprocess,sys,tarfile,time,urllib.request,zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).absolute().parent))
from e009_common import binding,write_json


def acquire(row,path):
    """Stream/check one new pinned package; reuse only an already identical file."""
    p=Path(path)
    if p.exists():
        b=binding(p)
        if b['sha256']!=row['sha256']or(row.get('bytes')is not None and b['bytes']!=row['bytes']):raise ValueError('Corrupt retained software; no fallback: '+p.name)
        return b
    temp=p.with_name(p.name+'.partial')
    if temp.exists():raise FileExistsError('Preserve partial download; fresh recorded attempt required')
    h=hashlib.sha256();n=0
    with urllib.request.urlopen(row['url'],timeout=60)as source,temp.open('xb')as target:
        for data in iter(lambda:source.read(1024**2),b''):
            n+=len(data)
            if n>2*1024**3 or(row.get('bytes')is not None and n>row['bytes']):raise ValueError('Software payload exceeds declared cap')
            target.write(data);h.update(data)
    if h.hexdigest()!=row['sha256']or(row.get('bytes')is not None and n!=row['bytes']):raise ValueError('Publisher software bytes differ')
    temp.rename(p);return dict(bytes=n,sha256=h.hexdigest())


def install(recipe,prefix,root):
    """Download hash-closed software, inspect wheel metadata and run the real installers."""
    recipe=Path(recipe);p=Path(prefix);root=Path(root);cfg=json.loads(recipe.read_text());logs=root/'logs';logs.mkdir(exist_ok=True)
    if p.exists():raise FileExistsError('Existing/partial runtime prefix refused; no reinstall fallback')
    if sys.platform!='linux':raise ValueError('Linux installer only; portable tests do not admit native binaries')
    packages=root/'runtime-payloads';packages.mkdir(exist_ok=True);conda=packages/'conda';wheels=packages/'wheels';conda.mkdir(exist_ok=True);wheels.mkdir(exist_ok=True)
    def run(argv):
        print('RUNTIME_COMMAND',json.dumps(list(map(str,argv))),flush=True)
        subprocess.run(list(map(str,argv)),check=True,cwd=root,env=os.environ.copy())
    mamba=Path(cfg['micromamba']['path'])
    if binding(mamba)!={k:cfg['micromamba'][k]for k in ['bytes','sha256']}:raise ValueError('Pinned micromamba archive differs')
    tool=root/'tools/bin/micromamba';tool.parent.mkdir(parents=True,exist_ok=True)
    if tool.exists():raise FileExistsError('Fresh installer path required')
    with tarfile.open(mamba)as a:
        member=a.getmember('bin/micromamba')
        if not member.isfile()or member.size>30*1024**2:raise ValueError('Installer archive member differs')
        with tool.open('xb')as out:out.write(a.extractfile(member).read())
    tool.chmod(0o700);run([tool,'--version'])
    rows=cfg['conda'];wheelrows=cfg['wheels'];results={}
    jobs=[('conda/'+x['filename'],x,conda/x['filename'])for x in rows]+[('wheels/'+x['filename'],x,wheels/x['filename'])for x in wheelrows.values()]
    def one(z):key,row,path=z;return key,acquire(row,path)
    with concurrent.futures.ThreadPoolExecutor(max_workers=4)as pool:
        for key,b in pool.map(one,jobs):results[key]=b;print('RUNTIME_PAYLOAD_VERIFIED',key,b['bytes'],flush=True)
    metadata={}
    for name,row in wheelrows.items():
        with zipfile.ZipFile(wheels/row['filename'])as a:
            choices=[z for z in a.namelist()if z.endswith('.dist-info/METADATA')]
            if len(choices)!=1 or a.getinfo(choices[0]).file_size>1024**2:raise ValueError('Wheel METADATA inventory differs')
            text=a.read(choices[0]).decode();msg=email.parser.Parser().parsestr(text)
            if msg['Name'].lower().replace('_','-')!=name or msg['Version']!=row['version']:raise ValueError('Actual wheel identity differs: '+name)
            metadata[name]=dict(version=msg['Version'],requires_python=msg['Requires-Python'],requires_dist=msg.get_all('Requires-Dist',[]),metadata_sha256=hashlib.sha256(text.encode()).hexdigest())
    write_json(root/'wheel-native-metadata.json',metadata)
    explicit=root/'python-explicit.txt';explicit.write_text('@EXPLICIT\n'+'\n'.join(str((conda/x['filename']).absolute().as_uri())+'#'+x['md5']for x in rows)+'\n')
    run([tool,'--no-rc','--root-prefix',root/'mamba','create','-y','--offline','-p',p,'--file',explicit])
    py=p/'bin/python';run([py,'-I','-B','-c','import ssl,sys;assert sys.version_info[:3]==(3,10,15);print(sys.version,ssl.OPENSSL_VERSION)'])
    requirements=root/'runtime-requirements.txt';requirements.write_text('\n'.join(name+'=='+row['version']+' --hash=sha256:'+row['sha256']for name,row in sorted(wheelrows.items()))+'\n')
    run([py,'-I','-B','-m','pip','--isolated','install','--no-index','--find-links',wheels,'--require-hashes','-r',requirements])
    wheel=Path(cfg['project_wheel']['path'])
    if binding(wheel)!={k:cfg['project_wheel'][k]for k in ['bytes','sha256']}:raise ValueError('Frozen dev8 wheel differs')
    run([py,'-I','-B','-m','pip','--isolated','install','--no-index','--no-deps',wheel]);run([py,'-I','-B','-m','pip','check']);run([p/'bin/dl-binner','--help'])
    write_json(root/'runtime-installed.json',dict(status='INSTALLED_NOT_NATIVE_GATE_ADMITTED',prefix=str(p),python=str(py),recipe=binding(recipe),payloads=results,wheel_metadata=binding(root/'wheel-native-metadata.json'),project_wheel=binding(wheel)))
    print('RUNTIME_INSTALLED_COMPLETE_OWNED',p,flush=True)

if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--recipe',type=Path,required=True);a.add_argument('--prefix',type=Path,required=True);a.add_argument('--root',type=Path,required=True);v=a.parse_args();install(v.recipe,v.prefix,v.root)
