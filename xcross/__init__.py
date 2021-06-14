'''
    xcross
    ======

    A utility for 1-line builds from the parent host.
'''

import argparse
import collections
import os
import pathlib
import re
import subprocess
import sys
import uuid

version_info = collections.namedtuple('version_info', 'major minor patch build')

__version_major__ = '0'
__version_minor__ = '1'
__version_patch__ = '2'
__version_build__ = ''
__version_info__ = version_info(major='0', minor='1', patch='2', build='')
__version__ = '0.1.2'

# Create our arguments.
parser = argparse.ArgumentParser(description='Cross-compile C/C++ with a single command.')
# Note: this can take 1 of 3 forms:
#   1). No argument provided, have an empty command.
#   2). Provide a command as a quoted string. This is written to file exactly,
#       so it can then be called locally.
#   3). Provide arguments standard on the command-line, as a list of args.
#       If any special characters are present, it errors out.
parser.add_argument(
    dest='command',
    nargs='*',
    help='''Build command to pass to the image.
This may be provided as a list of arguments, however, this will not work if any
bash control characters are present in the argument list.''',
)
parser.add_argument(
    '--target',
    help='''The target triple for the cross-compiled architecture.
This may also be supplied via the environment variable `CROSS_TARGET`.
Ex: `--target=alpha-unknown-linux-gnu`.''',
)
parser.add_argument(
    '--dir',
    help='''The directory to share to the docker image.
This may also be supplied via the environment variable `CROSS_DIR`.
This directory may be an absolute path or relative to
the current working directory. Both the input and output arguments
must be relative to this. Defaults to `/`.
Ex: `--dir=..`''',
)
parser.add_argument(
    '-E',
    '--env',
    action='append',
    help='''Pass through an environment variable to the image.
May be provided multiple times, or as a comma-separated list of values.
If an argument is provided without a value, it's passed through using
the value in the current shell.
Ex: `-E=CXX=/usr/bin/c++,CC=/usr/bin/cc,AR`''',
)
parser.add_argument(
    '--cpu',
    help='''Set the CPU model for the compiler/Qemu emulator.
This may also be supplied via the environment variable `CROSS_CPU`.
A single CPU type may be provided. To enumerate valid CPU types
for the cross compiler, you may run `cc -mcpu=x`, where `x` is an
invalid CPU type. To enumerate valid CPU types for the Qemu emulator,
you may run `run -cpu help`.
Ex: `--cpu=e500mc`''',
)
parser.add_argument(
    '--username',
    help='''The username for the Docker Hub image.
This may also be supplied via the environment variable `CROSS_USERNAME`.
Ex: `--username=ahuszagh`''',
)
parser.add_argument(
    '--repository',
    help='''The repository for the Docker Hub image.
This may also be supplied via the environment variable `CROSS_REPOSITORY`.
Ex: `--repository=cross`''',
)
parser.add_argument(
    '--docker',
    help='''The path or name of the Docker binary.
This may also be supplied via the environment variable `CROSS_DOCKER`.
Ex: `--docker=docker`''',
)
parser.add_argument(
    '-V', '--version',
    action='version',
    version=f'%(prog)s {__version__}'
)
base_script_name = '__ahuszagh_xcross_uuid_'

def error(message, code=126, show_help=True):
    '''Print message, help, and exit on error.'''

    sys.stderr.write(f'error: {message}.\n')
    if show_help:
        parser.print_help()
    sys.exit(code)

def get_current_dir():
    return pathlib.PurePath(os.getcwd())

def get_parent_dir(args):
    directory = args.dir or get_current_dir().root
    return pathlib.PurePath(os.path.realpath(directory))

def validate_username(username):
    return re.match('^[A-Za-z0-9_-]*$', username)

def validate_repository(repository):
    return re.match('^[A-Za-z0-9_-]+$', repository)

def validate_target(target):
    return re.match('^[A-Za-z0-9_-]+$', target)

def escape_single_quote(string):
    '''Escape a single quote in a string to be quoted.'''

    # We want to quote here, but we want to make sure we don't have
    # any injections, so we escpae single quotes inside, the only
    # character which is read in a single-quoted string.

    # Since escaping quotes inside single-quotes doesn't work...
    # we use that string concatenation works for adjacent values.
    # 'aaa''bbb' is the same as 'aaabbb', so 'aaa'\''bbb' works as
    # "aaa\'bbb"
    escaped = string.replace("'", "'\\''")
    return f"'{escaped}'"

def normpath(args):
    '''Normalize our arguments for paths on Windows.'''

    if os.name != 'nt':
        return

    # We want to be very... lenient here.
    # Backslash characters are **generally** not valid
    # in most cases, except for paths on Windows.
    #
    # Only change the value if:
    #   1. The path exists
    #   2. The path contains backslashes (IE, isn't a simple command).
    #   3. The path is relative to the parent dir shared to Docker.
    parent_dir = get_parent_dir(args)
    current_dir = get_current_dir()
    for index in range(len(args.command)):
        value = args.command[index]
        if '\\' in value and os.path.exists(value):
            path = pathlib.PureWindowsPath(os.path.realpath(value))
            if path.is_relative_to(parent_dir):
                relative = os.path.relpath(path, start=current_dir)
                posix = pathlib.PurePath(relative).as_posix()
                # Quote the path, to avoid valid paths with variable
                # substitution from occurring. `${a}bc` is a valid path
                # on Windows, believe it or not.
                args.command[index] = escape_single_quote(posix)

