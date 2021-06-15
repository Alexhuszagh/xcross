#!/usr/bin/env python
'''
    setup
    =====

    This is a relatively complicated setup script, since
    it does a few things to simplify version control
    and configuration files.

    There's a simple script that overrides the `build_py`
    command to ensure there's proper version control set
    for the library.

    There's also a more complex `configure` command
    that configures all images from template files,
    and also configures the `cmake` wrapper and the
    shell version information.
'''

import collections
import enum
import glob
import itertools
import re
import os
import setuptools
import shutil
import stat
import sys

try:
    from setuptools import setup, Command
    has_setuptools = True
except ImportError:
    from distutils.core import setup, Command
    has_setuptools = False
from distutils.command.build_py import build_py
try:
    import py2exe
except ImportError:
    if len(sys.argv) >= 2 and sys.argv[1] == 'py2exe':
        print('Cannot import py2exe', file=sys.stderr)
        exit(1)

HOME = os.path.dirname(os.path.realpath(__file__))

def read_version():
    '''Read the version data as a dict from a source file.'''

    with open(f'{HOME}/version', 'r') as file:
        contents = file.read()

    lines = [i for i in contents.splitlines() if i and not i.startswith('#')]
    pairs = [i.split('=') for i in lines]
    return {k.strip(): v.strip() for k, v in pairs}

version_data = read_version()

def get_version(prefix):
    '''Get the version keys from the version dict.'''

    major = version_data[f'{prefix}_MAJOR']
    minor = version_data[f'{prefix}_MINOR']
    patch = version_data[f'{prefix}_PATCH']
    build = version_data.get(f'{prefix}_BUILD', '')

    return (major, minor, patch, build)

# Read the xcross version information.
major, minor, patch, build = get_version('VERSION')
version = f'{major}.{minor}'
if patch != '0' or build != '':
    version = f'{version}.{patch}'
if build != '':
    version = f'{version}-{build}'
py2exe_version = f'{major}.{minor}.{patch}'

# Read the dependency version information.
# This is the GCC and other utilities version from crosstool-NG.
ubuntu_major, ubuntu_minor, _, _ = get_version('UBUNTU_VERSION')
ubuntu_version = f'{ubuntu_major}.{ubuntu_minor}'
ubuntu_name = version_data['UBUNTU_NAME']
gcc_major, gcc_minor, gcc_patch, _ = get_version('GCC_VERSION')
gcc_version = f'{gcc_major}.{gcc_minor}.{gcc_patch}'
mingw_major, mingw_minor, mingw_patch, _ = get_version('MINGW_VERSION')
mingw_version = f'{mingw_major}.{mingw_minor}.{mingw_patch}'
glibc_major, glibc_minor, _, _ = get_version('GLIBC_VERSION')
glibc_version = f'{glibc_major}.{glibc_minor}'
musl_major, musl_minor, musl_patch, _ = get_version('MUSL_VERSION')
musl_version = f'{musl_major}.{musl_minor}.{musl_patch}'
avr_major, avr_minor, avr_patch, _ = get_version('AVR_VERSION')
avr_version = f'{avr_major}.{avr_minor}.{avr_patch}'
uclibc_major, uclibc_minor, uclibc_patch, _ = get_version('UCLIBC_VERSION')
uclibc_version = f'{uclibc_major}.{uclibc_minor}.{uclibc_patch}'
expat_major, expat_minor, expat_patch, _ = get_version('EXPAT_VERSION')
expat_version = f'{expat_major}.{expat_minor}.{expat_patch}'
ct_major, ct_minor, ct_patch, _ = get_version('CROSSTOOL_VERSION')
ct_version = f'{ct_major}.{ct_minor}.{ct_patch}'
qemu_major, qemu_minor, qemu_patch, _ = get_version('QEMU_VERSION')
qemu_version = f'{qemu_major}.{qemu_minor}.{qemu_patch}'
android_ndk_version = version_data['ANDROID_NDK_VERSION']
android_sdk_version = version_data['ANDROID_SDK_VERSION']
android_clang_version = version_data['ANDROID_CLANG_VERSION']
riscv_toolchain_version = version_data['RISCV_TOOLCHAIN_VERSION']
riscv_binutils_version = version_data['RISCV_BINUTILS_VERSION']
riscv_gdb_version = version_data['RISCV_GDB_VERSION']
riscv_glibc_version = version_data['RISCV_GLIBC_VERSION']
riscv_newlib_version = version_data['RISCV_NEWLIB_VERSION']

# Read the long description.
description = 'Zero-setup cross compilation.'
with open(f'{HOME}/README.md') as file:
    long_description = file.read()


class CleanCommand(Command):
    '''A custom command to clean any previous builds.'''

    description = 'clean all previous builds'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        '''Clean build data.'''

        shutil.rmtree(f'{HOME}/build', ignore_errors=True)
        shutil.rmtree(f'{HOME}/dist', ignore_errors=True)
        shutil.rmtree(f'{HOME}/xcross.egg-info', ignore_errors=True)

        # Clean py2exe files
        dlls = glob.glob(f'{HOME}/*.dll')
        exes = glob.glob(f'{HOME}/*.exe')
        sos = glob.glob(f'{HOME}/*.so')
        for file in dlls + exes + sos:
            os.remove(file)

        # Need to remove the configured directories.
        shutil.rmtree(f'{HOME}/cmake/toolchain', ignore_errors=True)
        shutil.rmtree(f'{HOME}/docker/images', ignore_errors=True)
        shutil.rmtree(f'{HOME}/symlink/toolchain', ignore_errors=True)


class VersionCommand(Command):
    '''A custom command to configure the library version.'''

    description = 'set library version'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def replace(self, string, replacements):
        '''Replace template variable with value.'''

        for variable, value in replacements:
            string = string.replace(f'^{variable}^', value)
        return string

    def chmod(self, file):
        '''Make a file executable.'''

        flags = stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
        st = os.stat(file)
        os.chmod(file, st.st_mode | flags)

    def write_file(self, path, contents, chmod):
        '''Check if we need to write a file.'''

        try:
            with open(path, 'r') as file:
                old_contents = file.read()
                should_update = old_contents != contents
        except FileNotFoundError:
            should_update = True

        if should_update:
            with open(path, 'w') as file:
                file.write(contents)
            if chmod:
                self.chmod(path)

    def configure(self, template, outfile, chmod, replacements):
        '''Configure a template file.'''

        with open(template, 'r') as file:
            contents = file.read()
        contents = self.replace(contents, replacements)
        self.write_file(outfile, contents, chmod)

    def run(self):
        '''Modify the library version.'''

        xcross = f'{HOME}/xcross/__init__.py'
        self.configure(f'{xcross}.in', xcross, True, [
            ('VERSION_MAJOR', f"'{major}'"),
            ('VERSION_MINOR', f"'{minor}'"),
            ('VERSION_PATCH', f"'{patch}'"),
            ('VERSION_BUILD', f"'{build}'"),
            ('VERSION_INFO', f"version_info(major='{major}', minor='{minor}', patch='{patch}', build='{build}')"),
            ('VERSION', f"'{version}'"),
        ])

