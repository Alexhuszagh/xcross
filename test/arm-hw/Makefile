QEMU=qemu-system-arm
ENTRY=0x40000000
UART=0x09000000
CPU=cortex-a15
include ../arm/Makefile

run : main.elf
	$(QEMU) -M virt -cpu $(CPU) -kernel $^ \
	-nographic -serial mon:stdio -m 256M
