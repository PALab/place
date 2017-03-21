#! /bin/bash

bash ${PWD}/place/test/basic.sh
if [ $? -ne 0 ]
then
    exit $?
fi

python ${PWD}/place/test/test_DS345_driver.py
if [ $? -ne 0 ]
then
    exit $?
fi
exit 0
