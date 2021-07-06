ENTRY(_Reset)
SECTIONS
{
  . = 0xf00000; 

 .startup . : { startup.o(.text) }
 .text : { *(.text) }
 .data : { *(.data) }
 .bss : { *(.bss COMMON) }
 . = ALIGN(8);
 heap_low = .;
 . = . + 0x10000;
 heap_top = .;
 stack_bottom = .;
 . = . + 0x10000;
 stack_top = .;
}

