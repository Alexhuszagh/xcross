include ../riscv/Makefile
QEMU=qemu-system-riscv32

run : main.elf
	$(QEMU) -nographic -kernel $^ -serial mon:stdio
