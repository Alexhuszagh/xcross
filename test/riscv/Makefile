OBJCOPY=objcopy
OBJDUMP=objdump

.PHONY: all

all : main.bin

main.elf : ../common/main.c
	$(CC) -g $^ -o $@

main.bin : main.elf
	 $(OBJCOPY) -O binary $^ $@

clean :
	rm -f -v *.o *.elf *.bin
