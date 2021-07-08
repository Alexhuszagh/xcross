include ../mips/Makefile
QEMU=qemu-system-mipsel

run : main.elf
	$(QEMU) -nographic -bios $^
