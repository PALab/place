port module Scan exposing (Scan, Instrument, requestJson, jsonData, decoder, encoder)

{-| This module handles the web interface for a PLACE scan.


# Definition

@docs Scan, Instrument


# Ports

@docs requestJson, jsonData


# Transformations

@docs decoder, encoder

-}

import Html exposing (Html, div, h1, text, br, pre, button, option, select)
import Html.Events exposing (onClick, onInput)
import Html.Attributes exposing (id, selected, value)
import Json.Decode exposing (map4)
import Json.Encode exposing (Value, encode, object)
import List exposing (map, head, filter)
import WebSocket


-----------------------
-- EXPOSED INTERFACE --
-----------------------


{-| A scan is currently just a type and a list of instruments. Instruments are
responsible for their own configuration.
-}
type alias Scan =
    { scan_type : String
    , instruments : List Instrument
    }


{-| When this command is sent to a plugin, the plugin should reply with its
JSON data.
-}
port requestJson : String -> Cmd msg


{-| The module will listen on this port for JSON data from plugins.
-}
port jsonData : (Json.Encode.Value -> msg) -> Sub msg



----------
-- VIEW --
----------


view : Scan -> Html Msg
view scan =
    div []
        [ h1 [] [ text "PLACE interface" ]
        , text "Scan type: "
        , select [ onInput ChangeScanType ]
            [ option
                [ value "None", selected (scan.scan_type == "None") ]
                [ text "None" ]
            , option
                [ value "scan_point_test", selected (scan.scan_type == "scan_point_test") ]
                [ text "Point scan (test)" ]
            ]
        , br [] []
        , button [ onClick StartScan ] [ text "Start Scan" ]
        , button [ onClick RequestJson ] [ text "Preview JSON" ]

        {- debug code -}
        , br [] []
        , pre [] [ text <| encodeScan 4 scan ]

        {- end debug code -}
        ]



------------
-- UPDATE --
------------


type Msg
    = ChangeScanType String
    | UpdateInstruments Json.Encode.Value
    | StartScan
    | RequestJson


update : Msg -> Scan -> ( Scan, Cmd Msg )
update msg scan =
    case msg of
        ChangeScanType newValue ->
            ( { scan | scan_type = newValue }, Cmd.none )

        UpdateInstruments jsonValue ->
            case decoder jsonValue of
                Err err ->
                    ( { scan_type = err, instruments = [] }, Cmd.none )

                Ok new ->
                    ( { scan | instruments = updateInstruments new scan.instruments }
                    , Cmd.none
                    )

        StartScan ->
            ( scan
            , Cmd.batch
                [ requestJson "scan"
                , WebSocket.send socket <| encodeScan 0 scan
                ]
            )

        RequestJson ->
            ( scan, requestJson "scan" )



-------------------
-- SUBSCRIPTIONS --
-------------------


subscriptions : Scan -> Sub Msg
subscriptions scan =
    Sub.batch [ jsonData UpdateInstruments, WebSocket.keepAlive socket ]


socket =
    "ws://localhost:9130"



----------------
-- INSTRUMENT --
----------------


{-| All instruments that are used with PLACE must include three things:

1.  A `module_name`, which should match the name of the plugin directory and
    the Python module used to run the instrument.
2.  A 'class_name', which should match the Python class desired form the module.
3.  JSON configuration data, which will be passed into the class.

-}
type alias Instrument =
    { module_name : String
    , class_name : String
    , priority : Int
    , config : Value
    }


{-| Decode a JSON value into an instrument object list or an error string.
-}
decoder : Value -> Result String (List Instrument)
decoder =
    Json.Decode.decodeValue <|
        Json.Decode.list <|
            map4
                Instrument
                (Json.Decode.field "module_name" Json.Decode.string)
                (Json.Decode.field "class_name" Json.Decode.string)
                (Json.Decode.field "priority" Json.Decode.int)
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
        , ( "priority", Json.Encode.int instrument.priority )
        , ( "config", instrument.config )
        ]



-------------
-- HELPERS --
-------------


encodeScan : Int -> Scan -> String
encodeScan indent scan =
    encode indent <|
        object
            [ ( "scan_type", Json.Encode.string scan.scan_type )
            , ( "instruments", encoder scan.instruments )
            ]


{-| Replaces all instruments matching the module name with the instruments in
the new list.
-}
updateInstruments : List Instrument -> List Instrument -> List Instrument
updateInstruments newData oldData =
    case head newData of
        Nothing ->
            oldData

        Just data ->
            if data.class_name == "None" then
                filter (notModule data.module_name) oldData
            else
                newData ++ filter (notModule data.module_name) oldData


notModule : String -> Instrument -> Bool
notModule moduleName instrument =
    moduleName /= instrument.module_name



----------
-- MAIN --
----------


main : Program Never Scan Msg
main =
    Html.program
        { init = ( { scan_type = "None", instruments = [] }, Cmd.none )
        , view = view
        , update = update
        , subscriptions = subscriptions
        }
