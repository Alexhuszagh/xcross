#!/bin/bash
#
# Add non-root user to build libraries to.

set -ex

adduser --disabled-password --gecos "" crosstoolng
