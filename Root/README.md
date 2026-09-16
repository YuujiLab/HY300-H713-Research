# HY300 Pro Rooting & Privilege Escalation Research

## 1. Overview
This directory details methods for acquiring and maintaining root privileges on the HY300 / HY300 Pro projector (Allwinner H713 SoC, Android 11). Research covers standard systemless Magisk patching, static backdoor binaries (`sysu`), and analysis of vendor testing binaries.

## 2. Documentation Index

| Document | Focus Area | Key Topics |
| --- | --- | --- |
| **[MAGISK_GUIDE.md](MAGISK_GUIDE.md)** | Magisk Root Guide | No-root boot_a dumping via ADB, Magisk patching, fastboot flashing, and stock restoration |
| **[SYSU.md](SYSU.md)** | Custom Root Binary | Compilation of static ARMv7 `sysu`, permissions (`6755`), and SELinux contexts |
| **[wifi/README.md](wifi/README.md)** | Vendor Root Analysis | Reverse engineering `/system/bin/wifi` SUID binary, UART console root execution, and ADB restrictions |

## 3. Privilege Escalation Methods Summary

- **Method 1: Magisk Boot Patching (Recommended):** Best for general userland rooting. Completely self-contained: `boot_a` is extracted directly over unprivileged ADB without root, patched via Magisk, and flashed via fastboot.
- **Method 2: Static `sysu` Binary:** Best for offline system image injection or custom recovery environments, requiring no background daemons.
- **Method 3: Stock `/system/bin/wifi` Utility:** Vendor-provided factory diagnostic entry point; grants root execution exclusively when run from the hardware UART serial console (drops privileges in standard ADB shell).

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
