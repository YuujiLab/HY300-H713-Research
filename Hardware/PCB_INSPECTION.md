# HY300 Pro PCB Inspection & Hardware Components

## 1. Overview
This document catalogs the integrated circuits, debug headers, and hardware interfaces identified during physical board inspection and teardown of the HY300 / HY300 Pro projector. 

### Mainboard Identification
- **PCB Silkscreen Marking:** `HY200_QZ713DF_A1`
- **PCB Date Code:** `20250304` (March 4, 2025)
- **Factory Tracking Sticker:** `CGDD011425-HY200F 25-08-08A`
- **Configuration String:** `DW1G+8G+20800D4` (1GB RAM + 8GB eMMC + AIC8800D4 Wi-Fi 6)

## 2. Integrated Circuits & Core Silicon

| Component Class | Part Number / IC Markings | Manufacturer | Technical Specifications | Reference Photo |
| --- | --- | --- | --- | --- |
| **System-on-Chip (SoC)** | `Allwinner H713`<br>`R4150DA 25F1` | Allwinner Technology | Quad-core ARM Cortex-A53 CPU, ARM Mali-G31 MP2 GPU, 24.000 MHz crystal | [upside.jpg](pictures/upside.jpg) |
| **DDR3 RAM (Top Side)** | `J2108BCSE-DJ-F`<br>(2x 2Gb ICs) | Elpida / Micron | 2Gb (256MB) DDR3 SDRAM each, FBGA package (512MB total top) | [elpida_j2108bcse_ddr3_ram.jpg](pictures/elpida_j2108bcse_ddr3_ram.jpg) |
| **DDR3 RAM (Bottom Side)** | `K4B2G0846D-HCK0`<br>`SEC 216 / SEC 316`<br>(2x 2Gb ICs) | Samsung | 2Gb (256MB) DDR3-1600 SDRAM each, FBGA package (512MB total bottom) | [samsung_k4b2g0846_ddr3_ram.jpg](pictures/samsung_k4b2g0846_ddr3_ram.jpg) |
| **Non-Volatile Storage (eMMC)** | `THGBMHG6C1LBAIL`<br>`1844KAE VC7632 CHINA` | Kioxia (Toshiba) | 8GB eMMC 5.1 high-speed NAND flash storage, BGA-153 package | [kioxia_thgbmhg6c1lbail_8gb_emmc.jpg](pictures/kioxia_thgbmhg6c1lbail_8gb_emmc.jpg) |
| **Power Management (PMIC)** | `A8038S`<br>`4143210H` | A-Power / Vendor | Multi-channel buck converter / PMIC with 4x `2R2` power inductors | [a8038s_pmic_power.jpg](pictures/a8038s_pmic_power.jpg) |
| **Wireless & Bluetooth Module** | `AIC8800D40`<br>`2524-2 H8P2M813 FA049L2416` | AicSemi | Wi-Fi 6 (802.11ax, 2.4/5GHz) + Bluetooth 5.4 Dual-Mode, 40.17F MHz crystal | [aic8800d40_wifi6_bt_module.jpg](pictures/aic8800d40_wifi6_bt_module.jpg) |
| **Audio Power Amplifier** | `XA8870C`<br>`HWH952 YBECBA` | XA Semi | Class-D / Class-AB audio power amplifier driving internal speaker | [xa8870c_audio.jpg](pictures/xa8870c_audio.jpg) |

> **RAM Architecture Note:** The 1024 MB (1GB) DDR3 RAM capacity is achieved using a quad-die configuration of 4 discrete 2Gb (256MB) chips: 2x Elpida ICs on the component side and 2x Samsung ICs on the reverse side.

## 3. Peripheral Headers & Connectors

| Marking / Label | Connector Type | Subsystem / Function |
| --- | --- | --- |
| `HDMI` | HDMI Type-A Female | External video input to SoC receiver |
| `USB` | USB 2.0 Type-A Female | Host peripherals, ADB debugging, and FEL mode |
| `SPK` | 2-pin JST Header | Internal speaker output driven by XA8870C audio amp |
| `FAN` | 3-pin / 4-pin Header | Active cooling blower fan (PWM regulated) |
| `MOTO` | Multi-pin Header | Motorized optical focus stepper motor (Unpopulated) |
| `CAM` | FFC Header | Calibration camera / optical sensor for auto-keystone (Unpopulated) |
| `LED-` | 2-pin High-Current Terminal | High-power projection LED lamp harness |
| `IR` | 3-pin Header | Infrared remote control receiver module |
| `ANT` | U.FL / IPEX Coaxial | Wi-Fi 6 / Bluetooth RF antenna interconnect |
| `LCD / Display` | 40-pin FFC Receptacle | Digital MIPI/LVDS interface to LCD projection engine |

## 4. Hardware Debug Test Points
- **UART Serial (`TX` / `RX`):** Dedicated circular test pads adjacent to the SoC and heatsink (3.3V logic level, 115,200 baud). Connect Board TX -> Adapter RX, and Board RX -> Adapter TX.
- **Ground (`GND`):** Does not require a dedicated pad; can be soldered to any board ground plane or directly to the outer metal casing of the **USB port** or **HDMI receptacle**.
- **`POWERON`:** Hardware test point for power controller sequencing.
- **`UBOOT` / FEL Button:** Hardware recovery switch / test pad located beneath the HDMI port area that forces BootROM recovery (FEL mode) when held during power-on.

Annotated UART test pad locations are shown in [marked_uart_pads.jpg](marked_uart_pads.jpg).

## 5. Teardown Photo Archive
High-resolution macro photographs of the board and silicon are available in the [`pictures/`](pictures/) directory:
- [upside.jpg](pictures/upside.jpg): Board top view (Allwinner H713, Elpida RAM, HDMI, USB, LCD connector)
- [downside.jpg](pictures/downside.jpg): Board bottom view (Samsung RAM, Kioxia eMMC, A8038S PMIC, AIC8800D40 module, XA8870C amp)
- [tag.jpg](pictures/tag.jpg): Factory label sticker and board identification

## 6. Summary Findings
- The board uses a dual-sided DDR3 design pairing 2x Elpida and 2x Samsung 256MB chips to total 1024MB.
- Storage is provided by an 8GB Kioxia/Toshiba `THGBMHG6C1LBAIL` eMMC 5.1 IC.
- Power regulation is managed by an `A8038S` multi-phase PMIC with 4x `2R2` inductors.
- Audio is driven by an `XA8870C` power amplifier connected to the `SPK` header.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
