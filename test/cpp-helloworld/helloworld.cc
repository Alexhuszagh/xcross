#include <iostream>
#include <string>

int main() {
    std::string hello = std::string("Hello world!");
#ifndef NO_STDIO
    std::cout << hello << std::endl;
#endif
}
