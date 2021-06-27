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
import subprocess
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
if patch != '0':
    version = f'{version}.{patch}'
py2exe_version = f'{major}.{minor}.{patch}'

docker_major, docker_minor, docker_patch, docker_build = get_version('docker')
docker_version = f'{docker_major}.{docker_minor}'
if docker_patch != '0':
    docker_version = f'{docker_version}.{docker_patch}'

# Read the dependency version information.
# This is the GCC and other utilities version from crosstool-NG.
gcc_major, gcc_minor, gcc_patch, _ = get_version('gcc')
gcc_version = f'{gcc_major}.{gcc_minor}.{gcc_patch}'
binutils_major, binutils_minor, _, _ = get_version('binutils')
binutils_version = f'{binutils_major}.{binutils_minor}'
mingw_major, mingw_minor, mingw_patch, _ = get_version('mingw')
mingw_version = f'{mingw_major}.{mingw_minor}.{mingw_patch}'
glibc_major, glibc_minor, _, _ = get_version('glibc')
glibc_version = f'{glibc_major}.{glibc_minor}'
musl_major, musl_minor, musl_patch, _ = get_version('musl')
musl_version = f'{musl_major}.{musl_minor}.{musl_patch}'
musl_cross_major, musl_cross_minor, musl_cross_patch, _ = get_version('musl-cross')
musl_cross_version = f'{musl_cross_major}.{musl_cross_minor}.{musl_cross_patch}'
avr_major, avr_minor, avr_patch, _ = get_version('avr')
avr_version = f'{avr_major}.{avr_minor}.{avr_patch}'
uclibc_major, uclibc_minor, uclibc_patch, _ = get_version('uclibc')
uclibc_version = f'{uclibc_major}.{uclibc_minor}.{uclibc_patch}'
expat_major, expat_minor, expat_patch, _ = get_version('expat')
expat_version = f'{expat_major}.{expat_minor}.{expat_patch}'
isl_major, isl_minor, _, _ = get_version('isl')
isl_version = f'{isl_major}.{isl_minor}'
linux_major, linux_minor, linux_patch, _ = get_version('linux')
linux_version = f'{linux_major}.{linux_minor}.{linux_patch}'
linux_headers_major, linux_headers_minor, linux_headers_patch, _ = get_version('linux-headers')
linux_headers_version = f'{linux_headers_major}.{linux_headers_minor}.{linux_headers_patch}'
gmp_major, gmp_minor, gmp_patch, _ = get_version('gmp')
gmp_version = f'{gmp_major}.{gmp_minor}.{gmp_patch}'
mpc_major, mpc_minor, mpc_patch, _ = get_version('mpc')
mpc_version = f'{mpc_major}.{mpc_minor}.{mpc_patch}'
mpfr_major, mpfr_minor, mpfr_patch, _ = get_version('mpfr')
mpfr_version = f'{mpfr_major}.{mpfr_minor}.{mpfr_patch}'
buildroot_major, buildroot_minor, buildroot_patch, _ = get_version('buildroot')
buildroot_version = f'{buildroot_major}.{buildroot_minor}.{buildroot_patch}'
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

def check_call(code):
    '''Wrap `subprocess.call` to exit on failure.'''

    if code != 0:
        sys.exit(code)

def has_module(module):
    '''Check if the given module is installed.'''

    devnull = subprocess.DEVNULL
    code = subprocess.call(
        [sys.executable, '-m', module, '--version'],
        stdout=devnull,
        stderr=devnull,
    )
    return code == 0

def semver():
    '''Create a list of semantic versions for images.'''

    versions = [
        f'{docker_major}.{docker_minor}',
        f'{docker_major}.{docker_minor}.{docker_patch}'
    ]
    if docker_major != '0':
        versions.append(docker_major)

    return versions

def image_from_target(target):
    '''Get the full image name from the target.'''

    username = config['metadata']['username']
    repository = config['metadata']['repository']
    return f'{username}/{repository}:{target}'

def sorted_image_targets():
    '''Get a sorted list of image targets.'''

    # Need to write the total image list.
    metal_images = sorted([i.target for i in images if i.os.is_baremetal()])
    script_images = sorted([i.target for i in images if i.os.is_script()])
    os_images = sorted([i.target for i in images if i.os.is_os()])
    return os_images + metal_images + script_images

def subslice_targets(start=None, stop=None):
    '''Extract a subslice of all targets.'''

    targets = sorted_image_targets()
    if start is not None:
        targets = targets[targets.index(start):]
    if stop is not None:
        targets = targets[:targets.index(stop)+1]
    return targets

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
        shutil.rmtree(f'{HOME}/musl/config', ignore_errors=True)
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

