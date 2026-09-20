"""Read-only by default; explicit transformations produce a separate candidate."""
import argparse, hashlib, json, shutil
from pathlib import Path
from slk import cells, headers, migrate_models, extend_levels


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('map',type=Path)
    p.add_argument('--output',type=Path)
    p.add_argument('--migrate-models',action='store_true')
    p.add_argument('--extend-levels',action='store_true')
    args=p.parse_args()
    if (args.migrate_models or args.extend_levels) and not args.output:
        p.error('Transformations require --output; input is never overwritten')
    if args.output and not (args.migrate_models or args.extend_levels):
        p.error('--output requires an explicit transformation')
    src=args.map.resolve()
    if args.output:
        dst=args.output.resolve();reportpath=dst.with_suffix(dst.suffix+'.report.json')
        if dst==src or dst.exists() or reportpath.exists():
            p.error('Output map/report already exists or aliases input; choose a fresh path')
    from storm import Archive
    source_hash=digest(src)
    report={'source_sha256':source_hash,'tables':{},'changes':{},'runtime':'unverified'}
    changes={}
    with Archive(src) as ar:
        for table,skin in [('UnitUI.slk','UnitSkin.txt'),('ItemData.slk','ItemSkin.txt')]:
            key='Units\\'+table; sk='Units\\'+skin
            data=ar.read(key);oldskin=ar.read(sk)
            h=headers(cells(data)) if data else {}
            report['tables'][table]={'present':data is not None,'legacy_file_column':'file' in h,'existing_skin':oldskin is not None}
            if args.migrate_models and 'file' in h:
                new,skinbytes,count=migrate_models(data,oldskin)
                changes[key]=new;changes[sk]=skinbytes
                report['changes'][table]={'migrated_models':count}
        key='Units\\AbilityData.slk';data=ar.read(key)
        h=headers(cells(data)) if data else {}
        report['tables']['AbilityData.slk']={'present':data is not None,'columns':list(h)}
        if args.extend_levels and data:
            new,count=extend_levels(data)
            if count:
                changes[key]=new;report['changes']['AbilityData.slk']={'added_columns':count}
    if not args.output:
        print(json.dumps(report,ensure_ascii=False,indent=2));return
    if not changes:
        raise ValueError('No applicable changes; no output created')
    dst.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive creation protects a pre-existing output even if it appeared after inspection.
    with src.open('rb') as source,dst.open('xb') as target:
        shutil.copyfileobj(source,target)
    report['static_validation']='incomplete; do not use candidate'
    reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
    with Archive(dst,write=True) as ar:
        for name,data in changes.items():ar.add(name,data)
    with Archive(src) as old,Archive(dst) as new:
        for name,data in changes.items():
            if new.read(name)!=data:raise ValueError('Read-back mismatch: '+name)
        for name in ['war3map.j','war3map.lua','war3map.w3i','war3map.w3e','war3map.doo','war3map.w3a','Units\\UnitData.slk','Units\\UnitBalance.slk','Units\\UnitWeapons.slk']:
            if old.read(name)!=new.read(name):raise ValueError('Unrelated file changed: '+name)
    from archive_check import verify
    report['unchanged_original_blocks']=verify(src,dst,changes)
    if digest(src)!=source_hash:raise ValueError('Input changed during operation')
    report['output_sha256']=digest(dst)
    report['static_validation']='passed: changed entries read back; original non-allowlisted blocks preserved'
    reportpath.write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
