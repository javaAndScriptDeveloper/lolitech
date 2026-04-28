.global lab1
.syntax unified

#define A #2
#define B #3
#define C #4

lab1:
	push {lr}
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
	pop {pc}
