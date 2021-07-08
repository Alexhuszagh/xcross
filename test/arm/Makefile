OBJCOPY=objcopy
OBJDUMP=objdump

.PHONY: all

all : main.bin

main.o : ../common/main.c
	$(CC) -mcpu=$(CPU) -c $^ -o $@

startup.o : startup.S
	$(CC) -std=c99 -c $^ -o $@

syscalls.o : ../arm/syscalls.c
	$(CC) -DUART0_ADDR=$(UART) -nostartfiles -c $^ -o $@

main.elf : main.o startup.o syscalls.o
	$(CC) -mcpu=$(CPU) -nostartfiles \
	-Wl,--section-start=.text=$(ENTRY) \
	-T linker.ld $^ -o $@

main.bin : main.elf
	 $(OBJCOPY) -O binary $^ $@

clean :
	rm -f -v *.o *.elf *.bin
