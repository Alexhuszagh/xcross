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
import glob
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

major_re = re.compile(r'^VERSION_MAJOR\s*=\s*(\d+)$', re.M)
minor_re = re.compile(r'^VERSION_MINOR\s*=\s*(\d+)$', re.M)
patch_re = re.compile(r'^VERSION_PATCH\s*=\s*(\d+)$', re.M)
build_re = re.compile(r'^VERSION_BUILD\s*=\s*(\d*)$', re.M)
with open(f'{HOME}/version', 'r') as file:
    contents = file.read()
    major = major_re.search(contents).group(1)
    minor = minor_re.search(contents).group(1)
    patch = patch_re.search(contents).group(1)
    build = build_re.search(contents).group(1)
    version = f'{major}.{minor}'
    if patch != '0' or build != '':
        version = f'{version}.{patch}'
    if build != '':
        version = f'{version}-{build}'
    py2exe_version = f'{major}.{minor}.{patch}'

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
image = collections.namedtuple('image', 'os arguments')
android_images = [
    # Template:
    #   ('target', 'arch'),
    image(True, ('aarch64-unknown-linux-android', 'aarch64-linux-android')),
    image(True, ('armv7a-unknown-linux-androideabi', 'armv7a-linux-androideabi')),
    image(True, ('i686-unknown-linux-android', 'i686-linux-android')),
    image(True, ('x86_64-unknown-linux-android', 'x86_64-linux-android')),
]
crosstool_images = [
    # Template:
    #   ('target', 'arch', with_qemu, config=None),
    image(True, ('alphaev4-unknown-linux-gnu', 'alpha', True)),
    image(True, ('alphaev5-unknown-linux-gnu', 'alpha', True)),
    image(True, ('alphaev6-unknown-linux-gnu', 'alpha', True)),
    image(True, ('alphaev7-unknown-linux-gnu', 'alpha', True)),
    # alpha EV8 was never finished, and was canceled prior to release
    #image(True, ('alphaev8-unknown-linux-gnu', 'alpha', True)),
    # Alpha images fail with:
    #   checking iconv.h usability... make[2]: *** [Makefile:7091: configure-ld] Error 1
    #image(False, ('alphaev4-unknown-elf', 'alpha', False)),
    #image(False, ('alphaev5-unknown-elf', 'alpha', False)),
    #image(False, ('alphaev6-unknown-elf', 'alpha', False)),
    #image(False, ('alphaev7-unknown-elf', 'alpha', False)),
    image(False, ('arc-unknown-elf', 'arc', False)),
    # Fails in libc build pass 1:
    #   glibc: configure: error: The arc is not supported
    #image(True, ('arc-unknown-linux-gnu', 'arc', False)),
    #image(True, ('arcbe-unknown-linux-gnu', 'arcbe', False)),
    image(True, ('arc-unknown-linux-uclibc', 'arc', False)),
    image(False, ('arcbe-unknown-elf', 'arcbe', False)),
    image(True, ('arcbe-unknown-linux-uclibc', 'arcbe', False)),
    image(False, ('arm-unknown-elf', 'arm', False)),
    image(False, ('arm64-unknown-elf', 'aarch64', False)),
    image(False, ('arm64eb-unknown-elf', 'aarch64', False)),
    image(True, ('arm64eb-unknown-linux-gnu', 'aarch64_be', True)),
    image(False, ('armeb-unknown-elf', 'armeb', False)),
    image(True, ('armeb-unknown-linux-gnueabi', 'armeb', True)),
    image(False, ('avr', 'avr', False)),
    image(False, ('i386-unknown-elf', 'i386', False)),
    image(True, ('i386-w64-mingw32', 'i386', False, 'x86_64-w64-mingw32')),
    image(False, ('i486-unknown-elf', 'i386', False)),
    image(False, ('i586-unknown-elf', 'i386', False)),
    image(True, ('i686-multilib-linux-musl', 'i386', True, 'x86_64-multilib-linux-musl')),
    image(False, ('i686-unknown-elf', 'i386', False)),
    # Fails with fatal error: pthread.h: No such file or directory
    #image(True, ('i686-unknown-linux-uclibc', 'i386', True)),
    image(False, ('m68k-unknown-elf', 'm68k', False)),
    image(True, ('microblaze-xilinx-linux-gnu', 'microblaze', True)),
    image(True, ('microblazeel-xilinx-linux-gnu', 'microblazeel', True)),
    # Fails during compiling due to:
    #   bin/ld: cannot find -lxil
    #   This is the xilinx standard library, but we compiled against
    #   newlib.
    #image(False, ('microblaze-xilinx-elf', 'microblaze', False)),
    #image(False, ('microblazeel-xilinx-elf', 'microblazeel', False)),
    image(False, ('mips-unknown-o32', 'mips', False)),
    image(False, ('mips64-unknown-n64', 'mips', False)),
    image(False, ('mips64el-unknown-n64', 'mipsel', False)),
    image(False, ('mipsel-unknown-o32', 'mipsel', False)),
    # Fails during configuring GCC pass 2 due to:
    #    error: cannot compute suffix of object files: cannot compile
    #image(False, ('mips64-unknown-n32', 'mips', False)),
    #image(False, ('mips64el-unknown-n32', 'mipsel', False)),
    image(False, ('moxie-none-elf', 'moxie', False)),
    image(False, ('moxie-none-moxiebox', 'moxie', False)),
    # Fails during building binutils:
    #   BFD does not support target moxie-unknown-linux-gnu.
    #image(True, ('moxie-unknown-linux-gnu', 'moxie', False)),
    #image(True, ('moxieeb-unknown-linux-gnu', 'moxieeb', False)),
    image(False, ('moxieeb-none-elf', 'moxieeb', False)),
    # Fails during building libc pass 2:
    #   moxie-none-moxiebox-cc: error: this target is little-endian
    #   Expected since moxiebox only supports LE.
    #image(False, ('moxieeb-none-moxiebox', 'moxieeb', False)),
    image(False, ('nios2-none-elf', 'nios2', False)),
    image(True, ('nios2-unknown-linux-gnu', 'nios2', True)),
    image(False, ('ppc-unknown-elf', 'ppc', False)),
    image(False, ('ppcle-unknown-elf', 'ppcle', False)),
    # GCC does not support PPC64 and PPC64LE with ELF:
    #    Configuration powerpc64-unknown-elf not supported
    #image(False, ('ppc64-unknown-elf', 'ppc64', False)),
    #image(False, ('ppc64le-unknown-elf', 'ppc64le', False)),
    # Fails during compiling due to:
    #   undefined reference to `__init'
    # Adding -msim or -mads does not fix it.
    #image(False, ('ppc-unknown-eabi', 'ppc', False)),
    #image(False, ('ppcle-unknown-eabi', 'ppcle', False)),
    # Binutils does not support PPC64 and PPC64LE with EABI:
    #   BFD does not support target powerpc64-unknown-eabi.
    #image(False, ('ppc64-unknown-eabi', 'ppc64', False)),
    #image(False, ('ppc64le-unknown-eabi', 'ppc64le', False)),
    # GCC does not support SPEELF:
    #   Configuration powerpc-unknown-elfspe not supported
    #image(False, ('ppc-unknown-spe', 'ppc', False)),
    #image(False, ('ppcle-unknown-spe', 'ppcle', False)),
    #image(False, ('ppc64-unknown-spe', 'ppc64', False)),
    #image(False, ('ppc64le-unknown-spe', 'ppc64le', False)),
    image(True, ('ppcle-unknown-linux-gnu', 'ppcle', False)),
    # Fails with custom build of stock GCC:
    #   rv32i-based targets are not supported on stock GCC.
    #image(True, ('riscv32-unknown-linux-gnu', 'riscv32', False)),
    image(True, ('s390-unknown-linux-gnu', 's390', False)),
    # Fails during building binutils:
    #   checking for suffix of executables...
    #   make[2]: *** [Makefile:7088: configure-ld] Error 1
    #image(False, ('s390-unknown-elf', 's390', False)),
    #image(False, ('s390x-unknown-elf', 's390x', False)),
    image(False, ('sh1-unknown-elf', 'sh1', False, 'sh-unknown-elf')),
    image(False, ('sh2-unknown-elf', 'sh2', False, 'sh-unknown-elf')),
    image(False, ('sh2e-unknown-elf', 'sh2e', False, 'sh-unknown-elf')),
    image(False, ('sh3-unknown-elf', 'sh3', False, 'sh-unknown-elf')),
    image(True, ('sh3-unknown-linux-gnu', 'sh3', False)),
    image(True, ('sh3be-unknown-linux-gnu', 'sh3eb', False)),
    image(False, ('sh3e-unknown-elf', 'sh3e', False, 'sh-unknown-elf')),
    # Currently fails due to undefined reference to `__fpscr_values`.
    #image(True, ('sh3e-unknown-linux-gnu', 'sh3e', False)),
    image(False, ('sh4-100-unknown-elf', 'sh4', False, 'sh-unknown-elf')),
    image(False, ('sh4-200-unknown-elf', 'sh4', False, 'sh-unknown-elf')),
    image(False, ('sh4-300-unknown-elf', 'sh4', False, 'sh-unknown-elf')),
    image(False, ('sh4-340-unknown-elf', 'sh4', False, 'sh-unknown-elf')),
    image(False, ('sh4-500-unknown-elf', 'sh4', False, 'sh-unknown-elf')),
    image(False, ('sh4-unknown-elf', 'sh4', False, 'sh-unknown-elf')),
    image(False, ('sh4a-unknown-elf', 'sh4', False, 'sh-unknown-elf')),
    image(True, ('sh4be-unknown-linux-gnu', 'sh4eb', True)),
    # Fails during building libc pass 2:
    #   "multiple definition of `_errno'".
    #image(False, ('sh*be*-unknown-elf', 'sh', False, 'shbe-unknown-elf')),
    image(False, ('sparc-unknown-elf', 'sparc', False)),
    # Fails during building newlib due to:
    #   error: argument 'dirp' doesn't match prototype
    #image(False, ('sparc64-unknown-elf', 'sparc64', False)),
    # Fails in libc build pass 1:
    #   glibc 2.23+ do not support only support SPARCv9, and
    #   there's bugs with older glibc versions.
    #image(True, ('sparc-unknown-linux-gnu', 'sparc', True)),
    # Note: requires GCC-8, due to invalid register clobbing with source and dest.
    image(True, ('sparc-unknown-linux-uclibc', 'sparc', True)),
    image(False, ('thumb-unknown-elf', 'arm', False, 'arm-unknown-elf')),
    image(False, ('thumbeb-unknown-elf', 'armeb', False, 'armeb-unknown-elf')),
    image(True, ('thumbeb-unknown-linux-gnueabi', 'armeb', True, 'armeb-unknown-linux-gnueabi')),
    image(True, ('x86_64-multilib-linux-musl', 'x86_64', True)),
    image(False, ('x86_64-unknown-elf', 'x86_64', False)),
    image(True, ('x86_64-unknown-linux-uclibc', 'x86_64', True)),
    image(True, ('x86_64-w64-mingw32', 'x86_64', False)),
    # Fails during building libc pass 1:
    #   Newlib does not support Xtensa.
    #image(False, ('xtensa-unknown-elf', 'xtensa', False)),
    #image(False, ('xtensabe-unknown-elf', 'xtensaeb', False)),
    # Fails in libc build pass 2:
    #   little endian output does not match Xtensa configuration
    #image(True, ('xtensa-unknown-linux-uclibc', 'xtensa', True)),
    # Note: Qemu currently fails, but seems to be a Qemu error, since
    # the instructions seem to all be valid.
    image(True, ('xtensabe-unknown-linux-uclibc', 'xtensaeb', True)),
]
debian_images = [
    # Template:
    #   ('target', 'cc', 'libc6', 'arch'),
    image(True, ('alpha-unknown-linux-gnu', 'g++-10-alpha-linux-gnu', 'libc6.1-alpha-cross', 'alpha')),
    image(True, ('arm64-unknown-linux-gnu', 'g++-10-aarch64-linux-gnu', 'libc6-arm64-cross', 'aarch64')),
    image(True, ('armel-unknown-linux-gnueabi', 'g++-10-arm-linux-gnueabi', 'libc6-armel-cross', 'arm')),
    image(True, ('armelhf-unknown-linux-gnueabi', 'g++-10-arm-linux-gnueabihf', 'libc6-armel-armhf-cross', 'arm')),
    image(True, ('hppa-unknown-linux-gnu', 'g++-10-hppa-linux-gnu', 'libc6-hppa-cross', 'hppa')),
    image(True, ('i686-unknown-linux-gnu', 'g++-10-i686-linux-gnu', 'libc6-i386-cross', 'i386')),
    image(True, ('m68k-unknown-linux-gnu', 'g++-10-m68k-linux-gnu', 'libc6-m68k-cross', 'm68k')),
    image(True, ('mips-unknown-linux-gnu', 'g++-10-mips-linux-gnu', 'libc6-mips-cross', 'mips')),
    image(True, ('mips64-unknown-linux-gnu', 'g++-10-mips64-linux-gnuabi64', 'libc6-mips64-cross', 'mips64')),
    image(True, ('mips64el-unknown-linux-gnu', 'g++-10-mips64el-linux-gnuabi64', 'libc6-mips64el-cross', 'mips64el')),
    image(True, ('mips64r6-unknown-linux-gnu', 'g++-10-mipsisa64r6-linux-gnuabi64', 'libc6-mips64r6-cross', 'mips64')),
    image(True, ('mips64r6el-unknown-linux-gnu', 'g++-10-mipsisa64r6el-linux-gnuabi64', 'libc6-mips64r6el-cross', 'mips64el')),
    image(True, ('mipsel-unknown-linux-gnu', 'g++-10-mipsel-linux-gnu', 'libc6-mipsel-cross', 'mipsel')),
    image(True, ('mipsr6-unknown-linux-gnu', 'g++-10-mipsisa32r6-linux-gnu', 'libc6-mipsr6-cross', 'mips')),
    image(True, ('mipsr6el-unknown-linux-gnu', 'g++-10-mipsisa32r6el-linux-gnu', 'libc6-mipsr6el-cross', 'mipsel')),
    image(True, ('ppc-unknown-linux-gnu', 'g++-10-powerpc-linux-gnu', 'libc6-powerpc-cross', 'ppc')),
    image(True, ('ppc64-unknown-linux-gnu', 'g++-10-powerpc64-linux-gnu', 'libc6-ppc64-cross', 'ppc64')),
    image(True, ('ppc64le-unknown-linux-gnu', 'g++-10-powerpc64le-linux-gnu', 'libc6-ppc64el-cross', 'ppc64le')),
    image(True, ('riscv64-unknown-linux-gnu', 'g++-10-riscv64-linux-gnu', 'libc6-riscv64-cross', 'riscv64')),
    image(True, ('s390x-unknown-linux-gnu', 'g++-10-s390x-linux-gnu', 'libc6-s390-s390x-cross', 's390x')),
    image(True, ('sh4-unknown-linux-gnu', 'g++-10-sh4-linux-gnu', 'libc6-sh4-cross', 'sh4')),
    image(True, ('sparc64-unknown-linux-gnu', 'g++-10-sparc64-linux-gnu', 'libc6-sparc64-cross', 'sparc64')),
    image(True, ('thumbel-unknown-linux-gnueabi', 'g++-10-arm-linux-gnueabi', 'libc6-armel-cross', 'arm')),
    image(True, ('thumbelhf-unknown-linux-gnueabi', 'g++-10-arm-linux-gnueabihf', 'libc6-armel-armhf-cross', 'arm')),
    image(True, ('x86_64-unknown-linux-gnu', 'g++-10', 'libc6', 'x86_64')),
]
riscv_images = [
    # Template:
    #   ('target', 'arch', with_qemu),
    image(True, ('riscv32-multilib-linux-gnu', 'riscv32', True)),
    image(False, ('riscv32-unknown-elf', 'riscv32', False)),
    image(True, ('riscv64-multilib-linux-gnu', 'riscv64', True)),
    image(False, ('riscv64-unknown-elf', 'riscv64', False)),
]
other_images = [
    image(True, ('wasm')),
]

