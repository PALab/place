#!/bin/bash
set -e
pushd ~/place/elm
elm-make Place.elm --output ../web/place.js
cd plugins
elm-make AlazarTech.elm --output ../../web/plugins/alazartech.js
elm-make CustomScript1.elm --output ../../web/plugins/custom_script_1.js
elm-make DS345.elm --output ../../web/plugins/ds345_function_gen.js
elm-make H5Output.elm --output ../../web/plugins/h5_output.js
elm-make IQDemodulation.elm --output ../../web/plugins/iq_demodulation.js
elm-make NewFocus.elm --output ../../web/plugins/new_focus.js
elm-make PLACEDemo.elm --output ../../web/plugins/place_demo.js
elm-make PLACETemplate.elm --output $(mktemp -u /tmp/place_template_XXXXXXXXXX.js)
elm-make Polytec.elm --output ../../web/plugins/polytec.js
elm-make QuantaRay.elm --output ../../web/plugins/quanta_ray.js
elm-make SR560PreAmp.elm --output ../../web/plugins/sr560_preamp.js
elm-make SR850.elm --output ../../web/plugins/sr850_amp.js
elm-make TektronixDPO3014.elm --output ../../web/plugins/tektronix_dpo3014.js
elm-make TektronixMDO3014.elm --output ../../web/plugins/tektronix_mdo3014.js
elm-make XPSControl.elm --output ../../web/plugins/xps_control.js
elm-make ArduinoStage.elm --output ../../web/plugins/arduino_stage.js
popd
