port module Place exposing (main)

import Html exposing (Html)
import Html.Events
import Html.Attributes
import Json.Decode
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
    , instruments : List Module
    , postprocess : List Module
    , directory : String
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
    Html.div [] <|
        Html.h1 [] [ Html.text "PLACE interface" ]
            :: selectScanType scan
            :: inputUpdates scan
            :: directoryBox scan
            :: commentBox scan
            :: plotBox scan
            ++ jsonView scan


selectScanType : Scan -> Html Msg
selectScanType scan =
    Html.p []
        [ Html.text "Scan type: "
        , Html.select [ Html.Events.onInput ChangeType ]
            [ Html.option [ Html.Attributes.value "basic_scan", Html.Attributes.selected (scan.type_ == "basic_scan") ] [ Html.text "Basic Scan" ]
            , Html.option [ Html.Attributes.value "osldv_scan", Html.Attributes.selected (scan.type_ == "osldv_scan") ] [ Html.text "OSLDV Scan" ]
            , Html.option [ Html.Attributes.value "dwdcldv_scan", Html.Attributes.selected (scan.type_ == "dwdcldv_scan") ] [ Html.text "DWDCLDV Scan" ]
            ]
        , Html.button [ Html.Events.onClick StartScan ] [ Html.text "Start scan" ]
        ]


inputUpdates : Scan -> Html Msg
inputUpdates scan =
    Html.p []
        [ Html.text "Number of updates (steps): "
        , Html.input
            [ Html.Attributes.value <| toString scan.updates
            , Html.Attributes.type_ "number"
            , Html.Events.onInput ChangeUpdates
            ]
            []
        , Html.br [] []
        ]


directoryBox : Scan -> Html Msg
directoryBox scan =
    Html.p []
        [ Html.text "Save directory: "
        , Html.input [ Html.Attributes.value scan.directory, Html.Events.onInput ChangeDirectory ]
            []
        ]


commentBox : Scan -> Html Msg
commentBox scan =
    Html.p []
        [ Html.text "Comments:"
        , Html.br [] []
        , Html.textarea [ Html.Attributes.rows 3, Html.Attributes.cols 60, Html.Attributes.value scan.comments, Html.Events.onInput ChangeComments ] []
        , Html.br [] []
        ]


plotBox : Scan -> List (Html Msg)
plotBox scan =
    [ scan.plotData
    , Html.br [] []
    ]


jsonView : Scan -> List (Html Msg)
jsonView scan =
    if scan.showJson then
        [ Html.button [ Html.Events.onClick <| ChangeShowJson False ] [ Html.text "Hide JSON" ]
        , Html.br [] []
        , Html.pre [] [ Html.text <| encodeScan 4 scan ]
        ]
    else
        [ Html.button [ Html.Events.onClick <| ChangeShowJson True ] [ Html.text "Show JSON" ] ]



------------
-- UPDATE --
------------


type Msg
    = ChangeType String
    | ChangeDirectory String
    | ChangeUpdates String
    | ChangeShowJson Bool
    | ChangeComments String
    | UpdateModules Json.Encode.Value
    | StartScan
    | Plot String


update : Msg -> Scan -> ( Scan, Cmd Msg )
update msg scan =
    case msg of
        ChangeType newValue ->
            ( { scan | type_ = newValue }, Cmd.none )

        ChangeDirectory newValue ->
            ( { scan | directory = newValue }, Cmd.none )

        ChangeUpdates newValue ->
            ( { scan | updates = withDefault 1 <| String.toInt newValue }, Cmd.none )

        ChangeShowJson newValue ->
            ( { scan | showJson = newValue }, Cmd.none )

        ChangeComments newValue ->
            ( { scan | comments = newValue }, Cmd.none )

        UpdateModules jsonValue ->
            case decoder jsonValue of
                Err err ->
                    ( scanErrorState err, Cmd.none )

                Ok new ->
                    ( updateInstruments new scan
                    , Cmd.none
                    )

        StartScan ->
            ( scan, WebSocket.send socket <| encodeScan 0 scan )

        Plot data ->
            ( { scan
                | plotData =
                    Html.iframe
                        [ Html.Attributes.srcdoc data
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
    Sub.batch [ jsonData UpdateModules, WebSocket.listen socket Plot ]


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
type alias Module =
    { module_name : String
    , class_name : String
    , priority : Int
    , config : Value
    }


{-| Decode a JSON value into an instrument object list or an error string.
-}
decoder : Value -> Result String (List Module)
decoder =
    Json.Decode.decodeValue <|
        Json.Decode.list <|
            Json.Decode.map4
                Module
                (Json.Decode.field "module_name" Json.Decode.string)
                (Json.Decode.field "class_name" Json.Decode.string)
                (Json.Decode.field "priority" Json.Decode.int)
                (Json.Decode.field "config" Json.Decode.value)


{-| Encode an instrument object list into a JSON value.
-}
encoder : List Module -> Value
encoder instruments =
    Json.Encode.list <| map singleEncoder instruments


singleEncoder : Module -> Value
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
            , ( "directory", Json.Encode.string scan.directory )
            , ( "comments", Json.Encode.string scan.comments )
            , ( "instruments", encoder scan.instruments )
            , ( "postprocessing", encoder scan.postprocess )
            ]


{-| Replaces all instruments matching the module name with the instruments in
the new list.
-}
updateInstruments : List Module -> Scan -> Scan
updateInstruments newData scan =
    case head newData of
        Nothing ->
            scan

        Just data ->
            case data.module_name of
                "iq_demod" ->
                    if data.class_name == "None" then
                        { scan | postprocess = [] }
                    else
                        { scan | postprocess = [ data ] }

                otherwise ->
                    if data.class_name == "None" then
                        { scan | instruments = filter (notModule data.module_name) scan.instruments }
                    else
                        { scan | instruments = (newData ++ filter (notModule data.module_name) scan.instruments) }


notModule : String -> Module -> Bool
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
    { type_ = "basic_scan"
    , instruments = []
    , postprocess = []
    , directory = "/tmp/place_tmp"
    , updates = 1
    , comments = ""
    , plotData = Html.text ""
    , showJson = False
    }


scanErrorState : String -> Scan
scanErrorState err =
    { type_ = "basic_scan"
    , instruments = []
    , postprocess = []
    , directory = ""
    , updates = 0
    , comments = err
    , plotData = Html.strong [] [ Html.text "There was an error!" ]
    , showJson = True
    }
