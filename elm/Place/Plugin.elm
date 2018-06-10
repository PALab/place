module Place.Plugin exposing (Plugin)

import Json.Encode


type alias Plugin =
    { module_name : String
    , className : String
    , priority : Int
    , dataRegister : List String
    , config : Json.Encode.Value
    }