class TagCommand(Command):
    '''Scripts to automatically tag new versions.'''

    description = 'tag version for release'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        '''Tag version for git release.'''

        # Get our config.
        git = shutil.which('git')
        if not git:
            raise FileNotFoundError('Unable to find program git.')
        tag = f'v{version}'

        # Delete any existing, conflicting tags.
        devnull = subprocess.DEVNULL
        code = subprocess.call(
            f'GIT_DIR="{HOME}/.git" git rev-parse "{tag}"',
            shell=True,
            stdout=devnull,
            stderr=devnull,
        )
        if code == 0:
            check_call(subprocess.call(
                ['git', 'tag', '-d', tag],
                stdout=devnull,
                stderr=devnull,
            ))

        # Tag the release.
        check_call(subprocess.call(
            ['git', 'tag', tag],
            stdout=devnull,
            stderr=devnull,
        ))

class BuildImagesCommand(Command):
    '''Build all Docker images.'''

    description = 'build all docker images'
    user_options = [
        ('start=', None, 'Start point for test suite.'),
        ('stop=', None, 'Stop point for test suite.'),
    ]

    def initialize_options(self):
        self.start = None
        self.stop = None

    def finalize_options(self):
        pass

    def build_image(self, docker, target):
        '''Build a Docker image.'''

        command = [
            docker,
            'build',
            '-t',
            image_from_target(target),
            HOME,
            '--file',
            f'{HOME}/docker/images/Dockerfile.{target}'
        ]
        if subprocess.call(command) != 0:
            self.failures.append(target)
            return False
        return True

    def tag_image(self, docker, target, tag_name):
        '''Tag an image.'''

        image = image_from_target(target)
        tag = image_from_target(tag_name)
        check_call(subprocess.call([docker, 'tag', image, tag]))

    def build_versions(self, docker, target):
        '''Build all versions of a given target.'''

        if not self.build_image(docker, target):
            return
        for version in semver():
            self.tag_image(docker, target, f'{target}-{version}')
        if target.endswith('-unknown-linux-gnu'):
            self.tag_versions(docker, target, target[:-len('-unknown-linux-gnu')])

    def tag_versions(self, docker, target, tag_name):
        '''Build all versions of a given target.'''

        self.tag_image(docker, target, tag_name)
        for version in semver():
            self.tag_image(docker, target, f'{tag_name}-{version}')

    def run(self):
        '''Build all Docker images.'''

        docker = shutil.which('docker')
        if not docker:
            raise FileNotFoundError('Unable to find command docker.')

        # Push all our Docker images.
        self.failures = []
        self.build_versions(docker, 'base')
        for target in subslice_targets(self.start, self.stop):
            self.build_versions(docker, target)

        # Print any failures.
        if self.failures:
            print('Error: Failures occurred.')
            print('-------------------------')
            for failure in self.failures:
                print(failure)
            sys.exit(1)

class BuildAllCommand(BuildImagesCommand):
    '''Build Docker images and the Python library for dist.'''

    description = 'build all docker images and wheels for release'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        '''Build all images and package for release.'''

        BuildImagesCommand.run(self)
        self.run_command('clean')
        self.run_command('configure')
        self.run_command('build')
        self.run_command('sdist')
        self.run_command('bdist_wheel')

class BuildCommand(build_py):
    '''Override build.py to configure builds.'''

    def run(self):
        self.run_command('version')
        build_py.run(self)

class PushCommand(Command):
    '''Push all Docker images to Docker hub.'''

    description = 'push all docker images to docker hub'
    user_options = [
        ('start=', None, 'Start point for test suite.'),
        ('stop=', None, 'Stop point for test suite.'),
    ]

    def initialize_options(self):
        self.start = None
        self.stop = None

    def finalize_options(self):
        pass

    def push_image(self, docker, target):
        '''Push an image to Docker Hub.'''
        check_call(subprocess.call([docker, 'push', image_from_target(target)]))

    def push_versions(self, docker, target):
        '''Push all versions of a given target.'''

        self.push_image(docker, target)
        for version in semver():
            self.push_image(docker, f'{target}-{version}')

    def run(self):
        '''Push all Docker images to Docker hub.'''

        docker = shutil.which('docker')
        if not docker:
            raise FileNotFoundError('Unable to find command docker.')

        # Push all our Docker images.
        self.push_versions(docker, 'base')
        for target in subslice_targets(self.start, self.stop):
            self.push_versions(docker, target)
            if target.endswith('-unknown-linux-gnu'):
                self.push_versions(docker, target[:-len('-unknown-linux-gnu')])

