module Instrument exposing (Instrument, decoder, encoder)

{-| This module supports PLACE instrument plugins.

Since this module is just a type alias, it is not necessary that plugins import
this module. However, doing so will enforce proper typing and reduce errors.

# Definition
@docs Instrument

# Transformations
@docs decoder, encoder
-}

import Json.Decode exposing (map3)
import Json.Encode exposing (Value)
import List exposing (map)


{-| All instruments that are used with PLACE must include three things:

   1. A `module_name`, which should match the name of the plugin directory and
      the Python module used to run the instrument.
   2. A 'class_name', which should match the Python class desired form the module.
   3. JSON configuration data, which will be passed into the class.
-}
type alias Instrument =
    { module_name : String
    , class_name : String
    , config : Value
    }


{-| Decode a JSON value into an instrument object list or an error string.
-}
decoder : Value -> Result String (List Instrument)
decoder =
    Json.Decode.decodeValue <|
        Json.Decode.list <|
            map3
                Instrument
                (Json.Decode.field "module_name" Json.Decode.string)
                (Json.Decode.field "class_name" Json.Decode.string)
                (Json.Decode.field "config" Json.Decode.value)


{-| Encode an instrument object list into a JSON value.
-}
encoder : List Instrument -> Value
encoder instruments =
    Json.Encode.list <| map singleEncoder instruments


singleEncoder : Instrument -> Value
singleEncoder instrument =
    Json.Encode.object
        [ ( "module_name", Json.Encode.string instrument.module_name )
        , ( "class_name", Json.Encode.string instrument.class_name )
        , ( "config", instrument.config )
        ]
