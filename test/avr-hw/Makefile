QEMU=qemu-system-avr
OBJCOPY=objcopy
OBJDUMP=objdump

.PHONY: all

all : main.bin

main.elf : main.c
	$(CC) -g $^ -Wl,-u,vfprintf -o $@ \
	-Wl,--section-start,.data=0x801100,--defsym=__heap_end=0x80ffff

main.bin : main.elf
	 $(OBJCOPY) -O binary $^ $@

clean :
	rm -f -v *.o *.elf *.bin

run : main.elf
	$(QEMU) -machine uno -nographic -kernel $^ -serial mon:stdio
