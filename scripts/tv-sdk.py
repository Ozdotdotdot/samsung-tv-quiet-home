#!/usr/bin/env python3
import sys,json,pathlib,os
root=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'tools/samsung-tv-root/src'))
from samsung_tv_root.sdb import SdbClient
client=SdbClient(pathlib.Path(os.environ['TIZEN_SDB']),os.environ['TV_HOST'],timeout=20)
if __name__=='__main__':
 result=client.capture(sys.argv[1],timeout=30)
 print(result.output)
