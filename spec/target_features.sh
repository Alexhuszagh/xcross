#!/bin/bash
# Script to write the target features for the target.

set -ex

export DEBIAN_FRONTEND="noninteractive"

# Install dependencies. We store the installed
# dependencies so we don't accidentally delete
# necessary files, and we get rid of everything
# that was only required for the build.
apt-get update
before_installed=($(apt -qq list --installed 2>/dev/null | cut -d '/' -f 1))
apt-get install --assume-yes --no-install-recommends \
    python3
after_installed=($(apt -qq list --installed 2>/dev/null | cut -d '/' -f 1))

# Calculate the packages we need to remove later.
diff=()
for i in "${after_installed[@]}"; do
    skip=
    for j in "${before_installed[@]}"; do
        [[ $i == $j ]] && { skip=1; break; }
    done
    [[ -n $skip ]] || diff+=("$i")
done
declare -p diff

# Determine the target features and write to file.
python3 /target_features.py

# Cleanup
apt-get remove --purge --assume-yes "${diff[@]}"
apt-get autoremove --assume-yes
