include ../riscv/Makefile
QEMU=qemu-system-riscv64

run : main.elf
	$(QEMU) -nographic -kernel $^ -serial mon:stdio
