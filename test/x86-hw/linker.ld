ENTRY(_Reset)
SECTIONS
{
  . = 0x7c00;
  .text : {
    startup.o(.text)
    *(.text)
    *(.data)
    *(.rodata)
    __bss_start = .;
    *(.bss)
    *(COMMON)
    __bss_end = .;
  }
  .sig : AT(ADDR(.text) + 512 - 2)
  {
      SHORT(0xaa55);
  }
  /DISCARD/ : {
    *(.eh_frame)
  }
  stack_bottom = .;
  . = . + 0x1000;
  stack_top = .;
}
