#! /bin/bash
pylint -E ${RECIPE_DIR}/place --rcfile=${RECIPE_DIR}/place/pylintrc
#python -m unittest discover ${RECIPE_DIR}/place/plugins
