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

# IMPORTS
# -------

import collections
import enum
import glob
import itertools
import json
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

# CONFIG
# ------

def load_json(path):
    '''Load JSON files with C++-style comments.'''

    # Note: we need comments for maintainability, so we
    # can annotate what works and the rationale, but
    # we don't want to prevent code from working without
    # a complex parser, so we do something very simple:
    # only remove lines starting with '//'.
    with open(path) as file:
        lines = file.read().splitlines()
    lines = [i for i in lines if not i.strip().startswith('//')]
    return json.loads('\n'.join(lines))

HOME = os.path.dirname(os.path.realpath(__file__))
config = load_json(f'{HOME}/config/config.json')

def get_version(key):
    '''Get the version data from the JSON config.'''

    data = config[key]['version']
    major = data[f'major']
    minor = data[f'minor']
    patch = data.get(f'patch', '')
    build = data.get(f'build', '')

    return (major, minor, patch, build)

# Read the xcross version information.
major, minor, patch, build = get_version('xcross')
version = f'{major}.{minor}'
if patch != '0' or build != '':
    version = f'{version}.{patch}'
if build != '':
    version = f'{version}-{build}'
py2exe_version = f'{major}.{minor}.{patch}'

# Read the dependency version information.
# This is the GCC and other utilities version from crosstool-NG.
gcc_major, gcc_minor, gcc_patch, _ = get_version('gcc')
gcc_version = f'{gcc_major}.{gcc_minor}.{gcc_patch}'
mingw_major, mingw_minor, mingw_patch, _ = get_version('mingw')
mingw_version = f'{mingw_major}.{mingw_minor}.{mingw_patch}'
glibc_major, glibc_minor, _, _ = get_version('glibc')
glibc_version = f'{glibc_major}.{glibc_minor}'
musl_major, musl_minor, musl_patch, _ = get_version('musl')
musl_version = f'{musl_major}.{musl_minor}.{musl_patch}'
avr_major, avr_minor, avr_patch, _ = get_version('avr')
avr_version = f'{avr_major}.{avr_minor}.{avr_patch}'
uclibc_major, uclibc_minor, uclibc_patch, _ = get_version('uclibc')
uclibc_version = f'{uclibc_major}.{uclibc_minor}.{uclibc_patch}'
expat_major, expat_minor, expat_patch, _ = get_version('expat')
expat_version = f'{expat_major}.{expat_minor}.{expat_patch}'
ct_major, ct_minor, ct_patch, _ = get_version('crosstool-ng')
ct_version = f'{ct_major}.{ct_minor}.{ct_patch}'
qemu_major, qemu_minor, qemu_patch, _ = get_version('qemu')
qemu_version = f'{qemu_major}.{qemu_minor}.{qemu_patch}'
riscv_toolchain_version = config['riscv-gnu-toolchain']['riscv-version']
riscv_binutils_version = config['riscv-gnu-toolchain']['binutils-version']
riscv_gdb_version = config['riscv-gnu-toolchain']['gdb-version']
riscv_glibc_version = config['riscv-gnu-toolchain']['glibc-version']
riscv_newlib_version = config['riscv-gnu-toolchain']['newlib-version']

# Other config options.
bin_directory = f'{config["options"]["sysroot"]}/bin/'

# Read the long description.
description = 'Zero-setup cross compilation.'
with open(f'{HOME}/README.md') as file:
    long_description = file.read()

# COMMANDS
# --------

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
            ('BIN', f'"{bin_directory}"'),
            ('VERSION_MAJOR', f"'{major}'"),
            ('VERSION_MINOR', f"'{minor}'"),
            ('VERSION_PATCH', f"'{patch}'"),
            ('VERSION_BUILD', f"'{build}'"),
            ('VERSION_INFO', f"version_info(major='{major}', minor='{minor}', patch='{patch}', build='{build}')"),
            ('VERSION', f"'{version}'"),
        ])

# IMAGES
# ------

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
    Script = enum.auto()
    Windows = enum.auto()

    def is_baremetal(self):
        return self == OperatingSystem.BareMetal

    def is_script(self):
        return self == OperatingSystem.Script

    def is_os(self):
        return not (self.is_baremetal() or self.is_script())

    def to_triple(self):
        '''Get the identifier as a triple string.'''
        return triple_string[self]

    def to_cmake(self):
        '''Get the identifier for the CMake operating system name.'''
        return cmake_string[self]

    @staticmethod
    def from_triple(string):
        '''Get the operating system from a triple string.'''
        return triple_os[string]

    @staticmethod
    def from_cmake(string):
        '''Get the operating system from a CMake string.'''
        return cmake_os[string]

