.syntax unified
.cpu cortex-m4
//.fpu softvfp
.thumb
#define A #2
#define B #3
#define C #4

.global vtable_kernel
.global __kernel_reset__

.type vtable_kernel, %object
.type __kernel_reset__, %function

.section .interrupt_vector
vtable_kernel:
    .word __stack_start
    .word __kernel_reset__+1
    .size vtable_kernel, .-vtable_kernel

.section .rodata
    data: .asciz "kernel started!\n"
    data_end: .asciz "kernel ended!\n"
.section .text
__kernel_reset__:
    mov r0, #0
    ldr r0, =data
    bl dbgput_line

    mov r0, A
    mov r1, B
    mov r2, C
    mul r3, r0, r1
    cmp r3, #10
    blt else
    orr r0, r0, r1
    b endif
else:
    and r0, r0, r1
endif:
    mul r0, r2

    bl dbgput_num

    ldr r0, =data_end
    bl dbgput_line

    end:
    b end
