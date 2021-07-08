QEMU=qemu-system-ppc
OBJCOPY=objcopy
OBJDUMP=objdump

.PHONY: all

all : main.bin

startup.o : startup.S
	$(CC) -mbig-endian -g -c -gstabs+ -Wa,-alh=startup.lst,-L -o $@ $^

main.o : main.c
	$(CC) $(CFLAGS) -c -mcpu=8540 -g $^ -o $@

main.elf : main.o startup.o
	$(CC) -T linker.ld $^ -o $@

main.bin : main.elf
	 $(OBJCOPY) -O binary $^ $@

clean :
	rm -f -v *.o *.elf *.bin *.lst

run : main.elf
	$(QEMU) -cpu e500 -M ppce500 -nographic -bios $^
