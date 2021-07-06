#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main() {
  char* v = malloc(50);
  const char* s = "Hello world!";
  strcpy(v, s);
  printf("%s\n", v);
  while(1);
  return 0;
}
