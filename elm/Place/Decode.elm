module Place.Decode exposing (fromJson)

import Json.Encode
import Json.Decode
import Place.Plugin exposing (Plugin)


fromJson : Json.Encode.Value -> Result String (List Plugin)
fromJson =
    Json.Decode.decodeValue <|
        Json.Decode.list <|
            Json.Decode.map5
                Plugin
                (Json.Decode.field "module_name" Json.Decode.string)
                (Json.Decode.field "class_name" Json.Decode.string)
                (Json.Decode.field "priority" Json.Decode.int)
                (Json.Decode.field "data_register" (Json.Decode.list Json.Decode.string))
                (Json.Decode.field "config" Json.Decode.value)
