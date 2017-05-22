port module Scan exposing (Scan, Instrument, jsonData, decoder, encoder)

{-| This module handles the web interface for a PLACE scan.


# Definition

@docs Scan, Instrument


# Ports

@docs jsonData


# Transformations

@docs decoder, encoder

-}

import Html exposing (Html, div, h1, text, br, pre, button, option, select, textarea, iframe)
import Html.Events exposing (onClick, onInput)
import Html.Attributes exposing (selected, value, rows, cols, srcdoc, property, type_)
import Json.Decode exposing (map4)
import Json.Encode exposing (Value, encode, object)
import List exposing (map, head, filter)
import WebSocket
import Result exposing (withDefault)
import Helpers exposing (..)


-----------------------
-- EXPOSED INTERFACE --
-----------------------


{-| A scan is mostly just a type and a list of instruments. Instruments are
responsible for their own configuration.
-}
type alias Scan =
    { type_ : String
    , instruments : List Instrument
    , filename : String
    , updates : Int
    , comments : String
    , plotData : Html Msg
    , showJson : Bool
    }


{-| The module will listen on this port for JSON data from plugins.
-}
port jsonData : (Json.Encode.Value -> msg) -> Sub msg



----------
-- VIEW --
----------


view : Scan -> Html Msg
view scan =
    div [] <|
        h1 [] [ text "PLACE interface" ]
            :: selectScanType scan
            :: scanView scan


scanView : Scan -> List (Html Msg)
scanView scan =
    case scan.type_ of
        "test_scan" ->
            jsonView scan

        "basic_scan" ->
            inputUpdates scan
                ++ [ filenameBox scan ]
                ++ commentBox scan
                ++ plotBox scan
                ++ jsonView scan

        otherwise ->
            []


selectScanType : Scan -> Html Msg
selectScanType scan =
    Html.p []
        [ text "Scan type: "
        , select [ onInput ChangeScanType ]
            [ anOption scan.type_ "None" "None"
            , anOption scan.type_ "test_scan" "Test scan"
            , anOption scan.type_ "basic_scan" "Basic scan"
            ]
        , button [ onClick StartScan ] [ text "Start scan" ]
        ]


inputUpdates : Scan -> List (Html Msg)
inputUpdates scan =
    [ text "Number of updates (steps): "
    , Html.input
        [ value <| toString scan.updates
        , type_ "number"
        , onInput ChangeUpdates
        ]
        []
    , br [] []
    ]


filenameBox : Scan -> Html Msg
filenameBox scan =
    Html.p []
        [ Html.text "File name: "
        , Html.input [ value scan.filename, onInput ChangeFilename ]
            []
        ]


commentBox : Scan -> List (Html Msg)
commentBox scan =
    [ text "Comments:"
    , br [] []
    , textarea [ rows 3, cols 60, value scan.comments, onInput ChangeComments ] []
    , br [] []
    ]


plotBox : Scan -> List (Html Msg)
plotBox scan =
    [ scan.plotData
    , br [] []
    ]


jsonView : Scan -> List (Html Msg)
jsonView scan =
    if scan.showJson then
        [ button [ onClick <| ChangeShowJson False ] [ text "Hide JSON" ]
        , br [] []
        , pre [] [ text <| encodeScan 4 scan ]
        ]
    else
        [ button [ onClick <| ChangeShowJson True ] [ text "Show JSON" ] ]



------------
-- UPDATE --
------------


type Msg
    = ChangeScanType String
    | ChangeFilename String
    | ChangeUpdates String
    | ChangeShowJson Bool
    | ChangeComments String
    | UpdateInstruments Json.Encode.Value
    | StartScan
    | Plot String


update : Msg -> Scan -> ( Scan, Cmd Msg )
update msg scan =
    case msg of
        ChangeScanType newValue ->
            ( { scan | type_ = newValue }, Cmd.none )

        ChangeFilename newValue ->
            ( { scan | filename = newValue }, Cmd.none )

        ChangeUpdates newValue ->
            ( { scan | updates = withDefault 1 <| String.toInt newValue }, Cmd.none )

        ChangeShowJson newValue ->
            ( { scan | showJson = newValue }, Cmd.none )

        ChangeComments newValue ->
            ( { scan | comments = newValue }, Cmd.none )

        UpdateInstruments jsonValue ->
            case decoder jsonValue of
                Err err ->
                    ( scanErrorState err, Cmd.none )

                Ok new ->
                    ( { scan | instruments = updateInstruments new scan.instruments }
                    , Cmd.none
                    )

        StartScan ->
            ( scan, WebSocket.send socket <| encodeScan 0 scan )

        Plot data ->
            ( { scan
                | plotData =
                    iframe
                        [ srcdoc data
                        , Html.Attributes.property "scrolling" (Json.Encode.string "no")
                        ]
                        []
              }
            , Cmd.none
            )



-------------------
-- SUBSCRIPTIONS --
-------------------


subscriptions : Scan -> Sub Msg
subscriptions scan =
    Sub.batch [ jsonData UpdateInstruments, WebSocket.listen socket Plot ]


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
            [ ( "scan_type", Json.Encode.string scan.type_ )
            , ( "updates", Json.Encode.int scan.updates )
            , ( "filename", Json.Encode.string scan.filename )
            , ( "comments", Json.Encode.string scan.comments )
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
        { init = ( scanDefaultState, Cmd.none )
        , view = view
        , update = update
        , subscriptions = subscriptions
        }



-------------------
-- PRESET STATES --
-------------------


scanDefaultState : Scan
scanDefaultState =
    { type_ = "None"
    , instruments = []
    , filename = "/tmp/place_tmp.hdf5"
    , updates = 1
    , comments = ""
    , plotData = text ""
    , showJson = False
    }


scanErrorState : String -> Scan
scanErrorState err =
    { type_ = "None"
    , instruments = []
    , filename = ""
    , updates = 0
    , comments = err
    , plotData = Html.strong [] [ text "There was an error!" ]
    , showJson = True
    }