# There are two types of images:
#   1). Images with an OS layer.
#   2). Bare-metal machines.
# Bare-metal machines don't use newlibs nanomalloc, so these do not
# support system allocators.
class OperatingSystem(enum.Enum):
    '''Enumerations for known operating systems.'''

    Android = enum.auto()
    BareMetal = enum.auto()
    Linux = enum.auto()
    Web = enum.auto()
    Windows = enum.auto()

    def is_baremetal(self):
        return self == OperatingSystem.BareMetal

    def cmake_string(self):
        '''Get the identifier for the CMake operating system name.'''

        if self == OperatingSystem.Android:
            return 'Android'
        elif self == OperatingSystem.BareMetal:
            return 'Generic'
        elif self == OperatingSystem.Linux:
            return 'Linux'
        elif self == OperatingSystem.Windows:
            return 'Windows'
        else:
            # wasm is not implemented
            raise NotImplementedError

sysroot = '/opt'
build_jobs = '5'
bin_directory = f'{sysroot}/bin/'
android_ndk_directory = '/usr/local/ndk'

# Template:
#   (os, target, arch, prefix=arch, arch_abi=arch),
android_image = collections.namedtuple('android_image', 'os target arch prefix arch_abi')
# Template:
#   (os, target, arch, with_qemu, config=target, prefix=target, processor=None, flags=None),
crosstool_image = collections.namedtuple('crosstool_image', 'os target arch with_qemu config prefix processor flags')
# Template:
#   (os, target, cxx, libc, arch),
debian_image = collections.namedtuple('debian_image', 'os target cxx libc arch')
# Template:
#   (os, target, arch, with_qemu, march, mabi, prefix),
riscv_image = collections.namedtuple('riscv_image', 'os target arch with_qemu march mabi prefix')
# Template:
#   (os, target),
other_image = collections.namedtuple('other_image', 'os target')

