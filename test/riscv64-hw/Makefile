QEMU=qemu-system-riscv64
OBJCOPY=objcopy
OBJDUMP=objdump

.PHONY: all

all : main.bin

main.elf : main.c
	$(CC) -g main.c -o $@

main.bin : main.elf
	 $(OBJCOPY) -O binary  $< $@

clean :
	rm -f -v *.o *.elf *.bin *.lst

run:
	$(QEMU) -nographic -kernel main.elf -serial mon:stdio
