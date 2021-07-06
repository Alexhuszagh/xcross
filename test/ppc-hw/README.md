# ppc_hw

helloworld powerpc-app on qemu-e500

This is a minimal program that prints to the serial port.
A real program will have to do a lot more configuration.
Documentation and source code from a more complete processor 
setup can be found at Freescale, search for AN2551.

## Credits

This is a fork of [ara4711/ppc_hw](https://github.com/ara4711/ppc_hw), adapted to test a a bare-metal machine with malloc inside an xcross container.

- The program is based on a stripped version of the u-boot code,
  and the three header files in the inc folder have been copied from
  u-boot. A little hack was be done in processor.h (see AAA_HACK_DISABLE)
  to avoid having to include even more files .

- The file startup.S is essentially the same file as the file
  EclipseDemos/Juno/POWERPC/Freescale_MPC5554Demo/crt0.S
  From and archive at [macraigor](http://www.macraigor.com/gnu/hw_support_12.0.0_64-bit.exe)

- The file linker.ld is adapted from an 
  [article](http://opensourceforu.efytimes.com/2011/07/qemu-for-embedded-systems-development-part-2/) 
  on bare metal arm on qemu.

## Synopsis

At startup, tlb1, entry0 is mapped and code is executed from it.
  However, it is only 4kB so in real use this code will have to 
  map more code into memory. Since entry0 is in use, entry1 is used
  for the ccsrbar mapping. 

### Files
- startup.S  -- sets the stackpointer and calls c_entry
- main.c     -- implements c_entry which maps the ccsrbar to
                be able to access the serial port.
                Then it prints a message to the serial port.

## Instructions

From the source directory, run:

```bash
$ xcross --target ppc-unknown-elf make
$ timeout 0.1 qemu-system-ppc -cpu e500 -d guest_errors,unimp -M ppce500 -nographic -bios main.elf  -s || [[ $? -eq 124 ]]
```

This automatically builds the image in the correct container, and then exits with a 0 exit code if the command timed out.

### Usage

- `make`       -- compiles and links it.
- `make run`   -- let qemu run the compiled binary  (exit with `C-a x`)
