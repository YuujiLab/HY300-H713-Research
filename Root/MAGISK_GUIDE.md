# HY300 Pro Magisk Rooting Guide (Virtual A/B)

## 1. Overview
This procedure details the method for achieving stable root access on the HY300 / HY300 Pro projector (Allwinner H713 SoC, Android 11) using Magisk. 

> [!WARNING]
> **Virtual A/B Slot Warning:** Although the partition table declares dual slots, the device operates on a **Virtual A/B structure where only slot `_a` is functional**. Partitions under slot `_b` (`boot_b`, etc.) are empty dummy partitions filled with zeros (`0x00`). Do not switch slots to `_b`; all modifications and restores must target `boot_a`.

## 2. Prerequisites
- ADB and Fastboot platform-tools configured on host workstation.
- Magisk APK (v24.0 or higher recommended).
- **No external firmware package or prior root required**: The raw eMMC block device `/dev/block/mmcblk0` is world-readable (`0666`), allowing partition dumps directly over unprivileged ADB.

## 3. Step-by-Step Procedure

### Step 1: Verify Active Slot
Query the active A/B slot suffix via ADB:
```bash
adb shell getprop ro.boot.slot_suffix
```
The returned output is `_a`. Target partition is strictly `boot_a`.

### Step 2: Carve Stock `boot_a.img` via ADB (No Root Required)
Individual partition device nodes (`/dev/block/mmcblk0p*` and `/dev/block/by-name/*`) are permission-locked to `root:root (0600)`. However, the raw parent storage block (`/dev/block/mmcblk0`) has world-readable permissions (`0666`), allowing an unprivileged shell (`uid=2000`) to carve out partitions directly.

1. Locate partition 5 (`boot_a`) starting sector and sector count:
   ```bash
   adb shell "cat /sys/block/mmcblk0/mmcblk0p5/start && cat /sys/block/mmcblk0/mmcblk0p5/size"
   ```
*Expected output: Two numbers, representing sector offset (e.g., `205824`) and size (e.g., `131072`).*

2. Carve `boot_a` directly from the raw device to your host machine:
   ```bash
   adb exec-out "dd if=/dev/block/mmcblk0 bs=512 skip=<START> count=<SIZE> status=none" > boot_a.img
   ```
*(Replace `<START>` and `<SIZE>` with the numbers returned in the previous command).*

3. Make an untouched backup copy on your workstation:
   ```bash
   # Windows PowerShell
   Copy-Item .\boot_a.img .\boot_a_stock_backup.img
   # Linux/macOS
   cp boot_a.img boot_a_stock_backup.img
   ```
   
4. Verify image integrity (header must begin with `ANDROID!`):
   ```bash
   # Windows PowerShell
   Format-Hex -Path .\boot_a.img -Count 8
   # Linux/macOS
   head -c 8 boot_a.img
   ```

### Step 3: Patch Boot Image via Magisk App
1. Install Magisk on the projector:
   ```bash
   adb install Magisk.apk
   ```
2. Push the dumped `boot_a.img` to device storage:
   ```bash
   adb push boot_a.img /sdcard/Download/boot_a.img
   ```
3. Open the Magisk app on the projector, select **Install** -> **Select and Patch a File**, and choose `/sdcard/Download/boot_a.img`.
4. Pull the patched image back to your host machine:
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
- Sub-partitions under `/dev/block/mmcblk0p*` are restricted to `0600` (root-only), but the main disk `/dev/block/mmcblk0` is world-readable (`0666`), enabling reliable host carving without existing root or external firmware packages.
- The A/B partition scheme is Virtual A/B with functional data restricted to slot A.
- Recovery and rollbacks must be conducted by flashing the stock `boot_a` backup directly to `boot_a`.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