android_images = [
    android_image(OperatingSystem.Android, 'aarch64-unknown-linux-android', 'aarch64-linux-android', None, 'arm64-v8a'),
    android_image(OperatingSystem.Android, 'armv7a-unknown-linux-androideabi', 'armv7a-linux-androideabi', 'arm-linux-androideabi', 'armeabi-v7a'),
    android_image(OperatingSystem.Android, 'i686-unknown-linux-android', 'i686-linux-android', None, 'x86'),
    android_image(OperatingSystem.Android, 'x86_64-unknown-linux-android', 'x86_64-linux-android', None, 'x86_64'),
]
crosstool_images = [
    crosstool_image(OperatingSystem.Linux, 'alphaev4-unknown-linux-gnu', 'alpha', True, None, None, None, None),
    crosstool_image(OperatingSystem.Linux, 'alphaev5-unknown-linux-gnu', 'alpha', True, None, None, None, None),
    crosstool_image(OperatingSystem.Linux, 'alphaev6-unknown-linux-gnu', 'alpha', True, None, None, None, None),
    crosstool_image(OperatingSystem.Linux, 'alphaev7-unknown-linux-gnu', 'alpha', True, None, None, None, None),
    # alpha EV8 was never finished, and was canceled prior to release
    #crosstool_image(OperatingSystem.Linux, 'alphaev8-unknown-linux-gnu', 'alpha', True, None, None, None, None),
    # Alpha images fail with:
    #   checking iconv.h usability... make[2]: *** [Makefile:7091: configure-ld] Error 1
    #crosstool_image(OperatingSystem.BareMetal, 'alphaev4-unknown-elf', 'alpha', False, None, None, None, None),
    #crosstool_image(OperatingSystem.BareMetal, 'alphaev5-unknown-elf', 'alpha', False, None, None, None, None),
    #crosstool_image(OperatingSystem.BareMetal, 'alphaev6-unknown-elf', 'alpha', False, None, None, None, None),
    #crosstool_image(OperatingSystem.BareMetal, 'alphaev7-unknown-elf', 'alpha', False, None, None, None, None),
    #crosstool_image(OperatingSystem.BareMetal, 'alphaev8-unknown-elf', 'alpha', False, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'arc-unknown-elf', 'arc', False, None, None, None, None),
    # Fails in libc build pass 1:
    #   glibc: configure: error: The arc is not supported
    #crosstool_image(OperatingSystem.Linux, 'arc-unknown-linux-gnu', 'arc', False, None, None, None, None),
    #crosstool_image(OperatingSystem.Linux, 'arcbe-unknown-linux-gnu', 'arcbe', False, None, 'arceb-unknown-linux-gnu', None, None),
    crosstool_image(OperatingSystem.Linux, 'arc-unknown-linux-uclibc', 'arc', False, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'arcbe-unknown-elf', 'arcbe', False, None, 'arceb-unknown-elf', None, None),
    crosstool_image(OperatingSystem.Linux, 'arcbe-unknown-linux-uclibc', 'arcbe', False, None, 'arceb-unknown-linux-uclibc', None, None),
    crosstool_image(OperatingSystem.BareMetal, 'arm-unknown-elf', 'arm', False, None, 'arm-unknown-eabi', None, None),
    crosstool_image(OperatingSystem.BareMetal, 'arm64-unknown-elf', 'aarch64', False, None, 'aarch64-unknown-elf', None, None),
    crosstool_image(OperatingSystem.BareMetal, 'arm64eb-unknown-elf', 'aarch64', False, None, 'aarch64_be-unknown-elf', None, None),
    crosstool_image(OperatingSystem.Linux, 'arm64eb-unknown-linux-gnu', 'aarch64_be', True, None, 'aarch64_be-unknown-linux-gnu', None, None),
    crosstool_image(OperatingSystem.BareMetal, 'armeb-unknown-elf', 'armeb', False, None, 'armeb-unknown-eabi', None, None),
    crosstool_image(OperatingSystem.Linux, 'armeb-unknown-linux-gnueabi', 'armeb', True, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'avr', 'avr', False, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'i386-unknown-elf', 'i386', False, None, None, None, None),
    crosstool_image(OperatingSystem.Windows, 'i386-w64-mingw32', 'i386', False, 'x86_64-w64-mingw32', None, 'i686', 'CFLAGS="-m32" '),
    crosstool_image(OperatingSystem.BareMetal, 'i486-unknown-elf', 'i386', False, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'i586-unknown-elf', 'i386', False, None, None, None, None),
    crosstool_image(OperatingSystem.Linux, 'i686-multilib-linux-musl', 'i386', True, 'x86_64-multilib-linux-musl', None, 'i686', 'CFLAGS="-m32" '),
    crosstool_image(OperatingSystem.BareMetal, 'i686-unknown-elf', 'i386', False, None, None, None, None),
    # Fails with fatal error: pthread.h: No such file or directory
    #crosstool_image(OperatingSystem.Linux, 'i686-unknown-linux-uclibc', 'i386', True, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'm68k-unknown-elf', 'm68k', False, None, None, None, None),
    crosstool_image(OperatingSystem.Linux, 'microblaze-xilinx-linux-gnu', 'microblaze', True, None, None, None, None),
    crosstool_image(OperatingSystem.Linux, 'microblazeel-xilinx-linux-gnu', 'microblazeel', True, None, None, None, None),
    # Fails during compiling due to:
    #   bin/ld: cannot find -lxil
    #   This is the xilinx standard library, but we compiled against
    #   newlib.
    #crosstool_image(OperatingSystem.BareMetal, 'microblaze-xilinx-elf', 'microblaze', False, None, None, None, None),
    #crosstool_image(OperatingSystem.BareMetal, 'microblazeel-xilinx-elf', 'microblazeel', False, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'mips-unknown-o32', 'mips', False, None, 'mips-unknown-elf', None, None),
    crosstool_image(OperatingSystem.BareMetal, 'mips64-unknown-n64', 'mips', False, None, 'mips64-unknown-elf', None, 'CFLAGS="-mabi=32" '),
    crosstool_image(OperatingSystem.BareMetal, 'mips64el-unknown-n64', 'mipsel', False, None, 'mips64el-unknown-elf', None, 'CFLAGS="-mabi=32" '),
    crosstool_image(OperatingSystem.BareMetal, 'mipsel-unknown-o32', 'mipsel', False, None, 'mipsel-unknown-elf', None, None),
    # Fails during configuring GCC pass 2 due to:
    #    error: cannot compute suffix of object files: cannot compile
    #crosstool_image(OperatingSystem.BareMetal, 'mips64-unknown-n32', 'mips', False, None, 'mips64-unknown-elf', None, None),
    #crosstool_image(OperatingSystem.BareMetal, 'mips64el-unknown-n32', 'mipsel', False, None, 'mips64el-unknown-elf', None, None),
    crosstool_image(OperatingSystem.BareMetal, 'moxie-none-elf', 'moxie', False, None, 'moxie-unknown-elf', None, None),
    crosstool_image(OperatingSystem.BareMetal, 'moxie-none-moxiebox', 'moxie', False, None, None, None, None),
    # Fails during building binutils:
    #   BFD does not support target moxie-unknown-linux-gnu.
    #crosstool_image(OperatingSystem.Linux, 'moxie-unknown-linux-gnu', 'moxie', False, None, None, None, None),
    #crosstool_image(OperatingSystem.Linux, 'moxieeb-unknown-linux-gnu', 'moxieeb', False, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'moxieeb-none-elf', 'moxieeb', False, None, 'moxie-unknown-elf', None, None),
    # Fails during building libc pass 2:
    #   moxie-none-moxiebox-cc: error: this target is little-endian
    #   Expected since moxiebox only supports LE.
    #crosstool_image(OperatingSystem.BareMetal, 'moxieeb-none-moxiebox', 'moxieeb', False, None, 'moxie-none-moxiebox', None, None),
    crosstool_image(OperatingSystem.BareMetal, 'nios2-unknown-elf', 'nios2', False, None, None, None, None),
    crosstool_image(OperatingSystem.Linux, 'nios2-unknown-linux-gnu', 'nios2', True, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'ppc-unknown-elf', 'ppc', False, None, 'powerpc-unknown-elf', 'ppc', None),
    crosstool_image(OperatingSystem.BareMetal, 'ppcle-unknown-elf', 'ppcle', False, None, 'powerpcle-unknown-elf', 'ppcle', None),
    # GCC does not support PPC64 and PPC64LE with ELF:
    #    Configuration powerpc64-unknown-elf not supported
    #crosstool_image(OperatingSystem.BareMetal, 'ppc64-unknown-elf', 'ppc64', False, None, None, None, None),
    #crosstool_image(OperatingSystem.BareMetal, 'ppc64le-unknown-elf', 'ppc64le', False, None, None, None, None),
    # Fails during compiling due to:
    #   undefined reference to `__init'
    # Adding -msim or -mads does not fix it.
    #crosstool_image(OperatingSystem.BareMetal, 'ppc-unknown-eabi', 'ppc', False, None, 'powerpc-unknown-elf', 'ppc', None),
    #crosstool_image(OperatingSystem.BareMetal, 'ppcle-unknown-eabi', 'ppcle', False, None, 'powerpcle-unknown-elf', 'ppcle', None),
    # Binutils does not support PPC64 and PPC64LE with EABI:
    #   BFD does not support target powerpc64-unknown-eabi.
    #crosstool_image(OperatingSystem.BareMetal, 'ppc64-unknown-eabi', 'ppc64', False, None, 'ppc64-unknown-elf', None, None),
    #crosstool_image(OperatingSystem.BareMetal, 'ppc64le-unknown-eabi', 'ppc64le', False, None, 'ppc64le-unknown-elf', None, None),
    # GCC does not support SPEELF:
    #   Configuration powerpc-unknown-elfspe not supported
    #crosstool_image(OperatingSystem.BareMetal, 'ppc-unknown-spe', 'ppc', False, None, 'powerpc-unknown-elf', 'ppc', None),
    #crosstool_image(OperatingSystem.BareMetal, 'ppcle-unknown-spe', 'ppcle', False, None, 'powerpcle-unknown-elf', 'ppcle', None),
    #crosstool_image(OperatingSystem.BareMetal, 'ppc64-unknown-spe', 'ppc64', False, None, 'ppc64-unknown-elf', None, None),
    #crosstool_image(OperatingSystem.BareMetal, 'ppc64le-unknown-spe', 'ppc64le', False, None, 'ppc64le-unknown-elf', None, None),
    crosstool_image(OperatingSystem.Linux, 'ppcle-unknown-linux-gnu', 'ppcle', False, None, 'powerpcle-unknown-linux-gnu', 'ppcle', None),
    # Fails with custom build of stock GCC:
    #   rv32i-based targets are not supported on stock GCC.
    #crosstool_image(OperatingSystem.Linux, 'riscv32-unknown-linux-gnu', 'riscv32', False, None, None, None, None),
    crosstool_image(OperatingSystem.Linux, 's390-unknown-linux-gnu', 's390', False, None, 's390-ibm-linux-gnu', None, None),
    # Fails during building binutils:
    #   checking for suffix of executables...
    #   make[2]: *** [Makefile:7088: configure-ld] Error 1
    #crosstool_image(OperatingSystem.BareMetal, 's390-unknown-elf', 's390', False, None, None, None, None),
    #crosstool_image(OperatingSystem.BareMetal, 's390x-unknown-elf', 's390x', False, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'sh1-unknown-elf', 'sh1', False, 'sh-unknown-elf', None, 'sh1', 'CFLAGS="-m1" '),
    crosstool_image(OperatingSystem.BareMetal, 'sh2-unknown-elf', 'sh2', False, 'sh-unknown-elf', None, 'sh2', 'CFLAGS="-m2" '),
    crosstool_image(OperatingSystem.BareMetal, 'sh2e-unknown-elf', 'sh2e', False, 'sh-unknown-elf', None, 'sh2e', 'CFLAGS="-m2e" '),
    crosstool_image(OperatingSystem.BareMetal, 'sh3-unknown-elf', 'sh3', False, 'sh-unknown-elf', None, 'sh3', 'CFLAGS="-m3" '),
    crosstool_image(OperatingSystem.Linux, 'sh3-unknown-linux-gnu', 'sh3', False, None, None, None, None),
    crosstool_image(OperatingSystem.Linux, 'sh3be-unknown-linux-gnu', 'sh3eb', False, None, 'sh3eb-unknown-linux-gnu', None, None),
    crosstool_image(OperatingSystem.BareMetal, 'sh3e-unknown-elf', 'sh3e', False, 'sh-unknown-elf', None, 'sh3e', 'CFLAGS="-m3e" '),
    # Currently fails due to undefined reference to `__fpscr_values`.
    #crosstool_image(OperatingSystem.Linux, 'sh3e-unknown-linux-gnu', 'sh3e', False, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'sh4-100-unknown-elf', 'sh4', False, 'sh-unknown-elf', None, 'sh4-100', 'CFLAGS="-m4-100" '),
    crosstool_image(OperatingSystem.BareMetal, 'sh4-200-unknown-elf', 'sh4', False, 'sh-unknown-elf', None, 'sh4-200', 'CFLAGS="-m4-200" '),
    crosstool_image(OperatingSystem.BareMetal, 'sh4-300-unknown-elf', 'sh4', False, 'sh-unknown-elf', None, 'sh4-300', 'CFLAGS="-m4-300" '),
    crosstool_image(OperatingSystem.BareMetal, 'sh4-340-unknown-elf', 'sh4', False, 'sh-unknown-elf', None, 'sh4-340', 'CFLAGS="-m4-340" '),
    crosstool_image(OperatingSystem.BareMetal, 'sh4-500-unknown-elf', 'sh4', False, 'sh-unknown-elf', None, 'sh4-500', 'CFLAGS="-m4-500" '),
    crosstool_image(OperatingSystem.BareMetal, 'sh4-unknown-elf', 'sh4', False, 'sh-unknown-elf', None, 'sh4', 'CFLAGS="-m4" '),
    crosstool_image(OperatingSystem.BareMetal, 'sh4a-unknown-elf', 'sh4', False, 'sh-unknown-elf', None, 'sh4a', 'CFLAGS="-m4a" '),
    crosstool_image(OperatingSystem.Linux, 'sh4be-unknown-linux-gnu', 'sh4eb', True, None, 'sh4eb-unknown-linux-gnu', None, None),
    # Fails during building libc pass 2:
    #   "multiple definition of `_errno'".
    #crosstool_image(OperatingSystem.BareMetal, 'sh*be*-unknown-elf', 'sh', False, 'shbe-unknown-elf', None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'sparc-unknown-elf', 'sparc', False, None, None, None, None),
    # Fails during building newlib due to:
    #   error: argument 'dirp' doesn't match prototype
    #crosstool_image(OperatingSystem.BareMetal, 'sparc64-unknown-elf', 'sparc64', False, None, None, None, None),
    # Fails in libc build pass 1:
    #   glibc 2.23+ do not support only support SPARCv9, and
    #   there's bugs with older glibc versions.
    #crosstool_image(OperatingSystem.Linux, 'sparc-unknown-linux-gnu', 'sparc', True, None, None, None, None),
    # Note: requires GCC-8, due to invalid register clobbing with source and dest.
    crosstool_image(OperatingSystem.Linux, 'sparc-unknown-linux-uclibc', 'sparc', True, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'thumb-unknown-elf', 'arm', False, 'arm-unknown-elf', 'arm-unknown-eabi', 'thumb', 'CFLAGS="-mthumb" '),
    crosstool_image(OperatingSystem.BareMetal, 'thumbeb-unknown-elf', 'armeb', False, 'armeb-unknown-elf', 'armeb-unknown-eabi', 'thumbeb', 'CFLAGS="-mthumb" '),
    crosstool_image(OperatingSystem.Linux, 'thumbeb-unknown-linux-gnueabi', 'armeb', True, 'armeb-unknown-linux-gnueabi', None, 'thumbeb', 'CFLAGS="-mthumb" '),
    crosstool_image(OperatingSystem.Linux, 'x86_64-multilib-linux-musl', 'x86_64', True, None, None, None, None),
    crosstool_image(OperatingSystem.BareMetal, 'x86_64-unknown-elf', 'x86_64', False, None, None, None, None),
    crosstool_image(OperatingSystem.Linux, 'x86_64-unknown-linux-uclibc', 'x86_64', True, None, None, None, None),
    crosstool_image(OperatingSystem.Windows, 'x86_64-w64-mingw32', 'x86_64', False, None, None, None, None),
    # Fails during building libc pass 1:
    #   Newlib does not support Xtensa.
    #crosstool_image(OperatingSystem.BareMetal, 'xtensa-unknown-elf', 'xtensa', False, None, None, None, None),
    #crosstool_image(OperatingSystem.BareMetal, 'xtensabe-unknown-elf', 'xtensaeb', False, None, 'xtensa-unknown-elf', 'xtensaeb', None),
    # Fails in libc build pass 2:
    #   little endian output does not match Xtensa configuration
    #crosstool_image(OperatingSystem.Linux, 'xtensa-unknown-linux-uclibc', 'xtensa', True, None, None, None, None),
    # Note: Qemu currently fails, but seems to be a Qemu error, since
    # the instructions seem to all be valid.
    crosstool_image(OperatingSystem.Linux, 'xtensabe-unknown-linux-uclibc', 'xtensaeb', True, None, 'xtensa-unknown-linux-uclibc', 'xtensaeb', None),
]
debian_images = [
    debian_image(OperatingSystem.Linux, 'alpha-unknown-linux-gnu', f'g++-{gcc_major}-alpha-linux-gnu', 'libc6.1-alpha-cross', 'alpha'),
    debian_image(OperatingSystem.Linux, 'arm64-unknown-linux-gnu', f'g++-{gcc_major}-aarch64-linux-gnu', 'libc6-arm64-cross', 'aarch64'),
    debian_image(OperatingSystem.Linux, 'armel-unknown-linux-gnueabi', f'g++-{gcc_major}-arm-linux-gnueabi', 'libc6-armel-cross', 'arm'),
    debian_image(OperatingSystem.Linux, 'armelhf-unknown-linux-gnueabi', f'g++-{gcc_major}-arm-linux-gnueabihf', 'libc6-armel-armhf-cross', 'arm'),
    debian_image(OperatingSystem.Linux, 'hppa-unknown-linux-gnu', f'g++-{gcc_major}-hppa-linux-gnu', 'libc6-hppa-cross', 'hppa'),
    debian_image(OperatingSystem.Linux, 'i686-unknown-linux-gnu', f'g++-{gcc_major}-i686-linux-gnu', 'libc6-i386-cross', 'i386'),
    debian_image(OperatingSystem.Linux, 'm68k-unknown-linux-gnu', f'g++-{gcc_major}-m68k-linux-gnu', 'libc6-m68k-cross', 'm68k'),
    debian_image(OperatingSystem.Linux, 'mips-unknown-linux-gnu', f'g++-{gcc_major}-mips-linux-gnu', 'libc6-mips-cross', 'mips'),
    debian_image(OperatingSystem.Linux, 'mips64-unknown-linux-gnu', f'g++-{gcc_major}-mips64-linux-gnuabi64', 'libc6-mips64-cross', 'mips64'),
    debian_image(OperatingSystem.Linux, 'mips64el-unknown-linux-gnu', f'g++-{gcc_major}-mips64el-linux-gnuabi64', 'libc6-mips64el-cross', 'mips64el'),
    debian_image(OperatingSystem.Linux, 'mips64r6-unknown-linux-gnu', f'g++-{gcc_major}-mipsisa64r6-linux-gnuabi64', 'libc6-mips64r6-cross', 'mips64'),
    debian_image(OperatingSystem.Linux, 'mips64r6el-unknown-linux-gnu', f'g++-{gcc_major}-mipsisa64r6el-linux-gnuabi64', 'libc6-mips64r6el-cross', 'mips64el'),
    debian_image(OperatingSystem.Linux, 'mipsel-unknown-linux-gnu', f'g++-{gcc_major}-mipsel-linux-gnu', 'libc6-mipsel-cross', 'mipsel'),
    debian_image(OperatingSystem.Linux, 'mipsr6-unknown-linux-gnu', f'g++-{gcc_major}-mipsisa32r6-linux-gnu', 'libc6-mipsr6-cross', 'mips'),
    debian_image(OperatingSystem.Linux, 'mipsr6el-unknown-linux-gnu', f'g++-{gcc_major}-mipsisa32r6el-linux-gnu', 'libc6-mipsr6el-cross', 'mipsel'),
    debian_image(OperatingSystem.Linux, 'ppc-unknown-linux-gnu', f'g++-{gcc_major}-powerpc-linux-gnu', 'libc6-powerpc-cross', 'ppc'),
    debian_image(OperatingSystem.Linux, 'ppc64-unknown-linux-gnu', f'g++-{gcc_major}-powerpc64-linux-gnu', 'libc6-ppc64-cross', 'ppc64'),
    debian_image(OperatingSystem.Linux, 'ppc64le-unknown-linux-gnu', f'g++-{gcc_major}-powerpc64le-linux-gnu', 'libc6-ppc64el-cross', 'ppc64le'),
    debian_image(OperatingSystem.Linux, 'riscv64-unknown-linux-gnu', f'g++-{gcc_major}-riscv64-linux-gnu', 'libc6-riscv64-cross', 'riscv64'),
    debian_image(OperatingSystem.Linux, 's390x-unknown-linux-gnu', f'g++-{gcc_major}-s390x-linux-gnu', 'libc6-s390-s390x-cross', 's390x'),
    debian_image(OperatingSystem.Linux, 'sh4-unknown-linux-gnu', f'g++-{gcc_major}-sh4-linux-gnu', 'libc6-sh4-cross', 'sh4'),
    debian_image(OperatingSystem.Linux, 'sparc64-unknown-linux-gnu', f'g++-{gcc_major}-sparc64-linux-gnu', 'libc6-sparc64-cross', 'sparc64'),
    debian_image(OperatingSystem.Linux, 'thumbel-unknown-linux-gnueabi', f'g++-{gcc_major}-arm-linux-gnueabi', 'libc6-armel-cross', 'arm'),
    debian_image(OperatingSystem.Linux, 'thumbelhf-unknown-linux-gnueabi', f'g++-{gcc_major}-arm-linux-gnueabihf', 'libc6-armel-armhf-cross', 'arm'),
    debian_image(OperatingSystem.Linux, 'x86_64-unknown-linux-gnu', f'g++-{gcc_major}', 'libc6', 'x86_64'),
]
riscv_images = [
    # We also have some extensive flags for specific configurations of RISC-V.
    # The naming follows as this:
    #   riscv{BITS}-{ARCH}-{ABI}-{vendor}-{os}-{system}
    #   * `BITS` - 32 or 64
    #   * `ARCH` - A string of the format imafdc, in order.
    #       The `I` extension is the base integer instructions.
    #       The `M` extension is the base multiplication and division instructions.
    #       The `A` extension is the base atomic instructions.
    #       The `F` extension is for 32-bit float instructions.
    #       The `D` extension is for 64-bit float instructions.
    #       The `C` extension is for compressed instructions.
    #       The `ima` component is mandatory.
    #   * `ABI` - ilp32[d] or lp64[d]
    #       The `D` extension specifies that 64-bit floats should be passed in registers.
    #       The `F` extension (32-bit floats) is not supported,
    #           nor is `Q` (128-bit floats)
    #       The `E` extension (embedded) is only supported on bare-metal machines.
    riscv_image(OperatingSystem.Linux, 'riscv32-multilib-linux-gnu', 'riscv32', True, 'rv32imac', 'ilp32', 'riscv64-unknown-linux-gnu'),
    riscv_image(OperatingSystem.Linux, 'riscv32-multilib-linux-gnu', 'riscv32', True, 'rv32imac', 'ilp32', 'riscv64-unknown-linux-gnu'),
    # rv32i or rv64i plus standard extensions (a)tomics, (m)ultiplication and division, (f)loat, (d)ouble, or (g)eneral for MAFD
    #   -march=rv64imacd
    #   -mabi=ilp32 ilp32d ilp32e ilp32f lp64 lp64d lp64f
    # rv32i-ilp32
    riscv_image(OperatingSystem.BareMetal, 'riscv32-unknown-elf', 'riscv32', False, 'rv32imac', 'ilp32', 'riscv64-unknown-elf'),
    riscv_image(OperatingSystem.Linux, 'riscv64-multilib-linux-gnu', 'riscv64', True, 'rv64imac', 'lp64', 'riscv64-unknown-linux-gnu'),
    riscv_image(OperatingSystem.BareMetal, 'riscv64-unknown-elf', 'riscv64', False, 'rv64imac', 'lp64', 'riscv64-unknown-elf'),
]

