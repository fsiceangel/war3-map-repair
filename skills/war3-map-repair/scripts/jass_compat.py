"""Explicit, fingerprint-gated migration of the verified HLWL A4.6 JASS script.

Not a general return-bug rewriter. Unknown scripts are audited but never patched.
Latin-1 is a reversible byte mapping, not an assumption about map text encoding.
"""
import hashlib
import re

ORIGINAL_SHA256 = '18e56ecaad125d06bf86778307aaf071320184e2add4bf06a074d0c13694b2b4'
FIXED_SHA256 = 'b76bb9571969b0cb4bc424e877e2b488a6e3720b6be938135cbf1a1f67c4ac68'
PROFILE = 'hlwl-a4.6'


def audit(raw):
    digest = hashlib.sha256(raw).hexdigest()
    text = raw.decode('latin1')
    # Strip strings and comments before finding suspicious code patterns.
    code = re.sub(r'"(?:\\.|[^"\\])*"|//[^\r\n]*', '', text)
    casts = re.findall(r'(?m)^function (\w+) takes[^\r\n]* returns \w+\r?\nreturn [^\r\n]+\r?\nreturn (?:0|null)\r?\nendfunction', code)
    names = [n for n in ('GetSpellTargetX', 'GetSpellTargetY') if re.search(r'(?m)^function '+n+r' takes', code)]
    return {'script_sha256': digest, 'supported_profile': PROFILE if digest == ORIGINAL_SHA256 else None,
            'already_repaired': digest == FIXED_SHA256, 'suspected_return_bug_helpers': casts,
            'potential_native_name_collisions': names, 'runtime': 'unverified'}


def repair(raw):
    if hashlib.sha256(raw).hexdigest() != ORIGINAL_SHA256:
        raise ValueError('Unsupported script fingerprint (or already repaired); no heuristic rewrite permitted')
    s=raw.decode('latin1');original=s;nl='\r\n';stats={}
    assert 'HLWLCompat' not in s
    s=s.replace('globals\r\n','globals\r\nhashtable HLWLCompatTable=null\r\n',1)
    def change_body(name,body):
     nonlocal s
     pat=r'(?m)(^function '+re.escape(name)+r' takes[^\r\n]*\r\n).*?^endfunction'
     s,n=re.subn(pat,lambda m:m[1]+body.replace('\n',nl)+nl+'endfunction',s,flags=re.S)
     assert n==1,name
    for name in ['JX','QX']:change_body(name,'return GetHandleId(h)')
    for name,kind in [('KX','Group'),('NX','Location'),('OX','Rect')]:
     change_body(name,f'return Load{kind}Handle(HLWLCompatTable,S2I(LX),StringHash(MX))')
    assert s.count('set A=InitGameCache("YDWE.wav")')==1
    s=s.replace('set A=InitGameCache("YDWE.wav")','set A=InitGameCache("YDWE.wav")'+nl+'set HLWLCompatTable=InitHashtable()')
    # Split nested call arguments without touching quoted strings or rawcodes.
    def args(text):
     out=[];depth=0;start=0;quote=None;escape=False
     for i,c in enumerate(text):
      if quote:
       if escape:escape=False
       elif c=='\\':escape=True
       elif c==quote:quote=None
      elif c in '\"\'':quote=c
      elif c=='(':depth+=1
      elif c==')':depth-=1
      elif c==',' and depth==0:out.append(text[start:i]);start=i+1
     assert depth==0 and quote is None
     return out+[text[start:]]
    types={'GetUnitLoc':'Location','GetSpellTargetLoc':'Location','GetRandomLocInRect':'Location','AX':'Location','RectFromCenterSizeBJ':'Rect','EZ':'Group'}
    # Validate custom producing functions return the intended types.
    for name in ['AX','EZ']:
     assert re.search(r'function '+name+r' takes[^\r\n]* returns '+types[name].lower(),s)
    lines=s.split(nl);changes=[];keytypes={}
    for i,l in enumerate(lines):
     if not l.startswith('call StoreInteger(A,'):continue
     a=args(l[len('call StoreInteger('):-1]);assert len(a)==4
     if not a[3].startswith('JX('):continue
     val=a[3][3:-1];fname=re.match(r'(\w+)\(',val)[1];kind=types[fname]
     assert a[1].startswith('I2S(') and a[1].endswith(')')
     if a[2] in keytypes:assert keytypes[a[2]]==kind
     keytypes[a[2]]=kind
     lines[i]=f'call Save{kind}Handle(HLWLCompatTable,S2I({a[1]}),StringHash({a[2]}),{val})'
     changes.append({'line':i+1,'kind':kind})
    s=nl.join(lines);assert len(changes)==47,len(changes)
    # Every typed read uses a key written by a matching typed store.
    for name,kind in [('KX','Group'),('NX','Location'),('OX','Rect')]:
     for m in re.finditer(r'\b'+name+r'\(',s):
      start=m.end();depth=1;quote=False;i=start
      while depth:
       c=s[i]
       if c=='"':quote=not quote
       if not quote:
        if c=='(':depth+=1
        if c==')':depth-=1
       i+=1
      a=args(s[start:i-1]);assert keytypes[a[1]]==kind,(name,a)
    assert s.count('call FlushStoredMission(A,')==31
    s=s.replace('call FlushStoredMission(A,','call HLWLCompatFlushMission(A,')
    helper='function HLWLCompatFlushMission takes gamecache cache,string mission returns nothing\ncall FlushStoredMission(cache,mission)\ncall FlushChildHashtable(HLWLCompatTable,S2I(mission))\nendfunction\n'.replace('\n',nl)
    s=s.replace('function JX takes',helper+'function JX takes',1)
    s=s.replace('call FlushGameCache(A)','call FlushGameCache(A)'+nl+'call FlushParentHashtable(HLWLCompatTable)')
    # Rename identifiers, preserving quoted strings and comments byte-for-byte.
    token=r'"(?:\\.|[^"\\])*"|//[^\r\n]*|\b[A-Za-z_]\w*\b'
    rename={'GetSpellTargetX':'HLWLCompatSpellTargetX','GetSpellTargetY':'HLWLCompatSpellTargetY'}
    s=re.sub(token,lambda m:rename.get(m[0],m[0]),s)
    assert not re.search(r'return h\r?\nreturn 0',s)
    assert 'return GetStoredInteger(A,LX,MX)' not in s
    assert s.count('call SaveLocationHandle(')==sum(c['kind']=='Location' for c in changes)
    assert s.count('call StoreInteger(A,')==original.count('call StoreInteger(A,')-len(changes)
    # Core entrypoints, initialization and all action functions remain present.
    oldnames=set(re.findall(r'(?m)^function (\w+)',original));newnames=set(re.findall(r'(?m)^function (\w+)',s))
    assert newnames=={rename.get(n,n) for n in oldnames}|{'HLWLCompatFlushMission'}
    patched = s.encode('latin1')
    if hashlib.sha256(patched).hexdigest() != FIXED_SHA256:
        raise ValueError('Migration did not reproduce the verified script; refusing output')
    return patched, {'profile': PROFILE, 'typed_stores': len(changes), 'mission_flushes': 31,
                     'changed_handle_helpers': ['JX', 'QX', 'KX', 'NX', 'OX'],
                     'renamed_helpers': rename, 'output_script_sha256': FIXED_SHA256}
