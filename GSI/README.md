# HY300 Pro Generic System Image (GSI) Research

## 1. Overview
This directory documents experimental deployment of Generic System Images (GSI) on the HY300 / HY300 Pro projector platform (Allwinner H713 SoC). The device features an ARM64 kernel paired with a 32-bit (`armeabi-v7a`) Android 11 userspace.

## 2. Documentation Index

| Document | Focus Area | Key Topics |
| --- | --- | --- |
| **[GSI_DISCOVERIES.md](GSI_DISCOVERIES.md)** | Compatibility Findings | Treble implementation, `UDISK` userdata naming conflict, "Mount-to-Blank" display analysis, and HWC blockers |

## 3. Compatibility Summary
- **Architecture:** ARM32 A/B (VNDK 30)
- **Status:** Experimental / Bootable to ADB
- **Primary Blocker:** Proprietary Allwinner Hardware Composer (`sunxihwc`) timeout during SurfaceFlinger frame commit when `/data` is active.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
