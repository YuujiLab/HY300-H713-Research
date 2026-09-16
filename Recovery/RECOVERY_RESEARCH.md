# HY300 Pro Recovery Exploit & Legacy OTA Bypass Research

## 1. Overview
This document details an exploit chain developed for the HY300 / HY300 Pro projector (Allwinner H713 SoC, Android 11). The exploit bypasses modern Android Virtual A/B recovery requirements (`payload.bin` enforcement) by binary patching the stock recovery executable, forcing fallback to legacy Edify script execution (`update-binary`) to inject persistent root privileges into dynamic partitions.

## 2. Target Environment Specifications
- **Platform:** Allwinner H713 (`sun50iw12p1`)
- **OS Version:** Android 11 (API Level 30)
- **Partition Scheme:** Dynamic Partitions (`super`) with Virtual A/B slots
- **Security Posture:** Production user build (`ro.build.type=user`, `ro.debuggable=0`)

## 3. Exploit Stages & Implementation

### Stage 1: Debug Environment Preparation
To establish visibility into the recovery environment, the boot ramdisk was modified via `prop.default`:
- `ro.debuggable=1`: Enables userspace debugging hooks.
- `ro.adb.secure=0`: Disables ADB RSA authentication requirements.
- `service.adb.root=1`: Forces `adbd` to spawn with root UID (0).

Result: Root-level ADB access available immediately upon booting recovery.

### Stage 2: Recovery Binary Patching (Legacy Path Bypass)
Stock Android 11 recovery binaries strictly mandate streaming A/B updates via `payload.bin`. When provided with a traditional ZIP package containing an `update-binary` shell script, `InstallPackage` aborts execution.

Reverse engineering in Ghidra identified the gating condition:
- **Target Binary:** `/system/bin/recovery` (inside recovery ramdisk)
- **Target Function:** `InstallPackage`
- **Memory / File Offset:** `0x00030220`
- **Modification:** The conditional branch enforcing `payload.bin` was replaced with NOP instructions.

Result: The recovery routine falls back to the legacy Edify interpreter, executing arbitrary shell scripts located at `META-INF/com/google/android/update-binary` within signed or unsigned update ZIPs.

### Stage 3: Super Partition Loopback Mapping
The stock recovery ramdisk lacks device-mapper management tools (`dmctl`, `lpmake`, or `lp_setup`), preventing automated mounting of dynamic partitions.

Direct block inspection identified the `system_a` filesystem:
- Block container: `/dev/block/by-name/super` (`mmcblk0p9`)
- Filesystem type: ext4 (magic number `0xEF53`)
- Offset: Exactly 1,048,576 bytes (`1 MB` / `0x100000`)

Manual loopback mount executed in recovery:
```bash
losetup -o 1048576 /dev/block/loop0 /dev/block/by-name/super
mount -t ext4 -o rw /dev/block/loop0 /mnt/real_system
```

### Stage 4: Persistent Root Injection
Because the stock `system_a` filesystem is packed near full capacity, unused vendor assets (such as fallback bootanimations) were purged to reclaim blocks.

Injection parameters:
- **Binary:** Custom `sysu` executable placed at `/mnt/real_system/system/bin/sysu`
- **File Permissions:** `6755` (`rwsr-sr-x` with SetUID and SetGID bits enabled)
- **SELinux Security Context:** `u:object_r:su_exec:s0`

Result: Transitions any calling process directly to root UID 0 with an unconfined SELinux domain in the main Android OS.

## 4. Logical Partition Repacking Reference (`lpmake` & `build_super.py`)
When modifying dynamic partitions offline (such as replacing `system_a.img` with a patched build or a GSI), the physical `super` container must be rebuilt.

### Automated Repacking Helper (`build_super.py`)
To avoid manual byte calculations and syntax errors, use the included helper script [`build_super.py`](build_super.py):

1. Place your partition images (`system_a.img`, `vendor_a.img`, `product_a.img`, etc.) in the same folder as the script.
2. Execute the helper script:
   ```bash
   python build_super.py
   ```
3. The script inspects the exact byte size of each partition image and prints the complete, properly formatted `lpmake` command:
   - Configures the 2GB container device (`super:2147483648`).
   - Allocates the dynamic partition groups (`sb_a` / `sb_b` at `2,139,095,040` bytes).
   - Generates the exact partition definitions, image mappings, and `--sparse` flag targeting `super_new.img`.

### Manual `lpmake` Command Structure
For manual rebuilding, the underlying `lpmake` parameters for the HY300 platform are:

```bash
lpmake \
  --metadata-size 65536 \
  --super-name super \
  --metadata-slots 3 \
  --device super:2147483648 \
  --group sb_a:2139095040 \
  --partition system_a:readonly:974348288:sb_a \
  --image system_a=system_a.img \
  --sparse \
  -o super_new.img
```

## 5. Summary Findings
- Stock recovery enforcement of `payload.bin` can be bypassed with a single conditional branch patch at `0x00030220`.
- The `system_a` filesystem can be directly mounted via loopback at offset `1048576` on `/dev/block/by-name/super`.
- Root persistence is achieved by injecting `sysu` with `6755` permissions and `u:object_r:su_exec:s0` SELinux context.
- Updates can be executed headlessly via `/cache/recovery/command`.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
