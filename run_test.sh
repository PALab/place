#! /bin/bash
pylint -j ${CPU_COUNT} -E ${RECIPE_DIR}/place --rcfile=${RECIPE_DIR}/place/pylintrc
python -m unittest discover ${RECIPE_DIR}/place/plugins