# Add our RISC-V images with extensions.
def create_riscv_image(system, bits, arch, abi, with_qemu):
    '''Create a RISC-V image.'''

    triple_prefix = f'riscv{bits}-{arch}-{abi}'
    if system == OperatingSystem.Linux:
        target = f'{triple_prefix}-multilib-linux-gnu'
        riscv_prefix = 'riscv64-unknown-linux-gnu'
    elif system == OperatingSystem.BareMetal:
        target = f'{triple_prefix}-unknown-elf'
        riscv_prefix = 'riscv64-unknown-elf'
    march = f'rv{bits}{arch}'

    return riscv_image(system, target, triple_prefix, with_qemu, march, abi, riscv_prefix)

riscv_archs = 'fdc'
for bits in ['32', '64']:
    # Add Linux images.
    system = OperatingSystem.Linux
    abi = {'32': 'ilp32', '64': 'lp64'}[bits]
    for count in range(len('fdc') + 1):
        for arch in itertools.combinations(riscv_archs, count):
            # (os, target, arch, with_qemu, march, mabi, prefix),
            arch = f'ima{"".join(arch)}'
            riscv_images.append(create_riscv_image(system, bits, arch, abi, True))
            if 'd' in arch:
                riscv_images.append(create_riscv_image(system, bits, arch, f'{abi}d', True))

    # Bare-metal images don't support any other configurations.
    # Just add the two we support.
    system = OperatingSystem.BareMetal
    riscv_images.append(create_riscv_image(system, bits, 'imac', abi, False))

