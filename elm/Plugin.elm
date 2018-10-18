module Plugin exposing (Plugin, decode, encode)

import Json.Decode
import Json.Encode


{-| Configuration data for a PLACE plugin.
-}
type alias Plugin =
    { pythonModuleName : String
    , pythonClassName : String
    , elmModuleName : String
    , priority : Int
    , dataRegister : List String
    , config : Json.Encode.Value
    , progress : Json.Encode.Value
    }


decode : Json.Decode.Decoder Plugin
decode =
    Json.Decode.map7
        Plugin
        (Json.Decode.field "python_module_name" Json.Decode.string)
        (Json.Decode.field "python_class_name" Json.Decode.string)
        (Json.Decode.field "elm_module_name" Json.Decode.string)
        (Json.Decode.field "priority" Json.Decode.int)
        (Json.Decode.field "data_register" (Json.Decode.list Json.Decode.string))
        (Json.Decode.field "config" Json.Decode.value)
        (Json.Decode.field "progress" Json.Decode.value)


encode : Plugin -> Json.Encode.Value
encode plugin =
    Json.Encode.object
        [ ( "python_module_name", Json.Encode.string plugin.pythonModuleName )
        , ( "python_class_name", Json.Encode.string plugin.pythonClassName )
        , ( "elm_module_name", Json.Encode.string plugin.elmModuleName )
        , ( "priority", Json.Encode.int plugin.priority )
        , ( "data_register", Json.Encode.list <| List.map Json.Encode.string plugin.dataRegister )
        , ( "config", plugin.config )
        , ( "progress", plugin.config )
        ]
