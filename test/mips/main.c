#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Implement sbrk so newlib can implement malloc for string.
void* _sbrk (int incr) {
    extern char heap_low;
    static char* heap;
    if (heap == NULL) {
        heap = &heap_low;
    }
    char* prev_heap = heap;
    heap += incr;
    return (void*)prev_heap;
}

void* sbrk(int incr) {
    return _sbrk(incr);
}

// NOTE:
//  This doesn't properly print to console, but this is likely due to
//  missing usart definitions, but it does show linking works.
void main(void) {
  char* v = malloc(50);
  const char* s = "Hello world!";
  strcpy(v, s);
  printf("%s\n", s);
}
