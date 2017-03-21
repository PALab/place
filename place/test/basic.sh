#!/bin/bash

# run our tests from the Linux temp directory
# to avoid import conflicts
pushd /tmp

for module in \
    "place" \
    "place.alazartech" \
    "place.automate" \
    "place.automate.new_focus" \
    "place.automate.polytec" \
    "place.automate.quanta_ray" \
    "place.automate.SRS" \
    "place.automate.tektronix" \
    "place.automate.xps_control" \
    "place.scripts"
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

for module in \
    "place.alazartech.atsapi" \
    "place.automate.osci_card" \
    "place.automate.scan"
    do
        echo -n "Testing import ${module}..."
        python -c "
try:
  import ${module}
except OSError:\
  pass" >/dev/null
        if [ $? -ne 0 ]
            then
                echo "FAILED!"
                exit 99
        fi
        echo "passed."
    done

echo -n "Testing place_scan..."
place_scan --help >/dev/null
if [ $? -ne 0 ]
    then
        echo "FAILED!"
        exit 99
fi
echo "passed."

popd

