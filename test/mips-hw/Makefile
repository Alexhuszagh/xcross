include ../mips/Makefile
QEMU=qemu-system-mips

run : main.elf
	$(QEMU) -nographic -bios $^