cmake_string = {
    OperatingSystem.Android: 'Android',
    OperatingSystem.BareMetal: 'Generic',
    # script is not implemented
    OperatingSystem.Linux: 'Linux',
    OperatingSystem.Windows: 'Windows',
}
triple_string = {
    OperatingSystem.Android: 'linux',
    OperatingSystem.BareMetal: None,
    OperatingSystem.Script: 'script',
    OperatingSystem.Linux: 'linux',
    OperatingSystem.Windows: 'w64',
}
cmake_os = {v: k for k, v in cmake_string.items()}
triple_os = {v: k for k, v in triple_string.items()}

def extract_triple(triple):
    '''Extract components from the LLVM triple.'''

    # Due to how we designed this, we can only
    #   1. Omit the vendor, os and system.
    #   2. Omit the vendor.
    #   3. Omit the os.
    #   4. Have all 4 components.
    split = triple.split('-')
    arch = split[0]
    if len(split) == 1:
        # ('arch',) format.
        vendor = None
        os = OperatingSystem.BareMetal
        system = None
    elif len(split) == 3 and split[2] == 'mingw32':
        # ('arch', 'vendor', 'system')
        vendor = None
        os = OperatingSystem.Windows
        system = split[2]
    elif len(split) == 3:
        # ('arch', 'vendor', 'system')
        vendor = split[1]
        os = OperatingSystem.BareMetal
        system = split[2]
    elif len(split) == 4:
        # ('arch', 'vendor', 'os', 'system')
        vendor = split[1]
        os = OperatingSystem.from_triple(split[2])
        system = split[3]
    else:
        raise ValueError(f'Invalid LLVM triple, got {triple}')
    return (arch, vendor, os, system)

class Image:
    '''
    Parameters (and defaults) for custom images.

    * `target` - Image name of the target (resembling an LLVM triple).
    * `triple` - LLVM triple of the target. (arch, vendor, os, system)
    '''

    def __init__(self, target, triple=None, **kwds):
        self.target = target
        self.triple = triple or target
        self.arch, self.vendor, self.os, self.system = extract_triple(self.triple)
        for key, value in kwds.items():
            setattr(self, key, value)

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    @staticmethod
    def from_json(data):
        image_type = data.pop('type')
        return image_types[image_type].from_dict(data)

    @property
    def flags(self):
        return getattr(self, '_flags', '')

    @flags.setter
    def flags(self, value):
        self._flags = value

    @property
    def cflags(self):
        flags = self.flags
        if flags:
            return f'CFLAGS="{flags}" '
        return ''

    @property
    def os(self):
        return self._os

    @os.setter
    def os(self, value):
        if isinstance(value, str):
            value = OperatingSystem.from_triple(value)
        self._os = value

class AndroidImage(Image):
    '''Specialized properties for Android images.'''

    @property
    def os(self):
        return OperatingSystem.Android

    @os.setter
    def os(self, _):
        pass

    @property
    def abi(self):
        return getattr(self, '_abi', self.arch)

    @abi.setter
    def abi(self, value):
        self._abi = value

    @property
    def prefix(self):
        return getattr(self, '_prefix', self.arch)

    @prefix.setter
    def prefix(self, value):
        self._prefix = value

    @property
    def toolchain(self):
        return f'{self.arch}-linux-{self.system}'

    @property
    def qemu(self):
        return False

class CrosstoolImage(Image):
    '''Specialized properties for crosstool-NG images.'''

    @property
    def config(self):
        return getattr(self, '_config', self.target)

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def processor(self):
        return getattr(self, '_processor', self.arch)

    @processor.setter
    def processor(self, value):
        self._processor = value

    @property
    def qemu(self):
        return getattr(self, '_qemu', False)

    @qemu.setter
    def qemu(self, value):
        self._qemu = value