class ConfigureCommand(VersionCommand):
    '''Modify all configuration files.'''

    description = 'configure template files'

    def configure_dockerfile(self, target, template, with_qemu, replacements):
        '''Configure a Dockerfile from template.'''

        outfile = f'{HOME}/docker/Dockerfile.{target}'
        qemu = f'{HOME}/docker/Dockerfile.qemu.in'
        symlink = f'{HOME}/docker/Dockerfile.symlink.in'
        toolchain = f'{HOME}/docker/Dockerfile.toolchain.in'
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
        contents = '\n'.join(contents)
        contents = self.replace(contents, replacements)
        self.write_file(outfile, contents, False)

    def configure_android(self, target, arch):
        '''Configure an Android-SDK image.'''

        template = f'{HOME}/docker/Dockerfile.android.in'
        self.configure_dockerfile(target, template, False, [
            ('ARCH', arch),
            ('TARGET', target),
        ])

    def configure_crosstool(self, target, arch, with_qemu, config=None):
        '''Configure a crosstool-NG image.'''

        template = f'{HOME}/docker/Dockerfile.crosstool.in'
        if config is None:
            config = target
        self.configure_dockerfile(target, template, with_qemu, [
            ('ARCH', arch),
            ('CONFIG', config),
            ('TARGET', target),
        ])

    def configure_debian(self, target, gxx, libc, arch):
        '''Configure a debian-based docker file.'''

        template = f'{HOME}/docker/Dockerfile.debian.in'
        self.configure_dockerfile(target, template, True, [
            ('G++', gxx),
            ('LIBC', libc),
            ('ARCH', arch),
            ('TARGET', target),
        ])

    def configure_riscv(self, target, arch, with_qemu):
        '''Configure a RISC-V-based image.'''

        template = f'{HOME}/docker/Dockerfile.riscv.in'
        self.configure_dockerfile(target, template, with_qemu, [
            ('ARCH', arch),
            ('TARGET', target),
        ])

    def run(self):
        '''Modify configuration files.'''

        VersionCommand.run(self)

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

        # Configure images.
        for image in android_images:
            self.configure_android(*image.arguments)
        for image in crosstool_images:
            self.configure_crosstool(*image.arguments)
        for image in debian_images:
            self.configure_debian(*image.arguments)
        for image in riscv_images:
            self.configure_riscv(*image.arguments)

        # Need to write the total image list.
        images = android_images + crosstool_images + debian_images + riscv_images
        os_images = sorted([i.arguments[0] for i in images if i.os])
        metal_images = sorted([i.arguments[0] for i in images if not i.os])
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
