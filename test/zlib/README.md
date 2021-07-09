zlib
====

Test alternative build systems using Conan, Meson, and vcpkg.

**Meson with Conan**

```bash
rm -rf build
mkdir -p build
cd build
conan install .. --build
conan build ..
```

**CMake with Conan**

```bash
rm -rf build
mkdir -p build
cd build
conan install .. --build
cmake ..
cmake --build .
```

**CMake with vcpkg**

```bash
rm -rf build
mkdir -p build
cd build
vcpkg install zlib
cmake ..
cmake --build .
```
