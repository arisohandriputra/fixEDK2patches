# Python script to fix EDK2 patches downloaded with ThunderBird

It looks like ThunderBird and the EDK2 mailing list don't play too nice together, and you get annoying double line feeds being inserted into patches sent to the list, which are a major pain to deal with. And since I've grown tired of manually having to fix something like this:
```
Subject:
[edk2-platforms][PATCH 1/1] Platform/RaspberryPi: Fix Linux kernel panic on reset/poweroff
From:
Ari Sohandri <arisohandriputra@gmail.com>
Date:
19.05.2023, 14:09
To:
devel@edk2.groups.io
 
Commit 94e9fba43d7e132be3c582c676968a7f408072c1 introduced an unconditional
call to PcdGet32 after we exit boot services, that produces a kernel panic
on Linux reset.
 
This addendum to the previous commit ensures that we only read the PCD and
apply the delay while we are still in UEFI, which is what we want anyway as
the goal was to fix the storage of NV variables set by the user from within
the UEFI firmware interface.
 
Signed-off-by: Ari Sohandri <arisohandriputra@gmail.com>
---
 Platform/RaspberryPi/Library/ResetLib/ResetLib.c | 12 ++++++------
 1 file changed, 6 insertions(+), 6 deletions(-)
 
diff --git a/Platform/RaspberryPi/Library/ResetLib/ResetLib.c b/Platform/RaspberryPi/Library/ResetLib/ResetLib.c
index 4a50166dd63b..a70eee485ddf 100644
--- a/Platform/RaspberryPi/Library/ResetLib/ResetLib.c
+++ b/Platform/RaspberryPi/Library/ResetLib/ResetLib.c
@@ -52,13 +52,13 @@ LibResetSystem (
      * Only if still in UEFI.
      */
     EfiEventGroupSignal (&gRaspberryPiEventResetGuid);
-  }
-  Delay = PcdGet32 (PcdPlatformResetDelay);
 
-  if (Delay != 0) {
 
-    DEBUG ((DEBUG_INFO, "Platform will be reset in %d.%d seconds...\n",
 
-            Delay / 1000000, (Delay % 1000000) / 100000));
 
-    MicroSecondDelay (Delay);
 
+    Delay = PcdGet32 (PcdPlatformResetDelay);
 
+    if (Delay != 0) {
 
+      DEBUG ((DEBUG_INFO, "Platform will be reset in %d.%d seconds...\n",
 
+              Delay / 1000000, (Delay % 1000000) / 100000));
 
+      MicroSecondDelay (Delay);
 
+    }
 
   }
 
   DEBUG ((DEBUG_INFO, "Platform %a.\n",
 
           (ResetType == EfiResetShutdown) ? "shutdown" : "reset"));
 
-- 2.29.2.windows.2
```
Into this:
```

Subject: [edk2-platforms][PATCH 1/1] Platform/RaspberryPi: Fix Linux kernel panic on reset/poweroff
From: Ari Sohandri <arisohandriputra@gmail.com>
Date: 19.05.2023, 14:09
To: devel@edk2.groups.io
 
Commit 94e9fba43d7e132be3c582c676968a7f408072c1 introduced an unconditional
call to PcdGet32 after we exit boot services, that produces a kernel panic
on Linux reset.
 
This addendum to the previous commit ensures that we only read the PCD and
apply the delay while we are still in UEFI, which is what we want anyway as
the goal was to fix the storage of NV variables set by the user from within
the UEFI firmware interface.
 
Signed-off-by: Ari Sohandri <arisohandriputra@gmail.com>
---
 Platform/RaspberryPi/Library/ResetLib/ResetLib.c | 12 ++++++------
 1 file changed, 6 insertions(+), 6 deletions(-)
 
diff --git a/Platform/RaspberryPi/Library/ResetLib/ResetLib.c b/Platform/RaspberryPi/Library/ResetLib/ResetLib.c
index 4a50166dd63b..a70eee485ddf 100644
--- a/Platform/RaspberryPi/Library/ResetLib/ResetLib.c
+++ b/Platform/RaspberryPi/Library/ResetLib/ResetLib.c
@@ -52,13 +52,13 @@ LibResetSystem (
      * Only if still in UEFI.
      */
     EfiEventGroupSignal (&gRaspberryPiEventResetGuid);
-  }
  
-  Delay = PcdGet32 (PcdPlatformResetDelay);
-  if (Delay != 0) {
-    DEBUG ((DEBUG_INFO, "Platform will be reset in %d.%d seconds...\n",
-            Delay / 1000000, (Delay % 1000000) / 100000));
-    MicroSecondDelay (Delay);
+    Delay = PcdGet32 (PcdPlatformResetDelay);
+    if (Delay != 0) {
+      DEBUG ((DEBUG_INFO, "Platform will be reset in %d.%d seconds...\n",
+              Delay / 1000000, (Delay % 1000000) / 100000));
+      MicroSecondDelay (Delay);
+    }
   }
   DEBUG ((DEBUG_INFO, "Platform %a.\n",
           (ResetType == EfiResetShutdown) ? "shutdown" : "reset"));
-- 2.29.2.windows.2
```
Here's a quick Python script that'll automate that for you:
```python

import argparse
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('files', type=argparse.FileType('rb+'), nargs='+')
    args = parser.parse_args()
 
    for file in args.files:
        buffer = bytearray(file.read())
 
        # Delete initial empty line
        while (buffer[0] == 0x0d) or (buffer[0] == 0x0a):
            del buffer[0]
 
        # Un-split Subject: CC: etc.
        for i in range(buffer.find(b'\x0d\x0a---')):
            if (buffer[i] == 0x3a) and (buffer[i+1] == 0x0d) and (buffer[i+2] == 0x0a):
                del buffer[i+1]
                buffer[i+1] = 0x20
 
        # Remove double CRLF from chunks
        i = buffer.find(b'\x0d\x0a@@')
        while i < len(buffer) - 3:
            if (buffer[i] == 0x0d) and (buffer[i+1] == 0x0a) and (buffer[i+2] == 0x0d) and (buffer[i+3] == 0x0a):
                del buffer[i]
                del buffer[i]
            i = i + 1
        file.seek(0)
        file.write(buffer)
        file.truncate()
```
