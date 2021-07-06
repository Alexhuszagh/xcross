QEMU=qemu-system-arm
OBJCOPY=objcopy
OBJDUMP=objdump

.PHONY: all

all : main.bin

main.elf : main.c
	$(CC) -mcpu=arm926ej-s -g main.c -o $@

main.bin : main.elf
	 $(OBJCOPY) -O binary  $< $@

clean :
	rm -f -v *.o *.elf *.bin *.lst

run:
	QEMU_AUDIO_DRV=none $(QEMU) -cpu arm926 -m 128M -M versatilepb -nographic -bios main.bin
