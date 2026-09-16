# HY300 Pro Allwinner H713 FEL & BootROM Research

## 1. Overview
This directory contains low-level hardware reverse engineering and bring-up documentation for the Allwinner H713 SoC (`sun50iw12p1`). Research focuses on the on-chip BootROM (BROM), USB FEL recovery protocol (`1f3a:efe8`), SRAM memory mapping, and DDR3 DRAM bring-up using `sunxi-tools` with H713 support.

## 2. Documentation Index

| Document | Focus Area | Key Topics |
| --- | --- | --- |
| **[FEL_RESEARCH.md](FEL_RESEARCH.md)** | BROM Analysis & FEL Bring-Up | Consolidated reference: 40KB BROM memory map, boot flow sequence, SRAM `0x0010C000` resolution, H713 support in `sunxi-tools` ([YuujiLab/sunxi-tools](https://github.com/YuujiLab/sunxi-tools)), 1024MB DDR3 initialization, and direct U-Boot execution |

## 3. Architecture Summary
- **BootROM Size:** 40,960 bytes (`0xA000`), mirrored at `0x00000000` and `0x4A000000`
- **FEL Payload Destination:** SRAM A2 at `0x0010C000` (`fes1.fex`)
- **DRAM Parameters:** 1024 MB DDR3 @ 624 MHz (`0x40000000`)
- **USB Interface:** USB 2.0 High-Speed Bulk Endpoint (`VID:PID 1f3a:efe8`)

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
