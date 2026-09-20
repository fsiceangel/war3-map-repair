"""Conservative transformations of legacy Warcraft III SLK tables."""
import re

def cells(data):
 x=y=0; out={}
 for line in data.decode('latin1').splitlines():
  if not line.startswith('C;'):continue
  parts=re.findall(r'(?:[^;"\r\n]|"(?:[^"]|"")*")+',line)
  k=None
  for p in parts[1:]:
   if p.startswith('X'):x=int(p[1:])
   elif p.startswith('Y'):y=int(p[1:])
   elif p.startswith('K'):k=p[1:]
  if k is not None:
   assert (x,y) not in out,(x,y)
   out[x,y]=k
 return out

def headers(c):return {v.strip('"'):x for (x,y),v in c.items() if y==1}
def serialize(c):
 xmax=max(x for x,y in c);ymax=max(y for x,y in c)
 return ('ID;PWXL;N;E\r\nB;X%d;Y%d;D0\r\n'%(xmax,ymax)+'\r\n'.join('C;X%d;Y%d;K%s'%(x,y,c[x,y]) for x,y in sorted(c,key=lambda p:(p[1],p[0])))+'\r\nE\r\n').encode('latin1')

def migrate_models(data,oldskin):
 c=cells(data);h=headers(c);fx=h.get('file'); id_x=min(h.values())
 if fx is None:return data,oldskin,0
 models=[]
 for y in sorted(set(y for x,y in c if y>1)):
  if (fx,y) in c:
   rawcode=c[id_x,y].strip('"');model=c[fx,y].strip('"')
   if len(rawcode)!=4 or any(ch in model for ch in '\r\n'):
    raise ValueError('Invalid rawcode or multiline model path')
   # Standard model lookup suffix; preserve deliberate invisible/invalid paths.
   if '\\' in model and not re.search(r'\.[a-zA-Z0-9]{2,4}$',model):model+='.mdl'
   models.append((rawcode,model))
 if oldskin is not None:
  raise ValueError('Existing skin file: manual merge required; refusing overwrite')
 skin=('\r\n'.join('[%s]\r\nfile=%s\r\n'%p for p in models)).encode('latin1')
 kept={(x-(x>fx),y):v for (x,y),v in c.items() if x!=fx}
 new=serialize(kept);assert cells(new)==kept
 return new,skin,len(models)

def extend_levels(data):
 c=cells(data);h=headers(c);orig=dict(c);nextx=max(h.values());cols=0
 for base in ['Area','BuffID','Cast','Cool','Cost','DataA','DataB','DataC','DataD','DataE','DataF','DataG','DataH','DataI','Dur','EfctID','HeroDur','Rng','UnitID','targs']:
  if base+'4' not in h:continue
  for lv in [5,6]:
   if base+str(lv) in h:continue
   nextx+=1;cols+=1;c[nextx,1]='"'+base+str(lv)+'"'
   for (x,y),v in orig.items():
    if x==h[base+'4'] and y>1:c[nextx,y]=v
 new=serialize(c);assert cells(new)==c
 for k,v in orig.items():assert c[k]==v
 return new,cols

