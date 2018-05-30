#!/bin/bash
set -e
elm-make Place.elm --output ../web/static/web/Place.js
cd plugins
elm-make AlazarTech.elm --output ../../web/static/web/plugins/AlazarTech.js
elm-make CustomScript1.elm --output ../../web/static/web/plugins/CustomScript1.js
elm-make DS345.elm --output ../../web/static/web/plugins/DS345.js
elm-make H5Output.elm --output ../../web/static/web/plugins/H5Output.js
elm-make IQDemodulation.elm --output ../../web/static/web/plugins/IQDemodulation.js
elm-make NewFocus.elm --output ../../web/static/web/plugins/NewFocus.js
elm-make PlaceDemo.elm --output ../../web/static/web/plugins/PlaceDemo.js
elm-make PLACETemplate.elm --output $(mktemp -u /tmp/PlaceTemplate_XXXXXXXXXX.js)
elm-make Polytec.elm --output ../../web/static/web/plugins/Polytec.js
elm-make QuantaRay.elm --output ../../web/static/web/plugins/QuantaRay.js
elm-make SR560PreAmp.elm --output ../../web/static/web/plugins/SR560PreAmp.js
elm-make SR850.elm --output ../../web/static/web/plugins/SR850.js
elm-make TektronixDPO3014.elm --output ../../web/static/web/plugins/TektronixDPO3014.js
elm-make TektronixMDO3014.elm --output ../../web/static/web/plugins/TektronixMDO3014.js
elm-make XPSControl.elm --output ../../web/static/web/plugins/XPSControl.js
elm-make ArduinoStage.elm --output ../../web/static/web/plugins/ArduinoStage.js
elm-make MokuLab.elm --output ../../web/static/web/plugins/MokuLab.js
cd ..
