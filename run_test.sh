#! /bin/bash
bash ${SRC_DIR}/place/test/basic.sh
pylint -j ${CPU_COUNT} -E ${RECIPE_DIR}/place --rcfile=${RECIPE_DIR}/place/pylintrc
pylint -j ${CPU_COUNT} -E ${RECIPE_DIR}/samples/*.py --rcfile=${RECIPE_DIR}/place/pylintrc
python ${SRC_DIR}/place/test/test_ds345_driver.py
python ${SRC_DIR}/place/test/test_oscicard2.py
python ${SRC_DIR}/place/test/test_cc.py
python ${SRC_DIR}/place/test/test_tcc.py
python ${SRC_DIR}/place/test/test_ats_input_range.py
