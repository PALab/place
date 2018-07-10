module Plugin exposing (Model, encode, decode)

import Json.Encode
import Json.Decode


type alias Model =
    { pythonModuleName : String
    , pythonClassName : String
    , elmModuleName : String
    , priority : Int
    , dataRegister : List String
    , config : Json.Encode.Value
    }


encode : Model -> Json.Encode.Value
encode plugin =
    Json.Encode.object
        [ ( "python_module_name", Json.Encode.string plugin.pythonModuleName )
        , ( "python_class_name", Json.Encode.string plugin.pythonClassName )
        , ( "elm_module_name", Json.Encode.string plugin.elmModuleName )
        , ( "priority", Json.Encode.int plugin.priority )
        , ( "data_register", Json.Encode.list <| List.map Json.Encode.string plugin.dataRegister )
        , ( "config", plugin.config )
        ]


decode : Json.Decode.Decoder Model
decode =
    Json.Decode.map6
        Model
        (Json.Decode.field "python_module_name" Json.Decode.string)
        (Json.Decode.field "python_class_name" Json.Decode.string)
        (Json.Decode.field "elm_module_name" Json.Decode.string)
        (Json.Decode.field "priority" Json.Decode.int)
        (Json.Decode.field "data_register" (Json.Decode.list Json.Decode.string))
        (Json.Decode.field "config" Json.Decode.value)