class PublishCommand(Command):
    '''Publish a Python version.'''

    description = 'publish python version to PyPi'
    user_options = [
        ('test=', None, 'Upload to the test repository.'),
    ]

    def initialize_options(self):
        self.test = None

    def finalize_options(self):
        pass

    def run(self):
        '''Run the unittest suite.'''

        if not has_module('twine'):
            raise FileNotFoundError('Unable to find module twine.')
        self.run_command('clean')
        self.run_command('configure')
        self.run_command('build')
        self.run_command('sdist')
        self.run_command('bdist_wheel')
        if self.test:
            command = f'twine upload --repository testpypi {HOME}/dist/*'
        else:
            command = f'twine upload {HOME}/dist/*'
        check_call(subprocess.call(command, shell=True))

class TestCommand(Command):
    '''Run the unittest suite.'''

    description = 'run unittest suite'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        '''Run the unittest suite.'''

        if not has_module('tox'):
            raise FileNotFoundError('Unable to find module tox.')
        check_call(subprocess.call(['tox', HOME]))

class TestImagesCommand(Command):
    '''Run the Docker test suite.'''

    description = 'run docker test suite'
    user_options = [
        ('start=', None, 'Start point for test suite.'),
        ('stop=', None, 'Stop point for test suite.'),
        ('system=', None, 'Do full system tests.'),
    ]

    def initialize_options(self):
        self.start = None
        self.stop = None
        self.system = None

    def finalize_options(self):
        pass

    def git_clone(self, git, repository):
        '''Clone a given repository.'''
        check_call(subprocess.call([git, 'clone', repository, f'{HOME}/buildtests']))

    def run_test(
        self,
        docker,
        target,
        os_type,
        script=None,
        cpu=None,
        **envvars
    ):
        '''Run test for a single target.'''

        # Get our command.
        if script is None:
            script = 'image-test'
        command = f'/test/test/{script}.sh'
        if cpu is not None:
            command = f'export CPU={cpu}; {command}'

        # Check for additional flags.
        if self.nostartfiles(target):
            flags = envvars.get('FLAGS')
            if flags:
                flags = f'{flags} -nostartfiles'
            else:
                flags = '-nostartfiles'
            envvars['FLAGS'] = flags

        # Build and call our docker command.
        docker_command = [
            docker,
            'run',
            '-v', f'{HOME}:/test',
            '--env', f'IMAGE={target}',
            '--env', f'TYPE={os_type}',
        ]
        for key, value in envvars.items():
            docker_command += ['--env', f'{key}={value}']
        docker_command.append(image_from_target(target))
        docker_command += ['/bin/bash', '-c', command]
        subprocess.check_call(docker_command)

    def nostartfiles(self, target):
        '''Check if an image does not have startfiles.'''

        # i[3-6]86 does not provide start files, a known bug with newlib.
        # moxie cannot find `__bss_start__` and `__bss_end__`.
        # sparc cannot find `__stack`.
        # there is no crt0 for x86_64
        regex = re.compile(r'^(?:(?:i[3-7]86-unknown-elf)|(?:moxie.*-none-elf)|(?:sparc-unknown-elf)|(?:x86_64-unknown-elf))$')
        return regex.match(target)

    def skip(self, target):
        '''Check if we should skip a given target.'''

        # Check if we should skip a test.
        # PPCLE is linked to the proper library, which contains the
        # proper symbols, but still fails with an error:
        #   undefined reference to `_savegpr_29`.
        return target == 'ppcle-unknown-elf'

    def run_wasm(self, docker, **envvars):
        '''Run a web-assembly target.'''

        self.run_test(
            docker,
            'wasm',
            'script',
            **envvars,
            NO_PERIPHERALS='1',
            TOOLCHAIN1='jsonly',
            TOOLCHAIN2='wasm',
            TOOLCHAIN1_FLAGS='-s WASM=0',
            TOOLCHAIN2_FLAGS='-s WASM=1',
        )

    def run(self):
        '''Run the docker test suite.'''

        # Find our necessary commands.
        git = shutil.which('git')
        docker = shutil.which('docker')
        if not git:
            raise FileNotFoundError('Unable to find command git.')
        if not docker:
            raise FileNotFoundError('Unable to find command docker.')

        # Configure our test runner.
        has_started = True
        has_stopped = False
        if self.start is not None:
            has_started = False
        metal_images = sorted([i.target for i in images if i.os.is_baremetal()])
        os_images = sorted([i.target for i in images if i.os.is_os()])

        # Run OS images.
        self.git_clone(git, 'https://github.com/Alexhuszagh/cpp-helloworld.git')
        try:
            for target in os_images:
                if has_started or self.start == target:
                    has_started = True
                    if not self.skip(target):
                        self.run_test(docker, target, 'os')

                if self.stop == target:
                    has_stopped = True
                    break

            # Run the special images.
            if has_started and not has_stopped:
                self.run_wasm(docker)
                self.run_wasm(docker, CMAKE_FLAGS='-DJS_ONLY=1')
                self.run_test(docker, os_images[0], 'os', CMAKE_FLAGS='-GNinja')
                self.run_wasm(docker, CMAKE_FLAGS='-GNinja')
                self.run_test(docker, 'ppc-unknown-linux-gnu', 'os', cpu='e500mc', NORUN2='1')
                self.run_test(docker, 'ppc64-unknown-linux-gnu', 'os', cpu='power9')
                self.run_test(docker, 'mips-unknown-linux-gnu', 'os', cpu='24Kf')
        finally:
            shutil.rmtree(f'{HOME}/buildtests', ignore_errors=True)
        if has_stopped:
            return

        # Run metal images.
        self.git_clone(git, 'https://github.com/Alexhuszagh/cpp-atoi.git')
        try:
            for target in metal_images:
                if has_started or self.start == target:
                    has_started = True
                    if not self.skip(target):
                        self.run_test(docker, target, 'metal')

                if self.stop == target:
                    has_stopped = True
                    break
        finally:
            shutil.rmtree(f'{HOME}/buildtests', ignore_errors=True)
        if has_stopped:
            return

        # Check the full system tests.
        if self.system:
            self.run_test(docker, 'ppc-unknown-elf', 'metal', script='ppc-metal')

