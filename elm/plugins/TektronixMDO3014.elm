port module TektronixMDO3014 exposing (main)

import Html exposing (program, div)
import Tektronix exposing (Model, Msg, default, updateModel, viewModel)


className =
    "MDO3014"


moduleName =
    "tektronix_mdo3014"


main : Program Never Model Msg
main =
    program
        { init = default
        , view = \model -> div [] (viewModel className model)
        , update = updateModel className moduleName
        , subscriptions = \_ -> Sub.none
        }
