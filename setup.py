import distutils.cmd
import re
import os
import setuptools
import shutil

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

# Read the long description.
with open(f'{HOME}/README.md') as file:
    long_description = file.read()


class CleanCommand(distutils.cmd.Command):
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


class ConfigureCommand(distutils.cmd.Command):
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
        xcross = f'{HOME}/bin/xcross'
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


setuptools.setup(
    name="xcross",
    author="Alex Huszagh",
    author_email="ahuszagh@gmail.com",
    version=version,
    scripts=[f'{HOME}/bin/xcross'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>3.6.0',
    description="Zero-setup cross compilation.",
    license="Unlicense",
    keywords="compilers cross-compilation embedded",
    url="https://github.com/Alexhuszagh/xcross",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: The Unlicense (Unlicense)',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Embedded Systems',
    ],
    cmdclass={
        'clean': CleanCommand,
        'configure': ConfigureCommand,
    },
)
