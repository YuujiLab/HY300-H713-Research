# HY300 Pro Fastboot & Security Research

## 1. Overview
This document covers the low-level Fastboot architecture, device lock/unlock mechanisms, and security model of the HY300 / HY300 Pro projector based on the Allwinner H713 SoC (`sun50iw12p1`). Reverse engineering was performed on the userspace `fastbootd` binary and the vendor Fastboot HAL (`android.hardware.fastboot@1.0-impl.so`).

## 2. System Specifications
- **SoC:** Allwinner H713 (`sun50iw12p1`)
- **Architecture:** ARM Cortex-A53 (32-bit userspace)
- **OS Version:** Android 11 (API level 30)
- **Partition Scheme:** Dynamic Partitions enabled with Virtual A/B layout (`super` container; Slot A functional, Slot B dummy/zero-filled)
- **Default Kernel Parameters:**
  - `androidboot.vbmeta.device_state=locked`
  - `androidboot.trustchain=false`
  - `androidboot.secure_os_exist=0`
  - `androidboot.selinux=permissive`

## 3. Fastboot Architecture
Fastboot on this platform operates in two distinct tiers:

### Bootloader Fastboot
Low-level fastboot implementation running directly within U-Boot.
- Exposed via USB when triggered by bootloader commands or key sequences.
- Capabilities: Flashing raw physical partitions (`boot_a`, `env_a`, `recovery`). While slot `_b` partitions exist in GPT, they are non-functional zero-filled placeholders in stock firmware; flashing must target `_a`.
- Reports variables: `secure: yes`, `unlocked: no`.
- Integrity enforcement: AVB checks are bypassed by the bootloader; flashing raw partitions succeeds despite the "locked" status.

### Userspace Fastboot (fastbootd)
Android userspace service located within the boot ramdisk at `/system/bin/fastbootd`.
- Started from the recovery environment:
  ```text
  service fastbootd /system/bin/fastbootd
  ```
- Capabilities: Manages dynamic partitions (`system_a`, `vendor_a`, `product_a`) inside the `super` partition container.
- Interfaces directly with the Fastboot HAL (`device/softwinner/common/fastboot/Fastboot.cpp`).

## 4. Reverse Engineering & Binary Patching

### Lock Status Check (`GetDeviceLockStatus`)
In stock firmware, `fastbootd` calls `GetDeviceLockStatus()` before executing partition flash or erase commands. The function parses `/proc/cmdline` searching for `androidboot.verifiedbootstate=orange`. When absent, it returns `1` (locked), blocking flashing operations on logical partitions:
```text
FAILED (remote: 'Command not available on locked devices')
```

### The Binary Patch
Disassembly via Ghidra revealed that `GetDeviceLockStatus()` can be forced to return `0` (unlocked) at function entry using an ARM Thumb instruction pair:

- **Target Binary:** `/system/bin/fastbootd` (inside boot ramdisk)
- **Function:** `GetDeviceLockStatus()`
- **File Offset:** `0x28cc8`
- **Original Opcode:** Conditional parsing logic
- **Patch Opcode (ARM Thumb):** `00 20 70 47` (`MOVS R0, #0` ; `BX LR`)

Once repacked into the boot image ramdisk, `fastboot getvar unlocked` returns `yes`, restoring full flash and erase operations for all dynamic partitions.

## 5. Fastboot HAL & OEM Commands
The vendor HAL library (`android.hardware.fastboot@1.0-impl.so`) registers custom OEM handlers inside `Fastboot::doOemCommand()`:
- `fastboot oem unlock` -> `DoOemUnlock()`
- `fastboot oem lock` -> `DoOemLock()`
- `fastboot oem efex` -> `DoOemEfex()`

### OEM Unlock Logic (`DoOemUnlock`)
The HAL enforces three conditions before executing an official unlock:
1. **FRP Partition Flag:** Reads the last byte (`filesize - 1`) of the FRP partition (`/dev/block/by-name/frp`). With a 512 KB partition, the offset is `0x7FFFF`. If this byte is `1`, unlock ability is granted. If `0`, it returns:
   ```text
   Oem unlock ability is 0. Permission denied for this command
   ```
2. **Secure Storage:** Writes unlock state flags to Allwinner secure storage (`sunxi_secure_object_write`):
   - `fastboot_status_flag` = `"unlocked"`
   - `device_unlock` = `"unlock"`
3. **The Kernel Cmdline Gate:** Calls `GetSecure()`, which searches `/proc/cmdline` for `androidboot.verifiedbootstate`.

> **Critical Note:** The stock bootloader does not pass `androidboot.verifiedbootstate` to the kernel cmdline. As a consequence, `GetSecure()` always evaluates to false, causing `DoOemUnlock()` to exit early with `"The system is normal."`. The official OEM unlock command is effectively dead code on stock firmware.

### OEM Relock Logic (`DoOemLock`)
Writes `fastboot_status_flag = "locked"` to secure storage and executes a wipe of userdata. The FRP partition byte remains unchanged.

### OEM EFEX Command (`fastboot oem efex`)
Executes:
```cpp
SetProperty("sys.powerctl", "reboot,efex");
```
This commands the device to reboot directly into **Allwinner FEL mode** (`USB ID 1f3a:efe8`), providing low-level BootROM access for unbricking and memory operations without physical disassembly.

## 6. Summary Findings
- Android Verified Boot (AVB) enforcement is disabled at the bootloader stage (`androidboot.trustchain=false`).
- Flashing restrictions on logical partitions are enforced entirely by userspace `fastbootd`.
- Applying the 4-byte patch (`00 20 70 47`) at offset `0x28cc8` completely bypasses userspace locks.
- The `fastboot oem efex` command provides reliable software entry to FEL mode.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
