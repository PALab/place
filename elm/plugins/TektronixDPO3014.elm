port module TektronixDPO3014 exposing (main)

import Html exposing (program, div)
import Json.Encode
import Tektronix exposing (Model, Msg(UpdateProgress), default, updateModel, viewModel)


port processProgress : (Json.Encode.Value -> msg) -> Sub msg


pythonClassName =
    "DPO3014"


pythonModuleName =
    "tektronix_dpo3014"


elmModuleName =
    "TektronixDPO3014"


main : Program Never Model Msg
main =
    program
        { init = default
        , view = \model -> div [] (viewModel pythonClassName model)
        , update = updateModel pythonClassName pythonModuleName elmModuleName
        , subscriptions = always <| processProgress UpdateProgress
        }
