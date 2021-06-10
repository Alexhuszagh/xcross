import glob
import re
import os
import setuptools
import shutil
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


class ConfigureCommand(Command):
    '''A custom command to configure any template files.'''

    description = 'configure template files'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        '''Modify configuration files.'''

        # Read contents.
        xcross = f'{HOME}/xcross/__init__.py'
        shell = f'{HOME}/docker/version.sh'
        with open(f'{xcross}.in', 'r') as file:
            xcross_contents = file.read()
        with open(f'{shell}.in', 'r') as file:
           shell_contents = file.read()

        # Patch xcross.
        xcross_contents = xcross_contents.replace('^VERSION_MAJOR^', f"'{major}'")
        xcross_contents = xcross_contents.replace('^VERSION_MINOR^', f"'{minor}'")
        xcross_contents = xcross_contents.replace('^VERSION_PATCH^', f"'{patch}'")
        xcross_contents = xcross_contents.replace('^VERSION_BUILD^', f"'{build}'")
        xcross_contents = xcross_contents.replace('^VERSION_INFO^', f"version_info(major='{major}', minor='{minor}', patch='{patch}', build='{build}')")
        xcross_contents = xcross_contents.replace('^VERSION^', f"'{version}'")

        # Patch version.
        shell_contents = shell_contents.replace('^VERSION_MAJOR^', f"'{major}'")
        shell_contents = shell_contents.replace('^VERSION_MINOR^', f"'{minor}'")
        shell_contents = shell_contents.replace('^VERSION_PATCH^', f"'{patch}'")
        shell_contents = shell_contents.replace('^VERSION_BUILD^', f"'{build}'")
        shell_contents = shell_contents.replace('^VERSION_INFO^', f"('{major}' '{minor}' '{patch}' '{build}')")
        shell_contents = shell_contents.replace('^VERSION^', f"'{version}'")

        # Write contents
        with open(xcross, 'w') as file:
            file.write(xcross_contents)
        with open(shell, 'w') as file:
            file.write(shell_contents)


class BuildPy(build_py):
    """Override build.py to configure builds."""

    def run(self):
        self.run_command('configure')
        build_py.run(self)


script = f'{HOME}/bin/xcross'
if len(sys.argv) >= 2 and sys.argv[1] == 'py2exe':
    params = {
        'console': [{
            'script': f'{HOME}/xcross/__main__.py',
            'dest_base': 'xcross',
            #'version': py2exe_version,
            'description': description,
            'comments': long_description,
            'product_name': 'xcross',
            #'product_version': py2exe_version,
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
        'build_py': BuildPy,
        'clean': CleanCommand,
        'configure': ConfigureCommand,
    },
)