class TestAllCommand(TestImagesCommand):
    '''Run the Python and Docker test suites.'''

    def run(self):
        '''Run the docker test suite.'''

        self.run_command('test')
        TestImagesCommand.run(self)

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
    # This gets ignored anyway.
    OperatingSystem.Script: 'Script',
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

oses = {
    'linux': OperatingSystem.Linux,
    'none': OperatingSystem.BareMetal,
}

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
        # ('arch',)
        vendor = None
        os = OperatingSystem.BareMetal
        system = None
    elif len(split) == 2 and split[1] in oses:
        # ('arch', 'os')
        vendor = None
        os = oses[split[1]]
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
    def config(self):
        return getattr(self, '_config', self.target)

    @config.setter
    def config(self, value):
        self._config = value

    @property
    def hardcoded_cpulist(self):
        cpus = getattr(self, 'cpulist', '')
        if cpus:
            return f'export HARDCODED="{cpus}"\n'
        return ''

    @property
    def ld_library_path(self):
        path = getattr(self, 'library_path', '')
        if path:
            return f'export LD_LIBRARY_PATH="{path}"\n'
        return ''

    @property
    def ld_preload(self):
        path = getattr(self, 'preload', '')
        if path:
            return f'export LD_PRELOAD="{path}"\n'
        return ''

    @property
    def cc_cpu_list(self):
        cpulist = getattr(self, 'cc_cpulist', '')
        if cpulist:
            return f'export CC_CPU_LIST="{cpulist}"\n'
        return ''

    @property
    def run_cpu_list(self):
        cpulist = getattr(self, 'run_cpulist', '')
        if cpulist:
            return f'export RUN_CPU_LIST="{cpulist}"\n'
        return ''

    @property
    def flags(self):
        return getattr(self, '_flags', '')

    @flags.setter
    def flags(self, value):
        self._flags = value

    @property
    def optional_flags(self):
        return getattr(self, '_optional_flags', '')

    @optional_flags.setter
    def optional_flags(self, value):
        self._optional_flags = value

    @property
    def cflags(self):
        flags = self.flags
        if flags:
            return f'CFLAGS="{flags}" '
        return ''

    @property
    def optional_cflags(self):
        flags = self.optional_flags
        if flags:
            return f'OPTIONAL_CFLAGS="{flags}" '
        return ''

    @property
    def os(self):
        return self._os

    @os.setter
    def os(self, value):
        if isinstance(value, str):
            value = OperatingSystem.from_triple(value)
        self._os = value

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

class BuildRootImage(Image):
    '''Specialized properties for buildroot images.'''

    @property
    def use_32(self):
        return getattr(self, '_use_32', False)

    @use_32.setter
    def use_32(self, value):
        self._use_32 = value

    @property
    def symlink_sysroot(self):
        return getattr(self, '_symlink_sysroot', False)

    @symlink_sysroot.setter
    def symlink_sysroot(self, value):
        self._symlink_sysroot = value

