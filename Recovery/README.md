# HY300 Pro Recovery Reverse Engineering & Patches

## 1. Overview
This directory documents reverse engineering of the stock Android 11 recovery binary and exploitation techniques developed for the HY300 / HY300 Pro projector platform (Allwinner H713 SoC). Research focuses on disabling A/B payload enforcement to enable legacy ZIP installations and arbitrary payload injection.

## 2. Documentation & Research Files

| File | Focus Area | Description |
| --- | --- | --- |
| **[RECOVERY_RESEARCH.md](RECOVERY_RESEARCH.md)** | Exploit Chain & Analysis | Reverse engineering `/system/bin/recovery`, `0x00030220` branch patch, super partition loopback mounting, and `sysu` injection |
| **[build_super.py](build_super.py)** | Super Partition Builder | Python utility that inspects extracted partition images and auto-generates the exact `lpmake` command |

## 3. Key Achievements
- **Legacy Path Bypass:** NOP-ed the conditional branch enforcing `payload.bin` inside `/system/bin/recovery`, enabling support for legacy `META-INF/com/google/android/update-binary` scripts.
- **Dynamic Partition Loopback Mapping:** Mapped `system_a` directly from `/dev/block/by-name/super` at offset `1,048,576` (`1 MB`) without requiring device-mapper tools.
- **Root Persistence:** Automated persistent root injection (`sysu`, `6755`, `u:object_r:su_exec:s0`) executed via the standard `/cache/recovery/command` staging pipeline.
- **Automated Repacking:** Simplified `super` dynamic partition generation via `build_super.py`.

## 4. Implementation & Patching
The reverse engineering workflow, binary disassembly analysis, byte-level NOP patch specifications, and dynamic partition repacking workflow are fully documented in **[RECOVERY_RESEARCH.md](RECOVERY_RESEARCH.md)**. Command generation for `lpmake` can be run directly via [`build_super.py`](build_super.py).

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
