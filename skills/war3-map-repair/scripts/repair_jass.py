"""Audit legacy JASS or apply an explicit, verified migration profile to a new map."""
import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from jass_compat import audit, repair, PROFILE


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('map',type=Path)
    p.add_argument('--profile',choices=[PROFILE])
    p.add_argument('--output',type=Path)
    p.add_argument('--pjass',type=Path)
    p.add_argument('--common',type=Path)
    p.add_argument('--blizzard',type=Path)
    a=p.parse_args()
    if bool(a.output)!=bool(a.profile):p.error('--profile and --output must be specified together')
    compiler_args=[a.pjass,a.common,a.blizzard]
    if any(compiler_args) and not all(compiler_args):p.error('Compiler checks require --pjass, --common and --blizzard together')
    src=a.map.resolve();source_hash=sha(src)
    if a.output:
        dst=a.output.resolve();reportpath=dst.with_suffix(dst.suffix+'.report.json')
        if dst==src or dst.exists() or reportpath.exists():p.error('Refusing to overwrite input or existing output/report')
    from storm import Archive
    with Archive(src) as archive:
        scripts=[(n,archive.read(n)) for n in ['war3map.j','scripts\\war3map.j']]
        scripts=[(n,data) for n,data in scripts if data is not None]
        if len(scripts)!=1:raise ValueError('Expected exactly one JASS entry; ambiguous or absent script requires manual review')
        if archive.read('war3map.lua') is not None:raise ValueError('Lua/JASS ambiguity requires manual review')
    name,raw=scripts[0]
    report={'source_sha256':source_hash,'script_entry':name,**audit(raw)}
    payload=raw
    if a.profile:
        payload,details=repair(raw);report['migration']=details
    if a.pjass:
        with tempfile.TemporaryDirectory(prefix='war3-jass-check-') as folder:
            script=Path(folder)/'war3map.j';script.write_bytes(payload)
            result=subprocess.run([str(a.pjass.resolve()),str(a.common.resolve()),str(a.blizzard.resolve()),str(script)],capture_output=True,timeout=120)
            report['compiler']={'exit_code':result.returncode,'tool_sha256':sha(a.pjass),'common_sha256':sha(a.common),'blizzard_sha256':sha(a.blizzard)}
            if result.returncode:
                print((result.stdout+result.stderr).decode('utf8',errors='replace'))
                raise ValueError('Offline compiler rejected script; no output created')
    if not a.output:
        print(json.dumps(report,ensure_ascii=False,indent=2));return
    dst.parent.mkdir(parents=True,exist_ok=True)
    with src.open('rb') as source,dst.open('xb') as target:shutil.copyfileobj(source,target)
    report['static_validation']='incomplete; do not use output'
    reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
    with Archive(dst,write=True) as archive:archive.add(name,payload)
    with Archive(dst) as archive:
        if archive.read(name)!=payload:raise ValueError('Script read-back mismatch')
    from archive_check import verify
    report['unchanged_original_blocks']=verify(src,dst,[name])
    if sha(src)!=source_hash:raise ValueError('Input changed during operation')
    report['output_sha256']=sha(dst)
    report['static_validation']='passed: script read-back and non-script original block preservation'
    reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