class CrosstoolImage(Image):
    '''Specialized properties for crosstool-NG images.'''

    @property
    def patches(self):
        return getattr(self, '_patches', [])

    @patches.setter
    def patches(self, value):
        self._patches = value

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
    def qemu(self):
        return True

class MuslCrossImage(Image):
    '''Specialized properties for musl-cross images.'''

    @property
    def gcc_config(self):
        config = getattr(self, '_gcc_config', '')
        if config:
            return f'{config} '
        return ''

    @gcc_config.setter
    def gcc_config(self, value):
        self._gcc_config = value

class RiscvImage(Image):
    '''Specialized properties for RISC-V images.'''

    @property
    def processor(self):
        return self.target.split('-')[0]

    @property
    def bits(self):
        return int(re.match(r'^riscv(\d+)$', self.processor).group(1))

    @property
    def optional_flags(self):
        march = f'rv{self.bits}{self.extensions}'
        flags = f'-march={march} -mabi={self.abi}'
        if Image.optional_flags.fget(self):
            flags = f'{self.optional_flags} {flags}'
        return flags

class OtherImage(Image):
    '''Specialized properties for miscellaneous images.'''

image_types = {
    'android': AndroidImage,
    'buildroot': BuildRootImage,
    'crosstool': CrosstoolImage,
    'debian': DebianImage,
    'musl-cross': MuslCrossImage,
    'riscv': RiscvImage,
    'other': OtherImage,
}

# Get all images.
images = [Image.from_json(i) for i in load_json(f'{HOME}/config/images.json')]

# Add extensions
def add_android_extensions():
    '''Add Android extensions (null-op).'''

def add_buildroot_extensions():
    '''Add buildroot extensions (null-op).'''

def add_crosstool_extensions():
    '''Add crosstool-NG toolchain extensions (null-op).'''

def add_debian_extensions():
    '''Add Debian toolchain extensions (null-op).'''

def add_musl_cross_extensions():
    '''Add musl-cross toolchain extensions (null-op).'''

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
    add_buildroot_extensions()
    add_crosstool_extensions()
    add_debian_extensions()
    add_musl_cross_extensions()
    add_riscv_extensions()

add_extensions()