other_images = [
    other_image(OperatingSystem.Web, 'wasm'),
]

class ConfigureCommand(VersionCommand):
    '''Modify all configuration files.'''

    description = 'configure template files'

    def configure_scripts(self):
        '''Configure the build scripts.'''

        android = f'{HOME}/docker/android.sh'
        cmake = f'{HOME}/docker/cmake.sh'
        entrypoint = f'{HOME}/docker/entrypoint.sh'
        gcc = f'{HOME}/docker/gcc.sh'
        qemu = f'{HOME}/docker/qemu.sh'
        qemu_apt = f'{HOME}/docker/qemu-apt.sh'
        riscv_gcc = f'{HOME}/docker/riscv-gcc.sh'
        shortcut = f'{HOME}/symlink/shortcut.sh'
        self.configure(f'{android}.in', android, True, [
            ('NDK_DIRECTORY', android_ndk_directory),
            ('NDK_VERSION', android_ndk_version),
            ('CLANG_VERSION', android_clang_version),
        ])
        self.configure(f'{cmake}.in', cmake, True, [
            ('UBUNTU_NAME', ubuntu_name),
        ])
        self.configure(f'{entrypoint}.in', entrypoint, True, [
            ('BIN', f'"{bin_directory}"'),
        ])
        self.configure(f'{gcc}.in', gcc, True, [
            ('CROSSTOOL_VERSION', f'"{ct_version}"'),
            ('JOBS', build_jobs),
        ])
        self.configure(f'{qemu}.in', qemu, True, [
            ('JOBS', build_jobs),
            ('QEMU_VERSION', qemu_version),
            ('SYSROOT', f'"{sysroot}"'),
        ])
        self.configure(f'{qemu_apt}.in', qemu_apt, True, [
            ('BIN', f'"{bin_directory}"'),
        ])
        self.configure(f'{riscv_gcc}.in', riscv_gcc, True, [
            ('BINUTILS_VERSION', riscv_binutils_version),
            ('GCC_VERSION', gcc_version),
            ('GDB_VERSION', riscv_gdb_version),
            ('GLIBC_VERSION', riscv_glibc_version),
            ('JOBS', build_jobs),
            ('NEWLIB_VERSION', riscv_newlib_version),
            ('TOOLCHAIN_VERSION', riscv_toolchain_version),
        ])
        self.configure(f'{shortcut}.in', shortcut, True, [
            ('BIN', f'"{bin_directory}"'),
        ])

    def configure_ctng_config(self):
        '''Configure the scripts for crosstool-NG.'''

        patch = f'{HOME}/ct-ng/patch.sh'
        replacements = []

        # Patch the GCC version.
        old_gcc_major = '8'
        old_gcc_version = '8.3.0'
        replacements.append(('GCC_V_OLD', f'CT_GCC_V_{old_gcc_major}=y'))
        ct_gcc = [f'CT_GCC_V_{gcc_major}=y']
        for gcc_v in reversed(range(int(old_gcc_major), int(gcc_major))):
            ct_gcc.append(f'# CT_GCC_V_{gcc_v} is not set')
        replacements.append(('GCC_V_NEW', '\\n'.join(ct_gcc)))
        replacements.append(('GCC_OLD', old_gcc_version))
        replacements.append(('GCC_NEW', gcc_version))

        # Patch the MinGW version.
        old_mingw_major = '6'
        old_mingw_version = '6.0.0'
        replacements.append(('MINGW_V_OLD', f'CT_MINGW_V_{old_mingw_major}=y'))
        ct_mingw = [f'CT_MINGW_V_{mingw_major}=y']
        for mingw_v in reversed(range(int(old_mingw_major), int(mingw_major))):
            ct_mingw.append(f'# CT_MINGW_V_{mingw_v} is not set')
        replacements.append(('MINGW_V_NEW', '\\n'.join(ct_mingw)))
        replacements.append(('MINGW_OLD', old_mingw_version))
        replacements.append(('MINGW_NEW', mingw_version))

        # Configure the glibc version.
        old_glibc_major = '2'
        old_glibc_minor = '29'
        old_glibc_version = '2.29'
        replacements.append(('GLIBC_V_OLD', f'CT_GLIBC_V_{old_glibc_major}_{old_glibc_minor}=y'))
        ct_glibc = [f'CT_GLIBC_V_{glibc_major}_{glibc_minor}=y']
        if old_glibc_major == glibc_major:
            for glibc_v in reversed(range(int(old_glibc_minor), int(glibc_minor))):
                ct_glibc.append(f'# CT_GLIBC_V_{glibc_major}_{glibc_v} is not set')
        else:
            ct_glibc.append(f'# CT_GLIBC_V_{old_glibc_major}_{old_glibc_minor} is not set')
            for glibc_v in reversed(range(int(old_glibc_major) + 1, int(glibc_major))):
                ct_glibc.append(f'# CT_GLIBC_V_{glibc_major}_0 is not set')
        replacements.append(('GLIBC_V_NEW', '\\n'.join(ct_glibc)))
        replacements.append(('GLIBC_OLD', old_glibc_version))
        replacements.append(('GLIBC_NEW', glibc_version))

        # Configure the musl version.
        old_musl_major = '1'
        old_musl_minor = '1'
        old_musl_patch = '21'
        old_musl_version = '1.1.21'
        replacements.append(('MUSL_V_OLD', f'CT_MUSL_V_{old_musl_major}_{old_musl_minor}_{old_musl_patch}=y'))
        ct_musl = [
            f'CT_MUSL_V_{musl_major}_{musl_minor}_{musl_patch}=y',
            f'# CT_MUSL_V_{old_musl_major}_{old_musl_minor}_{old_musl_patch} is not set'
        ]
        replacements.append(('MUSL_V_NEW', '\\n'.join(ct_musl)))
        replacements.append(('MUSL_OLD', old_musl_version))
        replacements.append(('MUSL_NEW', musl_version))

        # Configure the expat version.
        old_expat_major = '2'
        old_expat_minor = '2'
        old_expat_version = '2.2.6'
        replacements.append(('EXPAT_V_OLD', f'CT_EXPAT_V_{old_expat_major}_{old_expat_minor}=y'))
        ct_expat = [
            f'CT_EXPAT_V_{expat_major}_{expat_minor}=y',
            f'# CT_EXPAT_V_{old_expat_major}_{old_expat_minor} is not set'
        ]
        replacements.append(('EXPAT_V_NEW', '\\n'.join(ct_expat)))
        replacements.append(('EXPAT_OLD', old_expat_version))
        replacements.append(('EXPAT_NEW', expat_version))

        self.configure(f'{patch}.in', patch, True, replacements)

    def configure_dockerfile(self, target, template, with_qemu, replacements):
        '''Configure a Dockerfile from template.'''

        # These files are read in the order they're likely to change,
        # as well as compile-time.
        #   Any template files may have long compilations, and will
        #   change rarely. Qemu is an apt package, and unlikely to change.
        #   Symlinks, toolchains, and entrypoints change often, but are
        #   cheap and easy to fix.
        outfile = f'{HOME}/docker/images/Dockerfile.{target}'
        qemu = f'{HOME}/docker/Dockerfile.qemu.in'
        symlink = f'{HOME}/docker/Dockerfile.symlink.in'
        toolchain = f'{HOME}/docker/Dockerfile.toolchain.in'
        entrypoint = f'{HOME}/docker/Dockerfile.entrypoint.in'
        contents = ['FROM ahuszagh/cross:base\n']
        with open(template, 'r') as file:
            contents.append(file.read())
        if with_qemu:
            with open(qemu, 'r') as file:
                contents.append(file.read())
        with open(symlink, 'r') as file:
            contents.append(file.read())
        with open(toolchain, 'r') as file:
            contents.append(file.read())
        with open(entrypoint, 'r') as file:
            contents.append(file.read())
        contents = '\n'.join(contents)
        contents = self.replace(contents, replacements)
        self.write_file(outfile, contents, False)

    def configure_android(self, image):
        '''Configure an Android-SDK image.'''

        # Configure the dockerfile.
        template = f'{HOME}/docker/Dockerfile.android.in'
        self.configure_dockerfile(image.target, template, False, [
            ('ARCH', image.arch),
            ('BIN', f'"{bin_directory}"'),
            ('ENTRYPOINT', f'"{bin_directory}/entrypoint.sh"'),
            ('TARGET', image.target),
        ])

        # Configure the CMake toolchain.
        processor = image.arch.split('-')[0]
        cmake_template = f'{HOME}/cmake/android.cmake.in'
        cmake = f'{HOME}/cmake/toolchain/{image.target}.cmake'
        os = image.os.cmake_string()
        self.configure(cmake_template, cmake, False, [
            ('ARCH_ABI', image.arch_abi or image.arch),
            ('NDK_DIRECTORY', android_ndk_directory),
            ('SDK_VERSION', android_sdk_version),
        ])

        # Configure the symlinks.
        symlink_template = f'{HOME}/symlink/android.sh.in'
        symlink = f'{HOME}/symlink/toolchain/{image.target}.sh'
        self.configure(symlink_template, symlink, True, [
            ('ARCH', image.arch),
            ('NDK_DIRECTORY', android_ndk_directory),
            ('PREFIX', image.prefix or image.arch),
            ('SDK_VERSION', android_sdk_version),
        ])

    def configure_crosstool(self, image):
        '''Configure a crosstool-NG image.'''

        # Configure the dockerfile.
        template = f'{HOME}/docker/Dockerfile.crosstool.in'
        self.configure_dockerfile(image.target, template, image.with_qemu, [
            ('ARCH', image.arch),
            ('BIN', f'"{bin_directory}"'),
            ('CONFIG', image.config or image.target),
            ('ENTRYPOINT', f'"{bin_directory}/entrypoint.sh"'),
            ('TARGET', image.target),
        ])

        # Get the proper dependent parameters for our image.
        os = image.os.cmake_string()
        if image.os == OperatingSystem.BareMetal:
            cmake_template = f'{HOME}/cmake/crosstool-elf.cmake.in'
            symlink_template = f'{HOME}/symlink/crosstool.sh.in'
        else:
            if image.with_qemu:
                cmake_template = f'{HOME}/cmake/crosstool-os-qemu.cmake.in'
                symlink_template = f'{HOME}/symlink/crosstool-qemu.sh.in'
            else:
                cmake_template = f'{HOME}/cmake/crosstool-os.cmake.in'
                symlink_template = f'{HOME}/symlink/crosstool.sh.in'

        # Configure the CMake toolchain.
        cmake = f'{HOME}/cmake/toolchain/{image.target}.cmake'
        prefix = image.prefix or image.config or image.target
        processor = image.processor or prefix.split('-')[0]
        self.configure(cmake_template, cmake, False, [
            ('PREFIX', prefix),
            ('PROCESSOR', processor),
            ('OS', os),
        ])

        # Configure the symlinks.
        symlink = f'{HOME}/symlink/toolchain/{image.target}.sh'
        self.configure(symlink_template, symlink, True, [
            ('ARCH', image.arch),
            ('FLAGS', image.flags or ''),
            ('PREFIX', prefix),
        ])

    def configure_debian(self, image):
        '''Configure a debian-based docker file.'''

        # Configure the dockerfile.
        template = f'{HOME}/docker/Dockerfile.debian.in'
        self.configure_dockerfile(image.target, template, True, [
            ('ARCH', image.arch),
            ('BIN', f'"{bin_directory}"'),
            ('ENTRYPOINT', f'"{bin_directory}/entrypoint.sh"'),
            ('G++', image.cxx),
            ('LIBC', image.libc),
            ('TARGET', image.target),
        ])

        # Get the proper dependent parameters for our image.
        if image.os != OperatingSystem.Linux:
            raise NotImplementedError

        os = image.os.cmake_string()
        if image.target == 'x86_64-unknown-linux-gnu':
            cmake_template = f'{HOME}/cmake/native.cmake.in'
            symlink_template = f'{HOME}/symlink/native.sh.in'
        else:
            cmake_template = f'{HOME}/cmake/debian.cmake.in'
            symlink_template = f'{HOME}/symlink/debian.sh.in'

        # Configure the CMake toolchain.
        cmake = f'{HOME}/cmake/toolchain/{image.target}.cmake'
        self.configure(cmake_template, cmake, False, [
            ('ARCH', image.arch),
            ('PROCESSOR', image.arch),
            ('OS', os),
        ])

        # Configure the symlinks.
        symlink = f'{HOME}/symlink/toolchain/{image.target}.sh'
        self.configure(symlink_template, symlink, True, [
            ('ARCH', image.arch),
            ('GCC_MAJOR', gcc_major),
        ])

    def configure_riscv(self, image):
        '''Configure a RISC-V-based image.'''

        # Get the proper dependent parameters for our image.
        os = image.os.cmake_string()
        if image.os == OperatingSystem.Linux:
            template = f'{HOME}/docker/Dockerfile.riscv-linux.in'
            cmake_template = f'{HOME}/cmake/riscv-linux.cmake.in'
            symlink_template = f'{HOME}/symlink/riscv-linux.sh.in'
        elif image.os == OperatingSystem.BareMetal:
            template = f'{HOME}/docker/Dockerfile.riscv-elf.in'
            cmake_template = f'{HOME}/cmake/riscv-elf.cmake.in'
            symlink_template = f'{HOME}/symlink/riscv-elf.sh.in'
        else:
            raise NotImplementedError

        # Configure the dockerfile.
        self.configure_dockerfile(image.target, template, image.with_qemu, [
            ('ARCH', image.arch),
            ('BIN', f'"{bin_directory}"'),
            ('ENTRYPOINT', f'"{bin_directory}/entrypoint.sh"'),
            ('TARGET', image.target),
        ])

        # Configure the CMake toolchain.
        cmake = f'{HOME}/cmake/toolchain/{image.target}.cmake'
        self.configure(cmake_template, cmake, False, [
            ('PROCESSOR', image.arch),
            ('OS', os),
        ])

        # Configure the symlinks.
        symlink = f'{HOME}/symlink/toolchain/{image.target}.sh'
        self.configure(symlink_template, symlink, True, [
            ('ARCH', image.arch),
            ('MABI', image.mabi),
            ('MARCH', image.march),
            ('PREFIX', image.prefix),
        ])

    def run(self):
        '''Modify configuration files.'''

        VersionCommand.run(self)

        # Make the required subdirectories.
        os.makedirs(f'{HOME}/cmake/toolchain', exist_ok=True)
        os.makedirs(f'{HOME}/docker/images', exist_ok=True)
        os.makedirs(f'{HOME}/symlink/toolchain', exist_ok=True)

        # Configure base version info.
        shell = f'{HOME}/docker/version.sh'
        cmake = f'{HOME}/cmake/cmake'
        images_sh = f'{HOME}/docker/images.sh'
        self.configure(f'{shell}.in', shell, True, [
            ('VERSION_MAJOR', f"'{major}'"),
            ('VERSION_MINOR', f"'{minor}'"),
            ('VERSION_PATCH', f"'{patch}'"),
            ('VERSION_BUILD', f"'{build}'"),
            ('VERSION_INFO', f"('{major}' '{minor}' '{patch}' '{build}')"),
            ('VERSION', f"'{version}'"),
        ])
        self.configure(f'{cmake}.in', cmake, True, [
            ('CMAKE', f"'/usr/bin/cmake'"),
        ])

        # Configure our build scripts.
        self.configure_scripts()

        # Configure our patch script for ct-ng files.
        self.configure_ctng_config()

        # Configure the base dockerfile.
        base_template = f'{HOME}/docker/Dockerfile.base.in'
        base = f'{HOME}/docker/images/Dockerfile.base'
        self.configure(base_template, base, False, [
            ('UBUNTU_VERSION', ubuntu_version),
            ('BIN', f'"{bin_directory}"'),
        ])

        # Configure images.
        for image in android_images:
            self.configure_android(image)
        for image in crosstool_images:
            self.configure_crosstool(image)
        for image in debian_images:
            self.configure_debian(image)
        for image in riscv_images:
            self.configure_riscv(image)

        # Need to write the total image list.
        images = android_images + crosstool_images + debian_images + riscv_images
        os_images = sorted([i.target for i in images if not i.os.is_baremetal()])
        metal_images = sorted([i.target for i in images if i.os.is_baremetal()])
        start = "\n    \""
        joiner = "\"\n    \""
        end = "\"\n"
        os_images = start + joiner.join(os_images) + end
        metal_images = start + joiner.join(metal_images) + end
        self.configure(f'{images_sh}.in', images_sh, True, [
            ('OS_IMAGES', os_images),
            ('METAL_IMAGES', metal_images),
        ])


