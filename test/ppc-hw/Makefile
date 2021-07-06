QEMU=qemu-system-ppc
OBJCOPY=objcopy
OBJDUMP=objdump

.PHONY: all

all : main.bin

startup.o : startup.S
	$(CC) -mbig-endian -g -c -gstabs+ -Wa,-alh=startup.lst,-L -o $@ $<

main.o : main.c
	$(CC) $(CFLAGS) -c -mcpu=8540 -g $< -o $@

main.elf : main.o startup.o  linker.ld
	$(CC) -T linker.ld main.o startup.o -o $@

main.bin : main.elf
	 $(OBJCOPY) -O binary  $< $@

nm_main:
	$(NM) main.elf
dis_main:
	$(OBJDUMP) --disassemble main.elf

clean :
	rm -f -v *.o *.elf *.bin *.lst

run:
	$(QEMU) -cpu e500 -M ppce500 -nographic -bios main.elf
