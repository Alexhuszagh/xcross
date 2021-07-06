#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void main(void) {
  char* v = malloc(50);
  const char* s = "Hello world!";
  strcpy(v, s);
  printf("%s\n", v);
  return 0;
}