class BuildCommand(build_py):
    """Override build.py to configure builds."""

    def run(self):
        self.run_command('version')
        build_py.run(self)


script = f'{HOME}/bin/xcross'
if len(sys.argv) >= 2 and sys.argv[1] == 'py2exe':
    params = {
        'console': [{
            'script': f'{HOME}/xcross/__main__.py',
            'dest_base': 'xcross',
            'description': description,
            'comments': long_description,
            'product_name': 'xcross',
        }],
        'options': {
            'py2exe': {
                'bundle_files': 1,
                'compressed': 1,
                'optimize': 2,
                'dist_dir': f'{HOME}',
                'dll_excludes': [],
            }
        },
        'zipfile': None
    }
elif has_setuptools:
    params = {
        'entry_points': {
            'console_scripts': ['xcross = xcross:main']
        }
    }
else:
    params = {
        'scripts': [f'{HOME}/bin/xcross']
    }

setuptools.setup(
    name="xcross",
    author="Alex Huszagh",
    author_email="ahuszagh@gmail.com",
    version=version,
    packages=['xcross'],
    **params,
    description=description,
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>3.6.0',
    license='Unlicense',
    keywords='compilers cross-compilation embedded',
    url='https://github.com/Alexhuszagh/xcross',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: The Unlicense (Unlicense)',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Embedded Systems',
    ],
    cmdclass={
        'build_py': BuildCommand,
        'clean': CleanCommand,
        'configure': ConfigureCommand,
        'version': VersionCommand,
    },
)
