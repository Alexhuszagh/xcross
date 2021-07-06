QEMU=qemu-system-i386
OBJCOPY=objcopy
OBJDUMP=objdump

.PHONY: all

all : main.bin

startup.o : startup.S
	$(CC) -g -c -m16 startup.S -o $@

main.o : main.c
	$(CC) -c -g -m16 main.c -std=c99 -o $@

main.elf : main.o startup.o
	$(CC) -T linker.ld -g main.o startup.o -ffreestanding \
	-fno-PIE -nostartfiles -nostdlib -Wl,-melf_i386 -o $@

main.bin : main.elf
	 $(OBJCOPY) -O binary  $< $@

clean :
	rm -f -v *.o *.elf *.bin

run:
	$(QEMU) -nographic -drive file=main.bin,format=raw -serial mon:stdio
