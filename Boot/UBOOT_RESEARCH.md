# HY300 Pro U-Boot Reverse Engineering Research

## 1. Overview
This document outlines the reverse engineering findings for the U-Boot bootloader extracted from the Allwinner H713 firmware (`sun50iw12p1`). The investigation focuses on binary architecture, command registration, environment script execution, and safe recovery strategies.

## 2. Binary Architecture & Ghidra Analysis
The extracted U-Boot binary was analyzed in Ghidra (ARMv7 32-bit little-endian configuration):

- **Detected Functions:** Approximately 1,376 functions identified across the binary.
- **Complexity Hotspots:** The largest routine corresponds to the SHA-256 compression algorithm used for image verification and hash checks.
- **Command Registration Architecture:** 
  - Many command strings and handlers lack direct call references (`xrefs`).
  - U-Boot uses macro-driven command tables (`U_BOOT_CMD`) placed in dedicated linker sections.
  - At runtime, commands are resolved by scanning the linker table rather than explicit static calls.
  - The absence of direct cross-references to a string does not indicate dead code.

## 3. Environment-Based Control Flow
Boot execution is driven by scripting in the `env` partition (`env.fex`), rather than compiled-in logic.

Key parameters observed in stock environment:
- `bootcmd`: Main execution script executed after the autoboot countdown expires (`run setargs_nand boot_normal`).
- `boot_normal`: Loads the `boot` partition into RAM address `0x45000000` and invokes `bootm`.
- `boot_recovery`: Loads the `recovery` partition into RAM address `0x45000000` and executes `bootm`.

Because the boot flow relies on environment parsing, custom fallback behavior (such as `bootlimit` and `altbootcmd`) can be introduced directly through environment manipulation without modifying the binary.

## 4. Safety & Recovery Strategy
Modifying bootloaders carries brick risk. A multi-tiered safety model was evaluated:

1. **Boot Ramdisk Modification (Lowest Risk):** Modifying `prop.default` and scripts inside the Android boot ramdisk. This executes in early userspace while leaving the bootloader intact.
2. **U-Boot Binary Patching (High Risk):** Modifying machine instructions in the bootloader executable. This should only be attempted when hardware unbricking (FEL mode or UART console access) is fully verified.

## 5. Summary Findings
- U-Boot is largely dynamic and script-driven via `env.fex`.
- Command dispatch relies on linker-placed structs, requiring memory-table inspection during reverse engineering.
- Environment modifications offer a safe vector for testing alternative boot sequences prior to any binary patching.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
