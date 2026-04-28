# System Programming — Lab Works

Two courses covering system programming from different angles: userspace C/C++ and Linux kernel modules in the first course, bare-metal ARM embedded systems in the third.

---

## First Course — C / C++ & Linux Kernel ([`ak_first/`](./ak_first))

**Stack:** C · C++ · GCC · Linux kernel API · Makefile

### Labs 1 & 2 — Calculator (C++)
Command-line calculator with basic arithmetic (`Add`, `Sub`, `Mul`, `Div`) and floating-point precision. Lab 2 adds more operators and input validation.

### Lab 3 — CLI Tool with Flag Parsing (C++)
Structured CLI application responding to `--help`, `--print`, `--creator` flags. Covers argument parsing and clean flag-driven program flow.

### Labs 5, 6, 7 — Linux Kernel Modules (C)
Three labs building and loading Linux kernel modules — `init`/`exit` routines, `printk` logging, multi-file modules, and inline Assembly (`.S`) subroutines. Built with the kernel Makefile system (`obj-m`).

---

## Third Course — ARM Embedded Systems ([`ak_third/`](./ak_third))

**Stack:** ARM Assembly · C · GNU arm-none-eabi toolchain · Linker scripts · Makefile

### Lab 1 — ARM Firmware Compilation
First bare-metal binary: minimal C startup routine, custom linker script, memory layout, vector table, and raw `firmware.bin` output.

### Lab 1b — Assembly Entry Point
Replaces the C startup with hand-written ARM Assembly (`start.S`, `lab1.S`) — initialises stack pointer, zeroes BSS, jumps to `main`.

### Lab 3 — Bootloader + Kernel
Two independently linked binaries: a **bootloader** that loads at the lowest address and hands off to a minimal **kernel** with a memory-mapped UART `print` subroutine. Mirrors a real two-stage boot process.
