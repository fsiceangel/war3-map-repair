import ctypes as C
import os, tempfile
from pathlib import Path
D=C.WinDLL(os.environ['STORMLIB_DLL'],use_last_error=True)
H=C.c_void_p; U=C.c_uint32; P=C.c_char_p

def bind(name,args,ret=C.c_bool):
 f=getattr(D,name);f.argtypes=args;f.restype=ret;return f
open_archive=bind('SFileOpenArchive',[C.c_wchar_p,U,U,C.POINTER(H)])
close_archive=bind('SFileCloseArchive',[H])
open_file=bind('SFileOpenFileEx',[H,P,U,C.POINTER(H)])
close_file=bind('SFileCloseFile',[H])
get_size=bind('SFileGetFileSize',[H,C.POINTER(U)],U)
read_file=bind('SFileReadFile',[H,H,U,C.POINTER(U),H])
add_file=bind('SFileAddFileEx',[H,C.c_wchar_p,P,U,U,U])
flush=bind('SFileFlushArchive',[H])
class Archive:
 def __init__(self,path,write=False):
  self.h=H(); self.path=Path(path).resolve()
  if not open_archive(str(self.path),0,0 if write else 0x100,C.byref(self.h)):raise C.WinError(C.get_last_error())
 def read(self,name):
  h=H()
  if not open_file(self.h,name.encode('latin1'),0,C.byref(h)):
   if C.get_last_error()==2:return None
   raise C.WinError(C.get_last_error())
  try:
   size=get_size(h,None);buf=C.create_string_buffer(size);n=U()
   if not read_file(h,buf,size,C.byref(n),None):raise C.WinError(C.get_last_error())
   assert n.value==size;return buf.raw
  finally:close_file(h)
 def add(self,name,data):
  with tempfile.TemporaryDirectory(prefix='war3-repair-') as folder:
   tmp=Path(folder)/'payload.bin';tmp.write_bytes(data)
   if not add_file(self.h,str(tmp.resolve()),name.encode('latin1'),0x80000200,2,2):raise C.WinError(C.get_last_error())

 def close(self):
  if self.h:close_archive(self.h);self.h=None
 def __enter__(self):return self
 def __exit__(self,*args):self.close()
