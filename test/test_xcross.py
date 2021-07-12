#!/usr/bin/env python

import errno
import os
import pytest
import sys

# Import our local xcross.
test_dir = os.path.dirname(os.path.realpath(__file__))
xcross_dir = os.path.dirname(test_dir)
sys.path.insert(0, xcross_dir)
import xcross

os.environ['CROSS_TARGET'] = 'alpha-unknown-linux-gnu'
os.environ['CROSS_WITH_PACKAGE_MANAGERS'] = ''

def run_validate_arguments(argv):
    args = xcross.process_args(argv)
    try:
        xcross.validate_arguments(args)
        return True
    except SystemExit:
        return False

def run_get_image(argv, expected):
    args = xcross.process_args(argv)
    xcross.validate_arguments(args)
    image = xcross.get_image(args)
    assert image == expected

def run_normpath(argv, expected):
    args = xcross.process_args(argv)
    xcross.normpath(args)
    assert args.command == expected

def run_format_command(argv, expected):
    args = xcross.process_args(argv)
    actual = xcross.format_command(args)
    assert actual == expected

def run_image_command(argv, expected):
    args = xcross.process_args(argv)
    xcross.validate_arguments(args)
    actual = xcross.image_command(args, '.').splitlines()
    assert actual[0].startswith('source /etc/profile')
    assert actual[1].startswith('cd /mnt/xcross')
    assert actual[2] == expected

def run_image(args, exit_code=0):
    with pytest.raises(SystemExit) as exit_error:
        xcross.main(['--target', 'alpha-unknown-linux-gnu'] + args)
    assert exit_error.value.code == exit_code

def test_get_image():
    run_get_image([
        '--target', 'alpha-unknown-linux-gnu'
    ], 'docker.io/ahuszagh/cross:alpha-unknown-linux-gnu')
    run_get_image([
        '--target', 'alpha-unknown-linux-gnu',
        '--server', '',
    ], 'ahuszagh/cross:alpha-unknown-linux-gnu')
    run_get_image([
        '--target', 'alpha-unknown-linux-gnu',
        '--server', '',
        '--username', '',
    ], 'cross:alpha-unknown-linux-gnu')
    run_get_image([
        '--target', 'alpha-unknown-linux-gnu',
        '--image-version', '0.1',
        '--server', '',
        '--username', '',
    ], 'cross:alpha-unknown-linux-gnu-0.1')

def test_simple_format_command():
    run_format_command([], '/bin/bash')
    run_format_command(['make'], 'make')
    run_format_command(['cmake ..'], 'cmake ..')
    run_format_command(['cmake', '..'], 'cmake ..')
    run_format_command(['c++', 'main o.cc'], 'c++ "main o.cc"')

def test_single_format_command():
    run_format_command(['c++ "main o.cc"'], 'c++ "main o.cc"')
    run_format_command(['c++ main\\ o.cc'], 'c++ main\\ o.cc')
    run_format_command(['c++ main\\ "o.cc'], 'c++ main\\ "o.cc')

def test_hyphen_command():
    run_format_command(['make', '-j', '5'], 'make -j 5')
    run_format_command([
        'cmake', '..', '-DBUILD_SHARED_LIBS=OFF'
    ], 'cmake .. -DBUILD_SHARED_LIBS=OFF')

def test_normpath_windows():
    if os.name != 'nt':
        return
    run_normpath([], [])
    run_normpath(['cmake'], ['cmake'])
    run_normpath(['cmake', '..\\..'], ['cmake', "'../..'"])
    run_normpath(['.\\xcross'], ["'xcross'"])
    run_normpath(['.\\env\\shared'], ["'env/shared'"])

def test_control_characters():
    run_format_command(['$(echo `whoami`)'], '$(echo `whoami`)')
    with pytest.raises(SystemExit):
        run_format_command(['$(echo', '`whoami`)'], '')
    with pytest.raises(SystemExit):
        run_format_command(['cmake', '--build', '.', '--config', 'Release;' 'echo', '5'], '')
    with pytest.raises(SystemExit):
        run_format_command(['echo', '${var[@]}'], '')
    with pytest.raises(SystemExit):
        run_format_command(['echo', '`whoami`'], '')
    with pytest.raises(SystemExit):
        run_format_command(['c++', '"main o.cc"'], '')
    with pytest.raises(SystemExit):
        run_format_command(['c++', 'main" o.cc'], '')
    with pytest.raises(SystemExit):
        run_format_command(['c++', "main' o.cc"], '')

def test_validate_arguments():
    assert not run_validate_arguments(['--target', 'x\\a'])
    assert not run_validate_arguments(['--username', 'a#huszagh'])
    assert not run_validate_arguments(['--repository', 'cross;5'])
    assert run_validate_arguments(['--target', 'alpha-unknown-linux-gnu'])
    assert run_validate_arguments(['--username', 'ahusz05-v1_23'])
    assert run_validate_arguments(['--repository', 'cross05-v1_23'])

def test_run_image_command():
    run_image_command(['make', '-j', '5'], 'make -j 5')

def test_run_image():
    run_image(['echo', 'helloworld'])
    run_image(['c++', '--version'])
    run_image(['cl'], exit_code=127)
    # Test detached mode. Ensure we clean up at the end.
    try:
        run_image(['--detach', 'echo', 'hellworld'])
        run_image(['--detach', 'echo', 'next'])
    finally:
        run_image(['--stop'])

def windows_permissions():
    # Check we don't have permissions to write if not admin.
    # Note that Docker runs as a non-administrator on Windows,
    # so just assume that it will fails.
    command = ['touch', '/mnt/xcross/sample_xcross_file']
    run_image(command, exit_code=errno.EPERM)

def unix_permissions():
    # Make sure all files produced have the same permissions.
    # This means we properly mapped the image.
    try:
        run_image(['touch', 'sample_xcross_file'])
        st = os.stat('sample_xcross_file')
        assert(st.st_uid == os.getuid())
        assert(st.st_gid == os.getgid())
    finally:
        os.unlink('sample_xcross_file')

    # Check sudo isn't enabled.
    run_image(['which', 'sudo'], exit_code=1)

    # Test with podman: ensure permissions don't fail.
    run_image(['ls', '-la', '--engine', 'podman'])

def test_permissions():
    if xcross.os_name() == 'nt':
        windows_permissions()
    else:
        unix_permissions()
