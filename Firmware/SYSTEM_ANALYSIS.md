# HY300 Pro System Firmware & Security Analysis

## 1. Overview
This document details system properties, runtime configuration, and security characteristics of the production Android 11 build running on the HY300 / HY300 Pro projector platform (Allwinner H713 SoC).

## 2. System Identification & Build Properties
Extracted via ADB properties:
- **SoC:** Allwinner H713 (`sun50iw12p1` / `ares` platform)
- **Android Version:** Android 11 (API Level 30)
- **Kernel:** Linux 4.9.170 (ARM64 Kernel)
- **Userspace ABI:** 32-bit (`armeabi-v7a`, `armeabi`)
- **Build Fingerprint:** `Allwinner/h713_tuna_p3/h713-tuna_p3:11/RP1A.201005.006/projector09220931:user/release-keys`
- **Build Type:** `ro.build.type=user`, `ro.debuggable=0`

While signed with release keys and marked as a production user build, the userspace environment retains extensive debugging and engineering facilities.

## 3. Engineering & Debugging Remnants
Inspection of the system image revealed utilities typically stripped from commercial Android production builds:
- **Diagnostics Tools:** `tcpdump`, `iperf`, `memtester`, `lsusb`
- **Kernel Debug Interfaces:** `/sys/kernel/debug` and `/sys/kernel/tracing` mounted and accessible
- **SELinux Enforcement:** Running in **Permissive** mode (`getenforce` returns `Permissive`), meaning SELinux policy violations are logged rather than blocked by the kernel.

## 4. Hidden Vendor Root Helper (`/system/bin/wifi`)
A notable artifact identified in `/system/bin/` is a setuid root binary named `wifi`:

- **Path:** `/system/bin/wifi`
- **Permissions:** `-rwsr-sr-x root root` (`4755` SUID)
- **Help String:**
  ```text
  usage: su [WHO [COMMAND...]]
  ```

### Functional Analysis & Execution Environments
The `wifi` binary is a renamed, modified vendor `su` helper intended for internal factory hardware testing:

- **UART Serial Shell Exclusive:** Root privilege escalation through `/system/bin/wifi` **only succeeds when executed within the hardware UART serial console shell** (`/dev/ttyS0`). Under the UART console, executing `wifi root <command>` runs with `uid=0(root) gid=0(root) euid=0(root)`.
- **ADB Shell Behavior:** When invoked from a standard Android `adb shell` session, the binary explicitly drops privileges, fails to grant UID 0, or drops execution back to unprivileged `uid=2000(shell)`.
- **Runtime Privilege Constraints:**
  1. Interactive shells are blocked via ADB (invoking `wifi root sh` drops immediately back to `uid=2000(shell)`).
  2. The process executes within the confined SELinux domain `u:r:shell:s0`.
  3. Essential Linux POSIX capabilities are stripped at runtime (missing `CAP_SYS_ADMIN`, `CAP_SYS_RAWIO`, `CAP_CHOWN`), preventing direct raw block device manipulation from this helper.

While restricted, this binary confirmed that the vendor included dormant root escalation primitives in the production firmware accessible over hardware serial.

## 5. System Modification & Root Attainment
Because the bootloader does not enforce Android Verified Boot (AVB) integrity checks, the system partition can be modified offline:
1. Extract `system_a` from `super`.
2. Inject a custom `su` binary (`sysu`) with SetUID root permissions (`chmod 6755`).
3. Set the SELinux file context to `u:object_r:su_exec:s0`.
4. Repack and re-flash the partition.

Once flashed, executing `sysu` transitions to root UID 0 with an unconfined SELinux domain, establishing a permanent interactive root shell.

## 6. Summary Findings
- Firmware is a production user build but retains factory debug utilities and permissive SELinux.
- A dormant SUID root binary (`/system/bin/wifi`) exists in `/system/bin/`, but root escalation functions exclusively when run from the hardware UART serial console shell (dropping capabilities in standard ADB).
- Full unconfined root across all interfaces is achievable by injecting `sysu` directly into the dynamic system image or patching the boot image with Magisk.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
