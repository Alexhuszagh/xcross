#!/usr/bin/env python

import os
import pathlib
import pytest
import sys

# Import our local xcross.
test_dir = os.path.dirname(os.path.realpath(__file__))
xcross_dir = os.path.dirname(test_dir)
sys.path.insert(0, xcross_dir)
import xcross

os.environ['CROSS_TARGET'] = 'alpha-unknown-linux-gnu'

def run_validate_arguments(argv):
    args = xcross.process_args(argv)
    try:
        xcross.validate_arguments(args)
        return True
    except SystemExit:
        return False

def run_normpath(argv, expected):
    args = xcross.process_args(argv)
    xcross.normpath(args)
    assert args.command == expected

def run_image_command(argv, expected):
    args = xcross.process_args(argv)
    actual = xcross.image_command(args)
    assert actual == expected

def test_simple_image_command():
    run_image_command([], '')
    run_image_command(['make'], 'make')
    run_image_command(['cmake ..'], 'cmake ..')
    run_image_command(['cmake', '..'], 'cmake ..')
    run_image_command(['c++', 'main o.cc'], 'c++ "main o.cc"')

def test_single_image_command():
    run_image_command(['c++ "main o.cc"'], 'c++ "main o.cc"')
    run_image_command(['c++ main\\ o.cc'], 'c++ main\\ o.cc')
    run_image_command(['c++ main\\ "o.cc'], 'c++ main\\ "o.cc')

def test_hyphen_command():
    run_image_command(['make', '-j', '5'], 'make -j 5')
    run_image_command(['cmake', '..', '-DBUILD_SHARED_LIBS=OFF'], 'cmake .. -DBUILD_SHARED_LIBS=OFF')

def test_normpath_windows():
    if os.name != 'nt':
        return
    run_normpath([], [])
    run_normpath(['cmake'], ['cmake'])
    run_normpath(['cmake', '..\\..'], ['cmake', "'../..'"])
    run_normpath(['.\\xcross'], ["'xcross'"])
    run_normpath(['.\\env\\shared'], ["'env/shared'"])

def test_control_characters():
    run_image_command(['$(echo `whoami`)'], '$(echo `whoami`)')
    with pytest.raises(SystemExit):
        run_image_command(['$(echo', '`whoami`)'], '')
    with pytest.raises(SystemExit):
        run_image_command(['cmake', '--build', '.', '--config', 'Release;' 'echo', '5'], '')
    with pytest.raises(SystemExit):
        run_image_command(['echo', '${var[@]}'], '')
    with pytest.raises(SystemExit):
        run_image_command(['echo', '`whoami`'], '')
    with pytest.raises(SystemExit):
        run_image_command(['c++', '"main o.cc"'], '')
    with pytest.raises(SystemExit):
        run_image_command(['c++', 'main" o.cc'], '')
    with pytest.raises(SystemExit):
        run_image_command(['c++', "main' o.cc"], '')

def test_validate_arguments():
    assert not run_validate_arguments(['--target', 'x\\a'])
    assert not run_validate_arguments(['--username', 'a#huszagh'])
    assert not run_validate_arguments(['--repository', 'cross;5'])
    assert run_validate_arguments(['--target', 'alpha-unknown-linux-gnu'])
    assert run_validate_arguments(['--username', 'ahusz05-v1_23'])
    assert run_validate_arguments(['--repository', 'cross05-v1_23'])