def image_command(args):
    '''Create the image command from the argument list.'''

    if args.command is None:
        return ''
    elif len(args.command) == 1:
        # This could still be a path, but we allow any escape characters here.
        normpath(args)
        return args.command[0]

    # Now need to validate our arguments: are any control characters
    # incorrectly present? We're pretty expansive here, since we can't
    # tell the difference between `( 'hello)'` and `( hello)` with
    # `["(", hello)"]`. So, just error if we have any potentially grammatical
    # character.
    if any(re.search('[;\n\\$!(){}`]', i) for i in args.command):
        error('Invalid control characters present: use a quoted string instead', show_help=False)

    # Normalize the paths inside, in case we have Windows-style paths.
    normpath(args)

    # No need to escape any characters: we've ensured all values are simple.
    return ' '.join(args.command)

def validate_arguments(args):
    '''Validate the parsed arguments.'''

    # Normalize our arguments.
    args.target = args.target or os.environ.get('CROSS_TARGET')
    args.dir = args.dir or get_current_dir().root
    args.cpu = args.cpu or os.environ.get('CROSS_DIR')
    args.cpu = args.cpu or os.environ.get('CROSS_CPU')
    if args.username is None:
        args.username = os.environ.get('CROSS_USERNAME')
    if args.username is None:
        args.username = 'ahuszagh'
    args.repository = args.repository or os.environ.get('CROSS_REPOSITORY')
    args.repository = args.repository or 'cross'
    args.docker = args.docker or os.environ.get('CROSS_DOCKER')
    args.docker = args.docker or 'docker'

    # Validate our arguments.
    if args.target is None or not validate_target(args.target):
        error('Must provide a valid target')
    if args.username is None or not validate_username(args.username):
        error('Must provide a valid Docker Hub username')
    if args.repository is None or not validate_repository(args.repository):
        error('Must provide a valid Docker Hub repository')

def docker_command(args):
    '''Create the docker command to invoke.'''

    # Normalize our paths here.
    parent_dir = get_parent_dir(args)
    current_dir = get_current_dir()
    if not os.path.isdir(parent_dir):
        error('`dir` is not a directory')
    if not current_dir.is_relative_to(parent_dir):
        error('`dir` must be a parent of the current working directory')
    relpath = current_dir.relative_to(parent_dir).as_posix()

    # Process our environment variables.
    # We don't need to escape these, since we aren't
    # using a shell. For example, `VAR1="Some Thing"`
    # and `VAR1=Some Thing` will both be passed correctly.
    args.env = args.env or []
    env = [item for e in args.env for item in e.split(',')]

    # Process our subprocess call.
    # We need to escape every custom argument, so we
    # can ensure the args are properly passed if they
    # have spaces. We use single-quotes for the path,
    # and escape any characters and use double-quotes
    # for the command, to ensure we avoid any malicious
    # escapes. This allows us to have internal `'` characters
    # in our commands, without actually providing a dangerous escape.
    image = f'{args.repository}:{args.target}'
    if args.username:
        image = f'{args.username}/{image}'
    command = ['docker', 'run', '-t']
    for var in env:
        command += ['--env', var]
    command += ['--volume', f'{parent_dir}:/src']
    command.append(image)
    chdir = f'cd /src/{escape_single_quote(relpath)}'

    script = f"/bin/bash {escape_single_quote(args.script_name)}"
    if args.cpu:
        script = f"export CPU={escape_single_quote(args.cpu)}; {script}"
    nonroot = f'su crosstoolng -c "{script}"'
    cmd = f'{chdir} && {nonroot}'
    command += ['/bin/bash', '-c', cmd]

    return command

def main(argv=None):
    '''Entry point'''

    # Parse and validate command-line options.
    args = parser.parse_args(argv)
    args.script_name = f'{base_script_name}{uuid.uuid4().hex}'
    validate_arguments(args)

    # Try to write the command to a script,
    # Do not use `exists` or `isfile`, then open, since
    # it could be written in between the time it was queried
    # and then written. We don't actually care enough to use
    # mkstemp, and since we create the file only if it doesn't
    # exist, in practice it's identical to mkstemp.
    open_flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY
    try:
        command = image_command(args)
        fd = os.open(args.script_name, open_flags)
        with os.fdopen(fd, 'w') as file:
            file.write(command)
    except OSError as err:
        if err.errno == errno.EEXIST:
            error(f'file {args.script_name} already exists. if you believe this is an error, delete {args.script_name}', show_help=False)
        else:
            # Unexpected error.
            raise

    # Create our docker command and call the script.
    try:
        code = subprocess.call(
            docker_command(args),
            shell=False,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
    finally:
        # Guarantee we cleanup the script afterwards.
        os.remove(args.script_name)

    sys.exit(code)
