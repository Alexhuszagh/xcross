#!/bin/bash
#
# Build crosstoolsng.

set -ex

# Build up until we have the dependencies for the host.
cd /src/ct-ng-build
su crosstoolng -c "mkdir -p /home/crosstoolng/src"
su crosstoolng -c "CT_DEBUG_CT_SAVE_STEPS=1 /src/crosstoolng/bin/ct-ng build.5"
