#!/bin/bash
set -e
elm-make Place.elm --output ../placeweb/static/placeweb/Place.js
cd plugins
elm-make ATS9440.elm --output ../../placeweb/static/placeweb/plugins/ATS9440.js
elm-make ATS660.elm --output ../../placeweb/static/placeweb/plugins/ATS660.js
elm-make CustomScript1.elm --output ../../placeweb/static/placeweb/plugins/CustomScript1.js
#elm-make DS345.elm --output ../../placeweb/static/placeweb/plugins/DS345.js
#elm-make H5Output.elm --output ../../placeweb/static/placeweb/plugins/H5Output.js
#elm-make IQDemodulation.elm --output ../../placeweb/static/placeweb/plugins/IQDemodulation.js
#elm-make NewFocus.elm --output ../../placeweb/static/placeweb/plugins/NewFocus.js
elm-make PlaceDemo.elm --output ../../placeweb/static/placeweb/plugins/PlaceDemo.js
elm-make PLACETemplate.elm --output $(mktemp -u /tmp/PlaceTemplate_XXXXXXXXXX.js)
elm-make Polytec.elm --output ../../placeweb/static/placeweb/plugins/Polytec.js
elm-make QuantaRay.elm --output ../../placeweb/static/placeweb/plugins/QuantaRay.js
elm-make SR560PreAmp.elm --output ../../placeweb/static/placeweb/plugins/SR560PreAmp.js
#elm-make SR850.elm --output ../../placeweb/static/placeweb/plugins/SR850.js
#elm-make TektronixDPO3014.elm --output ../../placeweb/static/placeweb/plugins/TektronixDPO3014.js
#elm-make TektronixMDO3014.elm --output ../../placeweb/static/placeweb/plugins/TektronixMDO3014.js
elm-make LongStage.elm --output ../../placeweb/static/placeweb/plugins/LongStage.js
elm-make ShortStage.elm --output ../../placeweb/static/placeweb/plugins/ShortStage.js
elm-make RotationalStage.elm --output ../../placeweb/static/placeweb/plugins/RotationalStage.js
#elm-make ArduinoStage.elm --output ../../placeweb/static/placeweb/plugins/ArduinoStage.js
elm-make MokuLab.elm --output ../../placeweb/static/placeweb/plugins/MokuLab.js
cd ..
