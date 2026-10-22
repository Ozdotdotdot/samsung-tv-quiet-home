using System;
using System.IO;
using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Collections.Generic;

// Owner-scoped package controls for this firmware; no arbitrary command execution.
class OwnerPackageControl {
 static readonly HashSet<string> Allowed = new HashSet<string> {
  "com.samsung.tv.bixbycapsuleviewer", "com.samsung.tv.bixby-prov",
  "com.samsung.tv.bixby-context-client", "com.samsung.tv.mybixby",
  "com.samsung.tv.ondevice-voice", "com.samsung.tv.vif",
  "com.samsung.tv.wakeup-engine-bixby", "com.samsung.tv.wakeup-engine-alexa",
  "com.samsung.tv.alexa-client", "com.samsung.tv.alexa-fullscreen-app",
  "com.samsung.tv.voiceassistant-music", "com.samsung.tv.cnvoice-assistant",
  "org.tizen.voice-app", "org.tizen.voice-app-service", "org.tizen.voice-client",
  "com.samsung.tv.targeted-ad-service", "com.samsung.tv.pisa-service",
  "com.samsung.tv.adagent-service", "org.tizen.pisa-control-service",
  "com.samsung.tv.acr", "com.samsung.tv.canalysis-service",
  "com.samsung.tv.vision-data-recognition-service", "com.samsung.tv.contents-recognition-dbmgr",
  "org.tizen.hbbtv", "org.tizen.hbbtv-service", "org.tizen.content-tiles-provider",
  "org.tizen.multi-assistant-service", "com.samsung.tv.utterance-recommender-core",
  "com.samsung.tv.action-planner-service", "com.samsung.tv.fuzzy-search-engine",
  "org.tizen.welcome-mode", "com.samsung.tv.context-aware-service", "com.samsung.tv.context-aware-agent"
 };
 [DllImport("libc.so.6", SetLastError=true)] static extern int setgroups(UIntPtr size, IntPtr groups);
 [DllImport("libc.so.6", SetLastError=true)] static extern int setresgid(uint r,uint e,uint s);
 [DllImport("libc.so.6", SetLastError=true)] static extern int setresuid(uint r,uint e,uint s);
 [DllImport("libc.so.6")] static extern uint getuid();
 [DllImport("libc.so.6")] static extern uint geteuid();
 static int Main(string[] args) {
  try {
   if(args.Length!=2 || (args[0]!="disable" && args[0]!="enable") || !Allowed.Contains(args[1]))
    throw new Exception("Use enable/disable with an explicitly allowed optional app ID");
   if(!File.ReadAllText("/etc/prd_info.ini").Contains("Version=T-KSU2EAKUC-2301.1;"))
    throw new Exception("Unexpected firmware");
   if(getuid()!=0 || geteuid()!=0) throw new Exception("Root parent required to select owner identity");
   if(setgroups(UIntPtr.Zero,IntPtr.Zero)!=0 || setresgid(100,100,100)!=0 || setresuid(5001,5001,5001)!=0)
    throw new Exception("Owner identity switch failed: "+Marshal.GetLastWin32Error());
   if(getuid()!=5001 || geteuid()!=5001) throw new Exception("Owner identity not confirmed");
   Console.WriteLine("Owner package request uid="+getuid()+" euid="+geteuid());
   var start=new ProcessStartInfo("/usr/bin/pkgcmd") { UseShellExecute=false };
   foreach(var a in new[]{args[0]=="disable"?"-D":"-A","-t","app","-n",args[1],"--global"}) start.ArgumentList.Add(a);
   using(var p=Process.Start(start)) {
    if(!p.WaitForExit(20000)) { p.Kill(); throw new Exception("Package command timed out; inspect flags before retrying"); }
    return p.ExitCode;
   }
  } catch(Exception e) { Console.Error.WriteLine(e.Message); return 1; }
 }
}
