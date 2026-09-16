# HY300 Pro UART Console & FEL Interface Research

## 1. Overview
Low-level serial debugging and hardware recovery on the HY300 / HY300 Pro projector (Allwinner H713 SoC, `sun50iw12p1`) are accessible via physical PCB debug test points. This document outlines the confirmed UART serial console configuration, command capabilities, and hardware FEL recovery procedures.

## 2. Hardware Test Points & Pinout
The serial console pads are located on the mainboard adjacent to the SoC and thermal heatsink:

- **Logic Level:** 3.3V TTL (requires a standard USB-to-UART bridge, e.g., FTDI, CP2102, or CH340)
- **Baud Rate:** 115,200 bps
- **Data Configuration:** 8 Data Bits, No Parity, 1 Stop Bit (8-N-1), Flow Control: None
- **Pin Mapping & Wiring:**
  - **Board `TX` (Transmit):** Connects to USB-UART adapter `RX`.
  - **Board `RX` (Receive):** Connects to USB-UART adapter `TX`.
  - **Ground (`GND`):** Does not require a dedicated pad; can be soldered directly to any exposed ground plane or metal shielding on the board, such as the outer metal housing of the **USB port** or the **HDMI port connector casing**.

*Note: The exact test pad positions are marked on [marked_uart_pads.jpg](marked_uart_pads.jpg).*

## 3. U-Boot Console Session (Confirmed)
Serial interaction was successfully established and verified. Live console access interrupts the autoboot countdown to drop into the interactive U-Boot shell:

- **Bootloader Banner:**
  ```text
  U-Boot 2018.05-00027-ge159793 (Aug 15 2025 - 10:07:31 +0000) Allwinner Technology
  arm-linux-gnueabi-gcc (Linaro GCC 7.2-2017.11) 7.2.1 20171011
  GNU ld (Linaro_Binutils-2017.11) 2.28.2.20170706
  ```
- **Key Commands Available:**
  - `efex`: Instantly reboot into Allwinner FEL USB recovery mode.
  - `fastboot`: Launch the USB Fastboot protocol handler.
  - `printenv` / `setenv` / `saveenv`: Read, modify, and persist U-Boot environment variables.
  - `md` / `mw` / `mm`: Inspect, write, and modify memory and hardware registers directly.
  - `sunxi_flash`: Direct low-level read/write operations against eMMC block partitions.
  - `gpt`: GUID Partition Table management.

A complete console log transcript is archived in [UART Log](uart_log.txt).

## 4. Hardware FEL Mode Entry
FEL mode is the Allwinner BootROM USB flashing interface used for unbricking, low-level memory loading, and factory production:

### Entry Methods
1. **IR Remote Trigger:** Hold **Volume+** during power-on until USB host detects the device.
2. **Hardware Test Point:** Ground the dedicated FEL test pad on the PCB while powering the board.
3. **Software Command:** From the U-Boot serial console, issue `efex` or `sunxi_fel`. From userspace fastbootd, issue `fastboot oem efex`.

### Host USB Detection
When in FEL mode, the SoC registers on the host USB bus:
- **VID / PID:** `1f3a:efe8` (Allwinner Technology sunxi SoC OTG connector in FEL mode)
- **Communication Protocol:** Supported via `sunxi-fel` (see detailed bring-up procedures in `FEL/`).

## 5. Summary Findings
- UART console access is confirmed operational at 115,200 baud (3.3V).
- Interactive U-Boot shell allows live hardware register inspection, environment tuning, and direct partition access.
- Both software (`efex`) and hardware test points reliably trigger BootROM FEL mode (`1f3a:efe8`).

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
