# HY300 Pro Magisk Rooting Guide (Virtual A/B)

## 1. Overview
This procedure details the method for achieving stable root access on the HY300 / HY300 Pro projector (Allwinner H713 SoC, Android 11) using Magisk. 

> [!WARNING]
> **Virtual A/B Slot Warning:** Although the partition table declares dual slots, the device operates on a **Virtual A/B structure where only slot `_a` is functional**. Partitions under slot `_b` (`boot_b`, etc.) are empty dummy partitions filled with zeros (`0x00`). Do not switch slots to `_b`; all modifications and restores must target `boot_a`.

## 2. Prerequisites
- ADB and Fastboot platform-tools configured on host workstation.
- Magisk APK (v24.0 or higher recommended).
- **No external firmware package or prior root required**: The stock `boot_a` image can be dumped directly over unprivileged ADB.

## 3. Step-by-Step Procedure

### Step 1: Verify Active Slot
Query the active A/B slot suffix via ADB:
```bash
adb shell getprop ro.boot.slot_suffix
```
The returned output is `_a`. Target partition is strictly `boot_a`.

### Step 2: Extract Stock `boot_a.img` via ADB (No Root Required)
Due to permissive SELinux and open block device read permissions on the Allwinner H713 firmware, standard ADB shell sessions (`uid=2000`) have direct read access to `/dev/block/by-name/`. The `su` command is **not required**.

1. Dump `boot_a` directly to internal device storage:
   ```bash
   adb shell "dd if=/dev/block/by-name/boot_a of=/sdcard/Download/boot_a.img bs=1M"
   ```
2. Pull a backup copy to your host computer for safe recovery:
   ```bash
   adb pull /sdcard/Download/boot_a.img boot_a_stock_backup.img
   ```

### Step 3: Patch Boot Image via Magisk App
1. Install Magisk on the projector:
   ```bash
   adb install Magisk.apk
   ```
2. Open the Magisk app on the projector UI, select **Install** -> **Select and Patch a File**, and choose `/sdcard/Download/boot_a.img`.
3. Once patching finishes, pull the patched boot image to the host:
   ```bash
   adb pull /sdcard/Download/magisk_patched_*.img boot_a_patched.img
   ```

### Step 4: Flash Patched Boot Image via Fastboot
1. Reboot the device into bootloader mode:
   ```bash
   adb reboot bootloader
   ```
2. Verify host communication:
   ```bash
   fastboot devices
   ```
3. Flash the patched image directly to slot `_a`:
   ```bash
   fastboot flash boot_a boot_a_patched.img
   ```
4. Reboot the projector:
   ```bash
   fastboot reboot
   ```

### Step 5: Verification
Verify root execution over ADB shell:
```bash
adb shell
su
id
# Expected output: uid=0(root) gid=0(root) groups=0(root) context=u:r:magisk:s0
```

## 4. Recovery & Fallback
If the device fails to complete boot or experiences a bootloop:
1. Re-enter fastboot mode via serial console or hardware FEL.
2. Restore the untouched factory stock backup created in Step 2:
   ```bash
   fastboot flash boot_a boot_a_stock_backup.img
   fastboot reboot
   ```
> [!CAUTION]
> Do not attempt to recover using `fastboot set_active b` or `fastboot --set-active=b`. Slot B partitions are zero-filled placeholders and cannot boot.

## 5. Summary Findings
- Magisk systemless root functions stably on the Allwinner H713 32-bit userspace / 64-bit kernel environment.
- Unprivileged ADB shell (`uid=2000`) has direct read access to `/dev/block/by-name/boot_a`, eliminating the need for external firmware dumps or pre-existing root to obtain the boot image.
- The A/B partition scheme is Virtual A/B with functional data restricted to slot A.
- Recovery and rollbacks must be conducted by flashing the stock `boot_a` backup directly to `boot_a`.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
