# HY300 Pro Hardware Research & Debug Interfaces

## 1. Overview
This directory contains teardown analysis, silicon specifications, component mappings, and debug interface research for the HY300 / HY300 Pro projector mainboard (Allwinner H713 SoC).

## 2. Documentation Index

| Document | Focus Area | Key Topics |
| --- | --- | --- |
| **[PCB_INSPECTION.md](PCB_INSPECTION.md)** | Board Layout & Silicon | SoC, 1GB DDR3 RAM, 8GB Toshiba eMMC, AIC8800D40 Wi-Fi 6, and annotated PCB test points |
| **[UART_FEL.md](UART_FEL.md)** | Serial & Hardware Debug | 115,200 baud 3.3V UART serial console, interactive U-Boot commands, and hardware FEL trigger |
| **[uart_log.txt](uart_log.txt)** | Serial Console Capture | Raw captured interactive terminal session dump from live U-Boot bootloader |

## 3. Core Hardware Specifications Summary
- **SoC:** Allwinner H713 (`sun50iw12p1` / TV303 family)
- **CPU:** Quad-Core ARM Cortex-A53
- **GPU:** ARM Mali-G31 MP2
- **RAM:** 1GB DDR3 (4x 2Gb ICs: 2x Elpida J2108BCSE top + 2x Samsung K4B2G0846D bottom)
- **Storage:** 8GB Kioxia / Toshiba eMMC 5.1 (`THGBMHG6C1LBAIL`)
- **PMIC:** A8038S multi-channel power management controller
- **Audio Amp:** XA8870C Class-D/AB audio amplifier
- **Wireless:** AIC8800D40 (Wi-Fi 6 802.11ax + Bluetooth 5.4 Dual-Mode)
- **Serial Debug:** 3.3V TTL UART (`115200 8-N-1`)

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
