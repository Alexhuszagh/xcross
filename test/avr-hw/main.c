#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// NOTE:
//  You would never use this program on a real AVR, and we don't
//  define any of the required usart definitions to properly
//  display stuff to the console, but it does show linking works.
void main(void) {
  char* v = malloc(50);
  const char* s = "Hello world!";
  strcpy(v, s);
  printf("%s\n", v);
}
