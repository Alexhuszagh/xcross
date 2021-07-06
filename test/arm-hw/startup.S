.global _Reset
_Reset:
    ldr sp, = stack_top
    bl main
    b .
