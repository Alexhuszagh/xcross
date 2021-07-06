QEMU=qemu-system-riscv32
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
	$(QEMU) -nographic -bios main.bin
