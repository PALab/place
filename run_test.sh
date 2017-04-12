#! /bin/bash

bash ${PWD}/place/test/basic.sh
if [ $? -ne 0 ]
then
    exit $?
fi

python ${PWD}/place/test/test_ds345_driver.py
if [ $? -ne 0 ]
then
    exit $?
fi
exit 0

python ${PWD}/place/test/test_oscicard2.py
if [ $? -ne 0 ]
then
    exit $?
fi
exit 0