class DebianImage(Image):
    '''Specialized properties for Debian images.'''

    @property
    def cxx(self):
        default = f'g++-{{version}}-{self.processor}-{self.os.to_triple()}-{self.system}'
        return getattr(self, '_cxx', default).format(version=gcc_major)

    @cxx.setter
    def cxx(self, value):
        self._cxx = value

    @property
    def libc(self):
        default = f'libc6-{self.arch}-cross'
        return getattr(self, '_libc', default)

    @libc.setter
    def libc(self, value):
        self._libc = value

    @property
    def prefix(self):
        return getattr(self, '_prefix', self.processor)

    @prefix.setter
    def prefix(self, value):
        self._prefix = value

    @property
    def processor(self):
        return getattr(self, '_processor', self.arch)

    @processor.setter
    def processor(self, value):
        self._processor = value

    @property
    def qemu(self):
        return True

class RiscvImage(Image):
    '''Specialized properties for RISC-V images.'''

    @property
    def processor(self):
        return self.target.split('-')[0]

    @property
    def qemu(self):
        return getattr(self, '_qemu', False)

    @qemu.setter
    def qemu(self, value):
        self._qemu = value

    @property
    def bits(self):
        return int(re.match(r'^riscv(\d+)$', self.processor).group(1))

    @property
    def cflags(self):
        march = f'rv{self.bits}{self.extensions}'
        flags = f'-march={march} -mabi={self.abi}'
        if self.flags:
            flags= f'{self.flags} {flags}'
        return f'CFLAGS="{flags}" '

class OtherImage(Image):
    '''Specialized properties for miscellaneous images.'''

image_types = {
    'android': AndroidImage,
    'crosstool': CrosstoolImage,
    'debian': DebianImage,
    'riscv': RiscvImage,
    'other': OtherImage,
}

# Get all images.
images = [Image.from_json(i) for i in load_json(f'{HOME}/config/images.json')]

# Add extensions
def add_android_extensions():
    '''Add Android extensions (null-op).'''

def add_crosstool_extensions():
    '''Add crosstool-NG toolchain extensions (null-op).'''

def add_debian_extensions():
    '''Add Debian toolchain extensions (null-op).'''

# Add our RISC-V images with extensions.
def create_riscv_image(os, bits, arch, abi):
    '''Create a RISC-V image.'''

    prefix = f'riscv{bits}-{arch}-{abi}'
    if os == OperatingSystem.Linux:
        target = f'{prefix}-multilib-linux-gnu'
        triple = 'riscv64-unknown-linux-gnu'
        qemu = True
    elif os == OperatingSystem.BareMetal:
        target = f'{prefix}-unknown-elf'
        triple = 'riscv64-unknown-elf'
        qemu = False
    else:
        raise ValueError(f'Unknown operating system {os.to_triple()}')

    return RiscvImage.from_dict({
        'target': target,
        'triple': triple,
        'qemu': qemu,
        'extensions': arch,
        'abi': abi
    })

def add_riscv_extensions():
    '''Add RISC-V extensions.'''

    riscv = config['riscv-gnu-toolchain']
    bits = riscv['bits']
    extensions = riscv['extensions']
    for key in extensions:
        os = OperatingSystem.from_triple(extensions[key]['type'])
        required_ext = extensions[key]['required']
        all_ext = extensions[key]['all']
        diff = ''.join([i for i in all_ext if i not in required_ext])
        for bits in riscv['bits']:
            abi = riscv['abi'][bits]
            for count in range(len(diff) + 1):
                for combo in itertools.combinations(diff, count):
                    arch = f'{required_ext}{"".join(combo)}'
                    images.append(create_riscv_image(os, bits, arch, abi))
                    if 'd' in arch:
                        images.append(create_riscv_image(os, bits, arch, f'{abi}d'))

def add_extensions():
    '''Add extensions for supported operating systems.'''

    add_android_extensions()
    add_crosstool_extensions()
    add_debian_extensions()
    add_riscv_extensions()

add_extensions()

# Filter images by types.
android_images = [i for i in images if isinstance(i, AndroidImage)]
crosstool_images = [i for i in images if isinstance(i, CrosstoolImage)]
debian_images = [i for i in images if isinstance(i, DebianImage)]
riscv_images = [i for i in images if isinstance(i, RiscvImage)]
other_images = [i for i in images if isinstance(i, OtherImage)]

