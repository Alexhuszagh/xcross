#include <cstdlib>
#include <cstring>
#include <iostream>
#include <zlib.h>

int main ()
{
    const char* input = "Hello world!";
    char deflated[100];
    char inflated[100];

    // Zlib requires `next_in` to not have const qualifiers,
    // even though it doesn't mutate the input.
    char* buffer = const_cast<char*>(input);

    // Compress
    z_stream compressor;
    compressor.opaque = Z_NULL;
    compressor.zalloc = Z_NULL;
    compressor.zfree = Z_NULL;
    compressor.avail_in = static_cast<uInt>(strlen(input) + 1);
    compressor.next_in = reinterpret_cast<Bytef*>(buffer);
    compressor.avail_out = static_cast<uInt>(sizeof(deflated));
    compressor.next_out = reinterpret_cast<Bytef*>(deflated);
    deflateInit(&compressor, Z_DEFAULT_COMPRESSION);
    deflate(&compressor, Z_FINISH);
    deflateEnd(&compressor);

    // Decompress
    auto next_out = reinterpret_cast<char*>(compressor.next_out);
    auto compressed_len = static_cast<uInt>(next_out - deflated);
    z_stream decompressor;
    decompressor.opaque = Z_NULL;
    decompressor.zalloc = Z_NULL;
    decompressor.zfree = Z_NULL;
    decompressor.avail_in = static_cast<uInt>(compressed_len);
    decompressor.next_in = reinterpret_cast<Bytef*>(deflated);
    decompressor.avail_out = static_cast<uInt>(sizeof(inflated));
    decompressor.next_out = reinterpret_cast<Bytef*>(inflated);
    inflateInit(&decompressor);
    inflate(&decompressor, Z_NO_FLUSH);
    inflateEnd(&decompressor);

    // Compare input and output.
    std::cout << "Input is:  \"" << input << "\"" << std::endl;
    std::cout << "Output is: \"" << inflated << "\"" << std::endl;

    return 0;
}
