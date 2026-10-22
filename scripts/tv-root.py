#!/usr/bin/env python3
"""AU8000 runtime-discovery adapter; preserve upstream root and cleanup checks."""
import sys,pathlib,asyncio,os,json
root=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools/samsung-tv-root/src'))
os.environ['SDB']=os.environ['TIZEN_SDB']
from samsung_tv_root import archive_root
capture=archive_root._capture
def capture_legacy(client,command,timeout=15):
 if command=='/usr/bin/dotnet --list-runtimes':
  verified=capture(client,'test -f /usr/share/dotnet/shared/Microsoft.NETCore.App/3.1.3/libcoreclr.so && test -f /usr/share/dotnet/shared/Microsoft.NETCore.App/3.1.3/System.Private.CoreLib.dll && echo verified-netcore-3.1.3',timeout)
  if verified!='verified-netcore-3.1.3':raise RuntimeError('Runtime files not verified')
  return 'Microsoft.NETCore.App 3.1.3 [/usr/share/dotnet/shared/Microsoft.NETCore.App]'
 return capture(client,command,timeout)
archive_root._capture=capture_legacy
payloads=root/'tools/root-release/samsung-tv-root-0.0.9-linux-x86_64/_internal/payloads/common31'
result=asyncio.run(archive_root.probe(os.environ['TV_HOST'],callback_host=os.environ['TV_CALLBACK_HOST'],sdb_timeout=20,accept_timeout=25,command_timeout=30,commands=tuple(sys.argv[1:]),payloads=payloads))
print(json.dumps(result,indent=2))
