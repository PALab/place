module Experiment.Plugin exposing (Plugin, encode, decode)

import Json.Encode
import Json.Decode


type alias Plugin =
    { module_name : String
    , className : String
    , priority : Int
    , dataRegister : List String
    , config : Json.Encode.Value
    }


encode : Plugin -> Json.Encode.Value
encode plugin =
    Json.Encode.object
        [ ( "module_name", Json.Encode.string plugin.module_name )
        , ( "class_name", Json.Encode.string plugin.className )
        , ( "priority", Json.Encode.int plugin.priority )
        , ( "data_register", Json.Encode.list <| List.map Json.Encode.string plugin.dataRegister )
        , ( "config", plugin.config )
        ]


decode : Json.Decode.Decoder Plugin
decode =
    Json.Decode.map5
        Plugin
        (Json.Decode.field "module_name" Json.Decode.string)
        (Json.Decode.field "class_name" Json.Decode.string)
        (Json.Decode.field "priority" Json.Decode.int)
        (Json.Decode.field "data_register" (Json.Decode.list Json.Decode.string))
        (Json.Decode.field "config" Json.Decode.value)