# Filter images by types.
android_images = [i for i in images if isinstance(i, AndroidImage)]
buildroot_images = [i for i in images if isinstance(i, BuildRootImage)]
crosstool_images = [i for i in images if isinstance(i, CrosstoolImage)]
debian_images = [i for i in images if isinstance(i, DebianImage)]
musl_cross_images = [i for i in images if isinstance(i, MuslCrossImage)]
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
        buildroot = f'{HOME}/docker/buildroot.sh'
        buildroot32 = f'{HOME}/docker/buildroot32.sh'
        cmake = f'{HOME}/docker/cmake.sh'
        entrypoint = f'{HOME}/docker/entrypoint.sh'
        gcc = f'{HOME}/docker/gcc.sh'
        gcc_patch = f'{HOME}/docker/gcc-patch.sh'
        musl = f'{HOME}/docker/musl.sh'
        qemu = f'{HOME}/docker/qemu.sh'
        qemu_apt = f'{HOME}/docker/qemu-apt.sh'
        riscv_gcc = f'{HOME}/docker/riscv-gcc.sh'
        shortcut = f'{HOME}/symlink/shortcut.sh'
        target_features = f'{HOME}/spec/target_features.py'
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
        self.configure(f'{buildroot}.in', buildroot, True, [
            ('BUILDROOT_VERSION', buildroot_version),
            ('JOBS', config["options"]["build_jobs"]),
        ])
        self.configure(f'{buildroot32}.in', buildroot32, True, [
            ('BUILDROOT_VERSION', buildroot_version),
            ('JOBS', config["options"]["build_jobs"]),
        ])
        self.configure(f'{entrypoint}.in', entrypoint, True, [
            ('BIN', f'"{bin_directory}"'),
        ])
        self.configure(f'{gcc}.in', gcc, True, [
            ('CROSSTOOL_VERSION', f'"{ct_version}"'),
            ('JOBS', config["options"]["build_jobs"]),
        ])
        self.configure(f'{gcc_patch}.in', gcc_patch, True, [
            ('CROSSTOOL_VERSION', f'"{ct_version}"'),
            ('JOBS', config["options"]["build_jobs"]),
        ])
        self.configure(f'{musl}.in', musl, True, [
            ('BINUTILS_VERSION', binutils_version),
            ('BINUTILS_XZ_SHA1', config['binutils']['version']['xz_sha1']),
            ('GCC_VERSION', gcc_version),
            ('GCC_XZ_SHA1', config['gcc']['version']['xz_sha1']),
            ('GMP_VERSION', gmp_version),
            ('GMP_BZ2_SHA1', config['gmp']['version']['bz2_sha1']),
            ('ISL_VERSION', isl_version),
            ('ISL_BZ2_SHA1', config['isl']['version']['bz2_sha1']),
            ('MPC_VERSION', mpc_version),
            ('MPC_GZ_SHA1', config['mpc']['version']['gz_sha1']),
            ('MPFR_VERSION', mpfr_version),
            ('MPFR_BZ2_SHA1', config['mpfr']['version']['bz2_sha1']),
            ('LINUX_HEADERS_VERSION', linux_headers_version),
            ('LINUX_HEADERS_XZ_SHA1', config['linux-headers']['version']['xz_sha1']),
            ('LINUX_VERSION', linux_version),
            ('LINUX_XZ_SHA1', config['linux']['version']['xz_sha1']),
            ('MUSL_CROSS_VERSION', musl_cross_version),
            ('MUSL_VERSION', musl_version),
            ('MUSL_GZ_SHA1', config['musl']['version']['gz_sha1']),
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
        self.configure(f'{target_features}.in', target_features, True, [
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

    def configure_musl_config(self):
        '''Configure the MUSL libc config files.'''

        template = f'{HOME}/musl/config.mak.in'
        for image in musl_cross_images:
            outfile = f'{HOME}/musl/config/{image.target}.mak'
            self.configure(template, outfile, False, [
                ('BINUTILS_VERSION', binutils_version),
                ('GCC_CONFIG', image.gcc_config),
                ('GCC_VERSION', gcc_version),
                ('GMP_VERSION', gmp_version),
                ('ISL_VERSION', isl_version),
                ('LINUX_HEADERS_VERSION', linux_headers_version),
                ('LINUX_VERSION', linux_version),
                ('MPC_VERSION', mpc_version),
                ('MPFR_VERSION', mpfr_version),
                ('MUSL_VERSION', musl_version),
                ('TARGET', image.config),
            ])

    def configure_dockerfile(
        self,
        image,
        template,
        replacements,
        use_base=True,
        use_toolchain=True,
        use_spec=True,
    ):
        '''Configure a Dockerfile from template.'''

        # These files are read in the order they're likely to change,
        # as well as compile-time.
        #   Any template files may have long compilations, and will
        #   change rarely. Qemu is an apt package, and unlikely to change.
        #   Symlinks, toolchains, and entrypoints change often, but are
        #   cheap and easy to fix.
        outfile = f'{HOME}/docker/images/Dockerfile.{image.target}'
        qemu = f'{HOME}/docker/Dockerfile.qemu.in'
        symlink = f'{HOME}/docker/Dockerfile.symlink.in'
        toolchain = f'{HOME}/docker/Dockerfile.toolchain.in'
        spec = f'{HOME}/docker/Dockerfile.spec.in'
        entrypoint = f'{HOME}/docker/Dockerfile.entrypoint.in'
        contents = []
        if use_base:
            contents.append('FROM ahuszagh/cross:base\n')
        if template is not None:
            with open(template, 'r') as file:
                contents.append(file.read())
        if image.qemu:
            with open(qemu, 'r') as file:
                contents.append(file.read())
        with open(symlink, 'r') as file:
            contents.append(file.read())
        if use_toolchain:
            with open(toolchain, 'r') as file:
                contents.append(file.read())
        if use_spec:
            with open(spec, 'r') as file:
                contents.append(file.read())
        with open(entrypoint, 'r') as file:
            contents.append(file.read())
        contents = '\n'.join(contents)

        # Add to the replacements all the shared values.
        replacements = replacements + [
            ('BIN', f'"{bin_directory}"'),
            ('ENTRYPOINT', f'"{bin_directory}/entrypoint.sh"'),
            ('FLAGS', f'"{image.flags}"'),
            ('OPTIONAL_FLAGS', f'"{image.optional_flags}"'),
            ('OS', image.os.to_triple() or 'unknown'),
            ('TARGET', image.target),
        ]

        # Replace the contents and write the output to file.
        contents = self.replace(contents, replacements)
        self.write_file(outfile, contents, False)

    def configure_cmake(self, image, template, replacements):
        '''Configure a CMake template.'''

        replacements = replacements + [
            ('PROCESSOR', image.processor),
            ('OS', image.os.to_cmake()),
        ]
        cmake = f'{HOME}/cmake/toolchain/{image.target}.cmake'
        self.configure(template, cmake, False, replacements)

    def configure_symlinks(self, image, template, replacements):
        '''Configure a symlink template.'''

        replacements = replacements + [
            ('CC_CPU_LIST', image.cc_cpu_list),
            ('FLAGS', image.cflags),
            ('HARDCODED', image.hardcoded_cpulist),
            ('LD_LIBRARY_PATH', image.ld_library_path),
            ('LD_PRELOAD', image.ld_preload),
            ('OPTIONAL_FLAGS', image.optional_cflags),
            ('RUN_CPU_LIST', image.run_cpu_list),
            ('TRIPLE', image.triple),
        ]
        symlink = f'{HOME}/symlink/toolchain/{image.target}.sh'
        self.configure(template, symlink, True, replacements)

    def configure_android(self, image):
        '''Configure an Android-SDK image.'''

        # Configure the dockerfile.
        template = f'{HOME}/docker/Dockerfile.android.in'
        self.configure_dockerfile(image, template, [
            ('ARCH', image.arch),
            ('TOOLCHAIN', image.toolchain),
        ])

        # Configure the CMake toolchain.
        cmake_template = f'{HOME}/cmake/android.cmake.in'
        self.configure_cmake(image, cmake_template, [
            ('ABI', image.abi),
            ('NDK_DIRECTORY', config['android']['ndk_directory']),
            ('SDK_VERSION', config['android']['sdk_version']),
        ])

        # Configure the symlinks.
        symlink_template = f'{HOME}/symlink/android.sh.in'
        self.configure_symlinks(image, symlink_template, [
            ('NDK_DIRECTORY', config['android']['ndk_directory']),
            ('PREFIX', f'{image.prefix}-linux-{image.system}'),
            ('SDK_VERSION', config['android']['sdk_version']),
            ('TOOLCHAIN', image.toolchain),
        ])

    def configure_buildroot(self, image):
        '''Configure a buildroot image.'''

        # Get the proper dependent parameters for our image.
        if image.symlink_sysroot:
            cmake_template = f'{HOME}/cmake/buildroot-qemu.cmake.in'
            symlink_template = f'{HOME}/symlink/buildroot-qemu-sysroot.sh.in'
        elif image.qemu:
            cmake_template = f'{HOME}/cmake/buildroot-qemu.cmake.in'
            symlink_template = f'{HOME}/symlink/buildroot-qemu.sh.in'
        else:
            cmake_template = f'{HOME}/cmake/buildroot.cmake.in'
            symlink_template = f'{HOME}/symlink/buildroot.sh.in'
        if image.use_32:
            template = f'{HOME}/docker/Dockerfile.buildroot32.in'
        else:
            template = f'{HOME}/docker/Dockerfile.buildroot.in'

        self.configure_dockerfile(image, template, [
            ('ARCH', image.processor),
            ('CONFIG', image.config),
        ])

        # Configure the CMake toolchain.
        self.configure_cmake(image, cmake_template, [
            ('TRIPLE', image.config),
        ])

        # Configure the symlinks.
        self.configure_symlinks(image, symlink_template, [
            ('ARCH', image.processor),
            ('TRIPLE', image.triple),
        ])

    def configure_crosstool(self, image):
        '''Configure a crosstool-NG image.'''

        # Configure the dockerfile.
        if image.patches:
            template = f'{HOME}/docker/Dockerfile.crosstool-patch.in'
            files = []
            for patch in image.patches:
                files += glob.glob(f'diff/{patch}.*')
            patches = [f'COPY ["{i}", "/src/diff/"]' for i in files]
            patches = '\n'.join(patches)
        else:
            template = f'{HOME}/docker/Dockerfile.crosstool.in'
            patches = ''
        self.configure_dockerfile(image, template, [
            ('ARCH', image.processor),
            ('CONFIG', image.config),
            ('PATCH', patches),
        ])

        # Get the proper dependent parameters for our image.
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
        self.configure_cmake(image, cmake_template, [
            ('TRIPLE', image.triple),
        ])

        # Configure the symlinks.
        self.configure_symlinks(image, symlink_template, [
            ('ARCH', image.processor),
            ('TRIPLE', image.triple),
        ])

    def configure_debian(self, image):
        '''Configure a debian-based docker file.'''

        # Configure the dockerfile.
        template = f'{HOME}/docker/Dockerfile.debian.in'
        self.configure_dockerfile(image, template, [
            ('ARCH', image.processor),
            ('G++', image.cxx),
            ('LIBC', image.libc),
        ])

        # Get the proper dependent parameters for our image.
        if image.os != OperatingSystem.Linux:
            raise NotImplementedError

        if image.target == 'x86_64-unknown-linux-gnu':
            cmake_template = f'{HOME}/cmake/native.cmake.in'
            symlink_template = f'{HOME}/symlink/native.sh.in'
        else:
            cmake_template = f'{HOME}/cmake/debian.cmake.in'
            symlink_template = f'{HOME}/symlink/debian.sh.in'

        # Configure the CMake toolchain.
        self.configure_cmake(image, cmake_template, [])

        # Configure the symlinks.
        self.configure_symlinks(image, symlink_template, [
            ('GCC_MAJOR', gcc_major),
            ('PREFIX', image.prefix),
            ('PROCESSOR', image.processor),
            ('OS', image.os.to_triple()),
            ('SYSTEM', image.system),
        ])

    def configure_musl(self, image):
        '''Configure a musl-cross-based image.'''

        # Get the proper dependent parameters for our image.
        os = image.os.to_cmake()
        if image.qemu:
            cmake_template = f'{HOME}/cmake/musl-qemu.cmake.in'
            symlink_template = f'{HOME}/symlink/musl-qemu.sh.in'
        else:
            cmake_template = f'{HOME}/cmake/musl.cmake.in'
            symlink_template = f'{HOME}/symlink/musl.sh.in'

        # Configure the dockerfile.
        template = f'{HOME}/docker/Dockerfile.musl.in'
        self.configure_dockerfile(image, template, [
            ('ARCH', image.processor),
            ('TRIPLE', image.config),
        ])

        # Configure the CMake toolchain.
        self.configure_cmake(image, cmake_template, [
            ('TRIPLE', image.config),
        ])

        # Configure the symlinks.
        self.configure_symlinks(image, symlink_template, [
            ('ARCH', image.processor),
            ('TRIPLE', image.config),
        ])

    def configure_riscv(self, image):
        '''Configure a RISC-V-based image.'''

        # Get the proper dependent parameters for our image.
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
        self.configure_dockerfile(image, template, [
            ('ARCH', image.processor),
            ('TRIPLE', image.triple),
        ])

        # Configure the CMake toolchain.
        self.configure_cmake(image, cmake_template, [])

        # Configure the symlinks.
        self.configure_symlinks(image, symlink_template, [
            ('ARCH', image.processor),
            ('TRIPLE', image.triple),
        ])

    def configure_other(self, image):
        '''Configure a miscellaneous image.'''

        # Configure the dockerfile.
        template = f'{HOME}/docker/Dockerfile.{image.target}.in'
        self.configure_dockerfile(image, template, [
            ('ARCH', image.target),
            ('BINDIR', bin_directory),
        ], use_base=False, use_toolchain=False, use_spec=False)

        # Configure the CMake toolchain.
        cmake_template = f'{HOME}/cmake/{image.target}.cmake.in'
        self.configure_cmake(image, cmake_template, [])

        # Configure the symlinks.
        symlink_template = f'{HOME}/symlink/{image.target}.sh.in'
        self.configure_symlinks(image, symlink_template, [])

    def run(self):
        '''Modify configuration files.'''

        VersionCommand.run(self)

        # Make the required subdirectories.
        os.makedirs(f'{HOME}/cmake/toolchain', exist_ok=True)
        os.makedirs(f'{HOME}/docker/images', exist_ok=True)
        os.makedirs(f'{HOME}/musl/config', exist_ok=True)
        os.makedirs(f'{HOME}/symlink/toolchain', exist_ok=True)

        # Configure base version info.
        cmake = f'{HOME}/cmake/cmake'
        emmake = f'{HOME}/symlink/emmake'
        make = f'{HOME}/symlink/make.in'
        self.configure(f'{cmake}.in', cmake, True, [
            ('CMAKE', f"'/usr/bin/cmake'"),
            ('WRAPPER', ''),
        ])
        self.configure(make, emmake, True, [
            ('MAKE', f"'/usr/bin/make'"),
            ('WRAPPER', 'emmake '),
        ])

        # Configure our build scripts, and other configurations.
        self.configure_scripts()
        self.configure_ctng_config()
        self.configure_musl_config()

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
        for image in buildroot_images:
            self.configure_buildroot(image)
        for image in crosstool_images:
            self.configure_crosstool(image)
        for image in debian_images:
            self.configure_debian(image)
        for image in musl_cross_images:
            self.configure_musl(image)
        for image in riscv_images:
            self.configure_riscv(image)
        for image in other_images:
            self.configure_other(image)

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
        'build_all': BuildAllCommand,
        'build_images': BuildImagesCommand,
        'build_py': BuildCommand,
        'clean': CleanCommand,
        'configure': ConfigureCommand,
        'publish': PublishCommand,
        'push': PushCommand,
        'tag': TagCommand,
        'test_images': TestImagesCommand,
        'test': TestCommand,
        'test_all': TestAllCommand,
        'version': VersionCommand,
    },
)
