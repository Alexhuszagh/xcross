OBJCOPY=objcopy
OBJDUMP=objdump

.PHONY: all

all : main.bin

main.o : ../mips/main.c
	$(CC) -c $^ -o $@

main.elf : main.o
	$(CC) -T../mips/linker.ld $^ -g -o $@

main.bin : main.elf
	 $(OBJCOPY) -O binary $^ $@

clean :
	rm -f -v *.o *.elf *.bin
