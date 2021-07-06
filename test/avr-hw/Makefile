QEMU=qemu-system-avr
OBJCOPY=objcopy
OBJDUMP=objdump

.PHONY: all

all : main.bin

main.elf : main.c
	$(CC) -g main.c -Wl,-u,vfprintf -Wl,--section-start,.data=0x801100,--defsym=__heap_end=0x80ffff -o $@

main.bin : main.elf
	 $(OBJCOPY) -O binary  $< $@

clean :
	rm -f -v *.o *.elf *.bin *.lst

run:
	$(QEMU) -machine uno -nographic -kernel main.elf -serial mon:stdio
