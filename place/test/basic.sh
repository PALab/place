#!/bin/bash

# This file is a robust import test for PLACE

# run our tests from the Linux temp directory
# to avoid import conflicts
pushd /tmp

for module in \
    "place" \
    "place.plugins" \
    "place.plugins.alazartech"
    do
        echo -n "Testing import ${module}..."
        python -c "import ${module}" >/dev/null
        if [ $? -ne 0 ]
            then
                echo "FAILED!"
                exit 99
        fi
        echo "passed."
    done

popd

