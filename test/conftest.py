#!/usr/bin/env python

import os
import subprocess
import sys

test_dir = os.path.dirname(os.path.realpath(__file__))
xcross_dir = os.path.dirname(test_dir)

def pytest_configure(config):
    '''Ensure xcross is properly versioned prior to running tests.'''

    # Only version if the command isn't run via tox.
    if 'TOX_PACKAGE' in os.environ:
        return
    command = [sys.executable, f'{xcross_dir}/setup.py', 'version']
    devnull = subprocess.DEVNULL
    subprocess.check_call(command, stdout=devnull, stderr=devnull)