def create_array(values):
    '''Create a bash array from a list of values.'''

    start = "(\n    \""
    joiner = "\"\n    \""
    end = "\"\n)"
    return start + joiner.join(values) + end

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
            ('CLANG_VERSION', config['android']['clang_version']),
            ('NDK_DIRECTORY', config['android']['ndk_directory']),
            ('NDK_VERSION', config['android']['ndk_version']),
            ('PREFIXES', create_array([i.prefix for i in android_images])),
            ('TOOLCHAINS', create_array([i.toolchain for i in android_images]))
        ])
        self.configure(f'{cmake}.in', cmake, True, [
            ('UBUNTU_NAME', config['ubuntu']['version']['name']),
        ])
        self.configure(f'{entrypoint}.in', entrypoint, True, [
            ('BIN', f'"{bin_directory}"'),
        ])
        self.configure(f'{gcc}.in', gcc, True, [
            ('CROSSTOOL_VERSION', f'"{ct_version}"'),
            ('JOBS', config["options"]["build_jobs"]),
        ])
        self.configure(f'{qemu}.in', qemu, True, [
            ('JOBS', config["options"]["build_jobs"]),
            ('QEMU_VERSION', qemu_version),
            ('SYSROOT', f'"{config["options"]["sysroot"]}"'),
        ])
        self.configure(f'{qemu_apt}.in', qemu_apt, True, [
            ('BIN', f'"{bin_directory}"'),
        ])
        self.configure(f'{riscv_gcc}.in', riscv_gcc, True, [
            ('BINUTILS_VERSION', riscv_binutils_version),
            ('GCC_VERSION', gcc_version),
            ('GDB_VERSION', riscv_gdb_version),
            ('GLIBC_VERSION', riscv_glibc_version),
            ('JOBS', config["options"]["build_jobs"]),
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
        self.configure_dockerfile(image.target, template, image.qemu, [
            ('ARCH', image.arch),
            ('BIN', f'"{bin_directory}"'),
            ('ENTRYPOINT', f'"{bin_directory}/entrypoint.sh"'),
            ('TARGET', image.target),
            ('TOOLCHAIN', image.toolchain),
        ])

        # Configure the CMake toolchain.
        cmake_template = f'{HOME}/cmake/android.cmake.in'
        cmake = f'{HOME}/cmake/toolchain/{image.target}.cmake'
        os = image.os.to_cmake()
        self.configure(cmake_template, cmake, False, [
            ('ABI', image.abi),
            ('NDK_DIRECTORY', config['android']['ndk_directory']),
            ('SDK_VERSION', config['android']['sdk_version']),
        ])

        # Configure the symlinks.
        symlink_template = f'{HOME}/symlink/android.sh.in'
        symlink = f'{HOME}/symlink/toolchain/{image.target}.sh'
        self.configure(symlink_template, symlink, True, [
            ('FLAGS', image.cflags),
            ('NDK_DIRECTORY', config['android']['ndk_directory']),
            ('PREFIX', f'{image.prefix}-linux-{image.system}'),
            ('SDK_VERSION', config['android']['sdk_version']),
            ('TOOLCHAIN', image.toolchain),
        ])

    def configure_crosstool(self, image):
        '''Configure a crosstool-NG image.'''

        # Configure the dockerfile.
        template = f'{HOME}/docker/Dockerfile.crosstool.in'
        self.configure_dockerfile(image.target, template, image.qemu, [
            ('ARCH', image.processor),
            ('BIN', f'"{bin_directory}"'),
            ('CONFIG', image.config),
            ('ENTRYPOINT', f'"{bin_directory}/entrypoint.sh"'),
            ('TARGET', image.target),
        ])

        # Get the proper dependent parameters for our image.
        os = image.os.to_cmake()
        if image.os == OperatingSystem.BareMetal:
            cmake_template = f'{HOME}/cmake/crosstool-elf.cmake.in'
            symlink_template = f'{HOME}/symlink/crosstool.sh.in'
        elif image.qemu:
            cmake_template = f'{HOME}/cmake/crosstool-os-qemu.cmake.in'
            symlink_template = f'{HOME}/symlink/crosstool-qemu.sh.in'
        else:
            cmake_template = f'{HOME}/cmake/crosstool-os.cmake.in'
            symlink_template = f'{HOME}/symlink/crosstool.sh.in'

        # Configure the CMake toolchain.
        cmake = f'{HOME}/cmake/toolchain/{image.target}.cmake'
        self.configure(cmake_template, cmake, False, [
            ('TRIPLE', image.triple),
            ('PROCESSOR', image.processor),
            ('OS', os),
        ])

        # Configure the symlinks.
        symlink = f'{HOME}/symlink/toolchain/{image.target}.sh'
        self.configure(symlink_template, symlink, True, [
            ('ARCH', image.processor),
            ('FLAGS', image.cflags),
            ('TRIPLE', image.triple),
        ])

    def configure_debian(self, image):
        '''Configure a debian-based docker file.'''

        # Configure the dockerfile.
        template = f'{HOME}/docker/Dockerfile.debian.in'
        self.configure_dockerfile(image.target, template, image.qemu, [
            ('ARCH', image.processor),
            ('BIN', f'"{bin_directory}"'),
            ('ENTRYPOINT', f'"{bin_directory}/entrypoint.sh"'),
            ('G++', image.cxx),
            ('LIBC', image.libc),
            ('TARGET', image.target),
        ])

        # Get the proper dependent parameters for our image.
        if image.os != OperatingSystem.Linux:
            raise NotImplementedError

        os = image.os.to_cmake()
        if image.target == 'x86_64-unknown-linux-gnu':
            cmake_template = f'{HOME}/cmake/native.cmake.in'
            symlink_template = f'{HOME}/symlink/native.sh.in'
        else:
            cmake_template = f'{HOME}/cmake/debian.cmake.in'
            symlink_template = f'{HOME}/symlink/debian.sh.in'

        # Configure the CMake toolchain.
        cmake = f'{HOME}/cmake/toolchain/{image.target}.cmake'
        self.configure(cmake_template, cmake, False, [
            ('PROCESSOR', image.processor),
            ('OS', os),
        ])

        # Configure the symlinks.
        symlink = f'{HOME}/symlink/toolchain/{image.target}.sh'
        self.configure(symlink_template, symlink, True, [
            ('FLAGS', image.cflags),
            ('GCC_MAJOR', gcc_major),
            ('PREFIX', image.prefix),
            ('PROCESSOR', image.processor),
            ('OS', image.os.to_triple()),
            ('SYSTEM', image.system),
        ])

    def configure_riscv(self, image):
        '''Configure a RISC-V-based image.'''

        # Get the proper dependent parameters for our image.
        os = image.os.to_cmake()
        if image.os == OperatingSystem.Linux:
            cmake_template = f'{HOME}/cmake/riscv-linux.cmake.in'
        elif image.os == OperatingSystem.BareMetal:
            cmake_template = f'{HOME}/cmake/riscv-elf.cmake.in'
        else:
            raise NotImplementedError
        if image.qemu:
            symlink_template = f'{HOME}/symlink/riscv-qemu.sh.in'
        else:
            symlink_template = f'{HOME}/symlink/riscv.sh.in'

        # Configure the dockerfile.
        template = f'{HOME}/docker/Dockerfile.riscv.in'
        self.configure_dockerfile(image.target, template, image.qemu, [
            ('ARCH', image.processor),
            ('BIN', f'"{bin_directory}"'),
            ('ENTRYPOINT', f'"{bin_directory}/entrypoint.sh"'),
            ('TARGET', image.target),
            ('TRIPLE', image.triple),
        ])

        # Configure the CMake toolchain.
        cmake = f'{HOME}/cmake/toolchain/{image.target}.cmake'
        self.configure(cmake_template, cmake, False, [
            ('PROCESSOR', image.processor),
            ('OS', os),
        ])

        # Configure the symlinks.
        symlink = f'{HOME}/symlink/toolchain/{image.target}.sh'
        self.configure(symlink_template, symlink, True, [
            ('ARCH', image.processor),
            ('FLAGS', image.cflags),
            ('TRIPLE', image.triple),
        ])

    def configure_other(self, image):
        '''Configure a miscellaneous image.'''

        template = f'{HOME}/docker/Dockerfile.{image.target}.in'
        dockerfile = f'{HOME}/docker/images/Dockerfile.{image.target}'
        with open(template) as file:
            contents = file.read()
        self.write_file(dockerfile, contents, False)

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
        ubuntu = config["ubuntu"]["version"]
        self.configure(base_template, base, False, [
            ('UBUNTU_VERSION', f'{ubuntu["major"]}.{ubuntu["minor"]}'),
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
        for image in other_images:
            self.configure_other(image)

        # Need to write the total image list.
        metal_images = sorted([i.target for i in images if i.os.is_baremetal()])
        script_images = sorted([i.target for i in images if i.os.is_script()])
        os_images = sorted([i.target for i in images if i.os.is_os()])
        self.configure(f'{images_sh}.in', images_sh, True, [
            ('OS_IMAGES', create_array(os_images)),
            ('METAL_IMAGES', create_array(metal_images)),
            ('SCRIPT_IMAGES', create_array(script_images)),
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
