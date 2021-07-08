ENTRY(_Reset)
SECTIONS
{
  .text : {
    */startup.o(.text)
    *(.text)
    *(.rodata)
    *(.data)
    *(COMMON)
  }
  .bss : { *(.bss) }
  . = ALIGN(8);
  heap_low = .;
  . = . + 0x1000000;
  heap_top = .;
  . = . + 0x1000000;
  stack_top = .;
}

