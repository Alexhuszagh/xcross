QEMU=qemu-system-aarch64
OBJCOPY=objcopy
OBJDUMP=objdump
ENTRY=0x40000000
UART=0x09000000
CPU=cortex-a57

.PHONY: all

all : main.bin

main.o : main.c
	$(CC) -mcpu=$(CPU) -c main.c -o $@

startup.o : startup.S
	$(CC) -std=c99 -c startup.S -o $@

syscalls.o : syscalls.c
	$(CC) -DUART0_ADDR=$(UART) -nostartfiles -c syscalls.c -o $@

main.elf : main.o startup.o syscalls.o
	$(CC) -mcpu=$(CPU) -nostartfiles \
	-Wl,--section-start=.text=$(ENTRY) \
	-T linker.ld startup.o main.o syscalls.o -o $@

main.bin : main.elf
	 $(OBJCOPY) -O binary  $< $@

clean :
	rm -f -v *.o *.elf *.bin

run:
	$(QEMU) -M virt -cpu $(CPU) -kernel main.elf \
	-nographic -serial mon:stdio -m 256M
