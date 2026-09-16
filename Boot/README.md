# HY300 Pro Boot Process & Security Research

## 1. Overview
This directory contains technical documentation, reverse engineering notes, and modification procedures for the boot chain of the HY300 / HY300 Pro projector (Allwinner H713 SoC, `sun50iw12p1`). Research covers early boot execution, U-Boot environment variables, Fastboot architecture, and visual customization.

## 2. Documentation Index

| Document | Focus Area | Key Topics |
| --- | --- | --- |
| **[BOOT_MODES.md](BOOT_MODES.md)** | Boot Modes & Triggers | IR remote triggers (`Vol+` to FEL, `Home` to Recovery), environment commands |
| **[FASTBOOT_RESEARCH.md](FASTBOOT_RESEARCH.md)** | Fastboot & Security | AVB bypass, `fastbootd` Ghidra binary patch (`0x28cc8`), Fastboot HAL OEM commands |
| **[UBOOT_RESEARCH.md](UBOOT_RESEARCH.md)** | U-Boot Reverse Engineering | Linker command tables, disassembly findings, script-driven boot control |

## 3. Boot Chain Architecture
The device boot flow progresses through the following sequential stages:

1. **BootROM (BROM):** Low-level hardware ROM executing on SoC reset. Supports FEL recovery over USB (`1f3a:efe8`).
2. **SPL (boot0):** Secondary program loader responsible for DRAM initialization and hardware timing setup.
3. **U-Boot:** Main bootloader executing in RAM. Reads `/oem/bootlogo.bmp`, evaluates IR remote triggers, and runs the script defined in `bootcmd`.
4. **Android Kernel (`boot_a`):** Decompresses and initializes hardware drivers and mounts dynamic partitions.
5. **Userspace Init & Services:** Launches Android framework services, including `bootanimation` and the `fastbootd` recovery subservice.

## 4. Reverse Engineering & Binary Modifications
- **Userspace `fastbootd` Lock Bypass:** Ghidra analysis and binary patching details for overriding `GetDeviceLockStatus()` are documented in [FASTBOOT_RESEARCH.md](FASTBOOT_RESEARCH.md).
- **OEM Partition Decoupling:** Visual assets and device branding are decoupled from the boot partition and stored on the writable `/oem` partition (see [OEM Documentation](../OEM/README.md)).

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
