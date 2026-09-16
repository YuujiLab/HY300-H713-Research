# Allwinner H713 BootROM Reverse Engineering & USB FEL Bring-Up Research

## 1. Overview
This document consolidates the reverse engineering of the on-chip BootROM (BROM), protocol analysis of the USB FEL recovery mode, adding Allwinner H713 support to `sunxi-tools` (repository: [https://github.com/YuujiLab/sunxi-tools](https://github.com/YuujiLab/sunxi-tools)), and the hardware bring-up of DDR3 RAM (1024 MB @ 624 MHz) with direct U-Boot execution on the Allwinner H713 SoC (`sun50iw12p1` / TV303 architecture).

## 2. Hardware Architecture & Memory Map
Disassembly of `brom_h713.bin` and the PhoenixSuite flasher engine (`usbtool.fex`) established the physical memory layout for the H713 platform:

| Region | Physical Address | Size | Description |
| --- | --- | --- | --- |
| **BROM (Hardware Shadow)** | `0x00000000` / `0x4A000000` | 40 KB (`0xA000`) | Internal BootROM executable image |
| **SRAM A2 Base** | `0x00100000` | ~160 KB | Primary internal static RAM |
| **Boot0 Staging Buffer** | `0x00104000` | 32 KB | SPL load buffer for `eGON.BT0` header verification |
| **BROM IRQ Stack** | `0x00105400` | — | Initialized at reset (`DAT_00000260`) |
| **Stage-1 FEL Target (`fes1.fex`)** | **`0x0010C000`** | **13.6 KB** | **Execution target for stage-1 DRAM init payload** |
| **DRAM Status Structure** | **`0x0010C340`** | 128 B | Status structure (`"DRAM"` ASCII magic + parameters) |
| **BROM SVC Stack** | `0x00121500` | — | Top of BROM stack (`scratchpad` in FEL VER) |
| **USB OTG MMIO** | `0x03000000` - `0x0300B000` | — | USB PHY & line status registers (`[BASE+0xA0]`) |
| **CCU / Watchdog** | `0x020500B8` / `0x02051014` | — | Clock control registers & watchdog reset |
| **SID / eFuses** | `0x03006000` (+ `0x200`) | 2 KB | Hardware chip ID & root keys |
| **DRAM Base** | `0x40000000` | 1024 MB | DDR3 SDRAM (accessible once initialized by `fes1`) |
| **Device Tree (`dtb`) Target** | `0x43000000` | 72 KB | Target staging address for `sunxi.fex` |
| **U-Boot Text Base** | `0x4A000000` | ~624 KB | `u-boot.fex` text load target in DRAM |

*Note: The BROM file is exactly 40,960 bytes (`0xA000`). It executes at `0x00000000` and is shadowed at `0x4A000000`.*

## 3. BootROM (BROM) Disassembly & Flow Analysis

### 3.1 Execution Sequence
The hardware execution sequence progresses as follows:

1. **Reset Vector (`0x00000000`):** Branches immediately to startup initialization at `FUN_00000044`.
2. **Core Setup (`FUN_00000044`):** Configures SVC and IRQ CPU modes, disables caches, and writes CCU register magic `0x16AA0000`.
3. **Hardware FEL Button Test:** Checks register `r6` against `0x5C`.
   - If matched: Branches directly to `FUN_000087dc(0x7F)` (Direct FEL entry).
   - If unmatched: Branches to `FUN_00000b68` (Main Boot Dispatcher).
4. **Main Boot Dispatcher (`FUN_00000b68`):**
   - Enables instruction cache via `MCR SCTLR |= 0x1000` (`FUN_00008b00`).
   - Evaluates security fuses via 4-pass check (`FUN_0000919c`).
5. **Boot Device Priority Ladder:**
   - Evaluates SD Card storage (`FUN_000002ec`).
   - Evaluates NAND / eMMC storage (`FUN_000003e8`).
   - Evaluates SPI Flash storage (`FUN_000004f0`).
   - Evaluates SPI NAND storage (`FUN_00000540`).
6. **Fallback to FEL:**
   - If all boot media fail to validate, branches to `FUN_00000598` / `FUN_00008aa8(0x104000)`.
   - If execution fails, drops into `FUN_000087dc` (FEL Mode).
7. **USB Line Status Check (`FUN_000087ac`):**
   - Enables USB PHY clocks (`0x020000F0`).
   - Reads line status at `USB_BASE+0xA0` via `FUN_00007738`.
   - If line status is `0` (no host active): Jumps to pre-loaded payload at SRAM `0x14000` / `0x0010C000` (`FUN_000092dc`).
   - If line status is non-zero (host active): Enters TrustZone FEL mode via `software_smc(0)` (`FUN_00000238`).

### 3.2 USB Subsystem Configuration
- **Endpoints:**
  - `EP0`: Bidirectional Control (16 bytes FIFO).
  - `EP1-IN`: Host -> Device Bulk (512 bytes FIFO).
  - `EP1-OUT`: Device -> Host Bulk (512 bytes FIFO).
- **USB Identification:** `VID:PID 1f3a:efe8` (Allwinner Technology sunxi SoC OTG connector in FEL mode).

### 3.3 eGON.BT0 Boot Image Header
All storage-loaded boot images utilize the standard eGON header checked at `0x00104000`:
```c
struct eGON_BT0_Header {
    uint32_t jump;          // +0x00: ARM32 branch instruction
    char     magic[8];      // +0x04: "eGON.BT0"
    uint32_t checksum;      // +0x0C: 32-bit word sum (zeroed during verify)
    uint32_t length_bt0;    // +0x10: Total image size (512-byte aligned)
    uint32_t hdr_version;   // +0x14: Header version / sector size
    uint32_t run_addr;      // +0x18: Execution run address
    uint32_t length_bt1;    // +0x1C: BT1-style length field
    uint8_t  boot_cookie;   // +0x20: 0x01 (BT1) or 0x04 (BT0)
    uint8_t  boot_device;   // +0x21: Boot device index
    uint8_t  boot_slot;     // +0x22: A/B slot index
    uint8_t  media_type;    // +0x2B: Flash media type
};
```

### 3.4 Embedded Cryptographic Signature Region
Offsets `0x9510` through `0x9787` in the BROM binary contain an embedded **RSA-2048 public key** evaluated by `FUN_000089a8` for secure boot signature validation.

## 4. FEL Protocol Architecture & PhoenixSuite Analysis

### 4.1 The Legacy Tool Failure Mode
Initial attempts to interact with the H713 using standard Linux `sunxi-tools` failed with USB bulk timeouts:
```text
usb_bulk_send() ERROR -7: Operation timed out
Assertion failed: strcmp(buf, "AWUS") == 0
```
Standard `sunxi-fel` assumed an SRAM base of `0x00010000` or `0x00020000`. Writing to `0x00014000` targeted unmapped address space on the H713, triggering a hardware bus fault that locked the USB endpoint.

### 4.2 Reverse Engineering `usbtool.fex`
Disassembly of PhoenixSuite's flashing executable (`usbtool.fex`) revealed the vendor execution flow:
```text
0x10001343: mov  ecx, dword ptr [edi + 0x20]   ; Loads 0x0010C000 from fes1 header
0x10001358: push 0x1001a630                     ; "down and run fes1 at addr 0x%x"
0x100013ae: call 0x10007710                     ; AW_FEL_1_WRITE to 0x0010C000
0x100013f9: call 0x10006c60                     ; AW_FEL_1_EXEC at 0x0010C000
0x100014b0: push 500ms; call Sleep
0x100011c9: call AW_FEL_1_READ 0x0010C340       ; Reads back DRAM status structure
0x100011ec: cmp  dword ptr [esp], 0x4D415244    ; Validates "DRAM" ASCII magic
```

PhoenixSuite relies on a two-stage bring-up:
1. Stage 1: Pre-loads `fes1.fex` into SRAM at **`0x0010C000`** to initialize clocks and DDR3 DRAM.
2. Stage 2: Once DRAM is mapped at `0x40000000`, loads U-Boot / FES2 into DRAM at **`0x4A000000`** to handle storage flashing.

### 4.3 FEL Request Frame Structure
Commands over USB EP0/EP1 utilize a 16-byte request header:
```c
struct FEL_Request {
    uint8_t  magic[8];      // "AWUS" (standard) or "AWUC" (command)
    uint16_t data_length;   // +0x08: Payload byte count for READ/WRITE
    uint8_t  pad;           // +0x0A: Padding
    uint8_t  cmd;           // +0x0B: Command opcode
    uint32_t address;       // +0x0C: Target memory address (little-endian)
};
```

Common opcodes:
- `0x0001`: `FEL_VER` (Query chip version and scratchpad)
- `0x0002`: `FEL_WRITE` (Write data to memory)
- `0x0003`: `FEL_EXEC` (Execute code at specified address)
- `0x0004`: `FEL_READ` (Read data from memory)

## 5. Allwinner H713 Tooling (`sunxi-tools`)
Support for the Allwinner H713 SoC (`sun50iw12p1`) was added to `sunxi-tools`. The updated repository with H713 support is maintained at:
**[https://github.com/YuujiLab/sunxi-tools](https://github.com/YuujiLab/sunxi-tools)**

Key modifications implemented for H713 support:
1. **SRAM Staging Address:** Configured target memory address mapping for H713 SRAM A2 (`0x0010C000`) instead of legacy sunxi SRAM addresses.
2. **Chip ID & Architecture Definitions:** Added detection for SoC ID `0x1855` (Allwinner H713 / `sun50iw12p1`).
3. **DRAM Handshake Verification:** Implemented handling for stage-1 `fes1.fex` execution and parsing of the 128-byte DRAM status structure at `0x0010C340`.

## 6. Step-by-Step USB Bring-Up & Verification

### 6.1 Bring-Up Commands
Using `sunxi-fel` with H713 support:

```bash
# 1. Query BROM hardware status
sunxi-fel version
# Output: AWUSBFEX soc=00001855(H713) 00000001 ver=0001 04 00 scratchpad=00121500 00000000 00000000

# 2. Upload fes1.fex to the true SRAM staging address
sunxi-fel write 0x0010C000 fes1.fex

# 3. Execute fes1 to initialize DDR3 memory controller
sunxi-fel exec 0x0010C000

# 4. Read back and verify DRAM status (500ms delay)
sunxi-fel read 0x0010C340 16 dram_status.bin

# 5. Upload U-Boot directly to DRAM
sunxi-fel write 0x4A000000 u-boot.fex

# 6. Execute U-Boot
sunxi-fel exec 0x4A000000
```

### 6.2 Hardware Verification Log
Executing the sequence above yielded successful DRAM initialization and bootloader execution via serial console:

```text
HELLO! BOOT0 is starting!
BOOT0 commit : fdc8c33-dirty
set pll start
SET PLL COMPLETE
Init DRAM...
dram_init_pmu
DRAM clk = 624 MHz
DRAM Type = 3 (3:DDR3,4:DDR4,7:LPDDR3,8:LPDDR4)
DRAM total size = 1024 MB
DRAM simple test OK.
dram size = 1024 MB
card 0 line count is 0
DRAM: 1024 MiB
Relocation Offset is: 45778000
CPU:   Allwinner Family
Model: sun50iw12
```

## 7. Ghidra Setup Reference
For reverse engineering BROM and SPL binaries in Ghidra:

- **BROM Segment:** Address `0x00000000` - `0x00009FFF` (40 KB, Read/Execute).
- **SRAM Segment:** Address `0x00100000` - `0x00127FFF` (160 KB, Read/Write/Execute).
- **`fes1.fex` Staging Block:** Add block at `0x0010C000`, size `0x3520` (13,600 bytes), ARM32 Little-Endian.

## 8. Summary Findings
- The Allwinner H713 SRAM execution address is `0x0010C000`, not `0x00014000`.
- Standard `sunxi-fel` fails due to incorrect SRAM address mapping, not protocol encryption.
- Updated `sunxi-tools` with H713 support ([YuujiLab/sunxi-tools](https://github.com/YuujiLab/sunxi-tools)) successfully initializes 1024 MB DDR3 RAM @ 624 MHz via USB.
- U-Boot can be loaded directly into DRAM at `0x4A000000` over FEL without flashing eMMC storage.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
