// NOTE:
//  This doesn't actually link to a C standard library, because
//  newlib is really difficult to work with x86. At some point,
//  I should probably migrate to picolibc for x86.
void main(void) {
    int i;
    const char s[] = "Hello world!";
    for (i = 0; i < sizeof(s); ++i) {
        __asm__ (
            "int $0x10" : : "a" ((0x0e << 8) | s[i])
        );
    }
    while (1) {
        __asm__ ("hlt");
    };
}
