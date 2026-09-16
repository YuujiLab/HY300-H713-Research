# HY300 Pro Firmware Architecture & Analysis

## 1. Overview
This directory contains technical documentation, storage layout specifications, and analysis of the Android 11 production firmware running on the HY300 / HY300 Pro projector (Allwinner H713 SoC, `sun50iw12p1`).

## 2. Documentation Index

| Document | Focus Area | Key Topics |
| --- | --- | --- |
| **[PARTITION_LAYOUT.md](PARTITION_LAYOUT.md)** | Partition Hierarchy | Complete 26-partition GPT map, Virtual A/B architecture (Slot A functional, Slot B fake/zeros), dynamic `super` volumes, and runtime mounts |
| **[SYSTEM_ANALYSIS.md](SYSTEM_ANALYSIS.md)** | System & Security Analysis | Android 11 build properties, engineering binaries, permissive SELinux, and `/system/bin/wifi` UART SUID root helper |
| **[EMMC_DUMPING.md](EMMC_DUMPING.md)** | Extraction Procedures | Unprivileged ADB dumping (no root required), full 7.8GB raw disk extraction, GPT validation, and partition carving |

## 3. Platform Architecture Summary
- **SoC:** Allwinner H713 (`sun50iw12p1`)
- **CPU Architecture:** Quad-core ARM Cortex-A53
- **Kernel:** Linux 4.9.170 (ARM64 Kernel)
- **Userspace:** Android 11 (32-bit `armeabi-v7a`)
- **Storage:** 8GB Toshiba eMMC (`mmcblk0`)
- **Partition Scheme:** Virtual A/B GPT (Slot A active, Slot B zero-filled placeholders)
- **System Partitions:** Logical device-mapper volumes contained in `super`

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
