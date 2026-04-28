# Embedded Systems — Lab Works

Three labs in ARM Assembly and C building firmware, a bootloader, and a bare-metal kernel from scratch — no OS, no stdlib.

**Stack:** ARM Assembly · C · GNU Toolchain (arm-none-eabi) · Linker scripts · Makefile

---

## Lab 1 — ARM Firmware Compilation

Toolchain setup and first bare-metal binary. Writing a minimal startup routine in C, compiling to an ELF, and producing a raw firmware image (`firmware.bin`) with a custom linker script. Covers memory layout, vector table, and the reset handler entry point.

---

## Lab 1b — Assembly Entry Point

Replaces the C startup with hand-written ARM Assembly (`start.S`, `lab1.S`). Initialises the stack pointer, zeroes BSS, and jumps to `main`. Demonstrates the exact machine-level contract between hardware reset and the first C instruction.

---

## Lab 3 — Bootloader + Kernel

The most complete lab: two separate binaries built and linked independently.

- **Bootloader** (`bootloader.S`) — loads into the lowest address, sets up the environment, and transfers control to the kernel image.
- **Kernel** (`kernel.S`, `print.S`) — a minimal kernel with a `print` subroutine that writes characters to a memory-mapped UART.
- Dual Makefile targets produce `bootloader.bin` and `kernel.bin`, mirroring a real two-stage boot process.
