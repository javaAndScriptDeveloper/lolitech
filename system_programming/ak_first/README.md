# Systems Programming — Lab Works

Six labs in C and C++ progressing from userspace CLI tools to Linux kernel module development.

**Stack:** C · C++ · GCC · Linux kernel API · Makefile

---

## Labs 1 & 2 — Calculator (C++)

Command-line calculator implementing basic arithmetic (`Add`, `Sub`, `Mul`, `Div`) with floating-point precision. Lab 2 extends it with additional operators and input validation.

---

## Lab 3 — CLI Tool with Flag Parsing (C++)

A structured CLI application that responds to flags: `--help`, `--print`, `--creator`. Demonstrates argument parsing, help text generation, and clean flag-driven program flow.

---

## Labs 5, 6, 7 — Linux Kernel Modules (C)

Three labs building and loading Linux kernel modules:

- Writing `init` / `exit` routines with `module_init` / `module_exit`.
- Printing to the kernel log via `printk`.
- Mixing C source files with inline Assembly (`.S` files).
- Building with the kernel Makefile system (`obj-m`).

The progression covers single-file modules, multi-file modules, and modules that call Assembly subroutines — giving hands-on experience with the kernel build system and ring-0 execution context.
