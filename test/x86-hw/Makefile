QEMU=qemu-system-i386
OBJCOPY=objcopy
OBJDUMP=objdump

.PHONY: all

all : main.bin

startup.o : startup.S
	$(CC) -g -c -m16 $^ -o $@

main.o : main.c
	$(CC) -c -g -m16 $^ -std=c99 -o $@

main.elf : main.o startup.o
	$(CC) -T linker.ld -g $^ -ffreestanding \
	-fno-PIE -nostartfiles -nostdlib -Wl,-melf_i386 -o $@

main.bin : main.elf
	 $(OBJCOPY) -O binary $^ $@

clean :
	rm -f -v *.o *.elf *.bin

run : main.bin
	$(QEMU) -nographic -drive file=$^,format=raw -serial mon:stdio
