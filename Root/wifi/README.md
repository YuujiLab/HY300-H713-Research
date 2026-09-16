# HY300 Pro Hidden Root Binary Analysis (`/system/bin/wifi`)

## 1. Overview
The stock production firmware of the HY300 / HY300 Pro projector contains an undocumented SetUID binary at `/system/bin/wifi`. Reverse engineering indicates this binary is a modified Allwinner vendor `su` implementation used for factory automated testing.

## 2. Binary Properties & Identification
- **Path:** `/system/bin/wifi`
- **Permissions:** `-rwsr-sr-x root root` (`4755` SUID)
- **Usage Banner:**
  ```text
  usage: su [WHO [COMMAND...]]
  ```

## 3. Privilege Escalation & Execution Environment
Privilege escalation via this binary depends strictly on the calling shell session:

### A. UART Serial Console Shell (`/dev/ttyS0`)
Executing commands via the hardware serial console succeeds:
```bash
wifi root <command>
# Executed as: uid=0(root) gid=0(root) euid=0(root)
```
In this environment, vendor diagnostic routines and root-level commands execute directly under root UID 0.

### B. ADB Shell Session
When invoked over a standard Android ADB shell session (`adb shell`):
- **Privilege Dropping:** The binary refuses to elevate the calling process or drops privileges back to unprivileged `uid=2000(shell)`.
- **Interactive Shell Blocking:** Executing `wifi root sh` drops immediately back to `shell`.
- **Capability Dropping:** Drops essential POSIX capabilities (`CAP_SYS_ADMIN`, `CAP_SYS_RAWIO`), preventing raw block writes to eMMC partitions.
- **SELinux Domain Confinement:** The spawned process remains confined to `context=u:r:shell:s0`.

## 4. Exploit Proof-of-Concept Wrappers
To analyze and bypass execution constraints, two wrapper utilities were created:

- **`systemshell.c`:** Leverages `wifi` to spawn an unconstrained shell under the `system` UID (1000).
- **`rootshell.c`:** Attempts to retain root UID 0 execution state across process forks.

### Compilation
```bash
arm-linux-gnueabi-gcc -static -O2 systemshell.c -o systemshell
arm-linux-gnueabi-gcc -static -O2 rootshell.c -o rootshell
```

## 5. Summary Findings
- The stock `/system/bin/wifi` binary functions as a root escalation helper **exclusively when executed within the hardware UART serial console shell**.
- Standard ADB shell sessions trigger internal privilege dropping, preventing elevation to UID 0 over USB.
- Runtime capability filtering prevents raw device access, requiring `sysu` or Magisk for persistent and full system modification.

---
*© Yuuji Lab. Licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).*
